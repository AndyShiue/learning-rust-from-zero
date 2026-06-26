# 手寫 reactor

## 本集目標

把前幾集的喚醒模式接到**真實的 I/O**——做出一個 reactor，讓我們的 runtime 第一次能處理網路連線。

## 概念說明

### executor 一行不改

這集有個讓人安心的核心訊息：**executor 完全沿用第 12 集**。`Task`、`spawn<T>`、`JoinHandle<T>`、`Shared<T>`、`block_on` 一行都不用改。

我們唯一要換掉的是「誰來 `wake`」。前面是 `Delay` 自己開一條計時 thread 來 `wake`；現在改成一條 **reactor thread**，它睡在 `mio::Poll` 上等真實的 I/O，醒來後找到對應的 `Waker` 把它 `wake()`。

要加的東西只有兩塊：一個 `Reactor`，以及兩個 I/O `Future`（`Accept` 和 `Read`）。

### 第一塊：`Reactor`

`Reactor` 跑在自己的 thread 上，睡在 `mio::Poll` 上。而那些跑在 executor thread 上的 `Future`，要怎麼跟它溝通？答案是**透過共享狀態，而不是傳訊息**。三樣東西用 `Arc` 共用：

- **`Registry`**（mio 的）：`Future` 拿它直接登記 / 取消 socket。
- **`AtomicUsize`**：reactor 用它替每個來源自分配獨一無二的 `Token`。
- **`Mutex<HashMap<Token, Waker>>`**：`Future` 在執行時把自己的 `Waker` 寫進去（用 `Token` 當鑰匙），reactor 收到事件後就照 `Token` 取出來 `wake`。

```rust,no_run
# extern crate mio;
# use std::cell::RefCell;
# use std::collections::{HashMap, VecDeque};
# use std::future::Future;
# use std::io::Read as _;
# use std::pin::Pin;
# use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
# use std::sync::{Arc, Mutex};
# use std::task::{Context, Poll, Wake, Waker};
# use mio::event::Source;
# use mio::net::{TcpListener, TcpStream};
# use mio::{Events, Interest, Poll as MioPoll, Registry, Token};
#
# struct Executor {
#     ready_queue: Mutex<VecDeque<Arc<Task>>>,
#     thread: std::thread::Thread,
#     task_count: AtomicUsize,
# }
# impl Executor {
#     fn new() -> Executor {
#         Executor {
#             ready_queue: Mutex::new(VecDeque::new()),
#             thread: std::thread::current(),
#             task_count: AtomicUsize::new(0),
#         }
#     }
# }
# struct Task {
#     future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
#     executor: Arc<Executor>,
#     queued: AtomicBool,
# }
# impl Task {
#     fn schedule(self: &Arc<Self>) {
#         if !self.queued.swap(true, Ordering::AcqRel) {
#             self.executor.ready_queue.lock().unwrap().push_back(self.clone());
#             self.executor.thread.unpark();
#         }
#     }
# }
# impl Wake for Task {
#     fn wake(self: Arc<Self>) { self.schedule(); }
#     fn wake_by_ref(self: &Arc<Self>) { self.schedule(); }
# }
# thread_local! {
#     static CURRENT: RefCell<Option<Arc<Executor>>> = RefCell::new(None);
# }
# fn spawn_task<F: Future<Output = ()> + Send + 'static>(future: F) {
#     CURRENT.with(|c| {
#         let executor = c.borrow().clone().expect("spawn 必須在 block_on 裡呼叫");
#         executor.task_count.fetch_add(1, Ordering::AcqRel);
#         let task = Arc::new(Task {
#             future: Mutex::new(Box::pin(future)),
#             executor: executor.clone(),
#             queued: AtomicBool::new(true),
#         });
#         executor.ready_queue.lock().unwrap().push_back(task);
#     });
# }
# fn run_executor(executor: &Arc<Executor>) {
#     loop {
#         loop {
#             let task = executor.ready_queue.lock().unwrap().pop_front();
#             let Some(task) = task else { break };
#             task.queued.store(false, Ordering::Release);
#             let waker = Waker::from(task.clone());
#             let mut cx = Context::from_waker(&waker);
#             let mut future = task.future.lock().unwrap();
#             if future.as_mut().poll(&mut cx).is_ready() {
#                 executor.task_count.fetch_sub(1, Ordering::AcqRel);
#             }
#         }
#         if executor.task_count.load(Ordering::Acquire) == 0 { break; }
#         std::thread::park();
#     }
# }
# fn block_on<F: Future<Output = ()> + Send + 'static>(future: F) {
#     let executor = Arc::new(Executor::new());
#     CURRENT.with(|c| *c.borrow_mut() = Some(executor.clone()));
#     spawn_task(future);
#     run_executor(&executor);
# }
#
struct Reactor {
    registry: Registry, // Future 用它登記 / 取消 socket
    next_token: AtomicUsize, // 自分配 Token
    wakers: Mutex<HashMap<Token, Waker>>, // Token -> 等待中的 Waker
}

impl Reactor {
    fn unique_token(&self) -> Token {
        Token(self.next_token.fetch_add(1, Ordering::Relaxed))
    }

    fn register(&self, source: &mut impl Source, token: Token, interest: Interest) {
        self.registry.register(source, token, interest).expect("登記失敗");
    }

    fn deregister(&self, source: &mut impl Source) {
        self.registry.deregister(source).expect("取消登記失敗");
    }

    fn set_waker(&self, token: Token, waker: Waker) {
        self.wakers.lock().unwrap().insert(token, waker);
    }

    // 跑在自己的 thread 上：睡在 poll 上，醒來照 Token 找 Waker 來 wake
    fn run(&self, mut poll: MioPoll) {
        let mut events = Events::with_capacity(128);
        loop {
            poll.poll(&mut events, None).expect("poll 失敗");
            for event in events.iter() {
                if let Some(waker) = self.wakers.lock().unwrap().remove(&event.token()) {
                    waker.wake();
                }
            }
        }
    }
}

fn start_reactor() -> Arc<Reactor> {
    let poll = MioPoll::new().expect("建立 Poll 失敗");
    let registry = poll.registry().try_clone().expect("複製 Registry 失敗");
    let reactor = Arc::new(Reactor {
        registry,
        next_token: AtomicUsize::new(0),
        wakers: Mutex::new(HashMap::new()),
    });
    // reactor 跑在自己的 thread 上
    let reactor_for_thread = reactor.clone();
    std::thread::spawn(move || reactor_for_thread.run(poll));
    reactor
}

// ===== 第二塊：I/O Future =====

struct Accept {
    reactor: Arc<Reactor>,
    listener: TcpListener,
    token: Token,
}

impl Accept {
    fn new(reactor: Arc<Reactor>, mut listener: TcpListener) -> Accept {
        let token = reactor.unique_token();
        reactor.register(&mut listener, token, Interest::READABLE);
        Accept { reactor, listener, token }
    }
}

impl Future for Accept {
    type Output = TcpStream;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<TcpStream> {
        let this = self.get_mut();
        // 先登記 Waker 給 reactor，再試一次 accept（順序刻意「先登記再試」避免 race）
        this.reactor.set_waker(this.token, cx.waker().clone());
        match this.listener.accept() {
            Ok((stream, _addr)) => {
                this.reactor.deregister(&mut this.listener);
                Poll::Ready(stream)
            }
            Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => panic!("accept 失敗：{e}"),
        }
    }
}

struct Read<'a> {
    reactor: Arc<Reactor>,
    stream: &'a mut TcpStream,
    buf: &'a mut [u8],
    token: Token,
}

impl<'a> Future for Read<'a> {
    type Output = usize;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<usize> {
        let this = self.get_mut();
        this.reactor.set_waker(this.token, cx.waker().clone()); // 先登記
        match this.stream.read(this.buf) { // 再試一次
            Ok(n) => Poll::Ready(n),
            Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => panic!("read 失敗：{e}"),
        }
    }
}

// 接一條連線，讀幾個 request 印出來（簡化：單一連線、不設逾時）
async fn serve(reactor: Arc<Reactor>, listener: TcpListener) {
    let mut stream = Accept::new(reactor.clone(), listener).await;

    let token = reactor.unique_token();
    reactor.register(&mut stream, token, Interest::READABLE);

    for i in 0..3 {
        let mut buf = vec![0u8; 1024];
        let n = Read { reactor: reactor.clone(), stream: &mut stream, buf: &mut buf, token }.await;
        if n == 0 {
            println!("連線關閉了");
            break;
        }
        println!("第 {i} 個 request：{}", String::from_utf8_lossy(&buf[..n]).trim());
    }

    reactor.deregister(&mut stream);
}

fn main() {
    let reactor = start_reactor();
    let addr = "127.0.0.1:8080".parse().expect("位址解析失敗");
    let listener = TcpListener::bind(addr).expect("綁定失敗");
    block_on(serve(reactor, listener));
}
```

> 上面隱藏了第 12 集的整套 executor，按程式碼框左上角可展開——這集真的一行都沒改它。

### 「先登記再試」為什麼重要

注意 `Accept` 和 `Read` 的 `poll` 都是**先** `set_waker`、**再**試一次 `accept` / `read`。這個順序是刻意的。

想像如果反過來：先試 `read` 拿到 `WouldBlock`（還沒資料），然後正要去登記 `Waker`——就在這個空檔，資料剛好到了，reactor 醒來想 `wake`，卻發現 `HashMap` 裡還沒有這個 `Token` 的 `Waker`，這個喚醒就**漏掉**了，於是這個 `Future` 永遠不會再被 poll。

把順序倒過來——先把 `Waker` 放好，再試一次 I/O——就堵住了這個空檔：萬一資料早就到了，這次的 `accept` / `read` 會直接成功回 `Ready`；萬一真的還沒到，`Waker` 也已經就位，等 reactor 通知。成功就回 `Ready`，`WouldBlock` 就回 `Pending`，乾淨俐落。

### 喚醒路徑完全沒變

把這集和第 12 集對照，你會發現喚醒的終點一模一樣。reactor 雖然跑在自己的 thread 上，但它呼叫的 `waker.wake()` 仍然是某個 `Task` 的 `Waker`——`wake` 一樣會把那個 `Task` 排回 ready queue、`unpark` executor。我們只是把「敲門的人」從計時 thread 換成了 reactor thread，門鈴和門後的流程完全沒動。

這就是 `Future` / `Waker` 這套設計漂亮的地方：不管喚醒的理由是「計時到了」還是「網路來資料了」，executor 都用同一套機制接住。

到這裡，我們從零手寫的 runtime 大功告成了！它能 `spawn`、能 `join`、能睡覺、能被計時器或真實 I/O 喚醒。接下來幾集，我們要轉回頭，把 `async fn` 背後那個一直被我們提到、卻還沒拆開的「狀態機」看個明白。

## 重點整理

- reactor 把喚醒接到真實 I/O：**executor 完全沿用第 12 集**，只把「誰來 `wake`」從計時 thread 換成 reactor thread。
- reactor 跑在自己的 thread、睡在 `mio::Poll` 上，醒來照 `Token` 從 `HashMap` 取出 `Waker` 來 `wake`。
- `Future` 與 reactor 透過 `Arc` 共享的 `Registry`、`AtomicUsize`、`Mutex<HashMap<Token, Waker>>` 溝通，不傳訊息。
- I/O `Future` 的 `poll` 一律「**先 `set_waker` 再試 I/O**」，避免漏接喚醒；成功回 `Ready`、`WouldBlock` 回 `Pending`。
- 不管喚醒來自計時器還是 I/O，最後都走「排回 ready queue ＋ `unpark`」同一條路。
