# 檔案 mod

## 本集目標

學會將 mod 拆分到不同檔案，理解 Rust 的檔案與 mod 對應規則。

## 概念說明

上一集我們把 mod 寫在同一個檔案裡，但實際專案不可能全部塞在一起。Rust 提供了一套規則，讓你把 mod 拆到獨立的檔案中。

### 基本拆分：mod + 獨立檔案

假設你有一個 `math` mod，想把它搬到自己的檔案。做法很簡單：

1. 在 `main.rs`（或 `lib.rs`）裡寫 `mod math;`（注意是分號，不是大括號）
2. 建立 `math.rs`，把 mod 的內容放進去

```ignore
src/
├── main.rs
└── math.rs
```

**main.rs：**
```rust,ignore
mod math;

fn main() {
    let result = math::add(3, 5);
    println!("3 + 5 = {}", result);
}
```

**math.rs：**
```rust,ignore
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

pub fn subtract(a: i32, b: i32) -> i32 {
    a - b
}
```

注意 `math.rs` 裡面**不需要再寫 `mod math { ... }`**——檔案本身就代表那個 mod。

### 子 mod 的資料夾結構

如果 `math` mod 底下還有子 mod，有兩種組織方式：

**方式一：用 `mod.rs`（傳統風格）**

```ignore
src/
├── main.rs
└── math/
    ├── mod.rs
    ├── basic.rs
    └── advanced.rs
```

`math/mod.rs` 就是 `math` mod 的入口，裡面聲明子 mod：

```rust,ignore
// math/mod.rs
pub mod basic;
pub mod advanced;
```

**方式二：同名檔案 + 資料夾（推薦）**

```ignore
src/
├── main.rs
├── math.rs          ← math mod 的入口
└── math/
    ├── basic.rs
    └── advanced.rs
```

```rust,ignore
// math.rs
pub mod basic;
pub mod advanced;
```

兩種方式效果完全一樣，選你喜歡的就好。比較新的專案傾向用方式二，因為不會有一堆檔案都叫 `mod.rs`，在編輯器裡比較好辨認。

### lib.rs vs main.rs

一個 Rust 專案（crate）有兩種類型：

- **binary crate**：有 `src/main.rs`，會編譯成可執行檔
- **library crate**：有 `src/lib.rs`，給別人使用的程式庫

一個專案可以**同時**有 `main.rs` 和 `lib.rs`。`main.rs` 是 binary crate 的根，`lib.rs` 是 library crate 的根。

```ignore
src/
├── main.rs    ← binary crate root
├── lib.rs     ← library crate root
├── math.rs
└── math/
    ├── basic.rs
    └── advanced.rs
```

在 `main.rs` 裡可以用 crate 名稱引用 `lib.rs` 裡的東西：

```rust,ignore
// main.rs
// 假設 Cargo.toml 的 [package] name = "my_project"
use my_project::math;

fn main() {
    let result = math::basic::add(1, 2);
    println!("{}", result);
}
```

## 範例程式碼

由於檔案 mod 涉及多個檔案，無法用單一檔案示範。以下是完整的多檔案範例，建立對應的檔案結構後用 `cargo run` 執行：

```ignore
src/
├── main.rs
├── math.rs
└── math/
    ├── basic.rs
    └── advanced.rs
```

**main.rs：**
```rust,ignore
mod math;

fn main() {
    let sum = math::basic::add(10, 20);
    println!("10 + 20 = {}", sum);

    let p = math::advanced::power(2, 8);
    println!("2 ^ 8 = {}", p);
}
```

**math.rs：**
```rust,ignore
pub mod basic;
pub mod advanced;
```

**math/basic.rs：**
```rust,ignore
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

**math/advanced.rs：**
```rust,ignore
pub fn power(base: i32, exp: u32) -> i32 {
    let mut result = 1;
    for _ in 0..exp {
        result *= base;
    }
    result
}
```

## 重點整理

- `mod math;`（分號結尾）告訴 Rust 去找子 mod
- 被拆出去的檔案裡**不需要**再寫 `mod math { ... }`，檔案本身就是 mod
- 子 mod 可以用 `math/mod.rs`（傳統）或 `math.rs` + `math/` 資料夾（推薦）
- `main.rs` 是 binary crate 的根，`lib.rs` 是 library crate 的根
- 一個專案可以同時是 binary crate 和 library crate
