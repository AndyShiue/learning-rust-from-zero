# 測試 `async` 程式

## 本集目標

學會用 `#[tokio::test]` 寫 `async` 測試，以及用虛擬時間讓牽涉延遲的測試跑得又快又穩。

## 正文

### `#[tokio::test]`

第 7 章學過用 `#[test]` 加 `cargo test` 寫測試。但 `#[test]` 標記的是一個普通函式，沒辦法 `.await`。要測 `async` 程式，Tokio 提供 `#[tokio::test]`——它會自動幫你的測試函式套上一個 runtime，你不用自己 `block_on`：

```rust,noplayground
# extern crate tokio;
#
async fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[tokio::test]
async fn test_add() {
    let result = add(2, 3).await;
    assert_eq!(result, 5);
}
#
# fn main() {}
```

就這麼簡單。`#[tokio::test]` 等於「`#[test]` + 自動準備 runtime + 允許 `async`」。其他和第 7 章一樣：放進 `#[cfg(test)] mod tests`、用 `cargo test` 執行、用 `assert_eq!` 之類的巨集檢查結果。

### 牽涉時間的測試怎麼辦

`async` 程式常常牽涉時間——timeout、延遲、定時重試。如果照實測，一個「5 秒後逾時」的邏輯，測試就得真的等 5 秒，又慢又煩。更糟的是，靠真實時間的測試常常不穩（有時候機器卡一下，時序就跑掉了，測試忽過忽不過）。

Tokio 的解法是**虛擬時間**：讓測試裡的時間由你**手動推進**，不必真的空等。兩個關鍵函式：

- `tokio::time::pause()`：把時間「暫停」，從此時間不會自己流動。
- `tokio::time::advance(duration)`：手動把時間往前快轉一段。

```rust,noplayground
# extern crate tokio;
#
use tokio::time::{self, Duration};

#[tokio::test]
async fn test_with_virtual_time() {
    time::pause(); // 暫停時間

    let start = time::Instant::now();

    // 把虛擬時間往前推 10 秒——瞬間完成，不必真的等
    time::advance(Duration::from_secs(10)).await;

    assert!(start.elapsed() >= Duration::from_secs(10));
}
#
# fn main() {}
```

這個測試**瞬間**就跑完了，即使邏輯上「過了 10 秒」。因為時間是虛擬的，`advance` 一下就跳過去了。如果你想讓測試從一開始就暫停時間，也可以直接寫 `#[tokio::test(start_paused = true)]`，省掉手動呼叫 `pause()`。

有了虛擬時間，凡是牽涉 timeout、延遲、重試間隔的測試，都能變得 **deterministic（每次結果一致）** 又快——你完全掌控時間怎麼走，不必看真實時鐘的臉色。

（小提醒：`pause` / `advance` 這些虛擬時間工具需要開啟 Tokio 的 `test-util` 功能，在 `Cargo.toml` 把 tokio 的 features 加上 `"test-util"` 即可。）

## 重點整理

- `#[tokio::test]` 自動幫測試函式套上 runtime、允許 `.await`，等於「`#[test]` + runtime + `async`」；其餘用法和第 7 章的 `cargo test` 一樣
- 牽涉時間的測試別用真實時間（又慢又不穩），改用 Tokio 的虛擬時間
- `tokio::time::pause()` 暫停時間、`tokio::time::advance(duration)` 手動快轉，讓 timeout / 延遲的測試瞬間完成且結果一致
- 也可用 `#[tokio::test(start_paused = true)]` 從頭暫停時間；虛擬時間工具需要 tokio 的 `test-util` 功能
