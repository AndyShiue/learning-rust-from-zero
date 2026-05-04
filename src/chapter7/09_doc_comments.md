# 文件註解

## 本集目標

學會撰寫文件註解，用 `cargo doc` 產生專業的 HTML 文件。

## 概念說明

Rust 把文件當作語言的一等公民——不是用外部工具硬擠出來的，而是內建在語法裡的。

### `///` 項目文件註解

三個斜線 `///` 是用來為**接下來的項目**（函數、struct、enum、trait 等）寫文件：

```rust,no_run
/// 計算兩個整數的最大公因數。
///
/// 使用歐幾里得演算法，效率為 O(log(min(a, b)))。
///
/// # Examples
///
/// ```
/// let result = gcd(12, 8);
/// assert_eq!(result, 4);
/// ```
pub fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        let temp = b;
        b = a % b;
        a = temp;
    }
    a
}
#
# fn main() {}
```

`///` 裡面支援完整的 **Markdown 語法**——標題、粗體、程式碼區塊、列表，全部都能用。

### `//!` mod/crate 層級文件

兩個斜線加驚嘆號 `//!` 是為**包含它的項目**寫文件，通常放在檔案最頂端：

```rust,no_run
//! # Math Library
//!
//! 這個 library 提供基本的數學運算函數。
//!
//! ## 功能
//!
//! - 基本算術運算
//! - 最大公因數計算
//! - 次方運算

pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
#
# fn main() {}
```

放在 `lib.rs` 頂端就是整個 crate 的文件，放在某個 mod 檔案頂端就是那個 mod 的文件。

### 常用的文件段落

Rust 社群有一些約定俗成的文件段落名稱：

- `# Examples` — 使用範例（最重要的一個！）
- `# Panics` — 什麼情況下會 panic
- `# Errors` — 如果回傳 `Result`，什麼情況下會是 `Err`

### cargo doc

寫好文件註解後，一行指令就能產生漂亮的 HTML 文件：

```bash
cargo doc --open
```

這會：
1. 編譯你的 crate（不執行）
2. 從所有 `///` 和 `//!` 產生 HTML 文件
3. 自動在瀏覽器打開

生成的文件就跟你在 docs.rs 上看到的一模一樣。

## 範例程式碼

```rust
//! # 溫度轉換工具
//!
//! 提供攝氏和華氏之間的轉換函數。

/// 攝氏轉華氏。
///
/// # 公式
///
/// `F = C × 9/5 + 32`
///
/// # Examples
///
/// ```
/// let f = celsius_to_fahrenheit(100.0);
/// assert!((f - 212.0).abs() < 0.001);
/// ```
pub fn celsius_to_fahrenheit(c: f64) -> f64 {
    c * 9.0 / 5.0 + 32.0
}

/// 華氏轉攝氏。
///
/// # 公式
///
/// `C = (F - 32) × 5/9`
///
/// # Examples
///
/// ```
/// let c = fahrenheit_to_celsius(32.0);
/// assert!((c - 0.0).abs() < 0.001);
/// ```
pub fn fahrenheit_to_celsius(f: f64) -> f64 {
    (f - 32.0) * 5.0 / 9.0
}

/// 溫度的表示方式。
///
/// 支援攝氏和華氏兩種單位。
pub enum Temperature {
    /// 攝氏溫度
    Celsius(f64),
    /// 華氏溫度
    Fahrenheit(f64),
}

impl Temperature {
    /// 將任何溫度轉換為攝氏。
    pub fn to_celsius(&self) -> f64 {
        match self {
            Temperature::Celsius(c) => *c,
            Temperature::Fahrenheit(f) => fahrenheit_to_celsius(*f),
        }
    }

    /// 將任何溫度轉換為華氏。
    pub fn to_fahrenheit(&self) -> f64 {
        match self {
            Temperature::Celsius(c) => celsius_to_fahrenheit(*c),
            Temperature::Fahrenheit(f) => *f,
        }
    }
}

fn main() {
    let boiling = Temperature::Celsius(100.0);
    println!("水的沸點：{}°C = {}°F", boiling.to_celsius(), boiling.to_fahrenheit());

    let body = Temperature::Fahrenheit(98.6);
    println!("體溫：{}°F = {}°C", body.to_fahrenheit(), body.to_celsius());
}
```

## 重點整理

- `///` 為接下來的項目（fn、struct、enum 等）撰寫文件
- `//!` 為包含它的項目（mod、crate）撰寫文件，通常放在檔案最頂端
- 文件註解支援完整的 Markdown 語法
- `# Examples` 是最重要的文件段落——好的範例勝過千言萬語
- `cargo doc --open` 一鍵產生並打開 HTML 文件
- 你在 docs.rs 上看到的文件，就是用同樣的機制產生的
