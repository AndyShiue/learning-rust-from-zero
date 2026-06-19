# `spawn` 與 `JoinHandle`

## 本集目標

上一集的 executor 已經能 `spawn` 很多個 `Output = ()` 的 task，並用 ready queue 排程：哪個 task 被喚醒，就把哪個 task 放回 queue，之後再 poll 它。

這一集只補一個能力：讓 `spawn` 可以接受**任何回傳型別**的 future，並回傳一個 `JoinHandle<T>`，讓另一個 task 可以 `.await` 它、拿回結果。

這裡要先釐清一件事：不是 future 直接通知 future。真正發生的是「等待結果的 task 把自己的 Waker 留在共享狀態裡；原 task 完成後，透過那個 Waker 喚醒等待者」。最後被喚醒的 task 仍然會回到 ready queue，等 executor 之後再 poll。

這樣拆開看，心智負擔會小很多：

```text
第 11 集：怎麼排程 task
第 12 集：task 做完後，結果怎麼交回來
```

## 概念說明

### executor 內部仍然只存同一種 task

上一集的 `Task` 裡有一個 future：

```rust,ignore
future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
```

也就是說，executor 內部只負責跑「完成時沒有直接回傳值」的標準 task。

為什麼要這樣？因為 executor 會把很多 task 放進同一套資料結構。如果有的 task 回傳 `i32`，有的回傳 `String`，有的回傳 `()`，它們就不能直接放在同一種 `Task` 裡。

那使用者真的想 spawn `Future<Output = T>` 怎麼辦？答案是：**包一層**。

### 把 `Future<Output = T>` 包成 `Future<Output = ()>`

假設使用者給我們一個 future：

```rust,ignore
async { 42 }
```

它的輸出是 `i32`。我們可以把它包成另一個 async block：

```rust,ignore
let wrapped = async move {
    let value = fut.await;
    // 把 value 存到某個共享地方
};
```

這個 `wrapped` 本身沒有回傳值，所以它是 `Future<Output = ()>`，可以塞進 executor 的 `Task`。真正的結果 `value` 則放到一個共享格子裡，讓 `JoinHandle<T>` 之後去拿。

可以把它想成：

- executor 只收「標準箱子」：`Output = ()`
- 你的 task 可以生出任何 `T`
- 包裝層負責把 `T` 放進寄物櫃
- `JoinHandle<T>` 是取物單，`.await` 它就能把 `T` 領回來

### 共享格子：`Shared<T>`

```rust,ignore
use std::sync::{Arc, Mutex};
use std::task::Waker;

struct Shared<T> {
    result: Mutex<Option<T>>,
    waker: Mutex<Option<Waker>>,
}
```

`result` 存 task 的結果。還沒完成時是 `None`，完成後變成 `Some(value)`。

`waker` 存的是「正在等待這個結果的 task」的 Waker。等結果放進來後，我們要叫醒那個正在 `.await JoinHandle` 的 task。

這個共享格子同時處理兩件事：

- `result` 回答「結果好了嗎？」
- `waker` 回答「如果結果好了，要叫醒誰？」

### `JoinHandle<T>` 本身也是 Future

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

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
```

`JoinHandle<T>` 的 `poll` 很直覺：

- 結果已經在 `result` 裡：取出來，回 `Ready(value)`。
- 結果還沒好：存下目前 task 的 Waker，回 `Pending`。

注意這裡的 Waker 是「等結果的 task」的 Waker，不是「正在工作的 task」的 Waker。這兩個很容易混在一起。

換句話說，`JoinHandle::poll` 遇到結果還沒好時，不會自己想辦法執行原 task；它只把等待者的聯絡方式留下來，然後回 `Pending`。

### 修改 `spawn`

現在 `spawn` 對 `T` 泛型：

```rust,ignore
impl Executor {
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

        // 後面和上一集一樣：
        // 建立 Task、把 wrapped 放進去、排進 ready queue

        JoinHandle { shared }
    }
}
```

`wrapped` 做三件事：

1. `.await` 使用者原本的 future，拿到 `T`
2. 把 `T` 放進 `Shared.result`
3. 如果有人正在等這個 `JoinHandle`，就叫醒它

這裡的「叫醒它」會走上一集的 ready queue 機制：等待者的 Waker 會把等待者 task 放回 ready queue，並用 `unpark()` 叫醒 executor。

所以第 12 集的核心模式是：

```text
某個結果還沒好
    -> 保存等待者的 Waker
    -> 回 Pending

結果好了
    -> 寫進 Shared
    -> 呼叫等待者的 Waker
    -> 等待者回到 ready queue
```

這個模式到了下一集會再出現一次，只是「結果好了」會換成「I/O ready 了」。

## 範例程式碼

這份程式是在上一集 executor 的基礎上，加上 `JoinHandle<T>`。它 spawn 一個回傳 `i32` 的 task，再從另一個 task `.await` 那個 handle。

```rust,ignore
use std::collections::VecDeque;
use std::future::Future;
use std::pin::Pin;
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::thread::Thread;
use std::time::{Duration, Instant};

struct Delay {
    when: Instant,
    started: bool,
}

impl Future for Delay {
    type Output = ();

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            return Poll::Ready(());
        }

        if !self.started {
            self.started = true;
            let waker = cx.waker().clone();
            let when = self.when;

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

fn delay(secs: u64) -> Delay {
    Delay {
        when: Instant::now() + Duration::from_secs(secs),
        started: false,
    }
}

type Queue = Arc<Mutex<VecDeque<Arc<Task>>>>;

struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    queue: Queue,
    executor_thread: Thread,
    queued: Mutex<bool>,
}

impl Task {
    fn schedule(self: &Arc<Self>) {
        let mut queued = self.queued.lock().unwrap();
        if !*queued {
            *queued = true;
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
            queued: Mutex::new(false),
        });

        self.remaining += 1;
        task.schedule();

        JoinHandle { shared }
    }

    fn run(&mut self) {
        while self.remaining > 0 {
            loop {
                let task = self.queue.lock().unwrap().pop_front();
                let Some(task) = task else { break };
                *task.queued.lock().unwrap() = false;

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
    }
}

fn main() {
    let mut executor = Executor::new();

    let handle = executor.spawn(async {
        delay(1).await;
        42
    });

    executor.spawn(async move {
        let result = handle.await;
        println!("task 回傳了 {}", result);
    });

    executor.run();
    println!("executor 結束");
}
```

跑起來會在約 1 秒後印出：

```text
task 回傳了 42
executor 結束
```

## 一步步看它怎麼跑

假設 A 是回傳 `42` 的 task，B 是等待 `JoinHandle` 的 task。

1. `spawn(A)`：A 被包成 `Output = ()` 的 `wrapped`，放進 ready queue，回傳 `JoinHandle<i32>`。
2. `spawn(B)`：B 會 `.await handle`，也被放進 ready queue。
3. executor 先 poll A。A 卡在 `delay(1).await`，回 `Pending`。
4. executor poll B。B poll `JoinHandle`，發現 `Shared.result` 還是 `None`，於是把 **B 的 Waker** 存進 `Shared.waker`，回 `Pending`。
5. queue 空了，executor 用 `thread::park()` 睡著。
6. 約 1 秒後，A 的計時器叫醒 A。A 被放回 ready queue，executor 被叫醒。
7. executor poll A，A 拿到 `42`。
8. A 的 `wrapped` 把 `42` 放進 `Shared.result`，再取出 **B 的 Waker** 並 `wake` 它；這不是直接繼續執行 B，只是把 B 排回 ready queue。
9. B 的 Waker 把 B 放回 ready queue，executor 下一輪 poll B。
10. 這次 `handle.await` 從 `Shared.result` 取到 `42`，B 繼續執行並印出結果。

這裡有兩種 Waker：

- **A 的 Waker**：A 的 `Delay` 到期時，用來叫醒「做事的 task A」。
- **B 的 Waker**：`JoinHandle` 等待結果時存起來，A 完成後用來叫醒「等結果的 task B」。

兩者最後都會走同一個排程機制：**把對應 task 放回 ready queue。**

## 重點整理

- executor 內部仍然只存 `Future<Output = ()>`，這樣所有 task 才能共用同一種 `Task`
- `spawn<T>` 會把 `Future<Output = T>` 包成 `Future<Output = ()>`
- task 的結果 `T` 放進 `Shared<T>`，`JoinHandle<T>` 負責去拿
- `JoinHandle<T>` 本身也是 Future；結果還沒好就存下等待者的 Waker 並回 `Pending`
- 原 task 完成後 wake 等待者；等待者會被放回 ready queue，之後再被 executor poll
- 這不是 future 直接通知 future，而是透過共享狀態與 Waker 喚醒「正在等待的 task」
- `spawn` 不開新的 OS thread；它只是把 future 變成 task，交給 executor 之後慢慢 poll
