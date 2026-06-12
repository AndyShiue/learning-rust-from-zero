# `catch_unwind`

## 本集目標

學會用 `catch_unwind` 攔截 panic。

## 概念說明

### 動機

正常情況下 panic 會讓當前的執行緒直接中止。但在 **FFI 邊界**，panic 不能往上傳到 C 那邊，否則是未定義行為（進階語言功能那章提過 FFI）。`catch_unwind` 讓你在 Rust 這邊攔住 panic，不讓它跨越語言邊界。

### 基本用法

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

`catch_unwind` 接受一個閉包，如果閉包正常回傳就得到 `Ok(值)`，如果 panic 了就得到 `Err`。

### `UnwindSafe`

`catch_unwind` 要求閉包是 `UnwindSafe` 的。為什麼？因為 panic 的時候，閉包裡的操作可能做到一半，資料處於不一致的狀態——跟多執行緒那章 poisoning 的道理一樣。

`&mut T` 不是 `UnwindSafe`：如果你透過 `&mut` 修改資料修到一半 panic 了，catch 之後那份資料可能是半成品。`&T`、`i32` 等不可變的東西是 `UnwindSafe` 的。

### `AssertUnwindSafe`

如果你確定沒問題，可以用 `AssertUnwindSafe` 包起來繞過檢查：

```rust,noplayground
use std::panic::{catch_unwind, AssertUnwindSafe};

fn main() {
    let mut data = vec![1, 2, 3];
    let result = catch_unwind(AssertUnwindSafe(|| {
        data.push(4);
    }));
}
```

這跟 poisoning 或 `unsafe` 的精神類似——你自己負責保證正確性。

### `panic = "abort"`

`Cargo.toml` 可以設定 `panic = "abort"`，這樣 panic 會直接終止程式，不會執行任何清理工作（包括 `drop`）。在這個設定下 `catch_unwind` 沒有用——panic 就是直接結束，沒有東西可以 catch。

```toml
[profile.release]
panic = "abort"
```

### 注意

`catch_unwind` 不是用來做一般的錯誤處理的——那是 `Result` 的工作。`catch_unwind` 只用在上面提到的那些特殊場景。

## 範例程式碼

```rust,editable
use std::panic;

fn might_fail(x: i32) -> i32 {
    if x == 0 {
        panic!("不能是零！");
    }
    100 / x
}

fn main() {
    let inputs = vec![10, 5, 0, 2];

    for x in inputs {
        let result = panic::catch_unwind(|| might_fail(x));
        match result {
            Ok(val) => println!("100 / {} = {}", x, val),
            Err(_) => println!("處理 {} 時 panic 了，跳過", x),
        }
    }

    println!("程式繼續執行");
}
```

## 重點整理

- `catch_unwind` 攔截 panic，回傳 `Ok(值)` 或 `Err`
- 主要用途：FFI 邊界，防止 panic 跨越語言邊界
- `UnwindSafe`：`&mut T` 不是 `UnwindSafe`（資料可能是半成品）
- `AssertUnwindSafe`：手動保證安全，繞過 `UnwindSafe` 檢查
- `panic = "abort"` 設定下 `catch_unwind` 無效
- 不要用 `catch_unwind` 做一般的錯誤處理——那是 `Result` 的工作

恭喜你完成了進階標準庫這一章！🎉 這一章介紹了標準庫和社群裡的各種實用工具——從 `AsRef`、排序、集合，到輸入輸出、字串方法、錯誤處理，再到 `catch_unwind`。
