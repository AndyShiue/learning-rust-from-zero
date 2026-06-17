# associated function

## 本集目標

學會用 `impl` 為 `struct` 或 `enum` 定義 associated function（關聯函數），以及用 `::` 呼叫。

## 概念說明

到目前為止，我們的函數都是「獨立的」——定義在最外層，和任何型別沒有關係。但很多時候，某些函數和特定的型別密切相關。比如說，「建立一個新的 `Point`」這件事，和 `Point` 這個型別有直接關係。

Rust 用 `impl` 區塊讓你把函數「附加」到型別上：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn new(x: i32, y: i32) -> Point {
        Point { x, y }
    }
}
#
# fn main() {}
```

這樣定義的函數叫做 **associated function**（關聯函數），因為它和 `Point` 這個型別「關聯」在一起。呼叫的時候用 `::`：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# impl Point {
#     fn new(x: i32, y: i32) -> Point {
#         Point { x, y }
#     }
# }
#
# fn main() {
    let p = Point::new(3, 7);
# }
```

`Point::new` 看起來是不是有點眼熟？之前用 `enum` 的時候也是用 `::` 啊！像 `Color::Red`。概念是一樣的——`::` 可以表示「某個型別底下的東西」。

associated function 最常見的用途就是 `new`——作為「建構函數」來建立型別的值。

## 範例程式碼

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    // associated function：建立一個新的 Point
    fn new(x: i32, y: i32) -> Point {
        Point { x, y }
    }

    // 也可以定義其他 associated function
    fn origin() -> Point {
        Point { x: 0, y: 0 }
    }
}

// enum 也可以有 impl！
enum Color {
    Red,
    Green,
    Blue,
}

impl Color {
    fn from_number(n: i32) -> Color {
        match n {
            0 => Color::Red,
            1 => Color::Green,
            _ => Color::Blue,
        }
    }
}

fn main() {
    // 用 :: 呼叫 associated function
    let p1 = Point::new(3, 7);
    println!("p1 = ({}, {})", p1.x, p1.y);

    let p2 = Point::origin();
    println!("p2 = ({}, {})", p2.x, p2.y);

    // enum 的 associated function
    let c = Color::from_number(1);
    match c {
        Color::Red => println!("紅"),
        Color::Green => println!("綠"),
        Color::Blue => println!("藍"),
    }
}
```

## 重點整理

- `impl 型別名 { ... }` 為型別定義 associated function
- associated function 用 `型別名::函數名()` 呼叫
- 最常見的用途是 `new` 函數，作為建構函數
- `struct` 和 `enum` 都可以有 `impl` 區塊
