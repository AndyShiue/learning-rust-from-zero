# proc macro

## 本集目標

認識三種 proc macro，理解它們的運作原理。這集只是大概介紹 proc macro 的概念和骨架，不會帶你實際寫一個完整的 proc macro。如果有需要，請自行搜尋相關教學。

## 概念說明

### 什麼是 proc macro

上一集的 `macro_rules!` 用模式匹配展開程式碼。但有些事情它做不到——例如讀取 `struct` 的欄位名稱來自動產生程式碼。`#[derive(Debug)]` 是怎麼知道你的 `struct` 有哪些欄位的？答案就是 **proc macro**（procedural macro）。

proc macro 拿到你的程式碼作為輸入（一串 token），然後產生新的程式碼（也是一串 token）。

### TokenStream

proc macro 的輸入和輸出都是 `TokenStream`——Rust 程式碼的 token 序列。`struct Foo { x: i32 }` 進來的時候，proc macro 看到的是一串 token：`struct`、`Foo`、`{`、`x`、`:`、`i32`、`}`。

### 三種 proc macro

**1. `derive` macro**

搭配 `#[derive(...)]` 使用，最常見。

```rust,ignore
#[proc_macro_derive(MyDerive)]
pub fn my_derive(input: TokenStream) -> TokenStream {
    // input：被 #[derive(MyDerive)] 標記的 struct / enum 的程式碼
    // 回傳：要「附加」在旁邊的新程式碼（原始 struct / enum 不會被取代）
    TokenStream::new()
}
```

使用：`#[derive(MyDerive)] struct Foo { x: i32 }`

**2. attribute macro**

自訂 attribute。

```rust,ignore
#[proc_macro_attribute]
pub fn my_attr(attr: TokenStream, item: TokenStream) -> TokenStream {
    // attr：attribute 的參數
    // item：被標記的整個項目
    // 回傳：「取代」原本的項目
    item
}
```

使用：`#[my_attr(some_arg)] fn my_function() { ... }`

**3. function-like macro**

看起來像函數呼叫。

```rust,ignore
#[proc_macro]
pub fn my_macro(input: TokenStream) -> TokenStream {
    // input：括號裡的內容
    // 回傳：展開後的程式碼
    input
}
```

使用：`my_macro!(任何 token);`

### 三者的差別

- **`derive`**：**附加**新程式碼，不取代原本的 `struct` / `enum`
- **attribute**：**取代**被標記的項目
- **function-like**：括號裡的內容被**展開**成新的程式碼

### 獨立 crate

proc macro 必須定義在獨立的 crate 裡，`Cargo.toml` 要加：

```toml
[lib]
proc-macro = true
```

### `syn` 和 `quote`

實務上通常搭配兩個社群 crate：
- **`syn`**：把 `TokenStream` 解析成結構化的資料（例如知道「這是一個 `struct`，有一個欄位叫 `x`」）
- **`quote`**：方便地從結構化資料生成 `TokenStream`

沒有它們你就得自己一個一個 token 處理，非常痛苦。

## 範例程式碼

以下是三種 proc macro 的最小骨架（需要在獨立的 proc-macro crate 裡）：

```rust,ignore
use proc_macro::TokenStream;

// 1. derive macro
#[proc_macro_derive(MyDerive)]
pub fn my_derive(input: TokenStream) -> TokenStream {
    // 用 syn 解析 input，用 quote 生成程式碼
    TokenStream::new() // 什麼都不生成
}

// 2. attribute macro
#[proc_macro_attribute]
pub fn my_attr(_attr: TokenStream, item: TokenStream) -> TokenStream {
    item // 原封不動回傳
}

// 3. function-like macro
#[proc_macro]
pub fn my_macro(input: TokenStream) -> TokenStream {
    input // 原封不動回傳
}
```

以下是使用端的程式碼（在另一個 crate 裡）：

```rust,ignore
// 假設 proc-macro crate 叫 my_macros
use my_macros::{MyDerive, my_attr, my_macro};

#[derive(MyDerive)]
struct Foo { x: i32 }

#[my_attr]
fn hello() {
    println!("hello");
}

fn main() {
    hello();
    my_macro!(這裡可以放任何 token);
}
```

## 重點整理

- proc macro 分三種：`derive`、attribute、function-like
- 本質是接收 `TokenStream`、回傳 `TokenStream` 的編譯期函數
- `derive` 附加程式碼、attribute 取代項目、function-like 展開內容
- 必須在獨立 crate 裡定義（`proc-macro = true`）
- 常用 `syn`（解析）和 `quote`（生成）兩個 crate
