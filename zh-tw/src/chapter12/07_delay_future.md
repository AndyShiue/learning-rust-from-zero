# 手寫一個 `Delay` `Future`

## 本集目標

親手實作一個 `Delay`——用它**模擬一個需要花很久才完成的事件**，第一次看到 `Poll::Pending` 真正派上用場。

## 概念說明

### 我們要做什麼

上一集的 `async` 區塊一 poll 就 `Ready` 了，所以還沒看到 `Pending` 的威力。要看懂 async 真正在處理的事，我們需要研究一個**現在還沒好、要過一陣子才會好**的 future。

真實世界裡這種 future 多得是：等網路回應、等硬碟把檔案讀完、等資料庫查詢——它們的共通點就是「現在還沒好，要花一段時間才完成」。但這些真東西要牽扯到作業系統、網路卡，設定起來很複雜，不適合拿來第一次認識 `Pending`。

所以我們用最簡單的替身：一個**計時器**。我們手寫一個 `Delay`——建立時給它一個「到期時間」，在到期之前 poll 它都回 `Pending`，到期之後才回 `Ready`。它什麼正事都沒做，就只是「等時間到」，但這恰好**模擬了一個需要花很久才完成的事件**：到期之前＝「事情還沒好」，到期＝「事情完成了」。

接下來第 8、9、10 集，我們都會拿這個 `Delay` 當那個「慢慢才會好的事件」，用它來研究 `.await`、並行、以及 Waker 怎麼運作。它同時也是所有「計時器」「逾時」類 future 的雛形。

### 用一個 struct 存狀態

一個自訂的 future，就是一個自己實作 `Future` trait 的 struct。它的欄位用來存「推進到一半需要記住的東西」。`Delay` 只需要記住一件事：什麼時候到期。

```rust,ignore
use std::time::Instant;

struct Delay {
    when: Instant, // 到期的那個時間點
}
```

`Instant` 是標準庫裡代表「某一個時間點」的型別，`Instant::now()` 是現在。

### 實作 poll

接著幫 `Delay` 實作 `Future`。邏輯很直白：被 poll 的時候，看看現在到期了沒。

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};
use std::time::Instant;
#
# struct Delay { when: Instant }

impl Future for Delay {
    type Output = (); // 時間到了就好了，沒有要回傳什麼有意義的值

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        if Instant::now() >= self.when {
            // 到期了，完成！
            Poll::Ready(())
        } else {
            // 還沒到期，回報「還沒好」
            Poll::Pending
        }
    }
}
```

`Output` 設成 `()`（unit type，第 2 章學過），因為「等時間」這件事本身不產出什麼值，重點是「等到了」。

`poll` 裡就是一個 `if`：現在的時間有沒有追過到期時間？追過了就 `Ready(())`，還沒就 `Pending`。

### 先忽略 Waker，但它其實有個洞

眼尖的你可能發現：我們完全沒用到 `cx`（裡面那個 Waker）。這代表：當 `Delay` 回 `Pending`，它**沒有任何方式通知 executor「我之後會好」**。

配上上一集那個笨 executor（`Pending` 就猛 loop 再 poll），勉強還能動——因為笨 executor 反正一直重 poll，總有一次會 poll 到時間已過。但這正是它燒 CPU 的原因：在到期之前，它就只是不停地問「好了沒？好了沒？」。

正確的做法應該是：`Delay` 在回 `Pending` 之前，想辦法安排「時間到的時候，用 Waker 把 executor 叫醒」，這樣 executor 就能安心睡到那個時候。怎麼做到這件事，是第 10 集的主題。這一集我們先接受這個洞，重點是體會 `Pending`／`Ready` 的切換。

## 範例程式碼

把 `Delay` 接到上一集的笨 executor 上跑跑看：

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};
use std::time::{Duration, Instant};

struct Delay {
    when: Instant,
}

impl Future for Delay {
    type Output = ();
    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Self::Output> {
        if Instant::now() >= self.when {
            println!("時間到，完成！");
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

// 第 6 集那台笨 executor
fn run<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let waker = Waker::noop();
    let mut cx = Context::from_waker(waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => {}
        }
    }
}

fn main() {
    let delay = Delay {
        when: Instant::now() + Duration::from_secs(2),
    };
    println!("開始等 2 秒...");
    run(delay);
}
```

跑起來會等大約 2 秒後印出「時間到，完成！」。（過程中 CPU 會被那個猛 poll 的迴圈燒著——這就是下一步要修的問題。）

## 重點整理

- 自訂 future = 一個自己 `impl Future` 的 struct；欄位用來存「推進到一半要記住的狀態」
- `Delay` 只記一個到期時間 `when`，`poll` 裡用 `if` 判斷到期沒：到了回 `Poll::Ready`，沒到回 `Poll::Pending`
- `Output` 可以是 `()`，代表「做完了但沒有有意義的回傳值」
- 我們的 `Delay` 還沒用 Waker，所以無法主動通知 executor「我之後會好」——只能靠笨 executor 一直重 poll
- 補上 Waker、讓 executor 能睡著等通知，是第 10 集的主題
