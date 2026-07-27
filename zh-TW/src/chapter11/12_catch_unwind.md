# `catch_unwind`

## 本集目標

學會用 `catch_unwind` 攔截 panic，並理解什麼時候適合使用它。

## 概念說明

### 基本用法

一般來說，沒有被攔截的 panic 最終會終止目前的執行緒。`catch_unwind` 可以在閉包周圍建立一道邊界，攔住離開閉包的 panic：

```rust,editable
use std::panic;

fn main() {
    let result = panic::catch_unwind(|| {
        println!("正常執行");
        42
    });
    println!("{:?}", result); // Ok(42)

    let result = panic::catch_unwind(|| {
        panic!("出事了阿北");
    });
    println!("{:?}", result); // Err(...)
}
```

閉包正常回傳時會得到 `Ok(值)`；閉包 panic 時則會得到 `Err`，程式之後可以繼續執行。

即使 panic 已經被攔住，終端機上仍可能顯示 panic 訊息。重點是程式會繼續執行，而且 `catch_unwind` 會回傳 `Err`。

### 為什麼要攔截 panic？

其中一個特殊用途是在提供給 C 呼叫的 Rust 函數裡攔截 panic。如果 `extern "C"` 函數裡的 panic 沒有被攔住，整個程式會在回到 C 之前自動中止。

為了避免中止，你可以在 Rust 函數裡使用 `catch_unwind`，再把 `Err` 轉成錯誤碼。本集最後的範例會示範這種寫法。如果你能接受程式中止，就不需要使用 `catch_unwind`。

### `UnwindSafe`

`catch_unwind` 要求閉包是 `UnwindSafe` 的。理由很簡單：panic 可能在修改做到一半時將操作打斷，而程式攔截 panic 後，可能繼續使用只更新到一半的資料。

`&mut T` 無法通過這項檢查。如果閉包透過可變參考修改資料後 panic，閉包外的資料可能會停在只更新一半的狀態。

大部分共享參考都能通過檢查，例如 `&i32` 和 `&String`，但並不是所有 `&T` 都可以。例如 `&Cell<T>` 和 `&RefCell<T>` 就不行，因為 `Cell` 和 `RefCell` 能透過共享參考修改資料。

`UnwindSafe` 只是提醒你思考 panic 後留下的狀態，並不會證明資料在邏輯上一定正確。

### `AssertUnwindSafe`

如果你已經考慮過可能留下的狀態，也知道該怎麼處理，`AssertUnwindSafe` 可以讓你明確要求 Rust 接受這個閉包：

```rust,editable
use std::panic::{catch_unwind, AssertUnwindSafe};

fn main() {
    let mut data = vec![1, 2, 3];
    let original_len = data.len();

    let result = catch_unwind(AssertUnwindSafe(|| {
        data.push(4);
        panic!("修改到一半時停止了");
    }));

    if result.is_err() {
        data.truncate(original_len);
    }

    println!("{:?}", data); // [1, 2, 3]
}
```

`AssertUnwindSafe` 不會自動幫你修復資料。它只是告訴 Rust：你願意負責在 panic 後檢查或恢復資料的狀態。

### `panic = "abort"`

`Cargo.toml` 可以設定：

```toml
[profile.release]
panic = "abort"
```

使用這個設定時，panic 會立刻終止整個程式，`catch_unwind` 無法將它攔下來。

### 不是一般的錯誤處理

`catch_unwind` 不是一般錯誤處理用的 `try`／`catch`。能預期的失敗應該使用 `Result`。只有在刻意需要限制 panic 影響範圍時才使用 `catch_unwind`，例如讓 FFI 函數回傳錯誤碼，而不是讓整個程式中止。

## 範例程式碼

```rust,editable
use std::panic;

// 模擬由 FFI 函數呼叫，而且我們無法完全控制的程式碼。
fn library_task(mode: i32) -> i32 {
    if mode == 0 {
        panic!("library task panic 了");
    }
    100 / mode
}

extern "C" fn ffi_entry(mode: i32) -> i32 {
    match panic::catch_unwind(|| library_task(mode)) {
        Ok(value) => value,
        Err(_) => -1, // 把 panic 轉成錯誤碼
    }
}

fn main() {
    println!("成功：{}", ffi_entry(4)); // 25
    println!("失敗：{}", ffi_entry(0)); // -1，程式會繼續執行
}
```

這裡的 panic 會在 `ffi_entry` 裡被攔下來，不會離開 `extern "C"` 函數。這個函數最後會正常回傳 `-1`。

## 重點整理

- `catch_unwind` 執行一個閉包，回傳 `Ok(值)` 或 `Err`。
- 被攔住的 panic 仍可能印出訊息，但程式可以繼續執行。
- 如果 `extern "C"` Rust 函數裡的 panic 沒有被攔住，整個程式會在回到 C 之前中止。只有想改成回傳錯誤碼等其他結果時，才需要事先攔截。
- `&mut T` 無法通過 `UnwindSafe` 檢查。大部分共享參考可以，但 `&Cell<T>` 和 `&RefCell<T>` 是例外。
- `AssertUnwindSafe` 會要求 Rust 接受你的判斷，但你仍要負責處理只更新到一半的資料。
- `panic = "abort"` 設定下，`catch_unwind` 無法攔截 panic。
- 能預期的失敗應該使用 `Result`，不要使用 `catch_unwind`。

恭喜你完成了進階標準庫這一章！🎉 這一章介紹了標準庫和社群裡的各種實用工具——從 `AsRef`、排序、集合，到輸入輸出、字串方法、錯誤處理，再到 `catch_unwind`。下一章我們將進入非同步的世界！
