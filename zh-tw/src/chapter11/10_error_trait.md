# `Error` `trait`

## 本集目標

學會自訂錯誤型別，以及用 `Box<dyn Error>` 統一處理不同種類的錯誤。

## 概念說明

### 回顧：`Result` 和 `?`

第 5 章學了 `Result<T, E>` 和 `?` 運算子。但當時錯誤型別都很單純——一個函數只會產生一種錯誤。實際的程式常常會碰到多種錯誤：讀檔案可能失敗（`io::Error`），解析數字也可能失敗（`ParseIntError`）。如果函數裡兩種都會發生，回傳的 `Result` 的 `E` 該填什麼？

### `Error` `trait`

標準庫定義了 `std::error::Error` `trait`，所有錯誤型別的共同介面：

```rust,noplayground
pub trait Error: std::fmt::Display + std::fmt::Debug {
    fn source(&self) -> Option<&(dyn Error + 'static)> { None }
}
#
# fn main() {}
```

要實作 `Error`，你的型別必須先實作 `Display` 和 `Debug`。`.source()` 回傳造成這個錯誤的底層原因，預設是 `None`。

### 自訂錯誤型別

用一個 `enum` 把所有可能的錯誤包在一起：

```rust,noplayground
use std::fmt;

#[derive(Debug)]
enum AppError {
    Io(std::io::Error),
    Parse(std::num::ParseIntError),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::Io(_) => write!(f, "輸入輸出操作失敗"),
            AppError::Parse(_) => write!(f, "整數解析失敗"),
        }
    }
}

impl std::error::Error for AppError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            AppError::Io(e) => Some(e),
            AppError::Parse(e) => Some(e),
        }
    }
}
#
# fn main() {}
```

以 `AppError::Parse` 為例，`Display` 會顯示「整數解析失敗」，而 `.source()` 會回傳原本的 `ParseIntError`，讓呼叫者需要時再查看更詳細的解析錯誤。這樣外層訊息和底層原因各自保留，不會把同一段錯誤文字印兩次。

第 5 章學了 `?`，當時說它遇到 `Err` 就提前回傳。其實 `?` 還多做了一件事：它會呼叫 `From::from(e)` 把錯誤轉換成函數回傳型別裡的 `E`。所以只要你幫底層錯誤實作了 `From`，`?` 就能自動轉換：

```rust,noplayground
# use std::fmt;
#
# #[derive(Debug)]
# enum AppError {
#     Io(std::io::Error),
#     Parse(std::num::ParseIntError),
# }
#
# impl fmt::Display for AppError {
#     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
#         match self {
#             AppError::Io(_) => write!(f, "輸入輸出操作失敗"),
#             AppError::Parse(_) => write!(f, "整數解析失敗"),
#         }
#     }
# }
#
# impl std::error::Error for AppError {
#     fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
#         match self {
#             AppError::Io(e) => Some(e),
#             AppError::Parse(e) => Some(e),
#         }
#     }
# }
#
impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self {
        AppError::Io(e)
    }
}

impl From<std::num::ParseIntError> for AppError {
    fn from(e: std::num::ParseIntError) -> Self {
        AppError::Parse(e)
    }
}
#
# fn main() {}
```

現在同一個函數裡可以用 `?` 處理兩種錯誤：

```rust,noplayground
# use std::fmt;
#
# #[derive(Debug)]
# enum AppError {
#     Io(std::io::Error),
#     Parse(std::num::ParseIntError),
# }
#
# impl fmt::Display for AppError {
#     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
#         match self {
#             AppError::Io(_) => write!(f, "輸入輸出操作失敗"),
#             AppError::Parse(_) => write!(f, "整數解析失敗"),
#         }
#     }
# }
#
# impl std::error::Error for AppError {
#     fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
#         match self {
#             AppError::Io(e) => Some(e),
#             AppError::Parse(e) => Some(e),
#         }
#     }
# }
#
# impl From<std::io::Error> for AppError {
#     fn from(e: std::io::Error) -> Self {
#         AppError::Io(e)
#     }
# }
#
# impl From<std::num::ParseIntError> for AppError {
#     fn from(e: std::num::ParseIntError) -> Self {
#         AppError::Parse(e)
#     }
# }
#
fn read_number(path: &str) -> Result<i32, AppError> {
    let content = std::fs::read_to_string(path)?; // io::Error → AppError
    let num = content.trim().parse::<i32>()?;     // ParseIntError → AppError
    Ok(num)
}
```

### 問題：每次都要寫這麼多？

自訂錯誤型別 + `impl Display` + `impl Error` + 每種 `From`... 很囉嗦。有沒有更簡單的方式？

### `Box<dyn Error>`

如果你不需要讓回傳型別列出一組可以窮舉 `match` 的錯誤種類，可以用 `Box<dyn Error>` 當通用錯誤型別：

```rust,noplayground
use std::error::Error;

fn read_number(path: &str) -> Result<i32, Box<dyn Error>> {
    let content = std::fs::read_to_string(path)?;
    let num = content.trim().parse::<i32>()?;
    Ok(num)
}
#
# fn main() {}
```

實作了 `Error + 'static` 的具體錯誤型別可以自動轉成 `Box<dyn Error>`，所以這些錯誤可以直接搭配 `?` 使用，不需要逐一手寫 `From`。

`Box<dyn Error>` 會抹除具體錯誤的靜態型別，因此呼叫者不能像處理自訂錯誤 `enum` 一樣進行窮舉 `match`。不過，錯誤資訊並未完全消失：仍可用 `.source()` 查看底層原因，也能在已知目標型別時使用 `.downcast_ref::<T>()` 檢查具體型別。

例如，呼叫者可以檢查 `Box<dyn Error>` 裡裝的是不是 `std::io::Error`：

```rust,no_run
# use std::error::Error;
#
# fn read_number(path: &str) -> Result<i32, Box<dyn Error>> {
#     let content = std::fs::read_to_string(path)?;
#     let num = content.trim().parse::<i32>()?;
#     Ok(num)
# }
#
fn main() {
    if let Err(error) = read_number("missing.txt") {
        if let Some(io_error) = error.downcast_ref::<std::io::Error>() {
            println!("這是 I/O 錯誤，種類是：{:?}", io_error.kind());
        } else {
            println!("這是其他錯誤：{}", error);
        }
    }
}
```

如果 `Box` 裡直接裝的是 `std::io::Error`，`.downcast_ref::<std::io::Error>()` 會回傳 `Some(&std::io::Error)`；型別不同就回傳 `None`。例如，`Box` 裡裝的是 `AppError` 時，即使 `AppError::Io` 內部包著 `std::io::Error`，`error.downcast_ref::<std::io::Error>()` 仍會回傳 `None`，因為直接裝在 `Box` 裡的型別是 `AppError`。這時要先呼叫 `.source()` 取得內部錯誤，再對它呼叫 `.downcast_ref::<T>()`。

`Box<dyn Error>` 本身不保證錯誤可以跨執行緒傳遞。如果錯誤需要送到其他執行緒，或 API 要求可跨執行緒的錯誤，常見的型別是 `Box<dyn Error + Send + Sync>`；放進去的錯誤也必須實作 `Send + Sync`。

### 什麼時候用哪個

- **快速原型、腳本、`main` 函數**：`Box<dyn Error>` 最省事。
- **函式庫、需要讓呼叫者精確處理錯誤**：自訂錯誤 `enum` + `impl Error` + `impl From`。

下一集會介紹社群 `crate` 怎麼大幅簡化自訂錯誤型別的寫法。

## 範例程式碼

```rust,editable
use std::error::Error;
use std::fs;

fn first_line_number(path: &str) -> Result<i32, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let first_line = content.lines().next().ok_or("檔案是空的")?;
    let num = first_line.trim().parse::<i32>()?;
    Ok(num)
}

fn main() {
    match first_line_number("number.txt") {
        Ok(n) => println!("讀到的數字：{}", n),
        Err(e) => println!("錯誤：{}", e),
    }
}
```

## 重點整理

- `Error` `trait` 要求 `Display + Debug`，是所有錯誤型別的共同介面。
- 自訂錯誤：定義 `enum` → `impl Display` → `impl Error`（用 `.source()` 保留原因）→ 為每種底層錯誤 `impl From`。
- 有了 `From`，`?` 就能自動把底層錯誤轉成你的自訂錯誤。
- `Box<dyn Error>`：會抹除具體錯誤的靜態型別，但仍可透過 `.source()` 或 downcast 檢查錯誤。
- 需要跨執行緒傳遞錯誤時，常用 `Box<dyn Error + Send + Sync>`。
- `Box<dyn Error>` 適合快速開發；自訂錯誤 `enum` 適合函式庫。
