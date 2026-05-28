# field shorthand

## 本集目標

學會用 field shorthand 簡化 `struct` 的建立和模式匹配。

## 概念說明

上一集在 match 裡寫了 `radius: r`，意思是把 `radius` 欄位取出來叫做 `r`。但如果你想讓變數名就叫做 `radius` 呢？按照之前的寫法要寫 `radius: radius`——欄位名和變數名重複了，有點囉嗦。

Rust 提供了一個簡寫：如果變數名和欄位名一樣，可以只寫一次：

```rust,noplayground
# enum Shape {
#     Circle { radius: f64 },
#     Rectangle { width: i32, height: i32 },
# }
#
# fn main() {
#     let radius = 42.0;
    // 完整寫法
    Shape::Circle { radius: radius };
    // 簡寫（field shorthand）
    Shape::Circle { radius };
# }
```

這個簡寫不只在 `match` 裡可以用，**建立 `struct` 的時候也可以用**：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
    let x = 3;
    let y = 7;
    // 完整寫法
    let p = Point { x: x, y: y };
    // 簡寫
    let p = Point { x, y };
# }
```

只要變數名和欄位名一樣，就能省略 `: 變數名` 的部分。

## 範例程式碼

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

enum Shape {
    Circle { radius: f64 },
    Rectangle { width: i32, height: i32 },
}

fn main() {
    // 建立 struct 時使用 field shorthand
    let x = 5;
    let y = 10;
    let p = Point { x, y }; // 等同於 Point { x: x, y: y }
    println!("點的座標：({}, {})", p.x, p.y);

    // 建立 enum struct variant 時也可以用
    let radius = 3.5;
    let s = Shape::Circle { radius }; // 等同於 Shape::Circle { radius: radius }

    // match 裡也可以用 field shorthand
    match s {
        Shape::Circle { radius } => {
            println!("圓形，半徑 = {}", radius);
        }
        Shape::Rectangle { width, height } => {
            println!("長方形 {}x{}", width, height);
        }
    }
}
```

## 重點整理

- 當變數名和欄位名相同時，可以只寫一次：`Point { x, y }` 等同於 `Point { x: x, y: y }`
- 這個簡寫叫做 **field shorthand**
- 建立 `struct` / `enum` variant 時可以用
- `match` 模式裡也可以用
- 這是一個很常見的寫法，實際寫 Rust 時常常用簡寫
