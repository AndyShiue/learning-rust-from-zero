# `Option` 常用方法

## 本集目標

學會 `Option` 的常用方法：`unwrap`、`expect`、`unwrap_or`、`flatten`，以及用 `if let` 取值。

## 概念說明

上一集我們用 `match` 來處理 `Option`，這是最安全的方式。但每次都寫 `match` 有時候太囉嗦了。Rust 提供了一些方便的方法。

### `unwrap`：暴力取值

```rust,noplayground
# fn main() {
    let x: Option<i32> = Some(42);
    let value = x.unwrap(); // 42
# }
```

如果是 `Some`，直接拿到裡面的值。但如果是 `None`，程式會 panic（崩潰）！所以 `unwrap` 要小心用——只在你**確定**不會是 `None` 的時候才用。

### `expect`：帶訊息的 `unwrap`

```rust,should_panic
# #![allow(unused_variables)]
#
# fn main() {
    let x: Option<i32> = None;
    let value = x.expect("不應該是 None"); // panic，印出你的訊息
# }
```

和 `unwrap` 一樣，但 panic 時會印出你自訂的訊息，方便除錯。

### `unwrap_or`：提供預設值

```rust,noplayground
# fn main() {
    let x: Option<i32> = None;
    let value = x.unwrap_or(0); // 0
# }
```

如果是 `Some` 就取出值，如果是 `None` 就用你給的預設值。不會 panic，很安全。

### `flatten`：把巢狀 `Option` 壓平

有時候你會碰到 `Option<Option<T>>` 這種巢狀結構：

```rust,noplayground
# fn main() {
    let nested: Option<Option<i32>> = Some(Some(42));
    let flat: Option<i32> = nested.flatten(); // Some(42)
# }
```

`flatten` 把兩層 `Option` 壓成一層。如果外層或內層是 `None`，結果就是 `None`。

## 範例程式碼

```rust
fn find_even(numbers: &[i32]) -> Option<i32> {
    for n in numbers {
        if *n % 2 == 0 {
            return Some(*n);
        }
    }
    None
}

fn main() {
    let nums = [1, 3, 5, 7];
    let has_even = [2, 4, 6];

    // unwrap_or：安全地提供預設值
    let result = find_even(&nums).unwrap_or(0);
    println!("偶數（沒找到就給 0）：{}", result);

    // expect：確定有值時使用
    let result2 = find_even(&has_even).expect("應該要有偶數");
    println!("找到偶數：{}", result2);

    // if let：第三章學過的語法
    if let Some(n) = find_even(&has_even) {
        println!("用 if let 取出：{}", n);
    }

    // flatten：壓平巢狀 Option
    let nested: Option<Option<i32>> = Some(Some(42));
    let flat = nested.flatten();
    println!("{:?}", flat);

    let nested_none: Option<Option<i32>> = Some(None);
    let flat_none = nested_none.flatten();
    println!("{:?}", flat_none);

    let outer_none: Option<Option<i32>> = None;
    let flat_outer = outer_none.flatten();
    println!("{:?}", flat_outer);
}
```

## 重點整理

- `unwrap()`：取出 `Some` 的值，`None` 時 panic——小心使用
- `expect("訊息")`：和 `unwrap` 一樣，但 panic 時印出自訂訊息
- `unwrap_or(預設值)`：`None` 時回傳預設值，不會 panic
- `flatten()`：把 `Option<Option<T>>` 壓成 `Option<T>`
- 搭配 `if let Some(x) = ...`（第三章學的）也很方便
