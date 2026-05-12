# `match` C-style `enum`

## 本集目標

學會用 `match` 來根據 `enum` 的值執行不同的程式碼，並理解「窮舉」的概念。

## 概念說明

上一集我們定義了 `enum`，但沒辦法根據它的值做不同的事。現在來學 `match`——Rust 最強大的**模式匹配**（pattern matching）工具。

`match` 的基本語法是：

```rust,ignore
match 變數 {
    模式1 => 做某件事,
    模式2 => 做另一件事,
    模式3 => 做第三件事,
}
```

每一行叫做一個「分支」（arm）。Rust 會從上到下檢查，找到第一個符合的模式就執行對應的程式碼。

**最重要的規則：`match` 必須窮舉所有可能的值。** 如果你的 `enum` 有三個 variant，你就必須處理全部三個。少寫一個，編譯器就會報錯。這是 Rust 幫你抓 bug 的方式——確保你不會忘記處理某種情況。

和 `struct` 還有 `enum` 一樣，`match` 的最後一個分支後面也可以加 trailing comma（結尾逗號）。Rust 社群慣例是加上的。

## 範例程式碼

```rust
enum Color {
    Red,
    Green,
    Blue,
}

fn main() {
    let c = Color::Green;

    match c {
        Color::Red => println!("紅色"),
        Color::Green => println!("綠色"),
        Color::Blue => println!("藍色"),
    }

    // 再來一個例子
    let light = Color::Red;

    match light {
        Color::Red => println!("停下來！"),
        Color::Green => println!("可以走了！"),
        Color::Blue => println!("這個交通燈有點奇怪..."),
    }
}
```

## 重點整理

- `match` 會根據值比對不同的模式，執行對應的分支
- 每個分支用 `=>` 分隔模式和要執行的程式碼
- **`match` 必須窮舉所有 variant**——少一個就編譯失敗
- 分支從上到下比對，第一個符合的就會執行
- `match` 是 Rust 處理 `enum` 最基本的方式
