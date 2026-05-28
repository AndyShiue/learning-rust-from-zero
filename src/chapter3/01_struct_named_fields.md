# `struct`（named fields）

## 本集目標

學會用 `struct` 把多個相關的值組合在一起，形成一個自訂型別。

## 概念說明

到目前為止，我們用過的型別都是 Rust 內建的：`i32`、`f64`、`bool`、`char`，還有 tuple、陣列和切片。但實際寫程式的時候，你會需要**自己定義新的型別**。

`struct` 就是 Rust 讓你定義新型別的方式之一。定義一個 `struct`，就是在告訴 Rust：「我要一個新的型別，它裡面包含這些欄位。」

比如說，一個「點」有 x 座標和 y 座標。我們可以用 tuple `(i32, i32)` 來表示，但 tuple 只能用 `.0`、`.1` 取值，看不出哪個是 `x`、哪個是 `y`。用 `struct` 就能幫每個欄位取名字。

定義 `struct` 的語法是：

```rust,editable
struct Point {
    x: i32,
    y: i32,
}
#
# fn main() {}
```

`struct` 定義一般放在 `fn main()` 外面，這樣其他函數也能用到。放在上面或下面都可以（和函數一樣，不受定義順序限制）。

建立一個 `struct` 的值時，要用 `型別名 { 欄位名: 值 }` 的寫法。取值的時候用 `.欄位名`。如果要修改 `struct` 的欄位，變數必須加 `mut`。

## 範例程式碼

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 3, y: 7 };
    println!("x 座標是 {}", p.x);
    println!("y 座標是 {}", p.y);

    // Point 是一個型別，就像 i32 一樣，可以用在型別標注上
    let p2: Point = Point { x: 100, y: 200 };
    println!("p2 的座標是 ({}, {})", p2.x, p2.y);

    // 也可以用 mut 讓 struct 的值可以修改
    let mut q = Point { x: 0, y: 0 };
    q.x = 10;
    q.y = 20;
    println!("q 的座標是 ({}, {})", q.x, q.y);
}
```

## 補充：trailing comma（結尾逗號）

注意 `struct` 定義裡，最後一個欄位後面也有逗號：

```rust,editable
struct Point {
    x: i32,
    y: i32, // ← 這個逗號可加可不加
}
#
# fn main() {}
```

Rust 允許在 `struct` 定義、`struct` 建立、函數呼叫等地方的最後一個項目後面加逗號。這叫做 **trailing comma**（結尾逗號）。加了不會錯，而且好處是之後新增欄位時，不用回去幫上一行補逗號，git diff 也比較乾淨。

Rust 社群慣例是**加上 trailing comma**。

## 重點整理

- `struct` 讓你定義一個有名字欄位的自訂型別
- `struct` 定義一般放在 `fn main()` 外面，上面或下面都可以（和函數一樣）
- 建立 `struct` 值的語法：`Point { x: 1, y: 2 }`
- 用 `.欄位名` 取得欄位的值，例如 `p.x`
- 如果要修改 `struct` 的欄位，變數必須加 `mut`
- 最後一個欄位後面的逗號（trailing comma）可加可不加，慣例是加
