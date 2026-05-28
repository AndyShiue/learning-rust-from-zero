# `enum` 攜帶 `struct` variant

## 本集目標

學會讓 `enum` 的 variant 用類似 `struct` 的方式攜帶有名字的欄位。

## 概念說明

上一集學了 tuple variant，欄位沒有名字，用位置來區分。但如果一個 variant 攜帶的資料比較多，沒有名字就很容易搞混。

Rust 允許你用類似 named-field `struct` 的寫法，讓 variant 的每個欄位都有名字：

```rust,noplayground
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: i32, height: i32 },
}
#
# fn main() {}
```

建立值的時候就像建立 `struct` 一樣：

```rust,noplayground
# enum Shape {
#     Circle { radius: f64 },
#     Rectangle { width: i32, height: i32 },
# }
#
# fn main() {
    let s = Shape::Circle { radius: 5.0 };
    let r = Shape::Rectangle { width: 10, height: 20 };
# }
```

同一個 `enum` 裡，有些 variant 可以用 tuple 形式，有些可以用 `struct` 形式，甚至有些不帶資料，完全可以混搭。

## 範例程式碼

```rust,editable
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: i32, height: i32 },
    Dot, // 不帶資料的 variant 也可以混在一起
}

fn main() {
    let s1 = Shape::Circle { radius: 5.0 };
    let s2 = Shape::Rectangle { width: 10, height: 20 };
    let s3 = Shape::Dot;

    // 目前還不能直接取出裡面的欄位
    // 第 10 集會學怎麼用 match 取出 struct variant 的資料
    println!("三種形狀都建立好了！");

    // 一個更生活化的例子
    let event = Event::Click { x: 100, y: 200 };
    println!("事件已建立！");
}

enum Event {
    Click { x: i32, y: i32 },
    KeyPress(char), // tuple 形式也可以混搭
    Quit,           // 不帶資料也行
}
```

## 重點整理

- variant 可以用 `struct` 形式攜帶有名字的欄位：`Circle { radius: f64 }`
- 建立值：`Shape::Circle { radius: 5.0 }`
- 同一個 enum 可以混搭：有的用 tuple 形式、有的用 `struct` 形式、有的不帶資料
- `struct` 形式的好處是欄位有名字，程式碼更容易讀懂
- 取出欄位資料需要用 `match`（第 10 集會學）
