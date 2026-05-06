# `?` 運算子

## 本集目標
學會用 `?` 運算子簡化錯誤傳播，避免一次又一次的 match。

## 概念說明

上一集學了 Result，我們用 match 來處理成功和失敗。但如果一個函數裡有好幾個可能失敗的操作呢？

```rust,no_run
fn do_stuff() -> Result<i32, String> {
    let a = match "42".parse::<i32>() {
        Ok(n) => n,
        Err(e) => return Err(format!("{:?}", e)),
    };
    let b = match "10".parse::<i32>() {
        Ok(n) => n,
        Err(e) => return Err(format!("{:?}", e)),
    };
    Ok(a + b)
}
#
# fn main() {}
```

每個 parse 都要 match 一次，太囉嗦了。`?` 運算子就是用來解決這個問題的。

### `?` 的本質

`?` 放在 `Result` 後面，做的事情就是：

- 如果是 `Ok(v)`，把 `v` 取出來，繼續往下跑
- 如果是 `Err(e)`，回傳 `Err`，提前離開函數

所以 `?` 就是 match + early return 的簡寫。

### 注意：錯誤型別要一致

使用 `Result` 的時候，Err 裡的型別必須和函數回傳的 Err 型別一致或有某種關聯（之後會講具體是哪種關聯）。如果沒有關聯，就不能直接用 `?`——你得先把錯誤轉成對的型別。

比如 `.parse()` 的錯誤型別是 `std::num::ParseIntError`，但你的函數回傳 `Result<_, String>`。這時候你可以用 match 自己轉換，然後再手動 return：

```rust,no_run
# fn stringify_err() -> Result<i32, String> {
#     let input = "1";
    let n = match input.parse::<i32>() {
        Ok(v) => Ok(v),
        Err(e) => return Err(format!("{:?}", e)),
    };
#     n
# }
#
# fn main() {}
```

或者先包一層把錯誤轉好的輔助函數，在那個函數回傳之後就能直接用 `?`——下面的範例程式碼就是這樣做的。

後面我們會教到更方便處理這種狀況的做法，不用每次都自己手動轉換錯誤型別。

### `?` 也能用在 Option

`?` 不只能用在 Result 上，也能用在 Option 上——如果是 `None`，就直接 `return None`。

### main 也能回傳 Result

如果 `main` 函數回傳 `Result<(), String>`，你就可以在 main 裡使用 `?`。

## 範例程式碼

```rust
// 手動轉換錯誤型別的輔助函數
fn parse_i32(input: &str) -> Result<i32, String> {
    match input.parse::<i32>() {
        Ok(n) => Ok(n),
        Err(e) => Err(format!("解析 '{}' 失敗：{:?}", input, e)),
    }
}

// 使用 ? 簡化錯誤傳播
fn add_two_strings(a: &str, b: &str) -> Result<i32, String> {
    let x = parse_i32(a)?; // Ok 就取值，Err 就提前回傳
    let y = parse_i32(b)?;
    Ok(x + y)
}

// ? 用在 Option 上：第一個元素是正數嗎？
fn first_is_positive(numbers: &[i32]) -> Option<bool> {
    // 如果切片是空的，.first() 回傳 None，? 直接 return None
    let first = numbers.first()?;
    Some(*first > 0)
}

// main 也能回傳 Result，這樣就能用 ?
fn main() -> Result<(), String> {
    let result = add_two_strings("42", "10")?;
    println!("42 + 10 = {}", result);

    // 錯誤的情況
    let bad = add_two_strings("42", "abc");
    match bad {
        Ok(n) => println!("結果：{}", n),
        Err(e) => println!("錯誤：{}", e),
    }

    let nums = [3, 7, 2];
    match first_is_positive(&nums) {
        Some(true) => println!("第一個元素是正數"),
        Some(false) => println!("第一個元素不是正數"),
        None => println!("空的切片"),
    }

    let empty: &[i32] = &[];
    match first_is_positive(empty) {
        Some(b) => println!("結果：{}", b),
        None => println!("空的切片，沒有第一個元素"),
    }

    Ok(())
}
```

## 重點整理
- `?` 是 match + early return 的簡寫
- `Result` 上用 `?`：Ok 取值，Err 提前回傳
- `Option` 上用 `?`：Some 取值，None 提前回傳
- 使用 `?` 時，錯誤型別必須和函數回傳型別一致——不一致時要另外處理
- `fn main() -> Result<(), String>` 讓 main 也能使用 `?`