# 手寫 `join`：讓多個 Future 並行

## 本集目標

親手寫一個吃**一整個 Vec** 的 `Join`，loop 著推進直到**所有** future 都完成；並驗證連「需要被 poll 很多次才會好」的 future 也照樣 join 得動。

## 概念說明

### 並行的秘密：一次 poll，推進每一個

上一集說，一個接一個 `.await` 是循序的。那要怎麼讓好幾個 `Delay` 同時倒數？

關鍵的洞察是：**並行其實只是「每次被 poll 的時候，把手上每一個還沒完成的 future 都 poll 一下」。** 想像你同時煮好幾鍋湯，你不會站著盯第一鍋滾、滾完才去開第二鍋的火——你會每個爐子都先開火，然後輪流去看哪鍋好了。「輪流看一下」就是 poll，「每個爐子都先開火」就是並行。

我們來寫一個 `JoinAll`：它包住**一個 Vec 的 future**，每次它自己被 poll，就把裡面每一個還沒完成的 future 各 poll 一次；全部都好了，它才算好。

### 實作一個吃 Vec 的 `JoinAll`

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

// 吃「一整個 Vec」的 future：loop 著推進，直到裡面每一個都完成
struct JoinAll {
    // 每個位置放一個 future，做完就換成 None
    // （Pin<Box<dyn Future>> 第 20 集會講；用 Option 是為了「做完之後把它拿掉」）
    futures: Vec<Option<Pin<Box<dyn Future<Output = ()>>>>>,
}

// 方便的建構函式：把一個 Vec<future> 包成 JoinAll
fn join_all(futures: Vec<Pin<Box<dyn Future<Output = ()>>>>) -> JoinAll {
    JoinAll {
        futures: futures.into_iter().map(Some).collect(),
    }
}

impl Future for JoinAll {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let this = self.get_mut(); // get_mut 先當黑盒子（第 18 集）

        let mut all_done = true;
        // loop 過每一個 future，把還沒完成的各 poll 一下
        for slot in &mut this.futures {
            if let Some(fut) = slot {
                if fut.as_mut().poll(cx).is_ready() {
                    *slot = None; // 這個完成了，拿掉
                } else {
                    all_done = false; // 還有人沒完成
                }
            }
        }

        // 全部都拿掉了（都完成）才算好；否則回 Pending，等下次再被 poll
        if all_done {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}
```

比起只能塞兩個 future 的寫法，這個 `JoinAll` 吃一個 Vec，數量隨你放。重點全在 `poll` 裡那個 `for` 迴圈：它**不會**卡在第一個 future 上等它做完，而是把每一個還沒完成的都 poll 一下、各往前推一點點，做完的換成 `None`；只有當全部都變成 `None`，才回 `Ready`。

### 為什麼這樣就會並行？

把這個 `JoinAll` 交給第 6 集那台「不斷重 poll」的笨 executor：每一輪 loop，executor poll 一次 `JoinAll`，`JoinAll` 就讓 Vec 裡每個 future 各前進一次。於是在同一條執行緒上，所有 future 的進度交錯著往前——這就是並行（concurrency）。

注意這裡**從頭到尾只有一條執行緒**，沒有開新 thread。並行不一定要靠多執行緒，「輪流推進很多件事」本身就是一種並行。這正是 async 的核心精神。

### 連「要 poll 很多次才會好」的 future 也 join 得動

到目前為止，我們塞進去的都是單純的 `Delay`。但 `JoinAll` 真正厲害的地方是：它**不在乎裡面的 future 有多難搞**。我們來塞一個更複雜的進去——一個裡面有**好幾個 `.await`** 的 async 區塊：

```rust,ignore
async {
    println!("多階段任務：第一階段開始");
    delay(1).await; // 第一個 .await
    println!("第一階段完成，進入第二階段");
    delay(1).await; // 第二個 .await
    println!("第二階段完成");
}
```

這個 future 得分**好幾次** poll 才會完成：第一次 poll 它會卡在第一個 `delay(1).await`（回 `Pending`），等第一秒過了、再被 poll 才往下走、卡在第二個 `.await`，再等一秒、再被 poll，才真的做完。

> **這裡先講明一件你還沒學到的事**：一個 future 裡**每多一個 `.await`，大致就多一個「可能要在這裡停下來、之後再被 poll 一次才能繼續」的點**。所以上面這個有兩個 `.await` 的 future，至少要被 poll 個好幾次才會走完。至於「為什麼 `.await` 會變成這種要再被 poll 一次的停頓點」，牽涉到 `async fn` 被編譯器改寫成**狀態機**的內幕，第 15 集會完整拆解。現在你只要先接受這個事實就好。

而關鍵是：**我們的 `JoinAll` 完全不需要為這種「要 poll 很多次」的 future 做任何特別處理。** 它的 `poll` 裡就只是「對每個還沒完成的 future 呼叫一次 poll」而已。那個多階段 future 還沒好就回 `Pending`、`JoinAll` 下一輪再 poll 它一次——一次推進一階段，自然就走完了。不管裡面的 future 要 poll 一次還是一百次，`JoinAll` 的邏輯都一模一樣。這正是 `poll`（「推進一次」）這個設計漂亮的地方：複雜的進度管理，都被關在每個 future 自己的 `poll` 裡了。

## 範例程式碼

把一個單純的 `delay(2)`、和那個有兩個 `.await` 的多階段任務一起丟進 `JoinAll`，讓它們並行：

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};
use std::time::{Duration, Instant};

struct Delay { when: Instant }
impl Future for Delay {
    type Output = ();
    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when { Poll::Ready(()) } else { Poll::Pending }
    }
}
fn delay(secs: u64) -> Delay { Delay { when: Instant::now() + Duration::from_secs(secs) } }

struct JoinAll {
    futures: Vec<Option<Pin<Box<dyn Future<Output = ()>>>>>,
}
fn join_all(futures: Vec<Pin<Box<dyn Future<Output = ()>>>>) -> JoinAll {
    JoinAll { futures: futures.into_iter().map(Some).collect() }
}
impl Future for JoinAll {
    type Output = ();
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        let mut all_done = true;
        for slot in &mut this.futures {
            if let Some(fut) = slot {
                if fut.as_mut().poll(cx).is_ready() {
                    *slot = None;
                } else {
                    all_done = false;
                }
            }
        }
        if all_done { Poll::Ready(()) } else { Poll::Pending }
    }
}

fn run<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let waker = Waker::noop();
    let mut cx = Context::from_waker(waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(v) => return v,
            Poll::Pending => {}
        }
    }
}

fn main() {
    let start = Instant::now();

    let futures: Vec<Pin<Box<dyn Future<Output = ()>>>> = vec![
        // 單純等 2 秒
        Box::pin(delay(2)),
        // 有兩個 .await 的多階段任務——需要被 poll 很多次才會完成
        Box::pin(async {
            println!("多階段任務：第一階段開始");
            delay(1).await;
            println!("第一階段完成，進入第二階段");
            delay(1).await;
            println!("第二階段完成");
        }),
    ];

    run(join_all(futures));

    // delay(2) 要 2 秒；多階段任務 1+1 也是 2 秒；並行之下總共大約只花 2 秒
    println!("全部完成，總共花了 {:?}", start.elapsed());
}
```

跑起來，多階段任務會一階一階印出進度，而它和那個 `delay(2)` 是**同時**在倒數的——一條執行緒、兩件事並行，總共約 2 秒。

## 重點整理

- 並行的本質：每次被 poll，就把手上每一個還沒完成的 future **都 poll 一下**，而不是卡在第一個
- `JoinAll` 吃一個 Vec 的 future，`poll` 裡用 `for` 迴圈讓每個各前進一次，做完的換成 `None`，全部完成才回 `Ready`
- 交給會重 poll 的 executor，多個 future 的進度就交錯前進，在**同一條執行緒**上達成並行（concurrency 不等於多執行緒）
- 一個 future 裡**每多一個 `.await`，大致就多一次「之後要再被 poll」的停頓**（為什麼？第 15 集的狀態機會解釋）
- 但 `JoinAll` 不必為「要 poll 很多次」的 future 做任何特別處理——它只管「對每個 future 呼叫一次 poll」，複雜度都關在各 future 自己的 `poll` 裡
- 實務上不用自己寫，用 `join!`（第 22 集）；但原理就是這個
