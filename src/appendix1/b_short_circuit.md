# `&&` 和 `||` 的短路行為

## 本集目標
理解 `&&` 和 `||` 不一定會執行兩邊——有時候執行完左邊就知道結果了。

## 概念說明

第一章學了 `&&`（而且）和 `||`（或者）。但有一個細節當時沒提：它們有**短路行為**（short-circuit evaluation）。

### `&&` 的短路

`&&` 的左邊如果是 `false`，右邊就不會被執行——因為不管右邊是什麼，整個結果一定是 `false`：

```rust
fn main() {
    let x = 0;
    // 左邊 x != 0 是 false，所以右邊 10 / x 不會被執行
    // 如果右邊被執行了，10 / 0 會 panic！
    if x != 0 && 10 / x > 2 {
        println!("大於 2");
    }
}
```

### `||` 的短路

`||` 的左邊如果是 `true`，右邊就不會被執行——因為不管右邊是什麼，整個結果一定是 `true`：

```rust
fn check() -> bool {
    println!("check 被呼叫了");
    true
}

fn main() {
    // 左邊已經是 true，check() 不會被呼叫
    if true || check() {
        println!("結果是 true");
    }
    // 只會印出 "結果是 true"，不會印出 "check 被呼叫了"
}
```

### 為什麼要知道這個

大部分時候你不需要特別在意短路行為。但當右邊的表達式有**副作用**（例如印東西、修改變數）或**可能出錯**（例如除以零）的時候，知道右邊不一定會執行就很重要了。

## 範例程式碼

```rust
fn is_even(n: i32) -> bool {
    println!("  檢查 {} 是不是偶數", n);
    n % 2 == 0
}

fn is_positive(n: i32) -> bool {
    println!("  檢查 {} 是不是正數", n);
    n > 0
}

fn main() {
    // &&：左邊 false 就不看右邊
    println!("--- && 短路 ---");
    let n = -3;
    if is_even(n) && is_positive(n) {
        println!("{} 是正偶數", n);
    } else {
        println!("{} 不是正偶數", n);
    }
    // is_even(-3) 回傳 false，is_positive 不會被呼叫

    // ||：左邊 true 就不看右邊
    println!("\n--- || 短路 ---");
    let n = 4;
    if is_even(n) || is_positive(n) {
        println!("{} 是偶數或正數", n);
    }
    // is_even(4) 回傳 true，is_positive 不會被呼叫

    // 實用場景：避免除以零
    println!("\n--- 實用場景 ---");
    let divisor = 0;
    if divisor != 0 && 100 / divisor > 10 {
        println!("商大於 10");
    } else {
        println!("除數是零或商不大於 10");
    }
}
```

## 重點整理
- `&&`：左邊是 `false` 就不看右邊，整個結果直接是 `false`
- `||`：左邊是 `true` 就不看右邊，整個結果直接是 `true`
- 這叫短路行為（short-circuit evaluation）
- 當右邊有副作用或可能出錯時，短路行為特別重要