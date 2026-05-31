# 巢狀 pattern matching

## 本集目標

學會在 `match` 裡面再解構更深層的結構——巢狀的模式匹配。

## 概念說明

到目前為止，我們的 `match` 都只解構一層。但如果資料結構是巢狀的呢？比如一個 tuple 裡面包著 `enum`，或是一個 `enum` 裡面包著另一個 `struct`？

Rust 的 pattern matching 可以一次解構好幾層，就像剝洋蔥一樣，一層一層往裡面拿。

比如說，你有一個 tuple `(i32, Shape)`，你可以在 `match` 裡同時解構 tuple 和裡面的 `Shape`：

```rust,editable
# enum Shape {
#     Circle(f64),
#     Rectangle(i32, i32),
# }
#
# fn main() {
    let data = (666, Shape::Circle(42.0));
    match data {
        (id, Shape::Circle(r)) => println!("#{} 是圓形，半徑 {}", id, r),
        (id, Shape::Rectangle(w, h)) => println!("#{} 是長方形 {}x{}", id, w, h),
    }
# }
```

一個模式裡，外層解構 tuple 取出 `id` 和 `Shape`，內層再解構 `Shape` 取出裡面的資料。全部在一行完成！

## 範例程式碼

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

struct Point {
    x: i32,
    y: i32,
}

fn main() {
    // 範例一：tuple 裡面包 enum
    let data = (1, Shape::Circle(5.0));

    match data {
        (id, Shape::Circle(r)) => {
            println!("形狀 #{} 是圓形，半徑 {}", id, r);
        }
        (id, Shape::Rectangle(w, h)) => {
            println!("形狀 #{} 是長方形 {}x{}", id, w, h);
        }
    }

    // 範例二：tuple 裡面包 struct
    let item = ("原點", Point { x: 0, y: 0 });

    match item {
        (name, Point { x, y }) => {
            println!("{}：座標 ({}, {})", name, x, y);
        }
    }
}
```

## 重點整理

- Rust 的 pattern matching 可以解構多層巢狀結構
- 可以在一個模式裡同時解構 tuple + `enum`、tuple + `struct` 等
- 巢狀解構讓你不需要寫多個 `match`，一次就能把所有資料取出來
- 寫法就是把模式一層一層嵌進去，和資料的結構對應
