# `cfg!` 巨集

## 本集目標

學會用 `cfg!` 在執行期根據條件選擇邏輯，以及跟 `#[cfg]` 的差別。

## 概念說明

### `cfg!` 回傳 `bool`

上一集學了 `#[cfg(...)]`——條件編譯，不符合條件的程式碼整塊被移除。但有時候你只是想根據條件走不同分支，不想移除整塊程式碼。`cfg!` 就是做這件事的：

```rust,editable
fn main() {
    if cfg!(target_os = "windows") {
        println!("你在 Windows 上");
    } else {
        println!("你不在 Windows 上");
    }
}
```

### 跟 `#[cfg]` 的差別

| | `#[cfg(...)]` | `cfg!(...)` |
|--|--|--|
| 作用 | 條件編譯：整段程式碼移除或保留 | 回傳 `bool` |
| 時機 | 不符合的程式碼消失，不會被編譯 | 兩邊都會被編譯，執行時選邊 |

重要差別：`#[cfg]` 不符合的那塊完全不存在，裡面就算有不存在的函數也不會報錯。但 `cfg!` 兩邊都會編譯——如果某一邊有編譯錯誤，不管條件成不成立都會報錯。

```rust,ignore
// #[cfg] 版：Windows 上不會編譯 linux_only()，不會報錯
#[cfg(target_os = "linux")]
fn linux_only() { /* Linux 特有功能 */ }

// cfg! 版：兩邊都會被編譯
if cfg!(target_os = "linux") {
    // linux_only(); // 如果函數不存在，在 Windows 上也會編譯錯誤！
}
```

### 常見條件

`#[cfg]` 和 `cfg!` 能用的條件一樣：

- `target_os = "windows"` / `"linux"` / `"macos"`
- `target_arch = "x86_64"` / `"aarch64"`
- `debug_assertions` — debug 模式下為 `true`
- `feature = "my_feature"` — Cargo feature
- `test` — 在 `cargo test` 時為 `true`

## 範例程式碼

```rust,editable
fn main() {
    if cfg!(debug_assertions) {
        println!("debug 模式");
    } else {
        println!("release 模式");
    }

    let os = if cfg!(target_os = "windows") {
        "Windows"
    } else if cfg!(target_os = "linux") {
        "Linux"
    } else if cfg!(target_os = "macos") {
        "macOS"
    } else {
        "其他"
    };
    println!("作業系統：{}", os);
}
```

## 重點整理

- `cfg!(...)` 回傳 `bool`，兩邊程式碼都會被編譯，執行時選擇
- `#[cfg(...)]` 是條件編譯，不符合的程式碼整塊移除
- 兩者能用的條件一樣：`target_os`、`debug_assertions`、`feature`、`test` 等
