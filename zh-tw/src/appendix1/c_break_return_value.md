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

原因是：`while` 和 `for` 可以在條件變成 false 或 iterator 走完時正常結束，完全不必執行到 `break`。在這種情況下，迴圈產生的是 `()`，而不是 `break` 帶出的值。

但 `loop` 沒有讓它正常結束的條件。如果一個 `loop` 會結束，就一定是執行了 `break`；如果沒有執行到 `break`，它就會一直跑下去，不會產生結果。正因如此，`break` 帶出的值可以成為整個 `loop` 的值。

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

- `let x = loop { break value; };` 讓 `loop` 成為表達式，回傳 `break` 帶出的值。
- 只有 `loop` 能這樣做；`while` 和 `for` 可以不經過 `break` 就正常結束。
- 常見用途是在迴圈中搜尋，找到後用 `break` 帶出結果。
