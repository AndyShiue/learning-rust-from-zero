# `extern` blocks

## 本集目標

學會呼叫 C 函數和讓 C 呼叫 Rust 函數。這集只是大概介紹 FFI 的功能。如果你想要一個完整的 FFI 例子（從建立 C 函式庫到在 Rust 裡呼叫），請自行搜尋相關教學。

## 概念說明

### FFI 是什麼

FFI（Foreign Function Interface）是讓不同程式語言互相呼叫函數的機制。Rust 可以呼叫 C 寫的函數，C 也可以呼叫 Rust 寫的函數。因為幾乎所有語言都能跟 C 互通，所以 Rust 透過 C 這個橋樑，就能跟大部分語言互動。

### 呼叫 C 函數

用 `unsafe extern "C"` 區塊宣告外部的 C 函數：

```rust
unsafe extern "C" {
    fn abs(x: i32) -> i32;
}

fn main() {
    let result = unsafe { abs(-42) };
    println!("abs(-42) = {}", result);
}
```

呼叫外部函數需要 `unsafe`——因為 Rust 沒辦法檢查 C 那邊的函數是不是安全的。

在 Rust 2024 edition 後，`extern` 區塊本身也需要 `unsafe`——因為你在宣告裡寫的函數簽名（參數型別、回傳型別等）是否正確，Rust 沒辦法驗證。如果簽名跟 C 那邊實際的不一樣，就會導致未定義行為。

### `safe fn`

如果你確定某個外部函數是安全的，可以標記 `safe`：

```rust
unsafe extern "C" {
    safe fn abs(x: i32) -> i32; // 你保證 abs 一定安全
}

fn main() {
    let result = abs(-42); // 不需要 unsafe 也能呼叫！
    println!("abs(-42) = {}", result);
}
```

### `"C"` 是什麼

`extern "C"` 的 `"C"` 指的是 **ABI**（Application Binary Interface）——函數在二進位層面的呼叫方式。`"C"` 是最常用的 ABI，幾乎所有語言都能跟 C ABI 互通。

### 讓 C 呼叫 Rust

```rust,noplayground
#[unsafe(no_mangle)]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}
#
# fn main() {}
```

- `extern "C"`：用 C ABI
- `#[unsafe(no_mangle)]`：不要混淆函數名稱，讓 C 能用 `add` 找到它。在 2024 edition 中，`no_mangle` 是 `unsafe` attribute，因為它改變了函數的連結方式，可能影響安全性

### `extern` 區塊裡也能宣告 `static` 變數

```rust,noplayground
unsafe extern "C" {
    static errno: i32; // C 那邊的全域變數
}
#
# fn main() {}
```

## 範例程式碼

```rust
unsafe extern "C" {
    safe fn abs(x: i32) -> i32;
    fn sqrt(x: f64) -> f64;
}

#[unsafe(no_mangle)]
pub extern "C" fn rust_add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    // 標記 safe 的函數不需要 unsafe
    println!("abs(-10) = {}", abs(-10));

    // 沒標記 safe 的需要 unsafe
    let root = unsafe { sqrt(25.0) };
    println!("sqrt(25) = {}", root);

    // Rust 的 extern "C" 函數也能在 Rust 裡直接呼叫
    println!("rust_add(3, 4) = {}", rust_add(3, 4));
}
```

## 重點整理

- `unsafe extern "C" { ... }` 宣告外部 C 函數
- 呼叫外部函數需要 `unsafe`；標記 `safe fn` 的除外
- `"C"` 是 ABI，指定函數在二進位層面的呼叫方式
- `#[unsafe(no_mangle)] pub extern "C" fn` 讓 C 可以呼叫 Rust