# 手寫一個 `Delay` `Future`

## 本集目標

親手寫出第一個會真的回 `Pending` 的 `Future`——一個計時器 `Delay`，並用上一集的 executor 跑它。

## 正文

### 為什麼要做一個 `Delay`

上一集說好了，這集要寫一個「會真的需要等」的 `Future`。但真實世界裡需要等的事件——等網路封包、等硬碟、等資料庫——背後都牽扯到作業系統的一堆概念，第一次認識 `Pending` 就碰這些太複雜了。

所以我們先用最簡單的東西撐著：一個**計時器**。規則很單純：

- 還沒到期 → 回 `Pending`（事情還沒好）。
- 到期了 → 回 `Ready`（完成）。

這個 `Delay` 就是我們接下來好幾集的主角，每當需要一個「要花時間才會好的事件」，我們就拿它來模擬，用它來研究 `.await`、join、還有 `Waker`。

### 寫出 `Delay`

`Delay` 記住一個「到期時間點」`when`，每次被 `poll` 時就比對現在的時間有沒有超過它：

```rust,noplayground
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};
use std::time::{Duration, Instant};

struct Delay {
    when: Instant, // 預計完成的時間點
}

impl Delay {
    fn new(duration: Duration) -> Delay {
        Delay {
            when: Instant::now() + duration, // 從現在算起，過 duration 之後到期
        }
    }
}

impl Future for Delay {
    type Output = ();

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            println!("Delay 完成了");
            Poll::Ready(()) // 到期了
        } else {
            Poll::Pending // 還沒到期，待會再來問
        }
    }
}
#
# fn main() {}
```

`poll` 的邏輯就是這麼直接：時間到了回 `Ready(())`，沒到回 `Pending`。`Output` 是 `()`，因為這個計時器完成時不需要給出什麼值，純粹是「時間到了」這個事件本身。

### 用我們的 executor 跑跑看

把上一集那個最笨的 `block_on` 搬過來，就能執行自己寫的 `Delay` 了：

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};
use std::time::{Duration, Instant};

struct Delay {
    when: Instant,
}

impl Delay {
    fn new(duration: Duration) -> Delay {
        Delay {
            when: Instant::now() + duration
        }
    }
}

impl Future for Delay {
    type Output = ();

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            println!("Delay 完成了");
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let mut cx = Context::from_waker(Waker::noop());
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => {}
        }
    }
}

fn main() {
    println!("開始");
    block_on(Delay::new(Duration::from_secs(1)));
    println!("一秒過去了");
}
```

跑起來，你會看到「開始」之後停頓一秒，才印出「一秒過去了」。我們第一個會真正回傳 `Pending` 的 `Future` 成功了！在這一秒之內，`block_on` 的迴圈瘋狂地一直 `poll` 並一直拿到 `Pending`，直到時間終於到了才拿到 `Ready`。

> **注意**：網頁版的程式碼沙盒不一定能清楚顯示出時間延遲。這一章後面還有不少類似的計時、等待範例；如果你想實際感受到「停一秒」「同時等不同工作」這類時間變化，建議把程式複製到自己的電腦上執行。

### 老實說：這個 `Delay` 被過度簡化了

這個版本能跑，但它其實**偷懶**了——`poll` 裡的 `cx` 參數被寫成 `_cx`，完全沒用到。

`cx` 裡裝著一個叫 `Waker` 的東西，正常的 `Future` 在回 `Pending` 之前，應該用它通知 executor「等我好了再來叫我」。但我們的 `Delay` 完全沒這麼做。那為什麼它還能跑？因為我們搭配的 executor 也一樣笨——它根本不睡覺，回 `Pending` 就馬上再 `poll`，所以就算沒人通知它也無所謂。

換句話說，這個 `Delay` 是**綁定**在這個笨 executor 上才能正常運作的。如果把它丟到一個「會睡覺、要被 `Waker` 叫醒才繼續」的真實 executor 上，它回了 `Pending` 卻從不通知對方，executor 就會一睡不醒——這個 `Delay` 等於永遠不會完成。

之後會修掉這個偷懶的部分。但在那之前，我們會先用這個 `Delay` 把 `.await` 和並行的一些觀念建立起來。下一集就來看在 `async` 裡 `.await` 這個 `Delay` 會發生什麼事。

## 重點整理

- 真實 I/O 太複雜，所以先用最簡單的計時器來第一次認識 `Pending`
- `Delay` 用一個計時器模擬「要花時間才會好的事件」：沒到期回 `Pending`，到期回 `Ready`，之後幾集都拿它當替代品
- 自訂 `Future` 一旦 `impl Future`、實作 `poll`，搭配上一集的 `block_on` 就能跑
- 這個 `Delay` 被過度簡化了：`poll` 沒用到 `cx` 裡的 `Waker`，只因為搭配的 executor 也不睡覺才剛好能跑；換到會睡覺的 executor 就會出問題，我們後面會修
