# `break` 回傳值

## 本集目標

學會用 `break` 從 `loop` 迴圈中回傳值，把迴圈當作表達式使用。

> 本集是**第 1 章**的補充。

## 概念說明

還記得 Rust 裡「幾乎所有東西都是表達式」嗎？`loop` 迴圈也不例外——你可以透過 `break` 帶一個值出來，讓整個 `loop` 變成一個表達式。

### 基本語法

```rust,noplayground
# fn main() {
    let result = loop {
        break 42;
    };
# }
```

這裡 `loop { break 42; }` 的型別是 `i32`，因為 `break` 帶出了 `42`。

### 為什麼只有 `loop` 能這樣做？

你可能會問：`while` 和 `for` 為什麼不行？

原因是：`while` 和 `for` 有可能**一次都不執行**。如果迴圈體從未執行，那 `break` 帶出的值根本不存在，編譯器就無法保證一定有回傳值。

但 `loop` 不同——它是無條件迴圈，**一定會進入迴圈體**，所以編譯器可以確定 `break` 一定會被執行到（否則就是無窮迴圈）。這就是為什麼只有 `loop` 能當表達式回傳值。

### 實際應用場景

最常見的用法是「在迴圈裡搜尋某個東西，找到就帶出來」：

```rust,ignore
# fn main() {
    let found = loop {
        // 做一些搜尋...
        if condition {
            break some_value;
        }
    };
# }
```

這比先宣告一個變數、在迴圈裡賦值、再 `break` 出來要簡潔得多。

## 範例程式碼

```rust,editable
fn main() {
    // 基本用法：loop 回傳值
    let lucky_number = loop {
        break 7;
    };
    println!("幸運數字：{}", lucky_number);

    // 實用範例：找到第一個大於 100 的平方數
    let mut n = 1;
    let result = loop {
        let square = n * n;
        if square > 100 {
            break square;
        }
        n += 1;
    };
    println!("第一個大於 100 的平方數：{}", result);
    println!("它是 {} 的平方", n);
}
```

## 重點整理

- `let x = loop { break value; };` 讓 `loop` 成為表達式，回傳 `break` 帶出的值
- 只有 `loop` 能這樣做，`while` 和 `for` 不行——因為它們可能一次都不執行
- 常見用途是在迴圈中搜尋，找到後用 `break` 帶出結果
