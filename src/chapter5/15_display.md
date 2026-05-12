# `Display` `trait`

## 本集目標

學會為自訂型別實作 `Display` `trait`，理解 `Display` 和 `Debug` 的差別，以及 `Display` 和 `ToString` 的關係。

## 概念說明

第二章我們學了 `{:?}` 來印出 tuple、陣列和加了 `#[derive(Debug)]` 的 `struct`。但 `{:?}` 是給開發者看的「`Debug` 格式」。如果你想用 `{}` 來印出自訂型別，就需要實作 `Display` `trait`。

### `Display` vs `Debug`

- **`Debug`**（`{:?}`）：給開發者看的格式，可以用 `#[derive(Debug)]` 自動產生
- **`Display`**（`{}`）：給使用者看的格式，**必須手動實作**，不能 `derive`

為什麼要分開？因為開發者需要看到所有欄位、型別資訊（`Debug` 格式），但使用者只需要看到好讀的文字。兩者的需求不同，所以不能用同一個 `trait` 解決。

### 實作 `Display`

```rust,noplayground
use std::fmt::Display;
use std::fmt::Formatter;
use std::fmt::Result;
#
# struct Point {
#     x: i32,
#     y: i32,
# }

impl Display for Point {
    fn fmt(&self, f: &mut Formatter) -> Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}
#
# fn main() {}
```

`fmt` 方法接收一個 `&mut Formatter`，你用 `write!` 巨集把想要的格式寫進去。`write!` 的用法和 `println!` 幾乎一樣，只是第一個參數是 `&mut Formatter`。

### `Display` 和 `ToString` 的關係

Rust 有一個 `ToString` `trait`，它只有一個方法：

```rust,ignore
fn to_string(&self) -> String;
```

重點來了——**你不需要自己實作 `ToString`**。標準庫裡有這樣一段程式碼：

```rust,ignore
impl<T: Display> ToString for T {
    fn to_string(&self) -> String {
        // 內部用 Display 的 fmt 方法來產生字串
        // ...
    }
}
```

這段的意思是：「對於**所有**實作了 `Display` 的型別 `T`，自動幫它實作 `ToString`。」這叫做 **blanket implementation**（毯子式實作）——像一條毯子，蓋住所有符合條件的型別。

所以只要實作 `Display`，你的型別就自動有 `.to_string()` 方法，不用額外做任何事。

## 範例程式碼

```rust
use std::fmt::Display;
use std::fmt::Formatter;

#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

// 手動實作 Display
impl Display for Point {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

#[derive(Debug)]
struct Color {
    r: u8,
    g: u8,
    b: u8,
}

impl Display for Color {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "R{}G{}B{}", self.r, self.g, self.b)
    }
}

fn main() {
    let p = Point { x: 3, y: 7 };

    // Debug 格式（給開發者看）
    println!("Debug: {:?}", p);

    // Display 格式（給使用者看）
    println!("Display: {}", p);

    // 因為有 Display，自動獲得 .to_string()
    let s = p.to_string();
    println!("to_string: {}", s);

    let c = Color { r: 255, g: 128, b: 0 };
    println!("Debug: {:?}", c);
    println!("Display: {}", c);
    println!("to_string: {}", c.to_string());
}
```

## 重點整理

- `Display` `trait` 讓你的型別可以用 `{}` 格式印出
- `Debug`（`{:?}`）給開發者看，可以 `derive`；`Display`（`{}`）給使用者看，必須手動實作
- 實作方式：`impl Display for MyType`，在 `fmt` 方法裡用 `write!` 寫格式
- 實作 `Display` 會自動獲得 `.to_string()` 方法（blanket implementation）
