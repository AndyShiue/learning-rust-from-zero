# 用 `Thread` 與 `Waker` 喚醒 executor

## 本集目標

讓 executor 學會睡覺：沒事做時 `park` 起來，等事件完成時用 `Waker` 把它叫醒。同時搞懂 `poll` 的兩條重要契約。

## 正文

### 不要再空轉了

到目前為止，我們的 executor 有個很糟的毛病：拿到 `Pending` 就馬上再 `poll`，整條執行緒被一個其實還在等的工作燒滿。真實的 runtime 不會這樣，它會在沒事做時去**睡覺**，等真的有進展了再被叫醒。

「叫醒」的工具，就是前幾集一直被我們冷落的 `Waker`。`cx.waker()` 拿得到一個 `Waker`，`Future` 在回 `Pending` 之前，應該把這個 `Waker` 交給「負責通知它好了的人」。等事件完成，那個人就呼叫 `waker.wake()`，把睡著的 executor 叫醒。

這一集我們就讓計時這件事改由**另一條 `Thread`** 負責：`Delay` 第一次被 `poll` 時，`spawn` 一條 `Thread` 去 `sleep`，睡飽了就 `wake()` executor。

### 自己做一個 `Waker`

先看 `Waker` 怎麼生出來。標準庫提供一個 `Wake` `trait`，你實作它的 `wake` 方法，描述「被喚醒時該做什麼」，再用 `Waker::from` 把它轉成 `Waker`。

我們希望「喚醒」的動作是把 executor 那條 `Thread` 叫醒，所以做一個記著 executor `Thread` 的小型別：

```rust,noplayground
use std::sync::Arc;
use std::task::Wake;
use std::thread::{self, Thread};

struct ThreadWaker {
    thread: Thread, // executor 那條 Thread
}

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.thread.unpark(); // 被喚醒 = 把那條 Thread unpark
    }
}
#
# fn main() {}
```

注意 `wake` 的 `self` 是 `Arc<Self>`（這也是上一集說的、能放在 `self` 位置的特別型別之一）。`Waker::from(Arc::new(...))` 就能把它變成一個 `Waker`。

### 會睡覺的 executor

有了 `ThreadWaker`，executor 就能改成「`Pending` 就 `park` 睡覺」：

```rust,noplayground
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
#
# struct ThreadWaker {
#     thread: Thread,
# }
#
# impl Wake for ThreadWaker {
#     fn wake(self: Arc<Self>) {
#         self.thread.unpark();
#     }
# }

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);

    // 做一個「會 unpark 目前這條 executor Thread」的 Waker
    let waker = Waker::from(Arc::new(ThreadWaker {
        thread: thread::current(),
    }));
    let mut cx = Context::from_waker(&waker);

    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(), // 沒事做，睡到被 unpark
        }
    }
}
```

### 會自己叫醒別人的 `Delay`

最後改寫 `Delay`：回 `Pending` 之前，`spawn` 一條 `Thread` 去睡，睡醒就 `wake()`：

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
use std::time::{Duration, Instant};

struct ThreadWaker {
    thread: Thread,
}

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.thread.unpark();
    }
}

struct Delay {
    when: Instant,
    started: bool, // 計時 Thread 開了沒
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
                let waker = cx.waker().clone(); // 拿一份 Waker 給計時 Thread
                let when = this.when;
                thread::spawn(move || {
                    let now = Instant::now();
                    if now < when {
                        thread::sleep(when - now);
                    }
                    waker.wake(); // 時間到，叫醒 executor
                });
            }
            Poll::Pending
        }
    }
}

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let waker = Waker::from(Arc::new(ThreadWaker {
        thread: thread::current(),
    }));
    let mut cx = Context::from_waker(&waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(),
        }
    }
}

fn main() {
    block_on(async {
        println!("開始");
        Delay::new(Duration::from_secs(1)).await;
        println!("一秒後");
        Delay::new(Duration::from_secs(1)).await;
        println!("兩秒後");
    });
}
```

這次 executor 不再空轉燒 CPU 了——它 `poll` 一次拿到 `Pending` 就 `park` 睡著，整整睡一秒，被計時 `Thread` 的 `wake()` 叫醒後才再 `poll`。

### `wake` 比 `park` 早發生會睡死嗎？

這裡有個值得擔心的時序問題。executor 的 `poll` 回 `Pending` 之後，到它真的執行 `thread::park()` 之間，有一個小空檔。萬一計時 `Thread` 剛好在這個空檔裡 `wake` → `unpark`，那 executor 不就「先被叫醒、然後才去睡」，結果這次 `unpark` 撲了個空、executor 一睡不醒嗎？

不會。`unpark` 的設計是：如果這條 `Thread` 還沒在 `park`，它會**留一張 permit（許可）**。下次這條 `Thread` 呼叫 `park()` 時，看到有 permit 就**立刻返回**，根本不睡。所以不管 `wake()`（也就是 `unpark`）落在 `park()` 之前還是之後，都不會漏接。正是因為 `park` / `unpark` 自帶這個保證，我們才敢直接拿它們來當「睡覺 / 叫醒」的工具。

### `poll` 的兩條契約

趁這套 `poll` / `wake` 邏輯剛兜好，把標準庫對 `Future::poll` 的兩條重要契約講清楚：

**契約一：只有最近一次 poll 給的 `Waker` 算數。** 每次 `poll`，`cx.waker()` 拿到的 `Waker` **可能不一樣**（例如 `Task` 被搬到別條 thread 上跑）。所以一個正確的 `Future`，每次 `poll` 都該把最新的 `Waker` 重新存一份，喚醒時用最新的那個。

我們的 `Delay` 卻偷懶了——靠 `started` 旗標，它只在第一次 `poll` 抓一次 `Waker` 就不管了。這之所以沒出事，純粹是因為我們的 executor 從頭到尾用**同一個** `Waker`，所以舊的剛好還能用。如果換一個每次給不同 `Waker` 的 executor，這個 `Delay` 就會叫醒失敗。實務上必須老實地每次重存，本章後面動真格時都會這麼做。

**契約二：`Ready` 之後不可以再 `poll`。** 一個 `Future` 一旦回了 `Ready`，就**不准**再被 poll，否則行為沒有保證（可能 panic、可能卡死）。所以 executor 必須記得：哪個 `Future` 做完了，就要把它移除、別再碰。我們現在的 `block_on` 拿到 `Ready` 就直接 `return`，自然不會犯規；但等到要同時管很多個 `Future` 時，這件事就得認真處理了（下一集就會做）。

### 一個 `Future` 一條 `Thread`？這不行

最後潑一盆冷水：我們現在是「每個在等的 `Delay` 都 `spawn` 一條 `Thread`」。這顯然不是好辦法——還記得第 2 集說的嗎？`Thread` 很吃記憶體。如果有一萬個連線在等，就要一萬條 `Thread`，這**正是 `async` 一開始想避免的問題**，結果我們又繞回去了。

接下來幾集要把這件事徹底解決。我們會先把每個被 `wake` 的 `Future` 包成一個叫 **`Task`** 的東西，讓它能排回 executor 的一條「ready queue」（待辦佇列）；之後就可以引入 **reactor**，用少少一條或幾條 `Thread` 盯住大量的 I/O，徹底擺脫「一個工作一條 `Thread`」。

## 重點整理

- `Future` 回 `Pending` 前該把 `cx.waker()` 交給「負責通知它的人」，事件完成時呼叫 `waker.wake()` 叫醒 executor
- 自製 `Waker`：實作 `Wake` `trait` 的 `wake` 方法，再用 `Waker::from(Arc::new(...))` 轉成 `Waker`
- executor 用 `thread::park()` 睡覺，`Waker` 用 `unpark()` 叫醒；`unpark` 會留 permit，所以 `wake` 落在 `park` 前或後都不漏接
- **契約一**：每次 `poll` 的 `Waker` 可能不同，正確的 `Future` 每次都要重存最新的 `Waker`（`Delay` 偷懶只存一次，是過度簡化）
- **契約二**：`Ready` 之後不可再 `poll`，executor 要把完成的 `Future` 移除
- 「一個 `Future` 一條 `Thread`」太耗資源，下一集起改用 `Task` + ready queue，再加上 reactor 來解決
