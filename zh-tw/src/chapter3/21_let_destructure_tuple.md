# `let` 解構 tuple

## 本集目標

學會用 `let` 直接把 tuple 的值拆開，分別賦值給不同的變數。

## 概念說明

之前我們學了在 `match` 裡解構 tuple，像是 `(x, y) => ...`。但其實**不用 `match`，用 `let` 就可以直接解構**！

```rust,noplayground
# fn main() {
    let (x, y) = (1, 2);
# }
```

這一行做了兩件事：

1. 建立一個 tuple `(1, 2)`
2. 把第一個值取出來叫 `x`，第二個值取出來叫 `y`

之前在第 2 章學 tuple 時，都是用 `t.0`、`t.1` 來取值。現在學了解構，你可以一行就把所有值拆開，每個值都有一個好讀的名字。

之前學的 `_` 和 `..` 也可以在 let 解構裡使用。

## `mut` 在綁定上

之前在第 1 章學了 `let mut x = 5;`。其實 `mut` 不是型別的一部分——它是**綁定（binding）的修飾**。

既然 let 解構就是在做 binding，自然也可以對個別變數加 `mut`：

```rust,compile_fail
# #![allow(unused)]
#
# fn main() {
    let (mut a, b) = (1, 2);
    a += 10; // OK，a 是可變的
    b += 10; // 錯誤，b 是不可變的
# }
```

同一個 pattern 裡，可以有些變數加 `mut`，有些不加——各自獨立。

這個規則不只適用於 `let`，**任何綁定變數的地方都能加 `mut`**：

- match 分支：`Some(mut x) => { x += 1; }`
- for 迴圈：`for mut x in [1, 2, 3] { ... }`
- 函數參數：`fn foo(mut x: i32) { x += 1; }`

之後學到的綁定變數也一樣。都是同一件事——`mut` 修飾的是 binding，不是型別。

## 範例程式碼

```rust,editable
fn main() {
    // 基本的 let 解構
    let (x, y) = (10, 20);
    println!("x = {}, y = {}", x, y);

    // 三個值的 tuple 也可以
    let (name, score, grade) = ("小明", 95, 'A');
    println!("{} 得了 {} 分，等級 {}", name, score, grade);

    // 搭配 _ 忽略不需要的值
    let (_, second, _) = (1, 2, 3);
    println!("只要第二個：{}", second);

    // 搭配 .. 忽略多個值
    let (first, ..) = (100, 200, 300, 400);
    println!("只要第一個：{}", first);

    // 個別加 mut
    let (mut a, b) = (1, 2);
    a += 10;
    println!("a = {}, b = {}", a, b);

    // 函數回傳 tuple，直接解構
    let (min, max) = min_max(7, 3);
    println!("最小 {}，最大 {}", min, max);
}

fn min_max(a: i32, b: i32) -> (i32, i32) {
    if a < b {
        (a, b)
    } else {
        (b, a)
    }
}
```

## 重點整理

- `let (x, y) = (1, 2);` 可以直接把 tuple 拆開
- 解構 tuple 比用 `.0`、`.1` 更好讀
- 可以搭配 `_` 忽略單個值，搭配 `..` 忽略多個值
- `mut` 是 binding 的修飾，不是型別的一部分——任何綁定變數的地方都能加 `mut`
- 函數回傳 tuple 時，可以用 `let` 解構直接取出每個值
