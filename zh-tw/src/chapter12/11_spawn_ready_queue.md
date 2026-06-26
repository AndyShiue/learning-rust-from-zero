# `spawn` 與 ready queue

## 本集目標

導入 `Task` 這個觀念，讓 executor 能同時養很多個 `Future`，並用 ready queue（待辦佇列）管理它們。

## 正文

### 為什麼需要 `Task`

前幾集的 executor 手上永遠只有**一個** `Future`，就在迴圈裡反覆 poll 它。但真實的 runtime 要同時養**很多**個 `Future`。

問題來了：當某個 `Future` 的 `Waker` 喊「我好了！」，如果 executor 手上有一堆裸 `Future`，它怎麼知道是**哪一個**好了、該去 poll 哪一個？光一個 `Future` 本身，是沒帶這個資訊的。

解法是給每個 `Future` 配一份「身分證＋隨身資料」，把它包成一個 **`Task`**。一個 `Task` 裝著：

- 它自己的那個 `Future`；
- 它該排回**哪條** ready queue；
- 該叫醒**哪條** executor thread；
- 一個避免自己重複排隊的旗標。

從此 executor 不再直接管 `Future`，而是管 `Task`。而所謂 `spawn`，就是「把一個 `Future` 包成 `Task`、交給 executor」。

### ready queue 與「按門鈴」

executor 有一條 **ready queue**：裡面排著「現在該被 poll 的 `Task`」。executor 的工作就是從 queue 裡拿 `Task` 出來 poll；queue 空了就去睡覺。

當一個 `Task` 被 `wake`，它就把**自己**放回 ready queue，然後 `unpark` 把睡著的 executor 叫醒。注意這個 `unpark` 只是一個**門鈴**——它只說「有事做了，起床！」，並不指出是哪個 `Task` 好了。真正「哪些 `Task` 該被 poll」的資訊，是放在 ready queue 裡的。

### 把它寫出來

這集的程式比較長，但骨架就是上面那幾句話。先看 `Task` 怎麼把自己排回 queue（這就是它的 `Wake` 實作）：

```rust,editable
use std::cell::RefCell;
use std::collections::VecDeque;
use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::time::{Duration, Instant};

# struct Delay {
#     when: Instant,
#     started: bool,
# }
# impl Delay {
#     fn new(d: Duration) -> Delay {
#         Delay { when: Instant::now() + d, started: false }
#     }
# }
# impl Future for Delay {
#     type Output = ();
#     fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
#         let this = self.get_mut();
#         if Instant::now() >= this.when {
#             Poll::Ready(())
#         } else {
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
// executor 共用的狀態
struct Executor {
    ready_queue: Mutex<VecDeque<Arc<Task>>>, // 該被 poll 的 Task 排在這
    thread: std::thread::Thread, // executor 那條 thread，用來 unpark
    task_count: AtomicUsize, // 還沒完成的 Task 數量
}

// 一個 Future ＋ 重新排程所需的隨身資料
struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    executor: Arc<Executor>,
    queued: AtomicBool, // 自己現在排在 queue 裡嗎？
}

impl Task {
    fn schedule(self: &Arc<Self>) {
        // swap 一步完成 check-and-set：只有把 false -> true 的那次才真的入列
        if !self.queued.swap(true, Ordering::AcqRel) {
            self.executor.ready_queue.lock().unwrap().push_back(self.clone());
            self.executor.thread.unpark(); // 按門鈴叫醒 executor
        }
    }
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        self.schedule();
    }
    fn wake_by_ref(self: &Arc<Self>) {
        self.schedule();
    }
}

thread_local! {
    // 目前正在跑的 executor，讓 spawn 找得到它（thread_local 就是「每條 thread 各自一份」的全域變數）
    static CURRENT: RefCell<Option<Arc<Executor>>> = RefCell::new(None);
}

// spawn：把一個 Future 包成 Task，交給目前的 executor
fn spawn<F: Future<Output = ()> + Send + 'static>(future: F) {
    CURRENT.with(|c| {
        let executor = c.borrow().clone().expect("spawn 必須在 block_on 裡呼叫");
        executor.task_count.fetch_add(1, Ordering::AcqRel);
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(future)),
            executor: executor.clone(),
            queued: AtomicBool::new(true), // 一建立就排進 queue
        });
        executor.ready_queue.lock().unwrap().push_back(task);
    });
}

fn block_on<F: Future<Output = ()> + Send + 'static>(future: F) {
    let executor = Arc::new(Executor {
        ready_queue: Mutex::new(VecDeque::new()),
        thread: std::thread::current(),
        task_count: AtomicUsize::new(0),
    });

    // 把這個 executor 設成「目前的」，讓 spawn 找得到
    CURRENT.with(|c| *c.borrow_mut() = Some(executor.clone()));

    // 傳進來的 Future 也 spawn 成一個 Task
    spawn(future);

    loop {
        // 先把 ready queue 清空
        loop {
            let task = executor.ready_queue.lock().unwrap().pop_front();
            let Some(task) = task else { break };

            task.queued.store(false, Ordering::Release); // poll 前先放掉旗標
            let waker = Waker::from(task.clone());
            let mut cx = Context::from_waker(&waker);
            let mut future = task.future.lock().unwrap();
            if future.as_mut().poll(&mut cx).is_ready() {
                executor.task_count.fetch_sub(1, Ordering::AcqRel); // 完成了
            }
        }

        // queue 空了。全部 Task 都完成了嗎？
        if executor.task_count.load(Ordering::Acquire) == 0 {
            break;
        }
        // 還有沒完成的，睡覺等門鈴
        std::thread::park();
    }
}

fn main() {
    block_on(async {
        spawn(async {
            println!("task A：開始");
            Delay::new(Duration::from_secs(1)).await;
            println!("task A：一秒到");
        });
        spawn(async {
            println!("task B：開始");
            Delay::new(Duration::from_secs(2)).await;
            println!("task B：兩秒到");
        });
        println!("main task：兩個 task 都 spawn 出去了");
    });
}
```

> 上面隱藏了第 10 集的 `Delay` 定義，按程式碼框左上角可展開。

跑起來，三個 `Task`（main、A、B）並行推進：A 在第一秒到期、B 在第二秒到期，各自到期時只把**自己**排回 queue 被 poll 一次，互不干擾。

### `queued` 旗標為什麼用 `swap`

`schedule` 裡的 `queued.swap(true, ...)` 是這集的小巧思。一個 `Task` 可能在很短時間內被 `wake` 好幾次，但它只該在 queue 裡出現一次，否則就會被重複 poll。

`swap(true)` 會把旗標設成 `true`，並回傳**舊值**。只有「舊值是 `false`」的那一次（代表它本來不在 queue 裡），才真的把 `Task` push 進去。後續的 `wake` 看到舊值已經是 `true`，就知道「已經排進去了」，直接跳過。這是第 9 章 atomic 的實際應用——用一個 atomic 操作同時完成「檢查＋設定」，不會有兩條 thread 同時擠進來的問題。

### 為什麼 `Future` 欄位這次要 `+ Send`

你可能注意到 `Task` 的 `future` 欄位型別寫成 `Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>`，比之前多了 `+ Send`，外面還包了一層 `Mutex`。為什麼？

順著推一遍就懂了：`Future` 被收進 `Task`，而 `Task` 又 `impl Wake`、兼任 `Waker`（理論上不一定要讓 `Task` 自己當 `Waker`，但這樣寫最省事）。`Waker::from(Arc<Task>)` 這個轉換要求 `Task: Send + Sync + 'static`。一個型別要 `Send + Sync`，它的**每個欄位**都得是 `Send + Sync`——包括那個 `Future`。

於是 `dyn Future` 得加上 `+ Send`（讓它能被搬到別條 thread），外面再包一層 `Mutex`（`Mutex<T>` 在 `T: Send` 時自動是 `Sync`）。上一集的 `Waker` 因為構造簡單，我們不必煩惱這些 bound；這集 `Task` 自己當 `Waker`，就得認真對待了。

下一集我們在這個基礎上，讓 `spawn` 能回傳結果——加上 `JoinHandle`。

## 重點整理

- 把每個 `Future` 包成 **`Task`**（`Future` ＋ 排程隨身資料），executor 從此管 `Task` 而非裸 `Future`
- **ready queue** 排著該被 poll 的 `Task`；`Task` 被 `wake` 時把自己排回 queue 再 `unpark` executor
- `unpark` 只是「起床」的門鈴，不說哪個 `Task` 好了；那資訊在 ready queue 裡
- `queued` 旗標用 `AtomicBool` + `swap` 做 check-and-set，避免同一個 `Task` 重複入列
- `Task` 自己當 `Waker`，`Waker::from(Arc<Task>)` 要求 `Task: Send + Sync + 'static`，所以 `Future` 欄位要 `+ Send` 並用 `Mutex` 包起來
