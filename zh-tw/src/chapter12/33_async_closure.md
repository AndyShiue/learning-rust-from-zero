# `async` 閉包

## 本集目標

認識 async 閉包 `async || { ... }`,以及讓高階函數能接受它的 `AsyncFn` 系列 trait。

## 概念說明

### 兩種寫法,差別很微妙

第 6 章學過閉包。把閉包和 async 結合,你會看到兩種長得很像、但其實不一樣的寫法:

```rust,ignore
let a = async || { do_work().await };   // async 閉包(閉包本身是 async 的)
let b = || async { do_work().await };   // 普通閉包,回傳一個 async 區塊
```

- 寫法 `b`(`|| async { ... }`)是**普通閉包**,它一被呼叫就**立刻回傳一個 future**(那個 `async` 區塊),自己不是 async 的。這是 async 閉包還沒穩定之前,大家一直用的寫法。
- 寫法 `a`(`async || { ... }`)是真正的 **async 閉包**,呼叫它會得到一個 future,要 `.await`。

兩者最關鍵的差別在**捕獲(capture)與生命週期**。普通閉包 `|| async { ... }` 有個惱人的問題:它回傳的 future 可能需要捕獲閉包借用的東西,但閉包和它回傳的 future 生命週期對不上,常常逼你得把所有東西 `move`、或 `clone` 一份,寫起來綁手綁腳。**async 閉包 `async || { ... }` 就是為了解決這個而生的**——它能更自然地讓產生的 future 借用閉包捕獲的變數,不用為了過編譯而到處 clone。

(async 閉包是比較新的語言功能。如果你看的舊教學或舊程式碼裡只有 `|| async { ... }` 的寫法,那多半是因為當時 `async || { ... }` 還不能用。)

### 怎麼把 async 閉包當參數收

第 6 章學過,要接受一個普通閉包當參數,用 `Fn` / `FnMut` / `FnOnce` 這組 trait。async 閉包有對應的一組:**`AsyncFn` / `AsyncFnMut` / `AsyncFnOnce`**。它們讓你寫出「我接受一個**可以被 await 的閉包**」的高階函數:

```rust,ignore
// 接受一個 async 閉包,呼叫它、await 結果
async fn call_twice<F>(f: F)
where
    F: AsyncFn(),
{
    f().await; // 呼叫 → 得到 future → await
    f().await; // 再來一次
}

#[tokio::main]
async fn main() {
    call_twice(async || {
        println!("做一次 async 工作");
    })
    .await;
}
```

`AsyncFn()` 的意思就是「一個呼叫後會給你一個 future 的閉包」。和第 6 章一樣,三者有寬鬆程度之分:`AsyncFnOnce`(只能呼叫一次)最寬鬆、`AsyncFn`(可重複呼叫、唯讀捕獲)最嚴格,設計 API 時一樣盡量收最寬鬆的那個。

### 在這之前,大家是怎麼做的

在 `AsyncFn` 出現之前,要寫「接受一個會回傳 future 的閉包」的高階函數,得用一個又長又繞的寫法——手動寫出「這個閉包回傳某個 `Future`」:

```rust,ignore
use std::future::Future;

// 舊寫法:F 是普通閉包,回傳值 Fut 必須是一個 Future
async fn call_twice_old<F, Fut>(f: F)
where
    F: Fn() -> Fut,
    Fut: Future<Output = ()>,
{
    f().await;
    f().await;
}
```

你得多引入一個型別參數 `Fut` 來代表「回傳的那個 future」,還要替它加上 `Future` bound。能用,但囉嗦,而且前面說的捕獲／生命週期問題也常在這種寫法下浮現。`AsyncFn` 把這一坨收乾淨成 `F: AsyncFn()`,意圖清楚多了。如果你在現有的 crate 裡看到 `F: Fn() -> Fut, Fut: Future` 這種簽名,認得出它就是「想接受一個 async 閉包」即可。

## 範例程式碼

一個小小的「重試」高階函數:接受一個 async 閉包,失敗就再試,最多試 `n` 次。

```rust,ignore
async fn retry<F>(times: u32, operation: F) -> Result<(), String>
where
    F: AsyncFn() -> Result<(), String>,
{
    for attempt in 1..=times {
        match operation().await {
            Ok(()) => return Ok(()),
            Err(e) => println!("第 {} 次失敗：{}", attempt, e),
        }
    }
    Err(format!("試了 {} 次都失敗", times))
}

#[tokio::main]
async fn main() {
    let mut count = 0;
    let result = retry(3, async || {
        count += 1;
        if count < 2 { Err(String::from("還沒成功")) } else { Ok(()) }
    })
    .await;

    println!("{:?}", result);
}
```

`retry` 不在乎你傳進來的工作具體是什麼,只要它是個「呼叫後可 await、回傳 `Result`」的 async 閉包就行——這正是 `AsyncFn` 讓高階函數能漂亮表達的東西。

## 重點整理

- `async || { ... }` 是 **async 閉包**;`|| async { ... }` 是「回傳 async 區塊的普通閉包」,兩者在**捕獲與生命週期**上不同
- async 閉包能更自然地讓產生的 future 借用捕獲的變數,省去舊寫法常被逼著 `move`／`clone` 的麻煩
- 接受 async 閉包當參數,用 **`AsyncFn` / `AsyncFnMut` / `AsyncFnOnce`**(對應第 6 章的 `Fn` 三兄弟)
- 舊寫法是 `F: Fn() -> Fut, Fut: Future<...>`——又長又繞;`AsyncFn` 把它收乾淨,看到舊簽名認得出意圖即可
- 至此,async 這一章從「怎麼用」到「怎麼運作」再到「實務工具」就走完了——恭喜你撐完全書最硬的一章！
