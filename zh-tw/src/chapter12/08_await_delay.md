# 用 `.await` 等待 `Delay`

## 本集目標

用 `.await` 等待上一集的 `Delay`，並透過 `println!` 親眼看到 `Future` 是怎麼「暫停又恢復」的。

## 正文

### 在 `.await` 前後印訊息

我們已經有了 `Delay`，也有了 `block_on`。現在把 `Delay` 放進一個 `async` block 裡，用 `.await` 等它，而且在每個 `.await` 的前後都加上 `println!`，看看執行的順序：

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
        Delay { when: Instant::now() + duration }
    }
}

impl Future for Delay {
    type Output = ();

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
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
    block_on(async {
        println!("開始");

        println!("等第一個 delay……");
        Delay::new(Duration::from_secs(1)).await;
        println!("第一個 delay 完成，繼續往下");

        println!("等第二個 delay……");
        Delay::new(Duration::from_secs(1)).await;
        println!("第二個 delay 完成，繼續往下");
    });
}
```

跑起來，輸出會像這樣一步一步出現：

```text
開始
等第一個 delay……
（停頓一秒）
第一個 delay 完成，繼續往下
等第二個 delay……
（停頓一秒）
第二個 delay 完成，繼續往下
```

### 它是怎麼「暫停又恢復」的

這個輸出順序揭露了 `Future` 的運作方式。記得整個 `async` block 本身就是一個 `Future`，`block_on` 不斷在 `poll` 它：

1. 第一次 `poll`：從頭開始跑，印出「開始」「等第一個 delay……」，然後遇到第一個 `.await`。這時 `Delay` 還沒到期，回 `Pending`——於是整個 `async` block 也跟著回 `Pending`，**從這裡暫停**。
2. 接下來 executor 一次又一次 `poll`，但 `Delay` 還沒到期，每次都卡在第一個 `.await` 那裡回 `Pending`，沒能往下走。
3. 一秒後 `Delay` 到期回傳 `Ready(())`，這次 `poll` 越過第一個 `.await`，印出「第一個 delay 完成」「等第二個 delay……」，遇到第二個 `.await` 又回 `Pending`，**在新的地方暫停**。
4. 再一秒，第二個 `Delay` 到期回傳 `Ready(())`，越過第二個 `.await`，印完最後一句，整個 `async` block 回 `Ready`，`block_on` 結束。

關鍵在於：**每次被 `poll`，`Future` 都從上次暫停的地方接著跑**，一路跑到下一個還沒好的 `.await` 才又停下。這種「能記住進度、暫停後又從原地恢復」的能力，正是上一集說的「狀態機」在背後撐著——但這集先看現象就好。

### `.await` 不會自動幫你並行

注意一個重點：上面兩個 `Delay` 是**一個接一個**等的，總共花了兩秒。第二個 `Delay` 是等第一個完成後才開始計時的。

這常讓新手誤會。`.await` 的意思是「等這件事好」，它**不會**自動把你的程式變成並行。連續寫兩個 `.await`，就是老老實實地依序等待，不會聰明地「兩個一起等」。

那如果我就是想讓兩個 `Delay` 同時計時、總共只花一秒，該怎麼辦？這就是下一集的主題——我們要自己動手寫一個能把多個 `Future` 並行推進的工具。

## 重點整理

- 在 `async` 裡用 `.await` 等待 `Delay`，搭配 `println!` 可以看到執行的步進過程
- 每次被 `poll`，`Future` 都從上次暫停處接著跑，直到遇到下一個沒完成的 `.await` 才回 `Pending`
- `Future` 能記住進度、暫停後從原地恢復，這是背後狀態機的功勞
- `.await` **不會**自動並行：連續兩個 `.await` 會依序等待，想並行得用別的工具（下一集）
