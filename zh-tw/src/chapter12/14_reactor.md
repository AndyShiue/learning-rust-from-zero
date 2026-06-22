# 手寫 reactor

## 本集目標

把第 11、12 集的喚醒模式接到真實 I/O。

```text
I/O 還沒好
    -> 保存目前 task 的 Waker
    -> 回 Pending

I/O ready 了
    -> reactor 呼叫那個 Waker
    -> task 回到 ready queue
    -> executor 再 poll task
```

我們會讓 reactor 跑在另一條 thread，分工很清楚：

```text
executor thread：poll task，推進 async 程式
reactor thread：等 mio I/O readiness，事件來了就 wake 對應 task
I/O future：自己試 read / accept，遇到 WouldBlock 就把 Waker 登記給 reactor
```

reactor 不是 task，也不會被 executor poll；它只是外部事件來源。

## 概念說明

### 跟第 12 集比，差在哪

好消息：**executor 一行都沒改。** 第 11、12 集裡讓 task「之後好了再 wake」的事件源頭，是 `Delay` 自己開的計時 thread；這一集**只把那個源頭換成真實 I/O**——一條 reactor thread 搭 `mio::Poll`（第 13 集的工具）同時盯住所有 socket，哪個 ready 就 wake 對應 task。

- executor、`Task`、`spawn<T>`、`JoinHandle<T>`、`block_on<T>`——**全部原封不動沿用第 12 集**。
- 新增的只有兩塊：① **`Reactor`**（一條 thread + 共享狀態，負責等 I/O readiness、好了就 wake 對應 task）；② **走 reactor 的 I/O future**（`Accept` / `Read`：試一次 I/O，遇到 `WouldBlock` 就把目前 task 的 Waker 登記給 reactor、回 `Pending`）。

一句話：第 12 集解決「task 的值怎麼交回來」，這集只把「誰來 wake」從計時 thread 換成 reactor，排程引擎完全不動。

### executor 不等 I/O，它只等「有 task 可以 poll」

executor 完全不碰 `mio::Poll`。它的迴圈跟第 12 集一模一樣：ready queue 有 task 就拿出來 poll，queue 空了但還有 task 沒完成，就 `thread::park()` 睡著；task 被 wake 時把自己排回 queue、`unpark()` executor。

差別只在「誰來 wake」：第 12 集是 `Delay` 的計時 thread，這集換成 reactor thread。對 executor 來說，喚醒它的人是誰，完全沒差——所以這一集 executor 的程式碼直接照搬第 12 集（完整版附在最後）。

### `Reactor`：和 task 共享兩樣狀態

reactor 跑在自己的 thread 上、睡在 `mio::Poll` 裡等 I/O。問題是：在 executor thread 上跑的 task，要怎麼把「我這顆 socket 拜託你盯著，好了叫醒我」告訴 reactor？

最直接的辦法是**共享狀態**——兩邊碰同一份資料，不必傳訊息。只要共享兩樣：

```text
registry：task 直接拿它登記 / 取消 socket
wakers 表（token -> Waker）：
    task 在 WouldBlock 時把自己的 Waker 寫進去
    reactor 收到該 token 的事件時，取出 Waker 來 wake
```

兩樣都用 `Arc` 給兩邊共用：`mio::Registry` 是 `Send + Sync`、可以 `try_clone`；`wakers` 表用 `Arc<Mutex<HashMap<Token, Waker>>>`。再加一個 `Arc<AtomicUsize>` 當共享的 token 計數器。

mio 有個方便特性幫我們省掉一大塊：**就算 reactor 正睡在 `poll.poll()` 裡，task 從另一條 thread 用共享的 `registry` 登記一個新 socket，mio 一樣會把它納入監看**，不必先把 reactor 戳醒。所以不需要 channel、也不需要任何「門鈴」。

```rust,ignore
use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::task::Waker;
use std::thread;

use mio::event::Source;
use mio::{Events, Interest, Poll as MioPoll, Registry, Token};

#[derive(Clone)]
struct Reactor {
    registry: Arc<Registry>,                   // 登記 / 取消 socket
    wakers: Arc<Mutex<HashMap<Token, Waker>>>, // token -> 等它的 task 的 Waker
    next_token: Arc<AtomicUsize>,              // 分配 token
}

impl Reactor {
    fn new() -> Reactor {
        let poll = MioPoll::new().unwrap();
        // registry 複製一份給 task 用；poll 本體留給 reactor thread
        let registry = Arc::new(poll.registry().try_clone().unwrap());
        let wakers: Arc<Mutex<HashMap<Token, Waker>>> = Arc::new(Mutex::new(HashMap::new()));

        let wakers_for_reactor = wakers.clone();
        thread::spawn(move || {
            let mut poll = poll;
            let mut events = Events::with_capacity(64);
            loop {
                poll.poll(&mut events, None).unwrap();
                for event in events.iter() {
                    // 有人在等這個 token，就 wake 它
                    if let Some(waker) = wakers_for_reactor.lock().unwrap().remove(&event.token()) {
                        waker.wake();
                    }
                }
            }
        });

        Reactor {
            registry,
            wakers,
            next_token: Arc::new(AtomicUsize::new(0)),
        }
    }

    // 分配一個 token，把 source 直接登記給 mio::Poll
    fn register(&self, source: &mut impl Source, interest: Interest) -> Token {
        let token = Token(self.next_token.fetch_add(1, Ordering::SeqCst));
        self.registry.register(source, token, interest).unwrap();
        token
    }

    // WouldBlock 時：把等這個 token 的 Waker 寫進共享表
    fn set_waker(&self, token: Token, waker: Waker) {
        self.wakers.lock().unwrap().insert(token, waker);
    }

    fn deregister(&self, source: &mut impl Source) {
        let _ = self.registry.deregister(source);
    }
}
```

reactor thread 的迴圈短到只剩骨架：**睡在 `poll.poll()` 上 → 醒來 → 對每個 event，從共享表取出 Waker、`wake()`**。它不 poll future、不碰業務邏輯。

`Source` 是 mio 對「可以被監看的東西」的抽象（`TcpListener`、`TcpStream` 都是）。`register` 自分配一個 token、把 socket 登記給 `Poll`、回傳 token；task 自己保有 socket。

### I/O future：先登記、再試一次

mio 的 socket 是非阻塞的：呼叫 `accept` / `read`，現在不能做就回 `WouldBlock`。這正好對上 `Future::poll`——**先把 Waker 登記給 reactor，再試一次 I/O；成功就 `Ready`，`WouldBlock` 就回 `Pending`。**

順序是刻意的：**先登記、再試**。如果反過來「先試、`WouldBlock` 才登記」，會有個空檔——就在「試完」到「登記」之間，readiness 剛好到了、reactor 卻還找不到 Waker，那次喚醒就溜走了（task 卡死）。先登記再試就沒有這個空檔：Waker 早就在表裡，之後任何 readiness 都接得到（這是避免 lost wakeup 的經典手法：先把自己掛上等待名單，再檢查條件）。

我們直接把這個邏輯寫成兩個自訂 future，連 `poll` 都自己寫（不靠任何 helper）：

```rust,ignore
use std::future::Future;
use std::io::{self, Read as _};
use std::pin::Pin;
use std::task::{Context, Poll};

use mio::net::{TcpListener, TcpStream};

struct Accept<'a> {
    reactor: Reactor,
    listener: &'a mut TcpListener,
    token: Token,
}

impl Future for Accept<'_> {
    type Output = io::Result<TcpStream>;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let me = self.get_mut();
        // 先登記 Waker，再試 accept：兩者之間沒有空檔，readiness 不會溜走
        me.reactor.set_waker(me.token, cx.waker().clone());
        match me.listener.accept() {
            Ok((stream, _)) => Poll::Ready(Ok(stream)),
            Err(e) if e.kind() == io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => Poll::Ready(Err(e)),
        }
    }
}

struct Read<'a> {
    reactor: Reactor,
    stream: &'a mut TcpStream,
    token: Token,
    buf: &'a mut [u8],
}

impl Future for Read<'_> {
    type Output = io::Result<usize>;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let me = self.get_mut();
        // 先登記 Waker，再試 read：兩者之間沒有空檔，readiness 不會溜走
        me.reactor.set_waker(me.token, cx.waker().clone());
        match me.stream.read(me.buf) {
            Ok(n) => Poll::Ready(Ok(n)),
            Err(e) if e.kind() == io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => Poll::Ready(Err(e)),
        }
    }
}
```

兩個 future 長得幾乎一樣，差別只在「試哪一個 I/O」。`self.get_mut()` 能用，是因為它們的欄位都能安全 move（都是 `Unpin`，第 18 集會講）。`use std::io::Read as _` 是把 `Read` trait 的方法引進來、但不佔用 `Read` 這個名字（留給我們的 struct）。

為了寫起來順手，包兩個小建構函式（它們只是把欄位塞好，沒別的）：

```rust,ignore
fn accept(reactor: Reactor, listener: &mut TcpListener, token: Token) -> Accept<'_> {
    Accept { reactor, listener, token }
}

fn read<'a>(reactor: Reactor, stream: &'a mut TcpStream, token: Token, buf: &'a mut [u8]) -> Read<'a> {
    Read { reactor, stream, token, buf }
}
```

reactor 之後看到這個 token ready，就取出這個 Waker、`wake()`，把 task 排回 ready queue；executor 下一次 poll 它時，`read` 再試一次。

### 把它兜成一個 task

root future 很單純：等一條連線進來，然後 `.await` 讀**幾個** request 印出來就好。每個 `read(...).await` 都是一次「試一下、不行就掛起、被 reactor 喚醒再試」。

```rust,ignore
async fn serve(reactor: Reactor, mut listener: TcpListener, listener_token: Token) {
    // 等一條連線（accept 遇到 WouldBlock 就交給 reactor）
    let mut stream = accept(reactor.clone(), &mut listener, listener_token).await.unwrap();
    let token = reactor.register(&mut stream, Interest::READABLE);

    // 讀 3 個 request：每個 read 都是一次 .await
    let mut buf = [0u8; 1024];
    for i in 1..=3 {
        let n = read(reactor.clone(), &mut stream, token, &mut buf).await.unwrap();
        println!("第 {i} 個 request：{}", String::from_utf8_lossy(&buf[..n]).trim_end());
    }

    reactor.deregister(&mut stream);
}
```

`accept` 和 `read` 都是在這顆 task 裡自己做的——reactor 沒幫你 accept、也沒幫你 read，它只負責「可以再試一次了」的通知。

（只服務一條、只讀幾個 request，是為了把焦點留在 reactor。要同時服務很多連線，就得「每條連線各開一顆 task」——那需要從正在跑的 task 內部 `spawn`，得多做一個可傳遞的 spawn handle；本集先不碰。）

## 完整範例程式碼

一條 executor thread 跑 ready queue，一條 reactor thread 等 I/O readiness。executor 那一段（`Task` / `Shared` / `JoinHandle` / `Executor`）就是第 12 集原封不動搬過來的。

```rust,ignore
use std::collections::{HashMap, VecDeque};
use std::future::Future;
use std::io::{self, Read as _};
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::thread::Thread;

use mio::event::Source;
use mio::net::{TcpListener, TcpStream};
use mio::{Events, Interest, Poll as MioPoll, Registry, Token};

// ---- Reactor：跑在自己的 thread，等 I/O readiness ----

#[derive(Clone)]
struct Reactor {
    registry: Arc<Registry>,
    wakers: Arc<Mutex<HashMap<Token, Waker>>>,
    next_token: Arc<AtomicUsize>,
}

impl Reactor {
    fn new() -> Reactor {
        let poll = MioPoll::new().unwrap();
        let registry = Arc::new(poll.registry().try_clone().unwrap());
        let wakers: Arc<Mutex<HashMap<Token, Waker>>> = Arc::new(Mutex::new(HashMap::new()));

        let wakers_for_reactor = wakers.clone();
        thread::spawn(move || {
            let mut poll = poll;
            let mut events = Events::with_capacity(64);
            loop {
                poll.poll(&mut events, None).unwrap();
                for event in events.iter() {
                    if let Some(waker) = wakers_for_reactor.lock().unwrap().remove(&event.token()) {
                        waker.wake();
                    }
                }
            }
        });

        Reactor {
            registry,
            wakers,
            next_token: Arc::new(AtomicUsize::new(0)),
        }
    }

    fn register(&self, source: &mut impl Source, interest: Interest) -> Token {
        let token = Token(self.next_token.fetch_add(1, Ordering::SeqCst));
        self.registry.register(source, token, interest).unwrap();
        token
    }

    fn set_waker(&self, token: Token, waker: Waker) {
        self.wakers.lock().unwrap().insert(token, waker);
    }

    fn deregister(&self, source: &mut impl Source) {
        let _ = self.registry.deregister(source);
    }
}

// ---- Executor：完全沿用第 12 集 ----

type Queue = Arc<Mutex<VecDeque<Arc<Task>>>>;

struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    queue: Queue,
    executor_thread: Thread,
    queued: AtomicBool,
}

impl Task {
    fn schedule(self: &Arc<Self>) {
        if !self.queued.swap(true, Ordering::SeqCst) {
            self.queue.lock().unwrap().push_back(self.clone());
            self.executor_thread.unpark();
        }
    }
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        self.schedule();
    }
}

struct Shared<T> {
    result: Mutex<Option<T>>,
    waker: Mutex<Option<Waker>>,
}

struct JoinHandle<T> {
    shared: Arc<Shared<T>>,
}

impl<T> Future for JoinHandle<T> {
    type Output = T;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<T> {
        if let Some(value) = self.shared.result.lock().unwrap().take() {
            Poll::Ready(value)
        } else {
            *self.shared.waker.lock().unwrap() = Some(cx.waker().clone());
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

    fn spawn<T: Send + 'static>(
        &mut self,
        fut: impl Future<Output = T> + Send + 'static,
    ) -> JoinHandle<T> {
        let shared = Arc::new(Shared {
            result: Mutex::new(None),
            waker: Mutex::new(None),
        });
        let shared_for_task = shared.clone();

        let wrapped = async move {
            let value = fut.await;
            *shared_for_task.result.lock().unwrap() = Some(value);
            if let Some(waker) = shared_for_task.waker.lock().unwrap().take() {
                waker.wake();
            }
        };

        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(wrapped)),
            queue: self.queue.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
        });

        self.remaining += 1;
        task.schedule();

        JoinHandle { shared }
    }

    fn block_on<T: Send + 'static>(
        &mut self,
        future: impl Future<Output = T> + Send + 'static,
    ) -> T {
        let handle = self.spawn(future);

        while self.remaining > 0 {
            loop {
                let task = self.queue.lock().unwrap().pop_front();
                let Some(task) = task else { break };
                task.queued.store(false, Ordering::SeqCst);

                let waker = Waker::from(task.clone());
                let mut cx = Context::from_waker(&waker);
                let mut future = task.future.lock().unwrap();

                if future.as_mut().poll(&mut cx).is_ready() {
                    self.remaining -= 1;
                }
            }

            if self.remaining > 0 {
                thread::park();
            }
        }

        let result = handle.shared.result.lock().unwrap().take().unwrap();
        result
    }
}

// ---- I/O future：自己 impl Future，沒有 poll_fn ----

struct Accept<'a> {
    reactor: Reactor,
    listener: &'a mut TcpListener,
    token: Token,
}

impl Future for Accept<'_> {
    type Output = io::Result<TcpStream>;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let me = self.get_mut();
        me.reactor.set_waker(me.token, cx.waker().clone());
        match me.listener.accept() {
            Ok((stream, _)) => Poll::Ready(Ok(stream)),
            Err(e) if e.kind() == io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => Poll::Ready(Err(e)),
        }
    }
}

struct Read<'a> {
    reactor: Reactor,
    stream: &'a mut TcpStream,
    token: Token,
    buf: &'a mut [u8],
}

impl Future for Read<'_> {
    type Output = io::Result<usize>;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let me = self.get_mut();
        me.reactor.set_waker(me.token, cx.waker().clone());
        match me.stream.read(me.buf) {
            Ok(n) => Poll::Ready(Ok(n)),
            Err(e) if e.kind() == io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => Poll::Ready(Err(e)),
        }
    }
}

fn accept(reactor: Reactor, listener: &mut TcpListener, token: Token) -> Accept<'_> {
    Accept { reactor, listener, token }
}

fn read<'a>(reactor: Reactor, stream: &'a mut TcpStream, token: Token, buf: &'a mut [u8]) -> Read<'a> {
    Read { reactor, stream, token, buf }
}

// ---- root future：等一條連線，讀幾個 request ----

async fn serve(reactor: Reactor, mut listener: TcpListener, listener_token: Token) {
    let mut stream = accept(reactor.clone(), &mut listener, listener_token).await.unwrap();
    let token = reactor.register(&mut stream, Interest::READABLE);

    let mut buf = [0u8; 1024];
    for i in 1..=3 {
        let n = read(reactor.clone(), &mut stream, token, &mut buf).await.unwrap();
        println!("第 {i} 個 request：{}", String::from_utf8_lossy(&buf[..n]).trim_end());
    }

    reactor.deregister(&mut stream);
}

fn main() {
    let reactor = Reactor::new();
    let mut executor = Executor::new();

    let mut listener = TcpListener::bind("127.0.0.1:8080".parse().unwrap()).unwrap();
    let token = reactor.register(&mut listener, Interest::READABLE);

    println!("在 127.0.0.1:8080 等一條連線（讀 3 個 request）");
    executor.block_on(serve(reactor, listener, token));
}
```

跑起來後，開另一個終端機用 `nc 127.0.0.1 8080` 連進去，每打一行就送一個 request，伺服器會依序印出前三個：

```text
在 127.0.0.1:8080 等一條連線（讀 3 個 request）
第 1 個 request：first
第 2 個 request：second
第 3 個 request：third
```

## 一步步看資料流

假設 `serve` 跑到某個 `read(...).await`：

1. executor poll 這個 task。
2. `Read::poll` 先 `set_waker`：把目前 task 的 Waker 寫進 reactor 的共享表（`token -> Waker`）。
3. 再試 `stream.read(buf)`。
4. 目前沒資料，得到 `WouldBlock`。
5. `Read::poll` 回 `Pending`，task 暫停（Waker 已經登記好了）。
6. reactor thread 之後從 `mio::Poll` 收到這個 socket 的 token。
7. reactor 從表裡取出 Waker，呼叫 `wake()`。
8. Waker 把 task 排回 ready queue，並 `unpark` executor。
9. executor 再 poll 這個 task。
10. `Read::poll` 再試一次；資料到了就回 `Ready(n)`。

整條路上只有 executor poll task。reactor 只負責「可以再試一次了」的通知。

## 重點整理

- executor 完全沿用第 12 集：`Task` / `spawn<T>` / `JoinHandle<T>` / `Shared<T>` / `block_on<T>` 一行都沒改；這集只把「誰來 wake」從 `Delay` 計時 thread 換成 reactor
- `Reactor` 跑在自己的 thread、睡在 `mio::Poll` 上等 I/O readiness；它不是 task、不會被 executor poll
- I/O future（`Accept` / `Read`）自己 `impl Future`：**先 `set_waker` 登記給 reactor，再試一次 I/O**，`WouldBlock` 就回 `Pending`（先登記再試，關掉「readiness 在登記前溜走」的 race；也不需要 `poll_fn` 之類的 helper）
- executor 與 reactor 用**共享狀態**溝通：共享 `mio::Registry`（task 直接登記 socket）與 `Arc<Mutex<HashMap<Token, Waker>>>`；mio 允許別條 thread 在 `poll()` 睡著時直接登記新 source，所以不需要 channel、也不需要任何門鈴
- 範例只服務一條連線、讀少少幾個 request，把焦點留在 reactor；要同時服務多條連線得「每條各開一顆 task」，那需要從 task 內部 spawn，本集先不碰
- 教學版簡化：單一連線、`unwrap` 錯誤處理、無計時器、無完整 shutdown / cancellation safety
