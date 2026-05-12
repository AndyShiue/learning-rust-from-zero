# `if` 當表達式

## 本集目標

學會把 `if` 當成一個「表達式」，直接用它來給變數賦值。

## 正文

這是第一章的最後一集！今天要介紹 Rust 一個很酷的特性——`if` 不只是判斷用的，它還可以**回傳值**。

### 先看一般的寫法

假設你要根據條件給變數不同的值，你可能會這樣寫：

```rust
fn main() {
    let condition = true;
    let x;

    if condition {
        x = 1;
    } else {
        x = 2;
    }

    println!("{}", x);
}
```

這樣沒問題，但 Rust 有一個更簡潔的寫法。

### if 當表達式

```rust
fn main() {
    let condition = true;
    let x = if condition { 1 } else { 2 };

    println!("{}", x);
}
```

跑起來印出 `1`。

看到了嗎？`if condition { 1 } else { 2 }` 整個放在 `let x =` 的右邊，直接把結果賦值給 `x`。

如果 `condition` 是 `true`，`x` 就是 1；如果是 `false`，`x` 就是 2。

### 注意：大括號裡面不加分號

```rust
# fn main() {
#     let condition = true;
    let x = if condition { 1 } else { 2 };
    //                      ^          ^
    //                   沒有分號     沒有分號
# }
```

這些值（1 和 2）後面**沒有分號**。在 Rust 裡，不加分號的值就是「回傳值」。這是 Rust 的表達式語法，之後學函數的時候會更詳細地講。

### 兩邊型別要一致！

```rust,compile_fail
fn main() {
    let condition = true;
    let x = if condition { 1 } else { "hello" }; // ❌ 錯誤！
}
```

這會報錯，因為 `1` 是整數，`"hello"` 是字串。Rust 不允許 `x` 有時候是數字、有時候是字串——它需要一個確定的型別。

兩邊的大括號裡，值的型別**必須相同**：

```rust,compile_fail
# fn main() {
#     let condition = true;
#
    // ✅ 兩邊都是整數
    let x = if condition { 1 } else { 2 };

    // ✅ 兩邊都是字串
    let msg = if condition { "好" } else { "壞" };

    // ❌ 一邊整數一邊字串
    let x = if condition { 1 } else { "hello" };
# }
```

### 這有什麼好處？

1. `x` 不需要是 `mut`
2. 程式碼更簡潔
3. Rust 的設計哲學：很多東西都可以是「表達式」，都能回傳值

## 重點整理

- `if` 在 Rust 裡是**表達式**，可以直接回傳值：`let x = if condition { 1 } else { 2 };`
- 大括號裡作為回傳值的部分**不加分號**
- `if` 和 `else` 兩邊的型別必須一致

恭喜你完成了第一章！🎉 你已經學會了 Rust 的基本語法，包括變數、運算、條件判斷、迴圈、型別等等。下一章我們會開始學更多 Rust 的特色功能！
