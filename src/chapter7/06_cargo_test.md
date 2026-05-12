# `cargo test`

## 本集目標

學會用 `#[test]` 寫測試、用 `assert!` 系列巨集驗證結果、用 `cargo test` 跑測試。

## 概念說明

### 為什麼要寫測試？

程式碼寫完之後，你怎麼確定它是對的？手動跑一遍？那下次改了程式碼又要再跑一遍。**自動化測試**讓你寫一次，之後隨時都能驗證——一個指令就知道有沒有東西壞掉。

### 最簡單的測試

在函數上面加 `#[test]`，它就變成測試函數：

```rust,noplayground
#[test]
fn it_works() {
    assert_eq!(2 + 2, 4);
}
#
# fn main() {}
```

跑 `cargo test`，Rust 會自動找出所有標了 `#[test]` 的函數並執行它們。如果測試函數 panic 了，那個測試就算失敗。

### `assert` 系列巨集

- `assert!(condition)` — 如果 `condition` 是 `false`，程式 panic
- `assert_eq!(left, right)` — 如果 `left != right`，程式 panic
- `assert_ne!(left, right)` — 如果 `left == right`，程式 panic

`assert_eq!` 和 `assert_ne!` 在失敗時會印出兩個值的 `Debug` 格式，方便你看到底哪裡不對。

`assert!` 系列不只能用在測試裡——你也可以在普通程式碼裡用它們來檢查條件。但要注意：`assert!` 在 debug 和 release 模式下**都會執行**，即使是正式發布的程式，條件不成立一樣會 panic。如果你只想在開發階段檢查、正式發布時自動移除，可以用 `debug_assert!`、`debug_assert_eq!`、`debug_assert_ne!`——它們在 release 模式下會被編譯器完全忽略。

不過在**測試**裡面，直接用 `assert!` 系列就好——測試本來就不會用 release build 跑。

### 測試預期中的 panic

有時候你想反過來確認某段程式碼**會** panic——比如存取超出範圍的索引。這時候用 `#[should_panic]`：

```rust,noplayground
#[test]
#[should_panic]
fn test_out_of_bounds() {
    let v = vec![1, 2, 3];
    let _ = v[10]; // 這裡會 panic
}
#
# fn main() {}
```

如果函數 panic 了，測試通過；如果函數**沒有** panic，測試反而失敗。

你還可以用 `expected` 參數指定 panic 訊息必須包含什麼字串，確保 panic 的原因是對的：

```rust,noplayground
#[test]
#[should_panic(expected = "index out of bounds")]
fn test_out_of_bounds_message() {
    let v = vec![1, 2, 3];
    let _ = v[10];
}
#
# fn main() {}
```

### 測試 `mod` 的慣用結構

上一集學了 `use super::*;`——測試最常這樣用。慣例是在檔案底部加一個測試 `mod`：

```rust,noplayground
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn multiply(a: i32, b: i32) -> i32 {
    a * b
}
#
# fn main() {}

#[cfg(test)]
mod tests {
    use super::*; // 把父 mod 的所有東西引進來

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_multiply() {
        assert_eq!(multiply(3, 4), 12);
    }
}
```

幾個重點：

- `#[cfg(test)]` 告訴編譯器：這個 `mod` **只在跑測試時才編譯**。正式發布的程式不會包含測試程式碼
- `mod tests` 是一個普通的 `mod`，只是慣例叫 `tests`
- `use super::*;` 把父 `mod`（也就是這個檔案的最外層）的所有東西引進來，這樣測試裡就能直接呼叫 `add`、`multiply` 等函數

### `cargo test`

```bash
cargo test
```

這個指令會：

1. 編譯你的程式碼（包含測試）
2. 執行所有 `#[test]` 函數
3. 報告哪些通過、哪些失敗

### 測試私有函數

因為 `mod tests` 是你程式碼的子 `mod`，而同一個 `mod` 裡的東西互相看得到——所以測試可以直接測試**私有函數**，不需要 `pub`。

## 範例程式碼

```rust
fn is_even(n: i32) -> bool {
    n % 2 == 0
}

fn abs(n: i32) -> i32 {
    if n >= 0 { n } else { -n }
}

fn clamp(value: i32, min: i32, max: i32) -> i32 {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_even() {
        assert!(is_even(4));
        assert!(!is_even(7));
        assert!(is_even(0));
    }

    #[test]
    fn test_abs() {
        assert_eq!(abs(5), 5);
        assert_eq!(abs(-3), 3);
        assert_eq!(abs(0), 0);
    }

    #[test]
    fn test_clamp() {
        assert_eq!(clamp(5, 0, 10), 5);   // 在範圍內，不變
        assert_eq!(clamp(-3, 0, 10), 0);  // 低於下限，變成 min
        assert_eq!(clamp(15, 0, 10), 10); // 超過上限，變成 max
    }

    #[test]
    fn test_not_equal() {
        assert_ne!(abs(-5), -5); // abs(-5) 應該是 5，不是 -5
    }

    // 測試預期中的 panic
    #[test]
    #[should_panic(expected = "already borrowed")]
    fn test_refcell_double_borrow() {
        use std::cell::RefCell;
        let cell = RefCell::new(42);
        let _r = cell.borrow();
        let _w = cell.borrow_mut(); // 已經有不可變借用，這裡會 panic
    }
}

fn main() {
    // main 裡可以不用寫什麼——測試透過 cargo test 跑
    println!("用 cargo test 來跑測試！");
}
```

## 重點整理

- `#[test]` 標記測試函數，`cargo test` 自動找到並執行所有測試
- `assert!(condition)`、`assert_eq!(a, b)`、`assert_ne!(a, b)` 驗證結果（debug 和 release 都會執行）
- `debug_assert!`、`debug_assert_eq!`、`debug_assert_ne!` 只在 debug 模式執行，release 時會被忽略
- `#[should_panic]` 測試預期中的 panic；加上 `expected = "..."` 可以確認 panic 訊息
- `#[cfg(test)]` 讓測試 `mod` 只在測試時編譯
- `use super::*;` 引入父 `mod` 的所有東西——測試最常用的寫法
- 測試可以直接測試私有函數（因為測試 `mod` 是子 `mod`）
