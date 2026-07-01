# `spawn` 與 ready queue

## 本集目標

導入 `Task` 這個觀念，讓 executor 能同時養很多個 `Future`，並用 ready queue（待辦佇列）管理它們。

## 正文

### 為什麼需要 `Task`

前幾集的 executor 手上永遠只有**一個** `Future`，就在迴圈裡反覆 `poll` 它。但真實的 runtime 要同時養**很多**個 `Future`。

問題來了：當某個 `Future` 的 `Waker` 喊「我好了！」，如果 executor 手上有一堆裸 `Future`，它怎麼知道是**哪一個**好了、該去 `poll` 哪一個？光一個 `Future` 本身，是沒帶這個資訊的。

解法是給每個 `Future` 配一份「隨身資料」，把它包成一個 **`Task`**。一個 `Task` 裝著：

- 它自己的那個 `Future`
- 它該排回**哪條** ready queue
- 該叫醒**哪條** executor `Thread`
- 一個避免自己重複排隊的旗標

從此 executor 不再直接管 `Future`，而是管 `Task`。而所謂 `spawn`，就是「把一個 `Future` 包成 `Task`、交給 executor」。

### ready queue 與「喚醒」

executor 將會有一條 **ready queue**：裡面排著「現在該被 `poll` 的 `Task`」。executor 的工作就是從 queue 裡拿 `Task` 出來 `poll`；queue 空了就去睡覺。

當一個 `Task` 被 `wake`，它就把**自己**放回 ready queue，然後 `unpark` 把睡著的 executor 叫醒。注意這個 `unpark` 只是一個**鬧鈴**——它只說「有事做了，起床！」，並不指出是哪個 `Task` 好了。真正「哪些 `Task` 該被 `poll`」的資訊，是放在 ready queue 裡的。

### 把它寫出來

這集的程式比較長，但骨架就是上面那幾句話。來看 `Task` 怎麼把自己排回 queue（這就是它的 `Wake` 實作），以及 `Executor` 怎麼顯式提供 `spawn` 和 `block_on`：

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
        Delay {
            when: Instant::now() + duration,
            started: false,
        }
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

// 一個 Future ＋ 重新排程所需的隨身資料
struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    queue: Queue,
    executor_thread: Thread,
    queued: AtomicBool, // 自己現在排在 queue 裡嗎？
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        // 拿到舊的 queued 值，同時把新的 true 留回去
        if !self.queued.swap(true, Ordering::SeqCst) {
            self.queue.lock().expect("取得鎖失敗").push_back(self.clone());
            self.executor_thread.unpark(); // 叫醒 executor
        }
    }
}

struct Executor {
    queue: Queue,
    executor_thread: Thread,
    remaining: usize, // 還沒完成的 Task 數量
}

impl Executor {
    fn new() -> Executor {
        Executor {
            queue: Arc::new(Mutex::new(VecDeque::new())),
            executor_thread: thread::current(),
            remaining: 0,
        }
    }

    // spawn：把一個 Future 包成 Task，排進 executor 的 queue
    fn spawn(&mut self, future: impl Future<Output = ()> + Send + 'static) {
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(future)),
            queue: self.queue.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
        });

        self.remaining += 1;
        task.wake(); // 新 task 需要第一次排進 ready queue
    }

    fn block_on(&mut self, future: impl Future<Output = ()> + Send + 'static) {
        // 傳進來的 Future 也 spawn 成一個 Task
        self.spawn(future);

        while self.remaining > 0 {
            // 先把 ready queue 清空
            loop {
                let task = self.queue.lock().expect("取得鎖失敗").pop_front();
                let Some(task) = task else { break };

                task.queued.store(false, Ordering::SeqCst); // poll 前先放掉旗標
                let waker = Waker::from(task.clone());
                let mut cx = Context::from_waker(&waker);
                let mut future = task.future.lock().expect("取得鎖失敗");

                if future.as_mut().poll(&mut cx).is_ready() {
                    self.remaining -= 1; // 完成了
                }
            }

            // queue 空了。全部 Task 都完成了嗎？
            if self.remaining > 0 {
                // 還有沒完成的，睡覺等人叫醒
                thread::park();
            }
        }
    }
}

fn main() {
    let mut executor = Executor::new();

    executor.spawn(async {
        println!("task A：開始");
        Delay::new(Duration::from_secs(1)).await;
        println!("task A：一秒到");
    });

    executor.block_on(async {
        println!("task B：開始");
        Delay::new(Duration::from_secs(2)).await;
        println!("task B：兩秒到");
    });

    println!("executor 結束");
}
```

跑起來，兩個 `Task`（A、B）並行推進：A 在第一秒到期、B 在第二秒到期，各自到期時只把**自己**排回 queue 被 `poll` 一次，互不干擾。`block_on` 會等到 executor 裡所有 `Task` 都完成才回來，所以最後才印出「executor 結束」。

### `queued` 旗標為什麼用 `swap`

`wake` 裡的 `queued.swap(true, ...)` 和第 9 集的 `Option::take` 很像：它不是單純「讀一個值」，而是**拿到舊值，同時把新值留在原本的位置**。

第 9 集的 `slot.take()` 是「把 `Some(fut)` 拿出來，原本的位置留下 `None`」。這裡的 `queued.swap(true, ...)` 則是「把舊的 `queued` 拿出來，原本的位置留下 `true`」。所以：

- 如果拿到的是 `false`，代表這個 `Task` 原本**不在** queue 裡，我們就把它 push 進去。
- 如果拿到的是 `true`，代表它已經在 queue 裡了，這次 `wake` 就不用再排一次。

為什麼不能先 `load` 再 `store`？因為 `wake` 可能來自不同 `Thread`。`swap` 把「看舊值」和「留下新值」綁成一次 atomic 操作，才不會兩條 thread 都同時看到 `false`、然後把同一個 `Task` 重複排進 queue。

### 為什麼 `Future` 欄位要是 `Send`

你可能會注意到 `Task` 的 `future` 欄位型別寫成 `Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>`，為什麼要 `Send`？

順著推一遍就懂了：`Future` 被收進 `Task`，而 `Task` 又 `impl Wake` 兼任 `Waker`（理論上不一定要讓 `Task` 自己當 `Waker`，但這樣寫最省事）。`Waker::from(Arc<Task>)` 這個轉換要求 `Task: Send + Sync + 'static`。一個型別要 `Send + Sync`，它的**每個欄位**都得是 `Send + Sync`——包括那個 `Future`。

於是 `dyn Future` 得加上 `+ Send`（讓它能被搬到別條 `Thread`），外面再包一層 `Mutex`（`Mutex<T>` 在 `T: Send` 時自動是 `Sync`）。上一集的 `Waker` 因為構造簡單，我們不必煩惱這些 bound；這集 `Task` 自己當 `Waker`，就得認真對待了。

下一集我們在這個基礎上，讓 `spawn` 能回傳結果——加上 `JoinHandle`。

## 重點整理

- 把每個 `Future` 包成 **`Task`**（`Future` ＋ 排程隨身資料），executor 從此管 `Task` 而非裸 `Future`
- **ready queue** 排著該被 poll 的 `Task`；`Task` 被 `wake` 時把自己排回 queue 再 `unpark` executor
- `unpark` 只是「起床」的鬧鈴，不說哪個 `Task` 好了；那資訊在 ready queue 裡
- `spawn` 是 `Executor` 的方法：把 `Future` 包成 `Task`，排進自己的 ready queue
- `queued.swap(true, ...)` 像 `Option::take`：拿到舊值、留下新值，且是一次 atomic 操作，避免同一個 `Task` 重複入列
- `Task` 自己當 `Waker`，`Waker::from(Arc<Task>)` 要求 `Task: Send + Sync + 'static`，所以 `Future` 欄位要 `+ Send` 並用 `Mutex` 包起來
