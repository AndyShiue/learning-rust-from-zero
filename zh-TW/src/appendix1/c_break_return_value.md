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

### 為什麼 `while` 和 `for` 不能這樣做？

你可能會問：`while` 和 `for` 為什麼不行？

原因是：`while` 和 `for` 可以在條件變成 false 或迭代器走完時正常結束，完全不必執行到 `break`。在這種情況下，迴圈產生的是 `()`，而不是 `break` 帶出的值。

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

## 搭配標籤使用 `break` 回傳值

像 `'search:` 這樣的標籤可以放在迴圈（`loop`、`while` 或 `for`）或一般的 block 表達式 `{ ... }` 前面。後者會形成 labeled block。這裡的 `'search` 是標籤，不是 lifetime。

`break 'label value` 會跳出有標籤的 `loop` 或 block，並讓該表達式產生 `value`。跳出最內層的 `loop` 時，可以省略標籤（寫成 `break value`）；在 labeled block 中則一定要寫出標籤。

```rust,editable
fn main() {
    let from_loop = 'search: loop {
        loop {
            break 'search 7;
        }
    };

    let from_block = 'answer: {
        let n = 7;
        if n > 5 {
            break 'answer n * 2;
        }
        0
    };

    println!("來自 loop：{}", from_loop);
    println!("來自 block：{}", from_block);
}
```

這裡的 `break 'search 7` 會直接跳出兩層 `loop`，讓有 `'search` 標籤的外層 `loop` 產生 `7`。`break 'answer n * 2` 會讓 labeled block 產生 `14`。

## 重點整理

- `let x = loop { break value; };` 讓 `loop` 成為表達式，回傳 `break` 帶出的值。
- `while` 和 `for` 不能用 `break` 回傳值，因為它們可以不經過 `break` 就正常結束。
- `break 'label value` 可以從有標籤的 `loop` 或 labeled block 回傳值；labeled block 一定要寫出標籤。
- 常見用途是在迴圈中搜尋，找到後用 `break` 帶出結果。
