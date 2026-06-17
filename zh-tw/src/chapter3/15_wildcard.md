# `_` wildcard

## 本集目標

學會用 `_` 來忽略不關心的值，以及在 `match` 裡建立預設分支。

## 概念說明

有時候在 `match` 裡，我們只關心某幾種情況，其他的都想「忽略」。Rust 提供了 `_`（底線）作為 **wildcard**（萬用字元），它可以匹配任何值，但不會把值綁定到變數上。

最常見的用法有兩種：

**1. 預設分支：`_ => ...`**

放在 `match` 的最後面，表示「其他所有情況都走這裡」：

```rust,editable
fn main() {
    let score = 95;
    match score {
        100 => println!("滿分！"),
        _ => println!("不是滿分"),
    }
}
```

**2. 忽略某個位置的值**

在 tuple 或 `enum` 的模式裡，用 `_` 佔住不需要的位置：

```rust,editable
fn main() {
    let point = (5, 5);
    match point {
        (0, _) => println!("在 y 軸上"), // 不關心第二個值
        (_, 0) => println!("在 x 軸上"), // 不關心第一個值
        (_, _) => println!("其他位置"),
    }
}
```

## 範例程式碼

```rust,editable
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn main() {
    // _ 作為預設分支
    let dir = Direction::Left;

    match dir {
        Direction::Up => println!("往上"),
        _ => println!("不是往上（可能是下、左、右）"),
    }

    // _ 忽略 tuple 裡的某個值
    let record = ("Alice", 95, 'A');

    match record {
        (name, _, _) => println!("名字是 {}", name),
    }

    // 混合使用
    let data = (1, Direction::Up);

    match data {
        (_, Direction::Up) => println!("方向是上（不管編號是多少）"),
        (id, _) => println!("編號 {}（方向不是上）", id),
    }

    // 在 i32 上使用 _ 作為預設
    let score = 87;

    match score {
        100 => println!("滿分！"),
        0 => println!("零分..."),
        _ => println!("得了 {} 分", score),
    }
}
```

## 重點整理

- `_` 是 wildcard，匹配任何值但不綁定變數
- `_ => ...` 放在 `match` 最後面當「預設分支」，處理所有未列出的情況
- 在模式裡用 `_` 忽略不需要的欄位
- 有了 `_`，`match` 就不用每個 variant 都寫出來了
