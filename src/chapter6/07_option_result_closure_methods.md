# `Option` / `Result` 的閉包方法

## 本集目標

認識 `Option` 和 `Result` 上接受閉包的常用方法，體會閉包如何讓程式碼更簡潔流暢。

## 概念說明

第 5 章我們用 `match` 處理 `Option` 和 `Result`，每次都要展開兩個分支。現在學了閉包，很多操作可以一行搞定。

### `Option` 的閉包方法

以下方法定義在 `Option<T>` 上，簽名中的 `T` 就是 `Option<T>` 的型別參數。

**`map` —— 轉換 `Some` 裡的值**

```rust,noplayground
# fn main() {
    // Option<T> 上的方法：
    // fn map<U>(self, f: impl FnOnce(T) -> U) -> Option<U>
    let x: Option<i32> = Some(5);
    let y = x.map(|v| v * 2); // Some(10)
# }
```

如果是 `None`，`map` 什麼都不做，直接回傳 `None`。不用寫 `match`。

**`and_then` —— 鏈式操作（可能失敗）**

`map` 的閉包回傳普通值，但如果你的轉換本身也可能回傳 `None` 呢？用 `and_then`：

```rust,noplayground
# fn main() {
    // Option<T> 上的方法：
    // fn and_then<U>(self, f: impl FnOnce(T) -> Option<U>) -> Option<U>
    let x: Option<i32> = Some(5);
    let y = x.and_then(|v| if v > 3 { Some(v * 2) } else { None });
# }
```

`and_then` 的閉包回傳 `Option`，避免了 `Option<Option<T>>` 的巢狀問題。其實 `and_then` 就等於先 `map` 再 `flatten`——`map` 會產生 `Option<Option<U>>`，`flatten` 再把它攤平成 `Option<U>`。`and_then` 一步到位。

**`unwrap_or_else` —— 給一個計算預設值的閉包**

```rust,editable
# fn main() {
    // Option<T> 上的方法：
    // fn unwrap_or_else(self, f: impl FnOnce() -> T) -> T
    let x: Option<i32> = None;
    let y = x.unwrap_or_else(|| {
        println!("沒有值，計算預設值...");
        42
    });
# }
```

跟 `unwrap_or` 不同，`unwrap_or_else` 的預設值是**惰性計算**的——只有在真的是 `None` 的時候才會執行閉包。

**`filter` —— 條件過濾**

```rust,noplayground
# fn main() {
    // Option<T> 上的方法：
    // fn filter(self, predicate: impl FnOnce(&T) -> bool) -> Option<T>
    let x: Option<i32> = Some(4);
    let y = x.filter(|v| v % 2 == 0); // Some(4)，因為 4 是偶數
    let z = x.filter(|v| v % 2 != 0); // None，因為 4 不是奇數
# }
```

### `Result` 的閉包方法

`Result` 也有類似的一套方法。以下方法定義在 `Result<T, E>` 上，`T` 是 `Ok` 的型別，`E` 是 `Err` 的型別。

**`map` —— 轉換 `Ok` 的值**

```rust,noplayground
# fn main() {
    // Result<T, E> 上的方法：
    // fn map<U>(self, f: impl FnOnce(T) -> U) -> Result<U, E>
    let r: Result<i32, String> = Ok(10);
    let doubled = r.map(|v| v * 2); // Ok(20)
# }
```

**`map_err` —— 轉換 `Err` 的值**

跟 `map` 相反——`map` 對 `Ok` 做事、`Err` 不動；`map_err` 對 `Err` 做事、`Ok` 不動。

```rust,noplayground
# fn main() {
    // Result<T, E> 上的方法：
    // fn map_err<F>(self, f: impl FnOnce(E) -> F) -> Result<T, F>
    let r: Result<i32, String> = Err(String::from("not found"));
    let r2 = r.map_err(|e| format!("錯誤：{}", e));
# }
```

**`and_then` —— 鏈式操作**

```rust,noplayground
# fn main() {
    // Result<T, E> 上的方法：
    // fn and_then<U>(self, f: impl FnOnce(T) -> Result<U, E>) -> Result<U, E>
    let r: Result<i32, String> = Ok(5);
    let r2 = r.and_then(|v| {
        if v > 0 {
            Ok(v * 10)
        } else {
            Err(String::from("必須是正數"))
        }
    });
# }
```

跟 `Option` 一樣，`and_then` 就等於 `map` 再 `flatten`。

**`unwrap_or_else` —— 從 `Err` 計算預設值**

```rust,editable
# fn main() {
    // Result<T, E> 上的方法：
    // fn unwrap_or_else(self, f: impl FnOnce(E) -> T) -> T
    let r: Result<i32, String> = Err(String::from("oops"));
    let value = r.unwrap_or_else(|e| {
        println!("發生錯誤：{}，使用預設值", e);
        0
    });
# }
```

### 跟 `match` 的比較

用 `match`：
```rust,noplayground
# fn main() {
#     let opt = Some(1);
    let result = match opt {
        Some(v) => Some(v * 2),
        None => None,
    };
# }
```

用閉包方法：
```rust,noplayground
# fn main() {
#     let opt = Some(1);
    let result = opt.map(|v| v * 2);
# }
```

一行搞定，而且意圖更清晰——「對 `Some` 裡的值做轉換」。

## 範例程式碼

```rust,editable
fn parse_and_double(input: &str) -> Result<i32, String> {
    input
        .parse::<i32>()
        .map_err(|e| format!("解析失敗：{}", e))
        .and_then(|n| {
            if n >= 0 {
                Ok(n * 2)
            } else {
                Err(String::from("不接受負數"))
            }
        })
}

fn find_even(numbers: &[i32]) -> Option<i32> {
    for n in numbers {
        if n % 2 == 0 {
            return Some(*n);
        }
    }
    None
}

fn main() {
    // Option 的 map
    let maybe_num: Option<i32> = Some(21);
    let doubled = maybe_num.map(|n| n * 2);
    println!("map: {:?}", doubled);

    // Option 的 and_then
    let result = maybe_num.and_then(|n| {
        if n > 10 { Some(n - 10) } else { None }
    });
    println!("and_then: {:?}", result);

    // Option 的 filter
    let even = maybe_num.filter(|n| n % 2 == 0);
    println!("filter(偶數): {:?}", even);

    // Option 的 unwrap_or_else
    let none_value: Option<i32> = None;
    let default = none_value.unwrap_or_else(|| {
        println!("計算預設值中...");
        99
    });
    println!("unwrap_or_else: {}", default);

    // Result 鏈式操作
    println!("\n--- Result 鏈式操作 ---");
    let good = parse_and_double("21");
    println!("parse_and_double(\"21\") = {:?}", good);

    let bad_parse = parse_and_double("abc");
    println!("parse_and_double(\"abc\") = {:?}", bad_parse);

    let negative = parse_and_double("-5");
    println!("parse_and_double(\"-5\") = {:?}", negative);

    // Result 的 unwrap_or_else
    let safe_value = parse_and_double("oops").unwrap_or_else(|e| {
        println!("錯誤處理：{}", e);
        0
    });
    println!("安全取值：{}", safe_value);

    // 組合 Option 方法
    println!("\n--- Option 鏈式操作 ---");
    let numbers = vec![1, 3, 5, 8, 11];
    let result = find_even(&numbers)
        .filter(|n| *n > 5)
        .map(|n| n * 10);
    println!("找第一個偶數，> 5 才乘 10：{:?}", result);
}
```

## 重點整理

- `Option` 和 `Result` 的 `map` 對內部值做轉換，`None` / `Err` 時不執行
- `and_then` 用於閉包本身也回傳 `Option` / `Result` 的情況，避免巢狀
- `unwrap_or_else` 懶惰計算預設值，只在 `None` / `Err` 時才執行閉包
- `Option` 的 `filter` 根據條件決定保留 `Some` 或轉成 `None`
- `Result` 的 `map_err` 可以轉換錯誤型別，方便錯誤處理鏈
- 這些方法可以鏈式呼叫，比層層 `match` 更簡潔易讀
- 你可能已經注意到：光看型別簽名就能猜出方法在做什麼（`Option<T>` 的 `map` 接受 `FnOnce(T) -> U`，回傳 `Option<U>`）。這是函數式程式設計的一大特色——型別本身就是文件
