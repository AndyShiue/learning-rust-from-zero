# 手寫 reactor

## 本集目標

把前幾集的喚醒功能接到**真實的 I/O**——做出一個 reactor，讓我們的 runtime 第一次能處理網路連線。

## 正文

### executor 一行不改

這集有件事能讓人安心：**executor 完全沿用第 12 集**。`Task`、`Executor::spawn<T>`、`JoinHandle<T>`、`Shared<T>`、`Executor::block_on` 一行都不用改。

我們唯一要換掉的是「誰來 `wake`」。前面是 `Delay` 自己開一條計時 `Thread` 來 `wake`；現在改成一條 **reactor thread**，它睡在 `mio::Poll` 上等真實的 I/O，醒來後找到對應的 `Waker` 把它 `wake()`。

要加的東西是一個 `Reactor`，以及兩個 I/O `Future`（`Accept` 和 `Read`）。

### `Reactor` 與 I/O `Future`

`Reactor` 跑在自己的 `Thread` 上，睡在 `mio::Poll` 上。而那些跑在 executor `Thread` 上的 `Future`，要怎麼跟它溝通？答案是**透過共享狀態，而不是傳訊息**。三樣東西用 `Arc` 共用：

- **`Registry`**（`mio` 的）：`Future` 拿它直接登記 / 取消 socket。
- **`AtomicUsize`**：reactor 用它替每個來源自分配獨一無二的 `Token`。
- **`Mutex<HashMap<Token, Waker>>`**：`Future` 在執行時把自己的 `Waker` 寫進去（用 `Token` 當鑰匙），reactor 收到事件後就照 `Token` 取出來 `wake`。

```rust,no_run
# extern crate mio;
#
use std::collections::{HashMap, VecDeque};
use std::future::Future;
use std::io::Read as _;
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
use mio::event::Source;
use mio::net::{TcpListener, TcpStream};
use mio::{Events, Interest, Poll as MioPoll, Registry, Token};

type Queue = Arc<Mutex<VecDeque<Arc<Task>>>>;

struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    queue: Queue,
    executor_thread: Thread,
    queued: AtomicBool,
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        if !self.queued.swap(true, Ordering::SeqCst) {
            self.queue.lock().expect("取得鎖失敗").push_back(self.clone());
            self.executor_thread.unpark();
        }
    }
}

struct Shared<T> {
    state: Mutex<(Option<T>, Option<Waker>)>,
}

struct JoinHandle<T> {
    shared: Arc<Shared<T>>,
}

impl<T> Future for JoinHandle<T> {
    type Output = T;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<T> {
        let mut state = self.shared.state.lock().expect("取得鎖失敗");
        if let Some(value) = state.0.take() {
            Poll::Ready(value)
        } else {
            state.1 = Some(cx.waker().clone());
            Poll::Pending
        }
    }
}

struct Executor {
    queue: Queue,
    executor_thread: Thread,
    remaining: usize,
}

impl Executor {
    fn new() -> Executor {
        Executor {
            queue: Arc::new(Mutex::new(VecDeque::new())),
            executor_thread: thread::current(),
            remaining: 0,
        }
    }

    fn spawn<T, F>(&mut self, future: F) -> JoinHandle<T>
    where
        F: Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        let shared = Arc::new(Shared { state: Mutex::new((None, None)) });
        let shared_for_task = shared.clone();

        let task_future = async move {
            let value = future.await;
            let mut state = shared_for_task.state.lock().expect("取得鎖失敗");
            state.0 = Some(value);
            if let Some(waker) = state.1.take() {
                waker.wake();
            }
        };

        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(task_future)),
            queue: self.queue.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
        });

        self.remaining += 1;
        task.wake();

        JoinHandle { shared }
    }

    fn block_on<T, F>(&mut self, future: F) -> T
    where
        F: Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        let handle = self.spawn(future);

        while self.remaining > 0 {
            loop {
                let task = self.queue.lock().expect("取得鎖失敗").pop_front();
                let Some(task) = task else { break };

                task.queued.store(false, Ordering::SeqCst);
                let waker = Waker::from(task.clone());
                let mut cx = Context::from_waker(&waker);
                let mut future = task.future.lock().expect("取得鎖失敗");

                if future.as_mut().poll(&mut cx).is_ready() {
                    self.remaining -= 1;
                }
            }

            if self.remaining > 0 {
                thread::park();
            }
        }

        handle.shared.state.lock().expect("取得鎖失敗").0.take().expect("結果應該已經算好了")
    }
}

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
        self.wakers.lock().expect("取得鎖失敗").insert(token, waker);
    }

    fn clear_waker(&self, token: Token) {
        self.wakers.lock().expect("取得鎖失敗").remove(&token);
    }

    // 跑在自己的 Thread 上：睡在 poll 上，醒來照 Token 找 Waker 來 wake
    fn run(&self, mut poll: MioPoll) {
        let mut events = Events::with_capacity(128);
        loop {
            poll.poll(&mut events, None).expect("poll 失敗");
            for event in events.iter() {
                let waker = self
                    .wakers
                    .lock()
                    .expect("取得鎖失敗")
                    .remove(&event.token());

                if let Some(waker) = waker {
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
    // reactor 跑在自己的 Thread 上
    let reactor_for_thread = reactor.clone();
    std::thread::spawn(move || reactor_for_thread.run(poll));
    reactor
}

// 開始實作新的 Future

struct Accept {
    reactor: Arc<Reactor>,
    listener: TcpListener,
    listener_token: Token,
}

impl Accept {
    fn new(reactor: Arc<Reactor>, mut listener: TcpListener) -> Accept {
        let listener_token = reactor.unique_token();
        reactor.register(&mut listener, listener_token, Interest::READABLE);
        Accept { reactor, listener, listener_token }
    }
}

impl Future for Accept {
    type Output = TcpStream;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<TcpStream> {
        let this = self.get_mut();
        // 順序刻意是「先登記 Waker，再試 accept」。
        // 如果先 accept 得到 WouldBlock，才準備登記 Waker，
        // 連線可能剛好在中間進來；reactor 那時找不到 Waker 可叫醒，
        // executor 就可能睡過頭。
        this.reactor.set_waker(this.listener_token, cx.waker().clone());
        match this.listener.accept() {
            Ok((stream, _addr)) => {
                // 這次 poll 可能「先登記、再立刻成功」。
                // 成功後就不需要再等 I/O 事件，所以要把剛剛存進去的 Waker 清掉。
                this.reactor.clear_waker(this.listener_token);
                this.reactor.deregister(&mut this.listener);
                Poll::Ready(stream)
            }
            Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => panic!("accept 失敗：{}", e),
        }
    }
}

struct Read<'a> {
    reactor: Arc<Reactor>,
    stream: &'a mut TcpStream,
    buf: &'a mut [u8],
    stream_token: Token,
}

impl<'a> Future for Read<'a> {
    type Output = usize;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<usize> {
        let this = self.get_mut();
        this.reactor.set_waker(this.stream_token, cx.waker().clone()); // 先登記
        match this.stream.read(this.buf) { // 再試一次
            Ok(n) => {
                // 清掉 Waker
                this.reactor.clear_waker(this.stream_token);
                Poll::Ready(n)
            }
            Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => panic!("read 失敗：{}", e),
        }
    }
}

// 接一條連線，讀幾個 request 印出來（簡化：單一連線、不設逾時）
async fn serve(reactor: Arc<Reactor>, listener: TcpListener) {
    let mut stream = Accept::new(reactor.clone(), listener).await;

    let stream_token = reactor.unique_token();
    reactor.register(&mut stream, stream_token, Interest::READABLE);

    for i in 0..3 {
        let mut buf = vec![0u8; 1024];
        let n = Read {
            reactor: reactor.clone(),
            stream: &mut stream,
            buf: &mut buf,
            stream_token,
        }
        .await;
        if n == 0 {
            println!("連線關閉了");
            break;
        }
        println!("第 {} 個 request：{}", i, String::from_utf8_lossy(&buf[..n]).trim());
    }

    reactor.clear_waker(stream_token);
    reactor.deregister(&mut stream);
}

fn main() {
    let reactor = start_reactor();
    let addr = "127.0.0.1:8080".parse().expect("位址解析失敗");
    let listener = TcpListener::bind(addr).expect("綁定失敗");

    let mut executor = Executor::new();
    executor.block_on(serve(reactor, listener));
}
```

> 注意：這段程式會在本機監聽 `127.0.0.1:8080`，需要另外用瀏覽器或 `curl` 連進來才看得到效果。網頁版沙盒不適合體驗這種互動式網路程式；如果想體驗完整成果，請在自己的電腦上執行這段程式碼。

### Token 跟 I/O 來源綁在一起

`Accept` 和 `Read` 沒有共用同一個 `Token`。`Accept` 裡的 `listener_token` 是給 `TcpListener` 用的；接到連線後，`serve` 另外建立 `stream_token`，登記給那條 `TcpStream`。

後面的三次 `Read` 會共用同一個 `stream_token`，這是刻意的：`Token` 是 I/O 來源的名牌，不是每一次 `.await` 都要換一張名牌。這個簡化範例同一時間只會等待這條 stream 上的一次 `read`，所以同一個 stream `Token` 對應一個等待中的 `Waker` 就夠了。

等 I/O 成功後，`Accept` / `Read` 會呼叫 `clear_waker`，把這次等待用的 `Waker` 從 `HashMap` 裡拿掉。這樣 reactor 裡就不會留下「已經不需要喚醒」的等待者。

### `WouldBlock` 是什麼

`mio` 的 socket 是**非阻塞**的。這代表你呼叫 `accept` 或 `read` 時，它不會因為「現在還沒有連線 / 還沒有資料」就把 executor `Thread` 卡在那裡等。它會立刻回來，並用 `WouldBlock` 告訴你：「現在還不能做這件事，晚點再試。」

所以 `WouldBlock` 在這裡不是「壞掉了」的錯誤，而是非阻塞 I/O 的正常狀態。對我們手寫的 `Future` 來說，它剛好對應到 `Poll::Pending`：

- `accept` / `read` 成功：代表真的拿到連線或資料，回 `Poll::Ready(...)`
- `WouldBlock`：代表現在還沒好，先回 `Poll::Pending`
- 其他錯誤：才是真的出問題，這個簡化範例直接 `panic`

### 「先登記再試」為什麼重要

注意 `Accept` 和 `Read` 的 `poll` 都是**先** `set_waker`、**再**試一次 `accept` / `read`。這個順序是刻意的。

這個「再試一次」不代表這一輪一定會成功。如果還是 `WouldBlock`，這次 `poll` 就回 `Pending`；等 reactor 之後收到事件、呼叫剛剛存好的 `Waker`，executor 下一輪再 `poll` 這個 `Future`，才會再試一次 I/O。

想像如果反過來：先試 `read` 拿到 `WouldBlock`（還沒資料），然後正要去登記 `Waker`——就在這個空檔，資料剛好到了，reactor 醒來想 `wake`，卻發現 `HashMap` 裡還沒有這個 `Token` 的 `Waker`，這個喚醒就**漏掉**了，於是這個 `Future` 永遠不會再被 `poll`。

把順序倒過來——先把 `Waker` 放好，再試一次 I/O——就堵住了這個空檔：萬一資料早就到了，這次的 `accept` / `read` 會直接成功回 `Ready`；萬一真的還沒到，`Waker` 也已經就位，等 reactor 通知下一輪再試。成功就回 `Ready`，`WouldBlock` 就回 `Pending`。不過也因為我們是「先登記再試」，所以如果這次 `accept` / `read` 真的立刻成功，剛剛放進 `HashMap` 的 `Waker` 就已經用不到了。這時候 `Accept` / `Read` 會在回 `Ready` 前呼叫 `clear_waker`，把它清掉。換句話說，`set_waker` 是為了避免「還沒登記就錯過喚醒」，`clear_waker` 則是為了避免「已經完成了，卻留下不需要的等待者」。

### 喚醒路徑完全沒變

把這集和第 12 集對照，你會發現喚醒的終點一模一樣。reactor 雖然跑在自己的 `Thread` 上，但它呼叫的 `waker.wake()` 仍然是某個 `Task` 的 `Waker`——`wake` 一樣會把那個 `Task` 排回 ready queue、`unpark` executor。我們只是把「負責叫醒 `Thread` 的人」從計時 `Thread` 換成了 reactor `Thread`，後面的流程完全沒動。

到這裡，我們從零手寫的 runtime 大功告成了！它能 `spawn`、能睡覺、能被計時器或真實 I/O 喚醒。接下來幾集，我們要轉回頭，把 `async fn` 背後那個一直被我們提到、卻還沒拆開的「狀態機」看個明白。

## 重點整理

- reactor 把喚醒接到真實 I/O：**executor 完全沿用第 12 集**，只把「誰來 `wake`」從計時 `Thread` 換成 reactor `Thread`
- reactor 跑在自己的 `Thread`、睡在 `mio::Poll` 上，醒來照 `Token` 從 `HashMap` 取出 `Waker` 來 `wake`
- `Future` 與 reactor 透過 `Arc` 共享的 `Registry`、`AtomicUsize`、`Mutex<HashMap<Token, Waker>>` 溝通，不傳訊息
- `Token` 是 I/O 來源的名牌：listener 有自己的 `listener_token`，stream 有自己的 `stream_token`；在我們的程式碼中同一條 stream 的多次 `Read` 可以共用同一個 stream `Token`
- `WouldBlock` 是非阻塞 I/O 的正常狀態，意思是「現在還不能做 `accept` / `read` 之類的 I/O 動作，晚點再試」，在 `Future` 裡對應 `Poll::Pending`
- I/O `Future` 的 `poll` 一律「**先 `set_waker` 再試 I/O**」，避免漏接喚醒；如果立刻成功，回 `Ready` 前要 `clear_waker` 清掉不再需要的等待者
- 不管喚醒來自計時器還是 I/O，最後都走「排回 ready queue ＋ `unpark`」同一條路
