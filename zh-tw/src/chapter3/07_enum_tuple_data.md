# `enum` 攜帶 tuple variant

## 本集目標

學會讓 `enum` 的 variant 攜帶額外的資料，像 tuple 一樣。

## 概念說明

之前學的 C-style `enum`，每個 variant 就只是一個名字，不帶任何資料。但很多時候，不同的選項需要攜帶不同的資料。

比如說，「形狀」可以是圓形或長方形。圓形需要一個半徑，長方形需要寬和高——它們需要的資料不一樣。在 Rust 裡，你可以讓每個 variant 攜帶資料：

```rust,noplayground
enum Shape {
    Circle(f64),         // 攜帶一個 f64（半徑）
    Rectangle(i32, i32), // 攜帶兩個 i32（寬、高）
}
#
# fn main() {}
```

這種寫法像是在 variant 名字後面加上 tuple 的欄位，所以叫做 **tuple variant**。

建立值的方式就像呼叫函數一樣，把資料放在括號裡：

```rust,noplayground
# enum Shape {
#     Circle(f64),
#     Rectangle(i32, i32),
# }
#
# fn main() {
    let s = Shape::Circle(3.14);
    let r = Shape::Rectangle(10, 20);
# }
```

注意：現在我們知道怎麼建立帶資料的 `enum` 了，但要「取出」裡面的資料，需要用 `match`——這個我們第 9 集會學。

## 範例程式碼

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

enum Message {
    Quit,           // 不帶資料（就像 C-style）
    Echo(i32),      // 帶一個 i32
    Move(i32, i32), // 帶兩個 i32
}

fn main() {
    let s1 = Shape::Circle(5.0);
    let s2 = Shape::Rectangle(10, 20);

    let m1 = Message::Quit;
    let m2 = Message::Echo(42);
    let m3 = Message::Move(3, 7);

    // 目前先建立值就好
    // 第 9 集會學怎麼用 match 取出裡面的資料
    println!("形狀和訊息都建立好了！");

    // 同一個 enum 裡，不同 variant 可以帶不同數量、不同型別的資料
    // 甚至有些 variant 不帶資料也完全沒問題（像 Message::Quit）
}
```

## 重點整理

- `enum` variant 可以攜帶資料：`Circle(f64)` 表示 Circle 帶一個 `f64`
- 建立帶資料的 variant：`Shape::Circle(5.0)`
- 同一個 `enum` 裡，不同 variant 可以帶不同的資料
- 有些 variant 可以不帶資料，有些帶一個，有些帶多個——很靈活
- 要取出 variant 裡的資料，需要用 `match`（第 9 集會學）
