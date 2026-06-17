# 文件註解

## 本集目標

學會撰寫文件註解，理解文件範例就是測試（doctest），並用 `cargo doc` 產生專業的 HTML 文件。

## 概念說明

Rust 把文件當作語言的一等公民——不是用外部工具硬擠出來的，而是內建在語法裡的。更厲害的是：文件裡的範例程式碼會被 `cargo test` 當成測試執行，所以 Rust 的文件範例永遠不會悄悄過期。

### `///` 項目文件註解

三個斜線 `///` 是用來為**接下來的項目**（函數、`struct`、`enum`、`trait` 等）寫文件：

```rust,noplayground
/// 計算兩個整數的最大公因數。
///
/// 使用歐幾里得演算法，效率為 O(log(min(a, b)))。
///
/// # Examples
///
/// ```
/// use my_math_lib::gcd;
///
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

### `//!` `mod`/crate 層級文件

兩個斜線加驚嘆號 `//!` 是為**包含它的項目**寫文件，通常放在檔案最頂端：

```rust,noplayground
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

放在 `lib.rs` 頂端就是整個 crate 的文件，放在某個 `mod` 檔案頂端就是那個 `mod` 的文件。

### 常用的文件段落

Rust 社群有一些約定俗成的文件段落名稱：

- `# Examples` — 使用範例（最重要的一個！）
- `# Panics` — 什麼情況下會 panic
- `# Errors` — 如果回傳 `Result`，什麼情況下會是 `Err`

### 文件範例就是測試（doctest）

重點來了。`# Examples` 裡的程式碼區塊不只是給人看的——**`cargo test` 會把每一個文件範例抽出來、編譯、執行**，這叫做 **doctest**。第 6 集學的 `cargo test` 其實除了跑 `#[test]` 函數之外，也會跑所有的 doctest。

每個文件範例會被當成一個**獨立的小程式**來編譯——它在你的 library **外面**，就像一個使用你 library 的人寫的程式。所以範例裡必須寫 `use my_math_lib::gcd;`，就像真正的使用者一樣。忘記寫 `use`，doctest 會編譯失敗——而**編譯失敗也算測試失敗**。順帶一提，範例裡不需要寫 `fn main()`，rustdoc 會自動幫你包一層。

這個設計帶來一個很美好的結果：**範例永遠是對的**。如果你改了函數的名字或簽名，卻忘了改文件裡的範例，`cargo test` 立刻就跳錯誤給你看。在很多語言裡，文件範例會隨著程式碼演進而悄悄過期；在 Rust，過期的範例會直接擋住你的測試。

一個要注意的地方：只有 **library crate** 的 doctest 會執行。binary crate 裡的文件註解一樣能產生文件，但裡面的範例**不會**被當成測試跑。

### `cargo doc`

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

換一個完整的例子。假設 `Cargo.toml` 裡 `[package]` 的 `name` 是 `temperature`，以下是 `src/lib.rs` 的內容：

```rust,noplayground
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
/// use temperature::celsius_to_fahrenheit;
///
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
/// use temperature::fahrenheit_to_celsius;
///
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
    ///
    /// # Examples
    ///
    /// ```
    /// use temperature::Temperature;
    ///
    /// let body = Temperature::Fahrenheit(98.6);
    /// assert!((body.to_celsius() - 37.0).abs() < 0.001);
    /// ```
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
#
# fn main() {}
```

## 重點整理

- `///` 為接下來的項目（`fn`、`struct`、`enum` 等）撰寫文件
- `//!` 為包含它的項目（`mod`、crate）撰寫文件，通常放在檔案最頂端
- 文件註解支援完整的 Markdown 語法
- `# Examples` 是最重要的文件段落——好的範例勝過千言萬語
- **文件範例就是 doctest**：`cargo test` 會編譯並執行所有文件範例，編譯失敗或 `assert` 失敗都算測試失敗
- doctest 以「library 使用者」的身分編譯，所以範例裡要寫 `use your_crate::...`
- doctest 只對 library crate 執行
- `cargo doc --open` 一鍵產生並打開 HTML 文件
- 你在 docs.rs 上看到的文件，就是用同樣的機制產生的
