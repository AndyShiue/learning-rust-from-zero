# use 基礎

## 本集目標
學會用 `use` 把長路徑縮短，並理解為什麼之前不用 `use` 就能用 `Option`、`Vec` 等型別。

## 概念說明

Rust 有非常多內建的函數、型別和 trait，為了組織它們，Rust 的標準庫用模組把東西分門別類。舉例來說，每個型別都有一個完整的**路徑**來說明它位於哪個模組裡，路徑用 `::` 分隔，像是 `std::string::String`（`String` 位於 `std` 的 `string` 模組裡）、`std::vec::Vec`、`std::fmt::Display`。平常要用某個型別，就要寫出它的完整路徑。

但奇怪的是，我們前面一直在用 `Vec`、`String`、`Option`、`Result` 這些型別，從來沒寫過 `std::vec::Vec` 這種完整路徑也能用，為什麼？

因為 Rust 有一個叫 **prelude** 的機制——Rust 預設就把最常用的函數、型別和 trait 引入到每個檔案裡。`Vec`、`String`、`Option`、`Result`、`Some`、`None`、`Ok`、`Err`，還有 `Clone`、`Copy` 等常用 trait，都在 prelude 裡面，所以不用寫完整路徑。

但不是所有東西都在 prelude 裡。比如 `std::fmt::Display` 這個 trait，就不在 prelude 裡。如果你想用它，就要寫完整路徑——或者用 `use` 把它引入。

### use 的語法

```rust,no_run
use std::fmt::Display;
#
# fn main() {}
```

這行的意思是：「把 `std::fmt::Display` 引入到當前的作用域，之後直接寫 `Display` 就好。」

`use` 不會引入新功能，它只是讓長路徑變短。沒有 `use`，你寫 `std::fmt::Display`；有了 `use`，你只需要寫 `Display`。

## 範例程式碼

```rust
use std::mem::size_of;

fn main() {
    // 沒有 use 的話，要寫完整路徑：
    println!("i32 的大小：{} bytes", std::mem::size_of::<i32>());

    // 有了 use，直接寫 size_of 就好：
    println!("bool 的大小：{} bytes", size_of::<bool>());
    println!("f64 的大小：{} bytes", size_of::<f64>());
    println!("char 的大小：{} bytes", size_of::<char>());
}
```

## 重點整理
- `use std::fmt::Display;` 把長路徑縮短，之後直接寫 `Display`
- `use` 只是路徑的簡寫，不引入新功能
- Rust 的編譯器預設引入 prelude 的常用型別和 trait（Vec、String、Option、Clone 等）
- 不在 prelude 裡的東西（如 `Display`）需要寫完整路徑或用 `use` 引入
