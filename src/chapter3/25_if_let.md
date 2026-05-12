# `if let`

## 本集目標

學會用 `if let` 來簡化「只關心一種模式」的 `match`。

## 概念說明

有時候你只關心 `enum` 的某一個 variant，其他的都不在意。用 `match` 寫的話，必須處理所有情況，就算你只想處理一個：

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn main() {
#     let c = Color::Blue;
    match c {
        Color::Red => println!("是紅色！"),
        _ => {}  // 其他情況什麼都不做
    }
# }
```

那個 `_ => {}` 看起來很多餘。Rust 提供了 `if let` 語法來簡化這種情況：

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn main() {
#     let c = Color::Blue;
    if let Color::Red = c {
        println!("是紅色！");
    }
# }
```

`if let 模式 = 值` 的意思是「如果這個值符合這個模式，就執行大括號裡的程式碼」。

你也可以加上 `else` 處理不符合的情況：

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn main() {
#     let c = Color::Blue;
    if let Color::Red = c {
        println!("是紅色！");
    } else {
        println!("不是紅色");
    }
# }
```

注意：`if let` 裡的 `=` 是一個等號，不是兩個。這不是在做比較，而是在做「模式比對」。

## 範例程式碼

```rust
enum Color {
    Red,
    Green,
    Blue,
}

enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

fn main() {
    let c = Color::Red;

    // 用 if let 檢查是不是 Red
    if let Color::Red = c {
        println!("是紅色！");
    }

    // 搭配 else
    let c2 = Color::Blue;

    if let Color::Red = c2 {
        println!("是紅色！");
    } else {
        println!("不是紅色");
    }

    // if let 也可以取出 variant 裡的資料
    let s = Shape::Circle(5.0);

    if let Shape::Circle(r) = s {
        println!("是圓形！半徑 = {}", r);
        let area = r * r * 3.14159;
        println!("面積大約 {}", area);
    }

    // 如果不是 Circle 就不會執行
    let s2 = Shape::Rectangle(10, 20);

    if let Shape::Circle(r) = s2 {
        println!("這行不會被執行，因為 s2 是 Rectangle");
        println!("半徑 {}", r);
    } else {
        println!("不是圓形");
    }
}
```

## `if let` guard

`if let` 也可以用在 `match` 的 guard 位置（第 20 集學的 `match` guard）。語法是 `模式 if let 模式2 = 表達式 =>`：

```rust
enum Wrapper {
    Value(i32),
    Empty,
}

fn lookup(key: i32) -> Wrapper {
    if key > 0 { Wrapper::Value(key * 10) } else { Wrapper::Empty }
}

fn main() {
    let items = [1, -2, 3];

    for item in items {
        match item {
            x if let Wrapper::Value(v) = lookup(x) => {
                println!("{} 查到了：{}", x, v);
            }
            x => println!("{} 查不到", x),
        }
    }
}
```

`x if let Wrapper::Value(v) = lookup(x)` 的意思是：先把值綁定到 `x`，然後用 `lookup(x)` 的結果再做一次模式比對——只有結果是 `Wrapper::Value(v)` 的時候這個分支才成立。

這個例子其實用一般的 `if let` 也寫得出來。但當程式邏輯更複雜——例如外層的 `match` 已經在比對其他模式，而你又需要在某個分支裡對另一個值做模式比對——`if let` guard 有時可以讓程式碼更好讀，不用在 `match` 的分支裡面再套一層 `if let`。

## 重點整理

- `if let 模式 = 值 { ... }` 是 `match` 只有一個分支時的簡寫
- 只在值符合模式時執行大括號裡的程式碼
- 可以加 `else` 處理不符合的情況
- 可以在模式裡取出資料，像 `if let Shape::Circle(r) = s`
- 比起寫 `match` + `_ => {}`，`if let` 更簡潔
- `if let` 也能用在 `match` guard：`模式 if let 模式2 = 表達式 => ...`
