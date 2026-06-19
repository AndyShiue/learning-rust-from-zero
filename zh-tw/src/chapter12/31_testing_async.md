# 測試 async 程式

## 本集目標

學會幫 async 程式寫測試:`#[tokio::test]`,以及用 `tokio::time` 控制時間,讓和「等待」有關的測試又快又穩。

## 概念說明

### `#[test]` 不能直接測 async fn

第 7 章學過用 `#[test]` 和 `cargo test` 寫測試。但測試函數如果是 `async fn`,會有問題——`#[test]` 不知道怎麼跑一個 future(它需要一個 runtime 來 `block_on`):

```rust,ignore
#[test]
async fn it_works() { // 行不通:普通的 #[test] 不會幫你跑 future
    let result = compute().await;
    assert_eq!(result, 42);
}
# async fn compute() -> i32 { 42 }
```

### `#[tokio::test]`:自動套上 runtime

tokio 提供 `#[tokio::test]`,專門解決這件事。它和 `#[test]` 用起來一樣,但會**自動幫你的測試函數建一個 runtime 並 `block_on`**,所以函數體裡可以直接 `.await`:

```rust,ignore
async fn compute() -> i32 {
    42
}

#[tokio::test]
async fn it_works() {
    let result = compute().await; // 可以直接 await
    assert_eq!(result, 42);
}
```

其實 `#[tokio::test]` 就是「`#[test]` + 自動 `block_on`」的組合,本質和第 21 集 `#[tokio::main]` 對 `main` 做的事一樣,只是這次施加在測試函數上。`cargo test` 跑法、`assert_eq!` 等斷言巨集都和第 7 章一模一樣。

### 和時間有關的測試:別真的去等

假設你要測一段「30 秒後逾時」的邏輯。如果測試裡真的 `sleep(30 秒)`,那這個測試每跑一次就要等 30 秒——慢到沒人想跑,而且依賴真實時鐘也容易不穩定。

tokio 提供了一個很漂亮的解法:**把時間「暫停」,然後用程式手動把它快轉。** 開啟方式是 `tokio::time::pause()`,之後用 `tokio::time::advance(時間)` 手動推進那個「假時鐘」。

```rust,ignore
use tokio::time::{advance, pause, Duration, Instant};

#[tokio::test]
async fn time_can_be_controlled() {
    pause(); // 暫停時鐘:從現在起,時間不會自己走

    let start = Instant::now();

    // 手動把時鐘往前快轉 30 秒(瞬間完成,不是真的等 30 秒)
    advance(Duration::from_secs(30)).await;

    // 對 tokio 來說,已經「過了」30 秒
    assert!(start.elapsed() >= Duration::from_secs(30));
}
```

`pause()` 之後,所有 `tokio::time::sleep`、逾時計時器都跟著那個假時鐘走。你用 `advance` 快轉,它們就「以為」時間到了——於是一個原本要等 30 秒的逾時測試,可以在**一瞬間**跑完,而且結果完全 deterministic(每次都一樣,不受真實機器快慢影響)。

(小提醒:`pause` / `advance` 需要用 tokio 的計時功能,且通常在 `current_thread` runtime 下使用;`#[tokio::test]` 預設就是這種,所以一般直接用即可。)

### 為什麼這很重要

「測試要快、要穩」是寫測試的鐵則。async 程式常常牽涉 `sleep`、逾時、重試間隔這些和時間有關的邏輯,如果每次都真的去等,測試就會又慢又飄。`pause` + `advance` 讓你能**精準控制時間的流動**,把「等 N 秒」變成「快轉 N 秒」,是測 async 邏輯時非常實用的一招。

## 範例程式碼

測一段「最多等 1 秒,逾時就回 `None`」的邏輯,但完全不用真的等 1 秒:

```rust,ignore
use tokio::time::{self, advance, pause, Duration};

// 被測的函數:最多等 work 完成 1 秒,逾時回 None
async fn with_timeout<F, T>(work: F) -> Option<T>
where
    F: std::future::Future<Output = T>,
{
    time::timeout(Duration::from_secs(1), work).await.ok()
}

#[tokio::test]
async fn times_out_after_one_second() {
    pause();

    // 一個永遠不會完成的工作
    let never = std::future::pending::<i32>();
    let fut = with_timeout(never);
    tokio::pin!(fut);

    // 還沒到 1 秒,結果還沒出來
    advance(Duration::from_millis(999)).await;
    // 再快轉一點點,跨過 1 秒,逾時應該觸發
    advance(Duration::from_millis(2)).await;

    assert_eq!(fut.await, None); // 逾時,回 None——整個測試瞬間跑完
}
```

## 重點整理

- `#[tokio::test]` = 「`#[test]` + 自動建 runtime 並 `block_on`」,讓測試函數能直接 `.await`
- `cargo test`、`assert_eq!` 等用法和第 7 章完全一樣
- 和時間有關的測試別真的去等:`tokio::time::pause()` 暫停時鐘,`advance(時間)` 手動快轉
- 這讓「等 30 秒」的逾時邏輯能在**一瞬間、deterministic** 地測完,測試又快又穩
- `tokio::time::timeout` 是包逾時的好工具,搭配 `pause`／`advance` 很好測
