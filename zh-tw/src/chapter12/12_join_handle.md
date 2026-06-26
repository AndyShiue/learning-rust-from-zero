# `spawn` 與 `JoinHandle`

## 本集目標

讓 `spawn` 出去的 `Task` 能把結果回傳，方法是加上 `JoinHandle`——一個可以 `.await` 的把手。

## 概念說明

### 和上一集只差三樣東西

上一集的 `spawn` 有個遺憾：它只收 `Future<Output = ()>`，工作做完就做完了，沒辦法把結果交回來。這集來補上。

好消息是，排程的核心邏輯**完全不動**，我們只在上面加三樣東西：

1. 新增一個共享狀態 `Shared<T>`，和一個 `JoinHandle<T>`（它本身也是一個 `Future`）。
2. `spawn<T>` 從只收 `Future<Output = ()>`，升級成收 `Future<Output = T>` 並回傳 `JoinHandle<T>`。
3. `block_on` 從回傳 `()`，升級成回傳「傳進去那個 `Future` 的值」`T`。

### 完成的一方，怎麼通知等待的一方

核心問題是：背景 `Task` 完成時，怎麼把結果交給「正在 `.await` 它的人」？

答案是**透過一塊共享狀態 `Shared<T>`**，而不是 `Future` 直接通知 `Future`。`Shared<T>` 裡放兩樣東西：算好的結果，以及「等待者的 `Waker`」。

流程是這樣的：

- `JoinHandle<T>` 本身**不是** `Task`，不會進 ready queue。它只是一個 `Future`，被「等待者 `Task`」在 `.await` 時順帶 poll。
- 等待者 poll `JoinHandle` 時，如果結果還沒好，`JoinHandle` 就把 `cx.waker()`（也就是**等待者自己的** `Waker`，因為 `JoinHandle` 沒有自己的 `Waker`）存進 `Shared<T>`，回 `Pending`。
- 等背景 `Task` 完成，它把結果放進 `Shared<T>`，再取出剛剛那個 `Waker`、`wake()`——於是等待者 `Task` 被排回 ready queue、executor 被 `unpark`。等待者再次被 poll 時，就能從 `Shared<T>` 拿到結果了。

```rust,editable
# use std::cell::RefCell;
# use std::collections::VecDeque;
# use std::future::Future;
# use std::pin::Pin;
# use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
# use std::sync::{Arc, Mutex};
# use std::task::{Context, Poll, Wake, Waker};
# use std::time::{Duration, Instant};
#
# struct Delay { when: Instant, started: bool }
# impl Delay {
#     fn new(d: Duration) -> Delay { Delay { when: Instant::now() + d, started: false } }
# }
# impl Future for Delay {
#     type Output = ();
#     fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
#         let this = self.get_mut();
#         if Instant::now() >= this.when { Poll::Ready(()) }
#         else {
#             if !this.started {
#                 this.started = true;
#                 let waker = cx.waker().clone();
#                 let when = this.when;
#                 std::thread::spawn(move || {
#                     let now = Instant::now();
#                     if now < when { std::thread::sleep(when - now); }
#                     waker.wake();
#                 });
#             }
#             Poll::Pending
#         }
#     }
# }
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
#
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
#
# thread_local! {
#     static CURRENT: RefCell<Option<Arc<Executor>>> = RefCell::new(None);
# }
#
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
#
# fn run(executor: &Arc<Executor>) {
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
#
// 背景 Task 與它的 JoinHandle 共用的狀態
struct Shared<T> {
    state: Mutex<(Option<T>, Option<Waker>)>, // (結果, 等待者的 Waker)
}

struct JoinHandle<T> {
    shared: Arc<Shared<T>>,
}

impl<T> Future for JoinHandle<T> {
    type Output = T;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<T> {
        let mut state = self.shared.state.lock().unwrap();
        if let Some(value) = state.0.take() {
            Poll::Ready(value) // 結果好了
        } else {
            state.1 = Some(cx.waker().clone()); // 還沒好，存等待者自己的 Waker
            Poll::Pending
        }
    }
}

// spawn<T>：收 Future<Output = T>，回傳 JoinHandle<T>
fn spawn<T, F>(future: F) -> JoinHandle<T>
where
    F: Future<Output = T> + Send + 'static,
    T: Send + 'static,
{
    let shared = Arc::new(Shared { state: Mutex::new((None, None)) });
    let shared_for_task = shared.clone();

    // 把 Future<Output = T> 包成 executor 看得懂的 Future<Output = ()>
    spawn_task(async move {
        let value = future.await; // 真正跑那個工作
        let mut state = shared_for_task.state.lock().unwrap();
        state.0 = Some(value); // 放進結果
        if let Some(waker) = state.1.take() {
            waker.wake(); // 叫醒在等的人
        }
    });

    JoinHandle { shared }
}

fn block_on<T, F>(future: F) -> T
where
    F: Future<Output = T> + Send + 'static,
    T: Send + 'static,
{
    let executor = Arc::new(Executor::new());
    CURRENT.with(|c| *c.borrow_mut() = Some(executor.clone()));

    let handle = spawn(future); // 傳進來的 Future 也 spawn 成 Task，留著它的 JoinHandle
    run(&executor); // 跑到所有 Task 完成（迴圈和上一集一模一樣）

    // 從 Shared 取出結果回傳
    handle.shared.state.lock().unwrap().0.take().expect("結果應該已經算好了")
}

fn main() {
    let result = block_on(async {
        // spawn 一個回傳 i32 的背景 task
        let handle = spawn(async {
            Delay::new(Duration::from_secs(1)).await;
            println!("背景 task：算好了");
            21 * 2
        });

        // 在這裡 .await 背景 task 的 JoinHandle，取得結果
        let value = handle.await;
        println!("main task：拿到背景結果 {value}");

        value + 100 // 自己再回傳一個值
    });
    println!("block_on 回傳：{result}");
}
```

> 上面隱藏了第 11 集的排程程式（`Executor`、`Task`、`spawn_task`、`run` 等），按程式碼框左上角可展開。

### 重點：完成的一方主動喚醒等待的一方

請特別記住這集的精神：這**不是** `Future` 直接通知 `Future`。`JoinHandle` 和背景 `Task` 之間沒有直接連線，它們只共用一塊 `Shared<T>`。等待的一方把自己的 `Waker` 留在共享狀態裡，完成的一方做完後從共享狀態取出這個 `Waker`、把它 `wake()`。所有的喚醒，最後都還是回到「排回 ready queue ＋ `unpark` executor」這條老路上。

到這裡，我們手寫的 executor 已經有模有樣了：能 `spawn`、能 `join`、能睡覺、能被叫醒。但它還缺一塊大拼圖——目前「等待」靠的還是替每個 `Delay` 開一條 thread。下一集起，我們要引入 `mio` 和 reactor，用少少幾條 thread 盯住真正的 I/O。

## 重點整理

- `JoinHandle<T>` 是一個 `Future`，`.await` 它就能拿到背景 `Task` 的回傳值。
- 排程核心不變，只加三樣：`Shared<T>` ＋ `JoinHandle<T>`、回傳 `JoinHandle<T>` 的 `spawn<T>`、回傳 `T` 的 `block_on`。
- `JoinHandle` 沒有自己的 `Waker`，它在 `.await` 時把**等待者自己的** `Waker` 存進 `Shared<T>`。
- 背景 `Task` 完成時把結果放進 `Shared<T>`，再取出那個 `Waker` `wake()`，喚醒等待者。
- 喚醒不是 `Future` 直接通知 `Future`，而是完成方透過共享狀態喚醒等待方。
