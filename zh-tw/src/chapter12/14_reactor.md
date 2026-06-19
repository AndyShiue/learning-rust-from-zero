# reactor thread 與 I/O readiness

## 本集目標

第 11 集做出 ready queue executor：task 被 wake 之後，會回到 queue，等 executor 再 poll。

第 12 集補上 `JoinHandle<T>`：結果還沒好時，`JoinHandle` 保存等待者的 Waker；結果好了，再用那個 Waker 喚醒等待者。

第 13 集認識 `mio::Poll`、`mio::Waker` 和 `Token`。現在可以把它們接到真正的 I/O readiness。

這一集要把同一個模式接到真正的 I/O：

```text
I/O 還沒好
    -> 保存目前 task 的 Waker
    -> 回 Pending

I/O ready 了
    -> reactor 呼叫那個 Waker
    -> task 回到 ready queue
    -> executor 再 poll task
```

這次我們會讓 reactor 跑在另一個 thread。這樣分工會很清楚：

```text
executor thread:
    poll task，推進 async 程式

reactor thread:
    等 mio I/O readiness，事件來了就 wake 對應 task

I/O future:
    自己嘗試 read / accept
    遇到 WouldBlock 就把 Waker 登記給 reactor
```

reactor 不是 task，也不會被 executor poll。它只是外部事件來源。

## 概念說明

### executor 不等 I/O，它只等「有 task 可以 poll」

第 11、12 集的 executor 不碰 `mio::Poll`。它只在 ready queue 空了但還有 task 沒完成時，用 `thread::park()` 睡覺；task 被 wake 時，再用 `Thread::unpark()` 叫醒它。

這一集改成兩條 thread：

```text
executor thread:
    ready queue 空了 -> thread::park()
    task 被 wake    -> task 進 queue，unpark executor

reactor thread:
    睡在 mio::Poll 上
    socket ready -> 找到 Waker，呼叫 wake()
```

所以 executor 不需要知道 `mio::Poll`。它只知道一件事：如果某個 task 被 wake，那個 task 就會進 ready queue。

### `WouldBlock` 由 I/O future 自己處理

`mio` 的 socket 是非阻塞的。你呼叫 `read` 或 `accept` 時，它不會一直卡住等資料；如果現在還不能做，就會回傳 `WouldBlock`。

這正好對應 `Future::poll` 的語意：

```text
read 成功
    -> Poll::Ready(...)

read 遇到 WouldBlock
    -> 把 cx.waker() 登記給 reactor
    -> Poll::Pending
```

注意：不是 reactor 幫 task 做 `read`。真正嘗試 I/O 的仍然是 task 裡面的 future。reactor 只負責在 OS 說「這個 socket 應該可以再試一次」時呼叫 Waker。

### reactor thread 需要一個自己的門鈴

executor thread 和 reactor thread 分開後，還有一個問題：socket 要怎麼註冊到 reactor？

我們會用 channel 傳指令給 reactor thread：

```text
executor thread -> reactor thread:
    RegisterStream
    RegisterListener
    SetWaker
    DeregisterStream
```

但 reactor thread 可能正睡在 `mio::Poll` 裡。如果只是把指令丟進 channel，它不一定會馬上醒來處理。

所以 reactor 自己會有一個 `mio::Waker`，專門叫醒 `mio::Poll`：

```text
送指令到 channel
    -> reactor_waker.wake()
    -> mio::Poll 醒來
    -> reactor thread 處理 channel 裡的指令
```

這個 `mio::Waker` 是 reactor 的「指令門鈴」，不是 executor 的總門鈴。

## ReactorHandle：外界只拿到一個 handle

`ReactorHandle` 是 executor thread 這邊會拿到的東西。它不直接暴露 `mio::Poll`，只提供幾個方法把指令送到 reactor thread。

```rust,ignore
use std::collections::HashMap;
use std::sync::{mpsc, Arc};
use std::task::Waker;
use std::thread;

use mio::net::{TcpListener, TcpStream};
use mio::{Events, Interest, Poll as MioPoll, Token, Waker as MioWaker};

const REACTOR_WAKE: Token = Token(0);

enum Command {
    RegisterListener {
        listener: TcpListener,
        interest: Interest,
        respond: mpsc::Sender<(TcpListener, Token)>,
    },
    RegisterStream {
        stream: TcpStream,
        interest: Interest,
        respond: mpsc::Sender<(TcpStream, Token)>,
    },
    SetWaker {
        token: Token,
        waker: Waker,
    },
    DeregisterStream {
        stream: TcpStream,
    },
}

#[derive(Clone)]
struct ReactorHandle {
    sender: mpsc::Sender<Command>,
    reactor_waker: Arc<MioWaker>,
}
```

`Token(0)` 留給 reactor 的指令門鈴。真正的 socket token 會從 `Token(1)` 開始。

接著建立 reactor thread：

```rust,ignore
impl ReactorHandle {
    fn new() -> ReactorHandle {
        let (sender, receiver) = mpsc::channel::<Command>();
        let (ready_sender, ready_receiver) = mpsc::channel();

        thread::spawn(move || {
            let mut poll = MioPoll::new().unwrap();
            let reactor_waker =
                Arc::new(MioWaker::new(poll.registry(), REACTOR_WAKE).unwrap());
            ready_sender.send(reactor_waker.clone()).unwrap();

            let mut events = Events::with_capacity(64);
            let mut wakers = HashMap::<Token, Waker>::new();
            let mut next_token = 1;

            loop {
                poll.poll(&mut events, None).unwrap();

                while let Ok(command) = receiver.try_recv() {
                    match command {
                        Command::RegisterListener {
                            mut listener,
                            interest,
                            respond,
                        } => {
                            let token = Token(next_token);
                            next_token += 1;
                            poll.registry().register(&mut listener, token, interest).unwrap();
                            respond.send((listener, token)).unwrap();
                        }
                        Command::RegisterStream {
                            mut stream,
                            interest,
                            respond,
                        } => {
                            let token = Token(next_token);
                            next_token += 1;
                            poll.registry().register(&mut stream, token, interest).unwrap();
                            respond.send((stream, token)).unwrap();
                        }
                        Command::SetWaker { token, waker } => {
                            wakers.insert(token, waker);
                        }
                        Command::DeregisterStream { mut stream } => {
                            let _ = poll.registry().deregister(&mut stream);
                        }
                    }
                }

                for event in events.iter() {
                    let token = event.token();

                    if token == REACTOR_WAKE {
                        continue;
                    }

                    if let Some(waker) = wakers.remove(&token) {
                        waker.wake();
                    }
                }
            }
        });

        let reactor_waker = ready_receiver.recv().unwrap();

        ReactorHandle {
            sender,
            reactor_waker,
        }
    }
}
```

這段裡 reactor 做的事很少：

- 收到註冊指令：把 socket 註冊到 `mio::Poll`，分配一個 token。
- 收到 `SetWaker`：記下 `token -> Waker`。
- 收到 I/O event：用 token 找出 Waker，呼叫 `wake()`。

它沒有 poll future，也沒有處理 request 的業務邏輯。

### 對外方法

把送指令的細節包起來：

```rust,ignore
impl ReactorHandle {
    fn send(&self, command: Command) {
        self.sender.send(command).unwrap();
        self.reactor_waker.wake().unwrap();
    }

    fn register_listener(
        &self,
        listener: TcpListener,
        interest: Interest,
    ) -> (TcpListener, Token) {
        let (sender, receiver) = mpsc::channel();
        self.send(Command::RegisterListener {
            listener,
            interest,
            respond: sender,
        });
        receiver.recv().unwrap()
    }

    fn register_stream(&self, stream: TcpStream, interest: Interest) -> (TcpStream, Token) {
        let (sender, receiver) = mpsc::channel();
        self.send(Command::RegisterStream {
            stream,
            interest,
            respond: sender,
        });
        receiver.recv().unwrap()
    }

    fn set_waker(&self, token: Token, waker: Waker) {
        self.send(Command::SetWaker { token, waker });
    }

    fn deregister_stream(&self, stream: TcpStream) {
        self.send(Command::DeregisterStream { stream });
    }
}
```

這是教學版，所以 `register_listener` / `register_stream` 會同步等 reactor 回覆。真實 runtime 會把這些細節包得更完整，也會處理錯誤、取消與關閉。

## Executor：只管理 ready queue

現在 executor 不再擁有 reactor，也不碰 `mio::Poll`。它只有 ready queue 和 executor thread handle。task 被 wake 時，會把自己排回 queue，然後 `unpark()` 睡著的 executor thread。

```rust,ignore
use std::collections::VecDeque;
use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Wake, Waker};
use std::thread;
use std::thread::Thread;

struct ExecutorState {
    queue: VecDeque<Arc<Task>>,
    remaining: usize,
}

type ExecutorShared = Arc<Mutex<ExecutorState>>;

struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    executor: ExecutorShared,
    executor_thread: Thread,
    queued: AtomicBool,
    completed: AtomicBool,
}

impl Task {
    fn schedule(self: &Arc<Self>) {
        if !self.completed.load(Ordering::SeqCst) && !self.queued.swap(true, Ordering::SeqCst) {
            self.executor.lock().unwrap().queue.push_back(self.clone());
            self.executor_thread.unpark();
        }
    }
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        self.schedule();
    }
}
```

這裡保留第 11 集最重要的精神：

```text
Task::wake()
    -> push ready queue
    -> unpark executor
```

executor 這次不是睡在 `mio::Poll`，而是用 `thread::park()` 睡著。

`completed` 是這一集因為多了 reactor thread 才加的保護：如果某個舊的 I/O readiness 在 task 完成後才送到，我們要忽略那次 wake，避免已經完成的 future 又被 poll。

### Spawner

`Spawner` 只是把 future 包成 task，排進 ready queue。

```rust,ignore
#[derive(Clone)]
struct Spawner {
    executor: ExecutorShared,
    executor_thread: Thread,
}

impl Spawner {
    fn spawn(&self, fut: impl Future<Output = ()> + Send + 'static) {
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(fut)),
            executor: self.executor.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
            completed: AtomicBool::new(false),
        });

        self.executor.lock().unwrap().remaining += 1;

        task.schedule();
    }
}
```

為了讓這一集集中在 reactor，這裡的 `Spawner` 只收 `Future<Output = ()>`。如果要回傳結果，就把上一集的 `Shared<T>` 與 `JoinHandle<T>` 加回來。

### Executor

`Executor::run` 只做一件事：拿 ready queue 裡的 task 來 poll。queue 空了但還有 task 沒完成時，就睡覺等下一次 wake。

```rust,ignore
struct Executor {
    shared: ExecutorShared,
    spawner: Spawner,
}

impl Executor {
    fn new() -> Executor {
        let shared = Arc::new(Mutex::new(ExecutorState {
            queue: VecDeque::new(),
            remaining: 0,
        }));
        let executor_thread = thread::current();

        Executor {
            shared: shared.clone(),
            spawner: Spawner {
                executor: shared,
                executor_thread,
            },
        }
    }

    fn spawner(&self) -> Spawner {
        self.spawner.clone()
    }

    fn run(&self) {
        loop {
            let task = {
                let mut state = self.shared.lock().unwrap();

                if let Some(task) = state.queue.pop_front() {
                    Some(task)
                } else if state.remaining == 0 {
                    None
                } else {
                    drop(state);
                    thread::park();
                    continue;
                }
            };

            let Some(task) = task else {
                break;
            };

            task.queued.store(false, Ordering::SeqCst);

            if task.completed.load(Ordering::SeqCst) {
                continue;
            }

            let waker = Waker::from(task.clone());
            let mut cx = Context::from_waker(&waker);
            let mut future = task.future.lock().unwrap();

            if future.as_mut().poll(&mut cx).is_ready() {
                task.completed.store(true, Ordering::SeqCst);
                self.shared.lock().unwrap().remaining -= 1;
            }
        }
    }
}
```

這個 executor 完全不知道 I/O token，也不知道 reactor thread 正在等什麼。它只相信 Waker：有 task 被 wake，就 poll 那個 task。

## 把非阻塞 I/O 包成可以 `.await`

接著寫一個小幫手，把「嘗試一次 I/O」轉成 `Poll`。

```rust,ignore
use std::future::poll_fn;
use std::io::{self, Read};
use std::task::Poll;

fn poll_io<T>(
    reactor: &ReactorHandle,
    token: Token,
    cx: &mut Context<'_>,
    mut op: impl FnMut() -> io::Result<T>,
) -> Poll<io::Result<T>> {
    match op() {
        Ok(value) => Poll::Ready(Ok(value)),
        Err(e) if e.kind() == io::ErrorKind::WouldBlock => {
            reactor.set_waker(token, cx.waker().clone());
            Poll::Pending
        }
        Err(e) => Poll::Ready(Err(e)),
    }
}
```

這裡就是本集的核心：

```text
WouldBlock
    -> 保存目前 task 的 Waker
    -> Pending
```

reactor 之後看到這個 token ready，就會呼叫這個 Waker。Waker 不會直接讓 `read` 成功；它只是讓 task 回 ready queue。executor 下一次 poll 這個 task 時，`read` 會再試一次。

有了 `poll_io`，`accept` 和 `read` 就可以這樣寫：

```rust,ignore
async fn accept(
    reactor: ReactorHandle,
    listener: &mut TcpListener,
    token: Token,
) -> io::Result<TcpStream> {
    poll_fn(|cx| poll_io(&reactor, token, cx, || listener.accept().map(|(s, _)| s))).await
}

async fn read(
    reactor: ReactorHandle,
    stream: &mut TcpStream,
    token: Token,
    buf: &mut [u8],
) -> io::Result<usize> {
    poll_fn(|cx| poll_io(&reactor, token, cx, || stream.read(buf))).await
}
```

## 服務連線

每個連線進來後，我們把它註冊給 reactor，拿到 token。之後 `read(...).await` 遇到 `WouldBlock` 時，就用這個 token 登記 Waker。

```rust,ignore
async fn handle(reactor: ReactorHandle, stream: TcpStream) {
    let (mut stream, token) = reactor.register_stream(stream, Interest::READABLE);
    let mut buf = [0u8; 1024];

    loop {
        match read(reactor.clone(), &mut stream, token, &mut buf).await {
            Ok(0) => break,
            Ok(n) => println!("收到: {}", String::from_utf8_lossy(&buf[..n]).trim_end()),
            Err(_) => break,
        }
    }

    reactor.deregister_stream(stream);
}
```

`server` 負責 accept。每接到一個連線，就 spawn 一個 task 去服務它。

```rust,ignore
async fn server(
    spawner: Spawner,
    reactor: ReactorHandle,
    mut listener: TcpListener,
    token: Token,
) {
    loop {
        match accept(reactor.clone(), &mut listener, token).await {
            Ok(stream) => spawner.spawn(handle(reactor.clone(), stream)),
            Err(_) => break,
        }
    }
}
```

注意 `accept` 和 `read` 都是在 task 裡做的。reactor thread 沒有幫你 accept，也沒有幫你 read；它只負責 readiness notification。

## 完整範例程式碼

這是一支迷你 runtime：一條 executor thread 跑 ready queue，一條 reactor thread 等 I/O readiness。

```rust,ignore
use std::collections::{HashMap, VecDeque};
use std::future::{poll_fn, Future};
use std::io::{self, Read};
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{mpsc, Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::thread::Thread;

use mio::net::{TcpListener, TcpStream};
use mio::{Events, Interest, Poll as MioPoll, Token, Waker as MioWaker};

const REACTOR_WAKE: Token = Token(0);

enum Command {
    RegisterListener {
        listener: TcpListener,
        interest: Interest,
        respond: mpsc::Sender<(TcpListener, Token)>,
    },
    RegisterStream {
        stream: TcpStream,
        interest: Interest,
        respond: mpsc::Sender<(TcpStream, Token)>,
    },
    SetWaker {
        token: Token,
        waker: Waker,
    },
    DeregisterStream {
        stream: TcpStream,
    },
}

#[derive(Clone)]
struct ReactorHandle {
    sender: mpsc::Sender<Command>,
    reactor_waker: Arc<MioWaker>,
}

impl ReactorHandle {
    fn new() -> ReactorHandle {
        let (sender, receiver) = mpsc::channel::<Command>();
        let (ready_sender, ready_receiver) = mpsc::channel();

        thread::spawn(move || {
            let mut poll = MioPoll::new().unwrap();
            let reactor_waker =
                Arc::new(MioWaker::new(poll.registry(), REACTOR_WAKE).unwrap());
            ready_sender.send(reactor_waker.clone()).unwrap();

            let mut events = Events::with_capacity(64);
            let mut wakers = HashMap::<Token, Waker>::new();
            let mut next_token = 1;

            loop {
                poll.poll(&mut events, None).unwrap();

                while let Ok(command) = receiver.try_recv() {
                    match command {
                        Command::RegisterListener {
                            mut listener,
                            interest,
                            respond,
                        } => {
                            let token = Token(next_token);
                            next_token += 1;
                            poll.registry().register(&mut listener, token, interest).unwrap();
                            respond.send((listener, token)).unwrap();
                        }
                        Command::RegisterStream {
                            mut stream,
                            interest,
                            respond,
                        } => {
                            let token = Token(next_token);
                            next_token += 1;
                            poll.registry().register(&mut stream, token, interest).unwrap();
                            respond.send((stream, token)).unwrap();
                        }
                        Command::SetWaker { token, waker } => {
                            wakers.insert(token, waker);
                        }
                        Command::DeregisterStream { mut stream } => {
                            let _ = poll.registry().deregister(&mut stream);
                        }
                    }
                }

                for event in events.iter() {
                    let token = event.token();

                    if token == REACTOR_WAKE {
                        continue;
                    }

                    if let Some(waker) = wakers.remove(&token) {
                        waker.wake();
                    }
                }
            }
        });

        let reactor_waker = ready_receiver.recv().unwrap();

        ReactorHandle {
            sender,
            reactor_waker,
        }
    }

    fn send(&self, command: Command) {
        self.sender.send(command).unwrap();
        self.reactor_waker.wake().unwrap();
    }

    fn register_listener(
        &self,
        listener: TcpListener,
        interest: Interest,
    ) -> (TcpListener, Token) {
        let (sender, receiver) = mpsc::channel();
        self.send(Command::RegisterListener {
            listener,
            interest,
            respond: sender,
        });
        receiver.recv().unwrap()
    }

    fn register_stream(&self, stream: TcpStream, interest: Interest) -> (TcpStream, Token) {
        let (sender, receiver) = mpsc::channel();
        self.send(Command::RegisterStream {
            stream,
            interest,
            respond: sender,
        });
        receiver.recv().unwrap()
    }

    fn set_waker(&self, token: Token, waker: Waker) {
        self.send(Command::SetWaker { token, waker });
    }

    fn deregister_stream(&self, stream: TcpStream) {
        self.send(Command::DeregisterStream { stream });
    }
}

struct ExecutorState {
    queue: VecDeque<Arc<Task>>,
    remaining: usize,
}

type ExecutorShared = Arc<Mutex<ExecutorState>>;

struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    executor: ExecutorShared,
    executor_thread: Thread,
    queued: AtomicBool,
    completed: AtomicBool,
}

impl Task {
    fn schedule(self: &Arc<Self>) {
        if !self.completed.load(Ordering::SeqCst) && !self.queued.swap(true, Ordering::SeqCst) {
            self.executor.lock().unwrap().queue.push_back(self.clone());
            self.executor_thread.unpark();
        }
    }
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        self.schedule();
    }
}

#[derive(Clone)]
struct Spawner {
    executor: ExecutorShared,
    executor_thread: Thread,
}

impl Spawner {
    fn spawn(&self, fut: impl Future<Output = ()> + Send + 'static) {
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(fut)),
            executor: self.executor.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
            completed: AtomicBool::new(false),
        });

        self.executor.lock().unwrap().remaining += 1;

        task.schedule();
    }
}

struct Executor {
    shared: ExecutorShared,
    spawner: Spawner,
}

impl Executor {
    fn new() -> Executor {
        let shared = Arc::new(Mutex::new(ExecutorState {
            queue: VecDeque::new(),
            remaining: 0,
        }));
        let executor_thread = thread::current();

        Executor {
            shared: shared.clone(),
            spawner: Spawner {
                executor: shared,
                executor_thread,
            },
        }
    }

    fn spawner(&self) -> Spawner {
        self.spawner.clone()
    }

    fn run(&self) {
        loop {
            let task = {
                let mut state = self.shared.lock().unwrap();

                if let Some(task) = state.queue.pop_front() {
                    Some(task)
                } else if state.remaining == 0 {
                    None
                } else {
                    drop(state);
                    thread::park();
                    continue;
                }
            };

            let Some(task) = task else {
                break;
            };

            task.queued.store(false, Ordering::SeqCst);

            if task.completed.load(Ordering::SeqCst) {
                continue;
            }

            let waker = Waker::from(task.clone());
            let mut cx = Context::from_waker(&waker);
            let mut future = task.future.lock().unwrap();

            if future.as_mut().poll(&mut cx).is_ready() {
                task.completed.store(true, Ordering::SeqCst);
                self.shared.lock().unwrap().remaining -= 1;
            }
        }
    }
}

fn poll_io<T>(
    reactor: &ReactorHandle,
    token: Token,
    cx: &mut Context<'_>,
    mut op: impl FnMut() -> io::Result<T>,
) -> Poll<io::Result<T>> {
    match op() {
        Ok(value) => Poll::Ready(Ok(value)),
        Err(e) if e.kind() == io::ErrorKind::WouldBlock => {
            reactor.set_waker(token, cx.waker().clone());
            Poll::Pending
        }
        Err(e) => Poll::Ready(Err(e)),
    }
}

async fn accept(
    reactor: ReactorHandle,
    listener: &mut TcpListener,
    token: Token,
) -> io::Result<TcpStream> {
    poll_fn(|cx| poll_io(&reactor, token, cx, || listener.accept().map(|(s, _)| s))).await
}

async fn read(
    reactor: ReactorHandle,
    stream: &mut TcpStream,
    token: Token,
    buf: &mut [u8],
) -> io::Result<usize> {
    poll_fn(|cx| poll_io(&reactor, token, cx, || stream.read(buf))).await
}

async fn handle(reactor: ReactorHandle, stream: TcpStream) {
    let (mut stream, token) = reactor.register_stream(stream, Interest::READABLE);
    let mut buf = [0u8; 1024];

    loop {
        match read(reactor.clone(), &mut stream, token, &mut buf).await {
            Ok(0) => break,
            Ok(n) => println!("收到: {}", String::from_utf8_lossy(&buf[..n]).trim_end()),
            Err(_) => break,
        }
    }

    reactor.deregister_stream(stream);
}

async fn server(
    spawner: Spawner,
    reactor: ReactorHandle,
    mut listener: TcpListener,
    token: Token,
) {
    loop {
        match accept(reactor.clone(), &mut listener, token).await {
            Ok(stream) => spawner.spawn(handle(reactor.clone(), stream)),
            Err(_) => break,
        }
    }
}

fn main() {
    let reactor = ReactorHandle::new();
    let executor = Executor::new();

    let listener = TcpListener::bind("127.0.0.1:8080".parse().unwrap()).unwrap();
    let (listener, token) = reactor.register_listener(listener, Interest::READABLE);

    println!("在 127.0.0.1:8080 等連線");
    executor
        .spawner()
        .spawn(server(executor.spawner(), reactor, listener, token));
    executor.run();
}
```

跑起來後，開另一個終端機用 `nc 127.0.0.1 8080` 連進去打字，伺服器那邊就會印出你送的訊息。

## 一步步看資料流

假設某個連線的 task 呼叫 `read(...).await`：

1. executor poll 這個 task。
2. `read` 嘗試 `stream.read(buf)`。
3. 目前沒資料，`read` 得到 `WouldBlock`。
4. `poll_io` 把目前 task 的 Waker 用 `SetWaker` 指令送到 reactor thread。
5. `read` 回 `Pending`，task 暫停。
6. reactor thread 之後從 `mio::Poll` 收到這個 socket 的 token。
7. reactor 用 token 找到 Waker，呼叫 `wake()`。
8. Waker 把 task 放回 ready queue，並叫醒 executor。
9. executor 再 poll 這個 task。
10. `read` 再試一次；如果資料真的到了，就回 `Ready`。

這整條路上，只有 executor poll task。reactor 只是負責「可以再試一次了」的通知。

## 重點整理

- executor 和 reactor 可以分開在不同 thread；executor 不需要擁有 `mio::Poll`
- reactor 不是 task，也不會被 executor poll
- I/O future 自己處理 `WouldBlock`：保存 Waker，回 `Pending`
- reactor thread 只等 I/O readiness；收到 token 後找到 Waker 並 wake
- task 的 Waker 仍然做同一件事：把 task 放回 ready queue，叫醒 executor
- `mio::Waker` 在這一集是 reactor 的指令門鈴，用來叫醒 `mio::Poll` 處理 channel 指令
- 教學版仍然簡化了很多細節：同步註冊、`unwrap` 錯誤處理、沒有 shutdown、沒有計時器，也沒有完整處理 cancellation safety
