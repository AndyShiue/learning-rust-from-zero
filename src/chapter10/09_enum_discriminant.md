# enum discriminant

## 本集目標
了解 enum variant 背後的整數值，以及如何自訂它。

## 概念說明

### 每個 variant 都有一個整數值

第三章學了 C-style enum。每個 variant 背後都有一個整數，叫做 **discriminant**。Rust 用它來區分目前是哪個 variant。

```rust,no_run
enum Color {
    Red,   // 0
    Green, // 1
    Blue,  // 2
}
#
# fn main() {}
```

預設從 0 開始，每個 variant 遞增 1。

### 用 as 取得 discriminant

上一集學了 `as`。C-style enum 可以用 `as` 轉成整數看到它的 discriminant：

```rust
# enum Color {
#     Red,   // 0
#     Green, // 1
#     Blue,  // 2
# }
#
fn main() {
    println!("{}", Color::Red as i32);   // 0
    println!("{}", Color::Green as i32); // 1
    println!("{}", Color::Blue as i32);  // 2
}
```

### 自訂 discriminant

手動指定值：

```rust
enum HttpStatus {
    Ok = 200,
    NotFound = 404,
    InternalError = 500,
}

fn main() {
    println!("{}", HttpStatus::NotFound as i32); // 404
}
```

沒指定的 variant 從前一個 +1：

```rust,no_run
enum Level {
    Low = 1,
    Medium,    // 2
    High,      // 3
    Critical = 10,
    Emergency, // 11
}
```

### #[repr] 控制底層型別

預設的底層型別由編譯器決定。用 `#[repr]` 明確指定：

```rust,no_run
#[repr(u8)]
enum Direction {
    North, // 0_u8
    South, // 1_u8
    East,  // 2_u8
    West,  // 3_u8
}
#
# fn main() {}
```

常見的選擇有 `u8`、`u16`、`u32`、`i32` 等。

### 帶資料的 enum 也有 discriminant

帶資料的 enum 內部也有 discriminant 來區分是哪個 variant，但你**不能用 `as` 取得它**：

```rust,compile_fail
enum Shape {
    Circle(f64),
    Rectangle(f64, f64),
}

fn main() {
    Shape::Circle(3.0) as i32 // 編譯錯誤！
}
```

## 範例程式碼

```rust
#[repr(u8)]
enum Command {
    Quit = 0,
    Move = 1,
    Write = 2,
    ChangeColor = 3,
}

enum Season {
    Spring = 1,
    Summer, // 2
    Autumn, // 3
    Winter, // 4
}

fn main() {
    println!("Quit = {}", Command::Quit as u8);
    println!("Write = {}", Command::Write as u8);

    println!("Spring = {}", Season::Spring as i32);
    println!("Winter = {}", Season::Winter as i32);

    // 用在 match 裡
    let cmd = Command::Move;
    match cmd {
        Command::Quit => println!("退出"),
        Command::Move => println!("移動"),
        Command::Write => println!("寫入"),
        Command::ChangeColor => println!("改顏色"),
    }
}
```

## 重點整理
- 每個 enum variant 都有一個整數 discriminant，預設從 0 遞增
- C-style enum 可以用 `as` 轉成整數看到 discriminant
- 手動指定值用 `= 數字`，沒指定的從前一個 +1
- `#[repr(u8)]` 等控制底層型別
- 帶資料的 enum 也有 discriminant，但不能用 `as` 取得
