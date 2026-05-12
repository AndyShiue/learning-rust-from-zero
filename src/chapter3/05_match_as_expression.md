# `match` 當表達式

## 本集目標

學會把 `match` 當作表達式使用，讓它回傳一個值。

## 概念說明

還記得第一章學過 `if` 可以當表達式嗎？

```rust
# fn main() {
#     let condition = true;
    let x = if condition { 1 } else { 2 };
# }
```

`match` 也可以！你可以把整個 `match` 放在 `let` 的右邊，讓每個分支回傳一個值：

```rust
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn main() {
#     let c = Color::Red;
    let msg = match c {
        Color::Red => "紅色",
        Color::Green => "綠色",
        Color::Blue => "藍色",
    };
# }
```

注意最後面有一個分號 `;`，因為整個 `let msg = match ... { ... };` 是一個 `let` 陳述式。

每個分支回傳的值的型別必須一致。如果第一個分支回傳 `&str`，其他分支也都要回傳 `&str`。

## 範例程式碼

```rust
enum Season {
    Spring,
    Summer,
    Autumn,
    Winter,
}

fn main() {
    let s = Season::Autumn;

    // match 當表達式，回傳 &str
    let name = match s {
        Season::Spring => "春天",
        Season::Summer => "夏天",
        Season::Autumn => "秋天",
        Season::Winter => "冬天",
    };
    println!("現在是{}", name);

    // match 當表達式，回傳 i32
    let temp = match s {
        Season::Spring => 22,
        Season::Summer => 35,
        Season::Autumn => 18,
        Season::Winter => 8,
    };
    println!("大約 {} 度", temp);
}
```

## 重點整理

- `match` 可以當表達式，整個 `match` 會回傳一個值
- 用法：`let x = match ... { ... };`（最後別忘了分號）
- 所有分支的回傳值型別必須一致
- 這和 `if` 表達式的概念相同——Rust 裡很多東西都可以是表達式
