# block 表達式

## 本集目標

學會用大括號 `{}` 建立 block 表達式，在裡面執行多行程式碼後回傳一個值。

## 概念說明

在 Rust 裡，一對大括號 `{}` 不只是作用域，它本身也是一個**表達式**，可以回傳值。規則很簡單：block 裡面最後一行如果不加分號，那一行的值就是整個 block 的回傳值。

```rust,editable
fn main() {
    let x = {
        let y = 5;
        y + 1 // 沒有分號 → 這就是 block 的回傳值
    };
    // x 現在是 6
}
```

這個概念在 `match` 裡特別有用。之前的 `match` 分支都只有一行，但如果你想在某個分支裡做多件事，就可以用 block：

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn describe_color() -> &'static str {
#     let c = Color::Red;
    match c {
        Color::Red => {
            println!("是紅色！");
            "red"
        }
        // ...
#         _ => "",
    }
# }
#
# fn main() {}
```

block 裡可以宣告變數、做計算，最後一行不加分號就是回傳值。

注意：如果 `match` 的分支用了 block `{}`，後面的逗號可以省略。因為 `}` 本身就是明確的結束標記，Rust 不需要逗號來分隔。但如果分支只有一行（沒有用 block），後面的逗號就不能省。

```rust,noplayground
# enum Season {
#     Spring,
#     Summer,
#     Autumn,
#     Winter,
# }
#
# fn describe_season() -> &'static str {
#     let s = Season::Summer;
    match s {
        Season::Summer => {
            println!("好熱啊！");
            "炎熱的夏天"
        }                             // ← 沒有逗號，OK
        Season::Autumn => "涼爽的秋天", // ← 一行的分支，要逗號
        // ...
#         _ => "",
    }
# }
#
# fn main() {}
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
    // block 表達式的基本用法
    let result = {
        let a = 10;
        let b = 20;
        a + b // 最後一行不加分號 → 回傳值
    };
    println!("result = {}", result);

    // 在 match 分支裡使用 block
    let s = Season::Summer;

    let description = match s {
        Season::Spring => {
            let temp = 22;
            println!("春暖花開");
            if temp > 20 {
                "溫暖的春天"
            } else {
                "還有點涼的春天"
            }
        }
        Season::Summer => {
            println!("好熱啊！");
            "炎熱的夏天"
        }
        Season::Autumn => "涼爽的秋天",
        Season::Winter => "寒冷的冬天",
    };
    println!("{}", description);
}
```

## 重點整理

- `{}` block 本身是一個表達式，最後一行不加分號就是回傳值
- `let x = { ... };` 可以在 block 裡做多行計算後把結果賦值給 x
- `match` 分支可以用 `=> { ... }` 來執行多行程式碼，而且 block 後面不用加逗號
- block 裡宣告的變數只在 block 內有效（作用域）
- block 表達式在 Rust 裡非常常見，是很重要的基礎概念
