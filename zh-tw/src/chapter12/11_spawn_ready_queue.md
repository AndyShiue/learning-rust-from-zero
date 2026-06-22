# `spawn` 與 ready queue

## 本集目標

這一集要做一個更接近真實 runtime 的 executor。它先**只處理 `Output = ()` 的 task**，目標是建立一個重要模型：

```text
task 被 wake
    -> 把 task 放回 ready queue
    -> 用 Thread::unpark() 叫醒睡著的 executor
    -> executor 從 ready queue 拿 task 出來 poll
```

`JoinHandle<T>` 和「task 回傳結果」先不要塞進來，下一集再講。這一集先把 executor 的排程方式釘牢。

## 概念說明

### 先講這一集的新主角：task

到上一集為止，我們的 executor 手上永遠只有**一個 future**：`run` 把它 `Box::pin` 起來，就在迴圈裡反覆 poll 它一個。但真實的 runtime 要同時養**很多個** future，而且每一個都可能在不同時間被各自的事件喚醒、各自需要「再被 poll 一次」。

這就帶出一個問題：當某個 future 的 Waker 喊「我好了」，executor 要怎麼知道是**哪一個** future、又該把它放回哪裡？一個裸的 future 身上沒有這些資訊——它不知道自己屬於哪個 executor、該排回哪條 queue。

所以這一集引入一個新觀念：**task**。task 就是「**一個 future，外加把它重新排程所需要的隨身資料**」。具體來說，我們會把每個 future 包成一顆 `Task`，讓它隨身帶著：

- 它自己的 future（要被 poll 的本體）
- 該排回哪條 ready queue
- 該叫醒哪條 executor thread
- 一個小旗標，記住自己是不是已經在 queue 裡（避免重複排隊）

從這一集起，**executor 不再直接管 future，而是管 task**。「把一個 future 包成 task、交給 executor 排程」這個動作，等一下就叫 `spawn`；而一顆 task 的 Waker 被呼叫時，做的事也很單純——把自己這顆 task 排回 ready queue。

接下來幾節，就把這件事一塊一塊拆開：Waker 怎麼排、ready queue 是什麼、executor 怎麼睡跟醒。

### Waker 只負責把 task 排回去

上一集已經看過 `Waker`：事件源可以呼叫 `wake()`，告訴 executor「這個 future 應該再被 poll 一次」。

可是光知道「該再 poll 一次」還不夠。executor 還需要知道：**到底是哪個 task 該被 poll？**

這一集先不碰真正的 I/O reactor，也不碰 `mio::Poll`。我們先用標準庫的 `thread::park()` / `Thread::unpark()` 來叫醒 executor thread。

流程會像這樣：

```text
executor 沒事做
    -> thread::park()

task 被 wake
    -> task 進 ready queue
    -> executor_thread.unpark()
```

`unpark` 只是一個門鈴。它不會告訴 executor 是哪個 task 好了。真正該 poll 哪個 task 的資訊放在 ready queue 裡，因為 queue 裡直接存著 `Arc<Task>`。

### ready queue：準備好被 poll 的 task

ready queue 是一個佇列，裡面放「現在應該被 poll 一次」的 task。

```text
ready queue:
[ task A, task C, task F ]
```

executor 的工作就是反覆做：

```text
從 ready queue 拿一個 task
    -> poll 它
    -> Ready：task 完成
    -> Pending：先放著，等它之後自己 wake
```

如果 ready queue 空了，但還有 task 沒完成，executor 就 `park()` 睡著。之後某個 task 的事件好了，Waker 會把 task 放回 queue，並 `unpark()` executor。

### 為什麼用 `park/unpark`

`park/unpark` 很適合這一集，因為它剛好表達「叫醒某條 thread」：

- `thread::park()`：目前 thread 睡覺。
- `executor_thread.unpark()`：叫醒那條 executor thread。

而且 `unpark` 有一個關鍵特性：如果 `unpark()` 發生在 `park()` 之前，這次喚醒**不會消失**。它會留下一張 permit，下一次 `park()` 會立刻返回。所以就算「wake 比 park 早一步」（task 被排回 queue、unpark 了，executor 卻還沒睡），也不會漏接、不會睡死（第 10 集詳述過這個 permit 特性）。

但也要記得：`unpark` 不攜帶資料。它只表示「醒來看看」。醒來後到底要 poll 哪些 task，仍然要看 ready queue。

### Task 與它的 Waker

把前面說的 task 寫成 struct，就是這樣——一個 future，配上「排回哪條 queue、叫醒哪條 thread、是否已排隊」這幾樣隨身資料：

```rust,ignore
use std::collections::VecDeque;
use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::task::Wake;
use std::thread::Thread;

type Queue = Arc<Mutex<VecDeque<Arc<Task>>>>;

struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    queue: Queue,
    executor_thread: Thread,
    queued: AtomicBool,
}

impl Task {
    fn schedule(self: &Arc<Self>) {
        // swap(true) 一步完成「讀舊值 + 設成 true」：只有讓 false→true 的那次會 push
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
```

`wake` 的意思是：「這個 task 應該再被 poll 一次」。所以它做兩件事：

1. 把 task 放進 ready queue。
2. `unpark()` executor thread。

`queued` 這個旗標用 `AtomicBool`（前面章節已教過 atomic）：`schedule` 用 `queued.swap(true, ...)` 一步完成「檢查＋設定」——只有讓 `false → true` 的那一次 `wake` 會真的把 task push 進 queue，避免同一個 task 被重複塞進去很多次。

### 為什麼 future 這次要加 `Send`

眼尖的你可能發現：`future` 欄位寫的是 `dyn Future<Output = ()> + Send`，多了一個 `+ Send`；第 6～10 集的 executor 並沒有這個要求。為什麼?

因為這一集的 future 會被裝進一個**會跨執行緒的東西**裡。鏈條是這樣：future 收進 `Task` → `Task` 兼任 `Waker`（它 `impl Wake`）→ 這個 Waker 會被 `Delay` `move` 到另一條計時 thread 去呼叫 `wake()`。

而「從 `Arc<Task>` 做出 `Waker`」這件事（`Waker::from(task.clone())`），標準庫要求 `Task: Send + Sync + 'static`。一顆 struct 要是 `Send + Sync`，它**每個欄位都得是**——包括 `future`。一個普通的 `dyn Future` 預設不是 `Send`，所以要補上 `+ Send`（外面再包 `Mutex` 補上 `Sync`），整顆 `Task` 才湊得齊 `Send + Sync`。

對照第 6～10 集：那時 future 被 `Box::pin` 釘在呼叫 executor 的那條 thread 上、就地反覆 poll，從不跨執行緒；Waker 也是另一個沒包 future 的小型別（`ThreadWaker`）。所以 future 不必是 `Send`。一句話：**`Send` 不是 future 自己要的，是被「要當 Waker、還要跨 thread 喚醒」的 `Task` 連帶要求的。**

### Executor、`spawn` 與 `block_on`

executor 只需要一條 queue、目前 executor thread 的 handle，以及還沒完成的 task 數量。`spawn` 把一個 future 包成 task、排進 queue；入口則是 `block_on`：它把你給的 future 也 `spawn` 成一顆 task，然後反覆清 ready queue，直到所有 task 都完成。

```rust,ignore
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

    fn spawn(&mut self, fut: impl Future<Output = ()> + Send + 'static) {
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(fut)),
            queue: self.queue.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
        });
        self.remaining += 1;
        task.schedule(); // 新 task 需要第一次 poll
    }

    fn block_on(&mut self, future: impl Future<Output = ()> + Send + 'static) {
        self.spawn(future); // 傳進來的 future 也只是被排進 queue 的一顆 task

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
    }
}
```

`block_on(future)` 取代了第 6、10 集那個直接的 `run`：它一樣是「吃一個 future、跑完才回傳」，只是背後多了一條 ready queue——把 root 也 spawn 成 task，跑到所有 task 都完成才回來。本集還沒有回傳值（future 是 `Output = ()`）；下一集才讓 `block_on` 回傳 `T`。

## 範例程式碼

這個範例跑兩個 task，各自等不同秒數：一個用 `spawn` 當背景 task，另一個交給 `block_on`。計時器到了，`Delay` 會呼叫當初存下來的 Waker；Waker 會把 task 放回 ready queue，並叫醒 executor。

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

    fn spawn(&mut self, fut: impl Future<Output = ()> + Send + 'static) {
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(fut)),
            queue: self.queue.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
        });
        self.remaining += 1;
        task.schedule();
    }

    fn block_on(&mut self, future: impl Future<Output = ()> + Send + 'static) {
        self.spawn(future);

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
    }
}

fn main() {
    let mut executor = Executor::new();

    // 背景 task：先 spawn 進 queue
    executor.spawn(async {
        delay(1).await;
        println!("A 完成");
    });

    // 主 task：交給 block_on，跑到所有 task 都完成才回來
    executor.block_on(async {
        delay(2).await;
        println!("B 完成");
    });

    println!("executor 結束");
}
```

執行時大致會先等 1 秒印出 `A 完成`，再等 1 秒印出 `B 完成`，最後印出 `executor 結束`。

## 一步步看它怎麼跑

1. `spawn(A)`：建立 A，放進 ready queue，叫醒 executor。
2. `block_on(B)`：先把傳進來的 future B 也 `spawn` 成 task、放進 ready queue，然後開始跑。
3. block_on 先清 ready queue：poll A，A 卡在 `delay(1).await`，計時 thread 記住 A 的 Waker，A 回 `Pending`。
4. 再 poll B，B 卡在 `delay(2).await`，計時 thread 記住 B 的 Waker，B 回 `Pending`。
5. queue 空了，但還有兩個 task 沒完成，executor 用 `thread::park()` 睡著。
6. 約 1 秒後，A 的計時 thread 呼叫 A 的 Waker。
7. A 的 Waker 把 A 放回 ready queue，並用 `unpark()` 叫醒 executor。
8. executor 醒來，從 ready queue 拿 A 出來 poll。A 完成，印出 `A 完成`。
9. 約再 1 秒後，B 用同樣流程被喚醒、被 poll、完成。
10. `remaining` 變成 0，`block_on` 回傳。

這就是本集最重要的模型：**喚醒 task，不是把資料寫給 executor，而是把 task 排回 ready queue。**

## 重點整理

- task = 一個 future ＋ 重新排程所需的隨身資料；從這集起 executor 管的是 task，不是裸 future
- task 的 `wake` = 把 task 放回 ready queue，表示「我準備好再被 poll 一次」
- `unpark` 是叫醒 executor 的門鈴；它不表示是哪個 task，真正該 poll 誰看 ready queue
- `unpark` 早於 `park` 也沒關係（permit 特性，第 10 集）
- `queued` 旗標用 `AtomicBool` + `swap(true, …)` 做 check-and-set，避免重複入列
- `future` 欄位這次要 `+ Send`：因為它被收進 `Task`、`Task` 兼任 `Waker`、`Waker::from(Arc<Task>)` 要求 `Task: Send + Sync + 'static`，連帶要求每個欄位都是 `Send`（外包 `Mutex` 補 `Sync`）
- `block_on(future)` 取代直接的 `run`：把 root 也 spawn 成 task，跑到所有 task 完成；本集還沒回傳值，下一集才回傳 `T`
