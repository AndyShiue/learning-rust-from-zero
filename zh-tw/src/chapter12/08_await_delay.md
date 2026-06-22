# 用 `.await` 等待 `Delay`

## 本集目標

用 `.await` 等待上一集的 `Delay`，並在每個 `.await` 前後印訊息，**親眼看到 future 是怎麼一段一段被推進的**：每次被 poll 都從上次暫停的地方繼續，遇到還沒完成的 `.await` 就回 `Pending`，被再次 poll 才越過它往下跑。

## 概念說明

### 在 async 區塊裡 `.await` 它

`Delay` 實作了 `Future`，所以可以對它 `.await`。我們在 async 區塊裡連著等兩個 `delay`，並在每個 `.await` 前後印訊息：

```rust,ignore
run(async {
    println!("開始");
    delay(1).await;
    println!("第一個 delay 完成，繼續");
    delay(1).await;
    println!("第二個 delay 完成，繼續");
});
```

跑起來會這樣**一段一段**出現（每段之間隔約 1 秒）：

```text
開始
（約 1 秒後）
第一個 delay 完成，繼續
（約 1 秒後）
第二個 delay 完成，繼續
```

### 它是怎麼一段一段跑的

關鍵在於 executor 是**反覆 poll 同一個 future**。每次 poll，這個 async 區塊都從「上次暫停的地方」繼續：

1. 第一次 poll：印出 `開始`，跑到 `delay(1).await`。第一個 `Delay` 還沒到期 → 回 `Pending`。整個 async 區塊就**停在這個 `.await`**。
2. executor 看到 `Pending`，等一下再 poll（我們的笨 executor 是猛重 poll）。每次 poll 都會**再從 `delay(1).await` 這裡試一次**——但因為前面的 `println!("開始")` 已經跑過了，不會再印第二次。
3. 約 1 秒後第一個 `Delay` 到期 → 回 `Ready`。async 區塊**越過第一個 `.await`**，印出 `第一個 delay 完成，繼續`，往下跑到第二個 `delay(1).await` → 又 `Pending`、停住。
4. 再約 1 秒，第二個到期 → 越過、印出 `第二個 delay 完成，繼續`，整個區塊跑完 → 回 `Ready`。

這就是 `.await` 的本質：**它是一個可以暫停、之後再從原地恢復的點。** future 不是「一口氣跑完」，而是被 poll 一次往前走一段、卡在 `.await` 回 `Pending`、下次被 poll 再從那裡接著走。前面跑過的部分不會重跑——它「記得」自己跑到哪了（這個「記得進度」的能力，背後就是第 15 集要講的狀態機）。

### `.await` 不會自動把程式變平行

注意輸出：兩個 `delay(1)` 加起來等了**約 2 秒**，不是 1 秒。因為兩個 `.await` 是**依序**的——第一個等完，才輪到第二個。`.await` 只是「在這裡等」，它**不會**自動讓兩件事同時進行。

如果你想讓兩個 `delay(1)` **同時**跑、總共只等約 1 秒，得有別的機制把它們「一起推進」。那就是下一集 `join` 要做的事。

## 範例程式碼

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
    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

fn delay(secs: u64) -> Delay {
    Delay {
        when: Instant::now() + Duration::from_secs(secs),
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
    run(async {
        println!("開始");
        delay(1).await;
        println!("第一個 delay 完成，繼續");
        delay(1).await;
        println!("第二個 delay 完成，繼續");
    });
}
```

## 重點整理

- `.await` 是一個**可暫停、可恢復**的點：future 被 poll 一次往前走一段，卡在還沒完成的 `.await` 回 `Pending`，下次被 poll 再從那裡繼續
- 前面跑過的部分不會重跑——future「記得」自己的進度（背後是第 15 集的狀態機）
- 在每個 `.await` 前後印訊息，就能看到這種「步進」：開始 → 等 → 越過 → 再等 → 再越過
- `.await` **不會自動平行化**：連著兩個 `.await` 會依序等待（兩個 `delay(1)` 共約 2 秒）；要讓它們同時跑，需要下一集的 `join`
