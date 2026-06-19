# 用 `.await` 等待 `Delay`

## 本集目標

在 async 裡 `.await` 我們自己寫的 `Delay`，用最簡單的 `println!` 親眼看到 future「從上次暫停的地方接著跑」的**步進感**；並看到 `.await` 不會自動幫你平行化。

## 概念說明

### 自己寫的 future 也能被 `.await`

`.await` 不挑食。只要一個東西實作了 `Future`，你就能 `.await` 它——不管它是 `async fn` 生出來的、是 `async` 區塊、還是我們上一集手刻的 `Delay`。把 `Delay` 放進一個 `async` 區塊，前後再放幾句 `println!`，就能觀察它怎麼跑。

### 在每個 `.await` 前後印一句，看它怎麼一步步走

我們寫一個 async 區塊，裡面等兩個 `delay`，並在每個 `.await` 前後都印一句話：

```rust,ignore
run(async {
    println!("開始");
    delay(1).await;                 // 等 1 秒
    println!("第一個 delay 完成，繼續");
    delay(1).await;                 // 再等 1 秒
    println!("第二個 delay 完成，繼續");
    println!("結束");
});
```

（`run` 就是第 6 集那台「不斷重 poll」的笨 executor。）跑起來，你會看到輸出像這樣**一階一階**地冒出來，而不是一次全部印完：

```text
（0 秒）開始
（約 1 秒後）第一個 delay 完成，繼續
（約 2 秒後）第二個 delay 完成，繼續
結束
```

「開始」立刻出現；接著畫面停住約一秒，才冒出「第一個 delay 完成，繼續」；再停約一秒，才冒出「第二個 delay 完成，繼續」和「結束」。這個一停一走的節奏，就是 async future 被 `.await` 推進的樣子。

### 為什麼會這樣：future 會「記住進度、從暫停處繼續」

這裡有個容易忽略但很關鍵的觀察：上面每一句 `println!` 都**只印了一次**。

但別忘了，`run` 是個「不斷重 poll」的笨 executor——在那「停住的一秒」裡，它其實把這個 future poll 了**成千上萬次**。如果每次 poll 都從頭跑一遍 async 區塊，「開始」就會被印爆。可是它沒有。為什麼？

因為 future 會**記住自己跑到哪了**。回想 `.await` 的行為：當 executor poll 這個 future，它會從**上次暫停的地方**接著跑，而不是從頭來。具體是這樣：

1. 第一次 poll：印出「開始」，跑到 `delay(1).await`。這時去 poll 裡面的 `Delay`——還沒到 1 秒 → `Delay` 回 `Pending` → 整個 future 也跟著**停在這個 `.await`**、回 `Pending`。
2. 接下來那一秒，executor 一直重 poll。每次都從「停在第一個 `.await`」的地方恢復，再去 poll `Delay`——還沒好 → 又回 `Pending`。**這段期間什麼都不印**（因為沒有越過任何 `.await`，「開始」那行早就跑過了不會重跑）。
3. 一秒後某次 poll：`Delay` 終於回 `Ready` → future 越過第一個 `.await`，往下印出「第一個 delay 完成，繼續」，跑到第二個 `delay(1).await` → 又 `Pending`。
4. 同樣再等一秒、再越過第二個 `.await`，印出剩下兩句，整個 future `Ready`，`run` 結束。

所以你看到的「一停一走」，就是 future 在「停在某個 `.await` 回 `Pending`」和「被 poll 時從那裡恢復、往下走到下一個 `.await`」之間切換。**每個 `.await` 就是一個可以停下來、之後再從這裡繼續的點**；future 牢牢記著自己停在哪，所以前面跑過的程式不會重跑。

（順帶一提：`.await` 一個 future，本質上就是「**把 poll 的責任往下傳**」——外層被 poll 時，會去 poll 它正在 `.await` 的那個內層 future；內層還沒好，外層就跟著停在這裡回 `Pending`。）

### `.await` 是循序的，不會自動平行化

最後戳破一個常見誤會：很多人以為 `.await` 是「叫它去背景跑，我繼續做別的」。**不是。** 上面那段，兩個 `delay(1)` 是**一個等完才等下一個**，所以總共花了約 **2 秒**，不是 1 秒。

```rust,ignore
delay(1).await; // 先把這 1 秒等完……
delay(1).await; // ……才輪到等這 1 秒
```

`.await` 的語意就是「等它做完我才往下走」，所以連續兩個 `.await` 必然是循序的，跟你平常寫的同步程式一個樣。那兩個 `delay(1)` 明明可以同時倒數、只花 1 秒，但你沒**明講**要它們並行，async 就不會自作主張。

> 想讓多個 future **同時**進行（兩個 `delay(1)` 只花 1 秒），得額外用工具把它們兜在一起——這正是下一集（第 9 集）手寫 `join` 要做的事。

## 範例程式碼

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

// 第 6 集那台笨 executor
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
    run(async {
        println!("開始");
        delay(1).await;
        println!("第一個 delay 完成，繼續");
        delay(1).await;
        println!("第二個 delay 完成，繼續");
        println!("結束");
    });
    // 兩個 delay(1) 是循序等的，所以大約是 2 秒，不是 1 秒
    println!("總共花了 {:?}", start.elapsed());
}
```

## 重點整理

- 任何實作 `Future` 的東西都能被 `.await`，包括我們手寫的 `Delay`
- 在 `.await` 前後印 `println!`，會看到輸出**一階一階**冒出來（0 秒、約 1 秒、約 2 秒）——這就是 future 被推進的步進感
- 每句 `println!` 只印一次：future 會**記住自己跑到哪**，被 poll 時從**上次暫停的 `.await`** 恢復，不會重跑前面的程式
- 每個 `.await` 是「可以停下來、之後再從這裡繼續」的點：內層還沒好就停在這回 `Pending`，下次被 poll 再從這恢復
- **`.await` 不會自動平行化**：連續兩個 `.await` 會依序等待（兩個 `delay(1)` 共約 2 秒）；想並行要等第 9 集的 `join`
