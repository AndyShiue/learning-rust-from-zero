# `let else`

## 本集目標

學會用 `let...else...` 在 pattern 不匹配時提前離開，寫出更扁平的程式碼。

## 概念說明

### `if let` 的反面

上一集學了 `while let`，再上一集學了 `if let`——「如果匹配成功就做某件事」。但有時候你想要的是反過來：「如果匹配**失敗**就提前離開，成功的話繼續往下走。」

假設我們有這個 `enum`：

```rust,noplayground
enum Color {
    Red,
    Green,
    Blue,
    Custom(i32, i32, i32),
}
#
# fn main() {}
```

用 `if let` 寫的話：

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
#     Custom(i32, i32, i32),
# }
#
fn describe(color: Color) {
    if let Color::Custom(r, g, b) = color {
        println!("自訂顏色：{} {} {}", r, g, b);
    } else {
        println!("不是自訂顏色，結束");
        return;
    }
    // 這裡想用 r, g, b⋯⋯但它們已經不在作用域了！
}
#
# fn main() {}
```

`r`、`g`、`b` 只活在 `if let` 的 `{}` 裡面，後面的程式碼用不到。

### `let...else...` 語法

`let...else...` 讓綁定的變數活在後面的程式碼裡，而不是只活在 `{}` 裡面：

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
#     Custom(i32, i32, i32),
# }
#
fn describe(color: Color) {
    let Color::Custom(r, g, b) = color else {
        println!("不是自訂顏色，結束");
        return;
    };
    // r, g, b 在這裡可以直接用！
    println!("紅：{}，綠：{}，藍：{}", r, g, b);
}
#
# fn main() {}
```

意思是：

1. 嘗試用 pattern 匹配 `color`
2. 如果成功，`r`、`g`、`b` 被綁定，程式繼續往下
3. 如果失敗，執行 `else` 裡面的程式碼

### `else` 裡面必須離開

`else` 區塊不能只是「做點事然後繼續」——它必須讓程式離開當前的流程。合法的寫法包括：

- `return` —— 離開函數
- `break` —— 離開迴圈
- `continue` —— 跳到迴圈下一輪

為什麼？因為如果 pattern 不匹配，變數就沒有被綁定。如果 `else` 之後程式繼續往下跑，那些變數就是未定義的——Rust 不允許這種事。

### 和 `if let` 的比較

- `if let`：匹配成功才進入 `{}` 區塊，綁定的變數只活在裡面
- `let...else...`：匹配失敗就離開，綁定的變數活在後面所有的程式碼裡

`let...else...` 讓程式碼更扁平——不用多縮排一層。

## 範例程式碼

```rust
enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

fn print_circle_info(shape: Shape) {
    let Shape::Circle(radius) = shape else {
        println!("不是圓形，跳過");
        return;
    };
    // radius 在這裡可以直接用
    println!("圓形，半徑 = {}", radius);
}

fn main() {
    print_circle_info(Shape::Circle(3.14));
    print_circle_info(Shape::Rectangle(10, 20));

    // 在迴圈裡搭配 continue
    let shapes = [
        Shape::Rectangle(3, 4),
        Shape::Circle(1.0),
        Shape::Rectangle(5, 6),
        Shape::Circle(2.5),
    ];

    println!("\n只印圓形：");
    for shape in shapes {
        let Shape::Circle(r) = shape else {
            continue;  // 不是圓形，跳過這一輪
        };
        println!("半徑：{}", r);
    }
}
```

## 重點整理

- `let pattern = expr else { return / break / continue };` 在匹配失敗時提前離開
- `else` 裡面必須離開當前流程（`return` / `break` / `continue`）
- 匹配成功的話，綁定的變數在後續程式碼還能使用
- 比 `if let` 更適合「失敗就離開，成功繼續」的場景——程式碼更扁平
