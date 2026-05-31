# `Result<T, E>`

## 本集目標

學會使用 `Result<T, E>` 處理可能失敗的操作，理解它和 `Option` 的對稱關係。

## 概念說明

上兩集學了 `Option<T>`——「可能有值，可能沒有」。但有時候，「沒有值」不夠——你還需要知道**為什麼**沒有。

比如解析數字，失敗時你想知道是「格式錯誤」還是「數字太大」。這就是 `Result<T, E>` 的用途。

### `Result` 的定義

```rust,noplayground
enum Result<T, E> {
    Ok(T),
    Err(E),
}
#
# fn main() {}
```

- `Ok(T)` 表示成功，裡面包著成功的值
- `Err(E)` 表示失敗，裡面包著錯誤資訊

和 `Option` 一樣，`Result`、`Ok`、`Err` 也是 Rust 預設就引入到每個檔案裡的。

### `Result` 和 `Option` 的對稱

| `Option` | `Result` |
|----------|----------|
| `Some(T)` | `Ok(T)` |
| `None` | `Err(E)` |

`Option` 只知道「有或沒有」，`Result` 還知道「為什麼沒有」。

### 回顧第 1 章的黑盒子

還記得第 1 章的 `.expect("讀取失敗")` 和 `.parse::<i32>().expect("請輸入數字")` 嗎？

`.parse()` 回傳的就是 `Result`。`expect` 的行為和 `Option` 的 `expect` 一模一樣——成功就取出 `Ok` 的值，失敗就 panic 並印出你的訊息。

現在我們終於能完整理解第 1 章的那段「黑盒子」程式碼了。

### 常用方法

和 `Option` 一樣，`Result` 也有：

- `unwrap()`：成功取出值，失敗 panic
- `expect("訊息")`：和 `unwrap` 一樣，但自訂 panic 訊息
- `unwrap_or(預設值)`：失敗時用預設值

## 範例程式碼

```rust,editable
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("除數不能是零"))
    } else {
        Ok(a / b)
    }
}

fn main() {
    // 用 match 處理 Result
    let result = divide(10, 3);
    match result {
        Ok(value) => println!("10 / 3 = {}", value),
        Err(msg) => println!("錯誤：{}", msg),
    }

    // 除以零的情況
    let bad = divide(10, 0);
    match bad {
        Ok(value) => println!("結果：{}", value),
        Err(msg) => println!("錯誤：{}", msg),
    }

    // unwrap_or：失敗時用預設值
    let safe = divide(10, 0).unwrap_or(0);
    println!("安全的結果：{}", safe);

    // 回顧第 1 章：parse 回傳 Result
    let input = "42";
    let num: Result<i32, _> = input.parse();
    match num {
        Ok(n) => println!("解析成功：{}", n),
        Err(e) => println!("解析失敗：{:?}", e),
    }

    // expect：確定不會失敗時使用
    let num2 = "100".parse::<i32>().expect("這不應該失敗");
    println!("{}", num2);
}
```

## 重點整理

- `Result<T, E>` 表示「成功（`Ok`）或失敗（`Err`）」，比 `Option` 多了錯誤資訊
- `Ok(T)` 對應成功，`Err(E)` 對應失敗
- `Result`、`Ok`、`Err` 和 `Option` 一樣，是 Rust 預設就引入每個檔案的
- `unwrap()`、`expect()`、`unwrap_or()` 的用法和 `Option` 完全對稱
- 第 1 章的 `.parse().expect(...)` 就是在用 `Result`——現在我們能理解了
