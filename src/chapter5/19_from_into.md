# `From<T>` / `Into<T>`

## 本集目標

學會使用標準庫的 `From` 和 `Into` trait 做型別轉換，理解「實作 `From` 就自動獲得 `Into`」的機制。

## 概念說明

上一集我們自己定義了 `Convert<T>` `trait`。其實 Rust 標準庫已經有一套更完整的轉換機制：`From` 和 `Into`。

### From

`From<T>` 的定義（簡化版）：

```rust,noplayground
trait From<T> {
    fn from(value: T) -> Self;
}
#
# fn main() {}
```

它的意思是：「我可以從 `T` 轉換而來。」

你一定見過這個：

```rust,noplayground
# fn main() {
    let s = String::from("hello");
# }
```

這就是 `String` 實作了 `From<&str>`——從 `&str` 轉換成 `String`。

### Into

`Into<T>` 是 `From` 的反方向：

```rust,noplayground
trait Into<T> {
    fn into(self) -> T;
}
#
# fn main() {}
```

重點：**你只需要實作 `From`，就自動獲得 `Into`。** 不需要自己實作 `Into`。

這又是一個 blanket implementation——Rust 有一個規則是「如果 `Y: From<X>`，那 `X` 自動實作 `Into<Y>`」。

### `TryFrom` / `TryInto`

有些轉換可能失敗——比如把一個很大的 `i64` 轉成 `i32` 可能會溢位。這時候用 `TryFrom` 和 `TryInto`，它們回傳 `Result` 而不是直接回傳值。

和 `From` / `Into` 一樣，實作 `TryFrom` 就自動獲得 `TryInto`。

## 範例程式碼

```rust
use std::fmt::Display;
use std::fmt::Formatter;

struct Celsius {
    value: f64,
}

struct Fahrenheit {
    value: f64,
}

impl Display for Celsius {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{}°C", self.value)
    }
}

impl Display for Fahrenheit {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{}°F", self.value)
    }
}

// 實作 From：從 Celsius 轉成 Fahrenheit
impl From<Celsius> for Fahrenheit {
    fn from(c: Celsius) -> Fahrenheit {
        Fahrenheit {
            value: c.value * 1.8 + 32.0,
        }
    }
}

fn main() {
    // String::from——我們一直在用的
    let s = String::from("hello");
    println!("{}", s);

    // 自訂的 From
    let boiling = Celsius { value: 100.0 };
    println!("攝氏：{}", boiling);
    let f = Fahrenheit::from(Celsius { value: 100.0 });
    println!("華氏：{}", f);

    // 自動獲得 Into（不需要另外實作）
    let body_temp = Celsius { value: 37.0 };
    let f2: Fahrenheit = body_temp.into();
    println!("體溫：{}", f2);

    // TryFrom 的例子：i32 轉 u8 可能失敗
    let big: i32 = 300;
    let result = u8::try_from(big);
    match result {
        Ok(n) => println!("轉換成功：{}", n),
        Err(e) => println!("轉換失敗：{:?}", e),
    }

    let small: i32 = 42;
    let ok = u8::try_from(small);
    match ok {
        Ok(n) => println!("轉換成功：{}", n),
        Err(e) => println!("轉換失敗：{:?}", e),
    }
}
```

## 重點整理

- `From<T>` 定義「從 `T` 轉換而來」：`String::from("hello")` 就是這個
- 實作 `From` 就自動獲得 `Into`——不需要另外實作
- `.into()` 是 `.from()` 的反方向：`let f: Fahrenheit = celsius.into();`
- `TryFrom` / `TryInto` 用於可能失敗的轉換，回傳 `Result`
- 實作 `TryFrom` 也會自動獲得 `TryInto`
