# ready queue 與 executor

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

`unpark` 只是一個門鈴。它不會告訴 executor 是哪個 task 好了。真正的 task 身分放在 ready queue 裡，因為 queue 裡直接存著 `Arc<Task>`。

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

而且 `unpark` 有一個方便的特性：如果 `unpark()` 發生在 `park()` 之前，這次喚醒不會直接消失。它會留下一張 permit，下一次 `park()` 會立刻返回。

但也要記得：`unpark` 不攜帶資料。它只表示「醒來看看」。醒來後到底要 poll 哪些 task，仍然要看 ready queue。

### Task 與它的 Waker

這一集的 `Task` 保存：

- 自己的 future
- 共用的 ready queue
- executor 所在的 thread handle
- 一個 `queued` 小旗標，避免同一個 task 被重複塞進 queue 太多次

```rust,ignore
use std::collections::VecDeque;
use std::future::Future;
use std::pin::Pin;
use std::sync::{Arc, Mutex};
use std::task::Wake;
use std::thread::Thread;

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
```

`wake` 的意思是：「這個 task 應該再被 poll 一次」。所以它做兩件事：

1. 把 task 放進 ready queue。
2. `unpark()` executor thread。

### Executor：queue + executor thread

executor 只需要一條 queue、目前 executor thread 的 handle，以及還沒完成的 task 數量。

```rust,ignore
struct Executor {
    queue: Queue,
    executor_thread: Thread,
    remaining: usize,
}
```

這裡沒有 `mio::Poll`，也沒有 `mio::Waker`。第 13 集會先介紹 `mio`，第 14 集再把 `mio::Poll` 放到 reactor thread 裡，專門等真正的 I/O readiness。

### `spawn`：建立 task，排進 ready queue

```rust,ignore
impl Executor {
    fn spawn(&mut self, fut: impl Future<Output = ()> + Send + 'static) {
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(fut)),
            queue: self.queue.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: Mutex::new(false),
        });

        self.remaining += 1;
        task.schedule(); // 新 task 需要第一次 poll
    }
}
```

剛 spawn 的 task 還沒被 poll 過，所以要先 `schedule()` 一次。這會把它放進 ready queue，並叫醒 executor。

### `run`：先跑 queue，空了才睡

```rust,ignore
use std::task::{Context, Waker};
use std::thread;

impl Executor {
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
```

重點是順序：

1. ready queue 裡有 task，就一直拿出來 poll。
2. queue 空了，但還有 task 沒完成，才 `park()`。
3. 之後某個 task 的 Waker 會把 task 放回 queue，並呼叫 `unpark()`。
4. executor 醒來，再回去清 ready queue。

這就是更接近真實 runtime 的形狀：事件源呼叫 task 的 Waker，Waker 把 task 排回 queue，executor 醒來後只處理 queue 裡的 task。

## 範例程式碼

這個範例 spawn 兩個 task，各自等不同秒數。計時器到了，`Delay` 會呼叫當初存下來的 Waker；Waker 會把 task 放回 ready queue，並叫醒 executor。

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
            queued: Mutex::new(false),
        });

        self.remaining += 1;
        task.schedule();
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

    executor.spawn(async {
        delay(1).await;
        println!("A 完成");
    });

    executor.spawn(async {
        delay(2).await;
        println!("B 完成");
    });

    executor.run();
    println!("executor 結束");
}
```

執行時大致會先等 1 秒印出 `A 完成`，再等 1 秒印出 `B 完成`，最後印出 `executor 結束`。

## 一步步看它怎麼跑

1. `spawn(A)`：建立 A，放進 ready queue，叫醒 executor。
2. `spawn(B)`：建立 B，也放進 ready queue。
3. `run` 先清 ready queue：poll A，A 卡在 `delay(1).await`，計時 thread 記住 A 的 Waker，A 回 `Pending`。
4. executor poll B，B 卡在 `delay(2).await`，計時 thread 記住 B 的 Waker，B 回 `Pending`。
5. queue 空了，但還有兩個 task 沒完成，executor 用 `thread::park()` 睡著。
6. 約 1 秒後，A 的計時 thread 呼叫 A 的 Waker。
7. A 的 Waker 把 A 放回 ready queue，並用 `unpark()` 叫醒 executor。
8. executor 醒來，從 ready queue 拿 A 出來 poll。A 完成，印出 `A 完成`。
9. 約再 1 秒後，B 用同樣流程被喚醒、被 poll、完成。
10. `remaining` 變成 0，`run` 結束。

這就是本集最重要的模型：**喚醒 task，不是把資料寫給 executor，而是把 task 排回 ready queue。**

## 重點整理

- task 的 `wake` = 把 task 放回 ready queue，表示「我準備好再被 poll 一次」
- `unpark` 是叫醒 executor 的門鈴；它不表示是哪個 task
- executor 先清 ready queue，queue 空了但還有 task 沒完成時，才用 `thread::park()` 睡覺
- task 身分放在 ready queue 裡；如果沒有 ready queue，醒來後仍然不知道該 poll 誰
- `Token` 主要留給 reactor/I/O 來源使用；第 13 集會介紹它，第 14 集會用 token 把 socket readiness 對應回 waker
- 這一集的 `spawn` 先只接受 `Future<Output = ()>`；下一集才加上 `JoinHandle<T>`，讓 task 可以回傳值
