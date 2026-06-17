# 多個值 `|`

## 本集目標

學會在 `match` 的同一個分支裡比對多個可能的值。

## 概念說明

有時候你想讓好幾個值都執行同樣的程式碼。比如說，星期六和星期天都是假日，不需要分開寫兩個分支。

Rust 用 `|`（直線符號）來表示「或」：

```rust,editable
fn main() {
    let day = 1;
    match day {
        6 | 7 => println!("假日"),
        _ => println!("工作日"),
    }
}
```

`6 | 7` 的意思是「6 或 7」。你可以用 `|` 串接任意多個值：

```rust,editable
fn main() {
    let n = 3;
    match n {
        1 | 2 | 3 => println!("前三名"),
        _ => println!("其他"),
    }
}
```

也可以搭配 `enum` 使用：

```rust,editable
enum Color {
    Red,
    Green,
    Blue,
}

fn main() {
    let color = Color::Red;
    match color {
        Color::Red | Color::Blue => println!("冷暖色"),
        Color::Green => println!("綠色"),
    }
}
```

## 範例程式碼

```rust,editable
enum Season {
    Spring,
    Summer,
    Autumn,
    Winter,
}

fn main() {
    // 數字的多值比對
    let month = 7;

    match month {
        3 | 4 | 5 => println!("春天"),
        6 | 7 | 8 => println!("夏天"),
        9 | 10 | 11 => println!("秋天"),
        12 | 1 | 2 => println!("冬天"),
        _ => println!("無效月份"),
    }

    // enum 的多值比對
    let s = Season::Autumn;

    let is_hot = match s {
        Season::Summer => true,
        Season::Spring | Season::Autumn | Season::Winter => false,
    };
    println!("天氣熱嗎？{}", is_hot);

    // 搭配 range pattern 和 |
    let ch = '5';

    match ch {
        'a'..='z' | 'A'..='Z' => println!("字母"),
        '0'..='9' => println!("數字"),
        ' ' | '\t' | '\n' => println!("空白字元"),
        _ => println!("其他"),
    }
}
```

## 重點整理

- `|` 在 `match` 裡表示「或」，讓同一個分支比對多個值
- 語法：`模式1 | 模式2 | 模式3 => ...`
- 可以搭配 `enum` variant 使用
- 也可以搭配 range pattern 使用：`'a'..='z' | 'A'..='Z'`
- 當多個值要做相同處理時，用 `|` 比寫多個分支更簡潔
