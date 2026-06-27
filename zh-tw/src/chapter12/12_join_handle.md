# `spawn` 與 `JoinHandle`

## 本集目標

讓 `spawn` 出去的 `Task` 能把結果回傳，方法是加上 `JoinHandle`——一個可以 `.await` 的把手。

## 正文

### 和上一集只差三樣東西

上一集的 `spawn` 有個遺憾：它只收 `Future<Output = ()>`，工作做完就做完了，沒辦法把結果交回來。這集來補上。

好消息是，排程的核心邏輯**完全不動**，我們只在上面加三樣東西：

1. 新增一個共享狀態 `Shared<T>`，和一個 `JoinHandle<T>`（它本身也是一個 `Future`）。
2. `Executor::spawn` 從只收 `Future<Output = ()>`，升級成收 `Future<Output = T>` 並回傳 `JoinHandle<T>`。
3. `Executor::block_on` 從回傳 `()`，升級成回傳「傳進去那個 `Future` 的值」`T`。

### 完成的一方，怎麼通知等待的一方

核心問題是：背景 `Task` 完成時，怎麼把結果交給「正在 `.await` 它的人」？

答案是**透過一塊共享狀態 `Shared<T>`**，而不是 `Future` 直接通知 `Future`。`Shared<T>` 裡放兩樣東西：算好的結果，以及「等待者的 `Waker`」。

流程是這樣的：

- `JoinHandle<T>` 本身**不是** `Task`，不會進 ready queue。它只是一個 `Future`，被「等待者 `Task`」在 `.await` 時順帶 `poll`。
- 等待者 poll `JoinHandle` 時，如果結果還沒好，`JoinHandle` 就把 `cx.waker()`（也就是**等待者自己的** `Waker`，因為 `JoinHandle` 沒有自己的 `Waker`）存進 `Shared<T>`，回 `Pending`。
- 等背景 `Task` 完成，它把結果放進 `Shared<T>`，再取出剛剛那個 `Waker`、`wake()`——於是等待者 `Task` 被排回 ready queue、executor 被 `unpark`。等待者再次被 poll 時，就能從 `Shared<T>` 拿到結果了。

```rust,editable
use std::collections::VecDeque;
use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
use std::time::{Duration, Instant};

struct Delay {
    when: Instant,
    started: bool,
}

impl Delay {
    fn new(duration: Duration) -> Delay {
        Delay { when: Instant::now() + duration, started: false }
    }
}

impl Future for Delay {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        if Instant::now() >= this.when {
            Poll::Ready(())
        } else {
            if !this.started {
                this.started = true;
                let waker = cx.waker().clone();
                let when = this.when;
                thread::spawn(move || {
                    let now = Instant::now();
                    if now < when {
                        thread::sleep(when - now);
                    }
                    waker.wake();
                });
            }
            Poll::Pending
        }
    }
}

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
        let mut state = self.shared.state.lock().expect("取得鎖失敗");
        if let Some(value) = state.0.take() {
            Poll::Ready(value) // 結果好了
        } else {
            state.1 = Some(cx.waker().clone()); // 還沒好，存等待者自己的 Waker
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

    // spawn<T>：收 Future<Output = T>，回傳 JoinHandle<T>
    fn spawn<T, F>(&mut self, future: F) -> JoinHandle<T>
    where
        F: Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        let shared = Arc::new(Shared { state: Mutex::new((None, None)) });
        let shared_for_task = shared.clone();

        // 把 Future<Output = T> 包成 executor 看得懂的 Future<Output = ()>
        let task_future = async move {
            let value = future.await; // 真正跑那個工作
            let mut state = shared_for_task.state.lock().expect("取得鎖失敗");
            state.0 = Some(value); // 放進結果
            if let Some(waker) = state.1.take() {
                waker.wake(); // 叫醒在等的人
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
        let handle = self.spawn(future); // 傳進來的 Future 也 spawn 成 Task，留著它的 JoinHandle

        // 跑到所有 Task 完成（迴圈和上一集一模一樣）
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

        // 從 Shared 取出結果回傳
        handle.shared.state.lock().expect("取得鎖失敗").0.take().expect("結果應該已經算好了")
    }
}

fn main() {
    let mut executor = Executor::new();

    // spawn 一個回傳 i32 的背景 Task
    let handle = executor.spawn(async {
        Delay::new(Duration::from_secs(1)).await;
        println!("背景 task：算好了");
        21 * 2
    });

    let result = executor.block_on(async move {
        // 在這裡 .await 背景 Task 的 JoinHandle，取得結果
        let value = handle.await;
        println!("main task：拿到背景結果 {}", value);

        value + 100 // 自己再回傳一個值
    });
    println!("block_on 回傳：{}", result);
}
```

### 一步步看它怎麼跑

假設 A 是上面那個背景 `Task`：它等一秒後算出 `42`。B 是傳給 `block_on` 的那個 `Task`：它 `.await` A 的 `JoinHandle`，拿到結果後再回傳 `142`。

1. `executor.spawn(A)`：`spawn` 先建立一層 `task_future`，負責等待 A、把結果寫進 `Shared<T>`、喚醒等待者。真正放進 ready queue 的是這層包裝後的 `Task`；`spawn` 同時回傳一個 `JoinHandle<i32>`，也就是程式裡的 `handle`。
2. `executor.block_on(B)`：B 也被 `spawn` 成一個 `Task`，放進 ready queue；`block_on` 自己保留 B 的 `JoinHandle`，最後要從裡面取出 B 的回傳值。
3. executor 先 `poll` A 這個 `Task`。實際被 `poll` 的是外層 `task_future`；它跑到 `let value = future.await`，才開始 poll 內層真正的 A。內層 A 跑到 `Delay::new(...).await`，開始 poll `Delay`；`Delay` 還沒完成，所以回 `Pending`。這個 `Pending` 一路傳回外層 `task_future`，A 這次 `poll` 就結束了。
4. A 回 `Pending` 後，executor 沒有睡覺，因為 ready queue 裡還有 B。它立刻 `poll` B 這個 `Task`。同樣地，先被 `poll` 的是 B 外面的 `task_future`；它跑到 `let value = future.await`，才開始 `poll` 傳給 `block_on` 的那個 `async` block。
5. B 內層的 `async` block 跑到 `handle.await`，於是 `poll` A 的 `JoinHandle`。這時 A 的結果還沒好，`JoinHandle` 把 B 的 `Waker` 存進 `Shared<T>`，回 `Pending`。這個 `Pending` 一路傳回 B 外面的 `task_future`，B 也先停住。
6. ready queue 空了，executor 用 `thread::park()` 睡著。
7. 約一秒後，A 的計時 `Thread` 呼叫 A 的 `Waker`，A 被排回 ready queue，executor 被 `unpark` 叫醒。
8. executor 再 `poll` A。這次還是先 `poll` A 外面的 `task_future`，它繼續 poll 內層 A；`Delay` 已經完成，所以 A 從 `.await` 後面繼續跑，先印出 `背景 task：算好了`，再算出 `42`。
9. A 外面的 `task_future` 拿到 `42`，把它放進 `Shared<T>`，再取出剛剛存著的 B 的 `Waker` 並 `wake()` 它。這不是直接繼續執行 B，而是把 B 排回 ready queue。
10. executor 接下來 `poll` B。B 外面的 `task_future` 繼續 `poll` 內層 `async` block；這次 `handle.await` 從 `Shared<T>` 取到 `42`，印出 `main task：拿到背景結果 42`，然後 B 回傳 `142`。
11. B 自己外面那層 `task_future` 把 `142` 寫進 B 自己的 `Shared<T>`。所有 `Task` 都完成後，`block_on` 從 B 的 `JoinHandle` 裡取出 `142` 回傳，最後印出 `block_on 回傳：142`。

這裡有兩個不同的 `Waker`：A 的 `Waker` 用來在計時完成時叫醒「做事的 A」；B 的 `Waker` 則是 `JoinHandle` 在等待 A 結果時存起來的，用來在 A 完成後叫醒「等結果的 B」。來源不同，但最後都走同一條路：把對應的 `Task` 排回 ready queue，再 `unpark` executor。

### 不是 `Future` 直接通知 `Future`

請特別記住這集的精神：`JoinHandle` 和背景 `Task` 之間沒有直接連線，它們只共用一塊 `Shared<T>`。等待的一方把自己的 `Waker` 留在共享狀態裡，完成的一方做完後從共享狀態取出這個 `Waker`、把它 `wake`。所有的喚醒，最後都還是回到「排回 ready queue + `unpark` executor」這條老路上。

到這裡，我們手寫的 executor 已經有模有樣了：能 `spawn`、能睡覺、能被叫醒。但它還缺一塊大拼圖——目前「等待」靠的還是替每個 `Delay` 開一條 `Thread`。下一集起，我們要引入 `mio` 和 reactor，用少少幾條 `Thread` 盯住真正的 I/O。

## 重點整理

- `JoinHandle<T>` 是一個 `Future`，`.await` 它就能拿到背景 `Task` 的回傳值
- 排程核心不變，只加三樣：`Shared<T>` ＋ `JoinHandle<T>`、回傳 `JoinHandle<T>` 的 `Executor::spawn<T>`、回傳 `T` 的 `Executor::block_on`
- `JoinHandle` 沒有自己的 `Waker`，它在 `.await` 時把**等待者自己的** `Waker` 存進 `Shared<T>`
- 背景 `Task` 完成時把結果放進 `Shared<T>`，再取出那個 `Waker` `wake()`，喚醒等待者
- 喚醒不是 `Future` 直接通知 `Future`，而是完成方透過共享狀態喚醒等待方
