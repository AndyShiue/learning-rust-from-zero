# `spawn` 與 `JoinHandle`

## 本集目標

上一集的 executor 已經能 `spawn` 很多個 `Output = ()` 的 task，並用 ready queue 排程。這一集只補一件事：讓 `spawn` 可以接受**任何回傳型別**的 future，並回傳一個 `JoinHandle<T>`，讓另一個 task 可以 `.await` 它、拿回結果。

關鍵釐清：不是 future 直接通知 future。真正發生的是「等待結果的 task 把自己的 Waker 留在共享狀態裡；原 task 完成後，透過那個 Waker 喚醒等待者」。

## 概念說明

### 跟第 11 集比，差在哪

第 11 集已經把排程做好了：`spawn` 一堆 `Output = ()` 的 task、用 ready queue 輪流 poll、`block_on` 跑到全部完成。這一集只在那之上加**三樣東西**，其餘原封不動：

1. **`spawn<T>` 收任意回傳型別**：從只收 `Future<Output = ()>`，變成收 `Future<Output = T>`，並回傳一個 `JoinHandle<T>`。
2. **`Shared<T>` 與 `JoinHandle<T>`**：task 的結果 `T` 放進共享格子 `Shared<T>`；`JoinHandle<T>` 本身也是 Future，`.await` 它就能把 `T` 領回來。
3. **`block_on` 開始回傳值**：第 11 集的 `block_on(future)` 回傳 `()`；這一集因為有了 `Shared<T>`，`block_on(future)` 可以回傳那個 future 的值 `T`。

ready queue、`park`/`unpark`、`Task` 結構這些第 11 集的東西完全沒動。一句話：**第 11 集解決「怎麼排 task」，這一集解決「task 做完後，值怎麼交回來」。**

### executor 內部仍然只存同一種 task

上一集的 `Task` 裡有一個 `Output = ()` 的 future。為什麼要這樣？因為 executor 會把很多 task 放進同一套資料結構；如果有的 task 回傳 `i32`、有的回傳 `String`，它們就不能直接放在同一種 `Task` 裡。

那使用者想 spawn `Future<Output = T>` 怎麼辦？答案是：**包一層**。把使用者的 future 包進一個 async block，這個 block 自己是 `Output = ()`（可以塞進 `Task`），它在內部 `.await` 原 future 拿到 `T`，再把 `T` 放進一個共享格子：

```rust,ignore
let wrapped = async move {
    let value = fut.await;            // 跑使用者的 future，拿到 T
    // 把 value 存到共享格子，再叫醒等待者
};
```

可以把它想成寄物櫃：executor 只收「標準箱子」（`Output = ()`），你的 task 算出任何 `T`，包裝層負責把 `T` 放進寄物櫃，`JoinHandle<T>` 是取物單，`.await` 它就能領回 `T`。

### 共享格子 `Shared<T>` 與 `JoinHandle<T>`

```rust,ignore
struct Shared<T> {
    result: Mutex<Option<T>>,    // task 的結果：還沒好是 None，好了是 Some(value)
    waker: Mutex<Option<Waker>>, // 正在等這個結果的 task 的 Waker
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
```

這裡要看清楚一件事：**`JoinHandle<T>` 本身不是 task、不會進 ready queue。** 它只是一個普通的 `Future`，被「等待它的那個 task」順帶 poll。當你在某個 task 裡 `handle.await`，`JoinHandle::poll` 就會：

- 結果已經在 `result` 裡：取出來，回 `Ready(value)`。
- 結果還沒好：用 `cx.waker()` 拿到「**正在 poll 它的那個 task（等待者）自己的 Waker**」存進 `Shared`，回 `Pending`。

注意：`JoinHandle` **沒有自己的 Waker**，它存的是「等待者 task 的 Waker」——也就是 executor poll 那個等待者 task 時，透過 `Context` 傳進來的 `cx.waker()`。

### 修改 `spawn`

`spawn` 對 `T` 泛型，把使用者的 future 包成 `wrapped`，完成時寫結果並叫醒等待者，最後回傳 `JoinHandle`：

```rust,ignore
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
        let value = fut.await;                                 // 1. 跑原 future，拿到 T
        *shared_for_task.result.lock().unwrap() = Some(value); // 2. 把 T 放進 Shared
        if let Some(waker) = shared_for_task.waker.lock().unwrap().take() {
            waker.wake();                                      // 3. 叫醒正在等的人
        }
    };

    // 後面和上一集一樣：把 wrapped 包成 Task、排進 ready queue
    // self.remaining += 1; task.schedule();

    JoinHandle { shared }
}
```

`wrapped` 完成時的「叫醒它」會走第 11 集的 ready queue 機制：等待者的 Waker → 把等待者 task 排回 ready queue + `unpark()` executor。所以核心模式是：

```text
某個結果還沒好
    -> 保存等待者的 Waker
    -> 回 Pending

結果好了
    -> 寫進 Shared
    -> 呼叫等待者的 Waker
    -> 等待者 task 回到 ready queue
```

（下一集會再出現同一個模式，只是「結果好了」換成「I/O ready 了」。）

### `block_on` 開始回傳值

`block_on<T>` 把傳進來的 future 也 spawn 成 task、保留它的 `JoinHandle`，跑完所有 task 後，從那個 `Shared` 取出結果回傳：

```rust,ignore
fn block_on<T: Send + 'static>(
    &mut self,
    future: impl Future<Output = T> + Send + 'static,
) -> T {
    let handle = self.spawn(future); // root 也 spawn 成 task，但保留它的 JoinHandle

    // …… 跟第 11 集一樣的迴圈：清 ready queue、空了就 park ……

    // 所有 task 都完成了，root 的結果一定已經寫進它的 Shared
    let result = handle.shared.result.lock().unwrap().take().unwrap();
    result
}
```

## 範例程式碼

spawn 一個回傳 `i32`（42）的背景 task；`block_on` 的 root 在裡面 `.await` 它的 `JoinHandle` 拿到結果，自己再回傳一個值（84）。

```rust,ignore
use std::collections::VecDeque;
use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, Ordering};
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

fn main() {
    let mut executor = Executor::new();

    // 背景 task：回傳 i32，先 spawn，拿到它的 JoinHandle
    let handle = executor.spawn(async {
        delay(1).await;
        42
    });

    // root task：裡面 .await 上面那個 JoinHandle，自己再回傳一個值
    let result = executor.block_on(async move {
        let from_task = handle.await;
        println!("task 回傳了 {}", from_task);
        from_task * 2
    });

    println!("block_on 拿到 {}", result);
}
```

跑起來會在約 1 秒後印出：

```text
task 回傳了 42
block_on 拿到 84
```

## 一步步看它怎麼跑

假設 A 是回傳 `42` 的背景 task，B 是傳給 `block_on` 的 future（裡面 `.await` A 的 `JoinHandle`，自己再回傳 `84`）。

1. `spawn(A)`：A 被包成 `Output = ()` 的 `wrapped`，放進 ready queue，回傳 `JoinHandle<i32>`（就是 main 裡的 `handle`）。
2. `block_on(B)`：root B 也被 `spawn` 成 task、放進 ready queue（block_on 保留 B 的 `JoinHandle`，最後要從裡面取值），然後開始跑迴圈。
3. block_on 先 poll A。A 卡在 `delay(1).await`，回 `Pending`。
4. poll B。B poll `handle`（`JoinHandle`），發現 `Shared.result` 還是 `None`，於是把 **B 的 Waker** 存進 `Shared.waker`，回 `Pending`。
5. queue 空了，executor 用 `thread::park()` 睡著。
6. 約 1 秒後，A 的計時器叫醒 A。A 被放回 ready queue，executor 被叫醒。
7. executor poll A，A 拿到 `42`。
8. A 的 `wrapped` 把 `42` 放進 `Shared.result`，再取出 **B 的 Waker** 並 `wake` 它；這不是直接繼續執行 B，只是把 B 排回 ready queue。
9. executor 下一輪 poll B。這次 `handle.await` 從 `Shared.result` 取到 `42`，印出，B 接著回傳 `84`。
10. B 的 `wrapped` 把 `84` 寫進 **B 自己的 `Shared`**；`remaining` 變成 0，迴圈結束。
11. `block_on` 從這個 future 的 `Shared` 取出 `84` 回傳，main 印出 `block_on 拿到 84`。

這裡有**兩種 Waker**：A 的 Waker（A 的計時器到期時叫醒「做事的 task A」）、B 的 Waker（`JoinHandle` 等待結果時存起來，A 完成後用來叫醒「等結果的 task B」）。兩者最後都走同一個排程機制：把對應 task 放回 ready queue。

## 重點整理

- executor 內部仍然只存 `Future<Output = ()>`，所有 task 共用同一種 `Task`
- `spawn<T>` 把 `Future<Output = T>` 包成 `Output = ()` 的 task，結果放進 `Shared<T>`
- `JoinHandle<T>` 本身不是 task、不會進 ready queue；它只是被「等待者 task」順帶 poll 的 `Future`，沒有自己的 Waker——`poll` 時用 `cx.waker()` 拿到**等待者 task 自己的 Waker** 存進 `Shared`
- 原 task 完成後，由它取出那個 Waker `wake()`，把**等待者 task** 排回 ready queue 並 `unpark()` executor
- 不是 future 直接通知 future，而是完成的一方透過共享狀態與 Waker 喚醒等待的一方
- `block_on(future)` 這集會回傳那個 future 的值 `T`（第 11 集只回傳 `()`）：把 root 也 spawn 成 task，跑完從它的 `Shared` 取出結果
