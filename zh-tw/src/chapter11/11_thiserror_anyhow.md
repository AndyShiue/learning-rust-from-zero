# `thiserror` / `anyhow` 簡介

## 本集目標

認識兩個社群最常用的錯誤處理 crate。

## 概念說明

這集介紹的不是標準庫的內容，而是兩個社群 crate。但它們在 Rust 生態裡幾乎是標配，非常實用，所以放在這裡一起介紹。

使用前要先安裝：

```bash
cargo add thiserror
cargo add anyhow
```

### 背景

上一集看到自訂錯誤要寫一堆重複的程式碼（`enum` + `Display` + `Error` + 每種 `From`）。`thiserror` 和 `anyhow` 幫你解決這個問題。

### `thiserror`：給函式庫用

`thiserror` 用 `derive` macro 自動生成 `Display`、`Error`、`From`：

```rust,editable
# extern crate thiserror;
#
use thiserror::Error;

#[derive(Debug, Error)]
enum AppError {
    #[error("輸入輸出錯誤：{0}")]
    Io(#[from] std::io::Error),

    #[error("解析錯誤：{0}")]
    Parse(#[from] std::num::ParseIntError),

    #[error("自訂錯誤：{0}")]
    Custom(String),
}
```

- `#[error("...")]` 自動生成 `Display` 的實作
- `#[from]` 自動生成 `From` 的實作
- 上一集手動寫了幾十行的東西，現在幾行就搞定

使用方式跟上一集一樣——`?` 會自動轉換：

```rust,editable
# extern crate thiserror;
#
# use thiserror::Error;
#
# #[derive(Debug, Error)]
# enum AppError {
#     #[error("輸入輸出錯誤：{0}")]
#     Io(#[from] std::io::Error),
#
#     #[error("解析錯誤：{0}")]
#     Parse(#[from] std::num::ParseIntError),
#
#     #[error("自訂錯誤：{0}")]
#     Custom(String),
# }
#
fn read_number(path: &str) -> Result<i32, AppError> {
    let content = std::fs::read_to_string(path)?;
    let num = content.trim().parse::<i32>()?;
    Ok(num)
}
```

呼叫端一樣可以 `match` 精確處理每種錯誤。

### `anyhow`：給應用程式用

如果你不需要讓呼叫者區分錯誤種類（例如 `main` 函數、CLI 工具），`anyhow` 更簡單：

```rust,editable
# extern crate anyhow;
#
use anyhow::{Context, Result};

fn read_number(path: &str) -> Result<i32> {
    let content = std::fs::read_to_string(path)
        .context("讀取檔案失敗")?;
    let num = content.trim().parse::<i32>()
        .context("解析數字失敗")?;
    Ok(num)
}
#
# fn main() {}
```

- `anyhow::Result<T>` 就是 `Result<T, anyhow::Error>`
- `anyhow::Error` 類似 `Box<dyn Error>`，但更好用
- `.context("...")` 幫錯誤加上額外說明，方便除錯
- 不用定義任何錯誤型別，任何 `Error` 都能自動轉換

### 兩者的關係

- **`thiserror`**：幫你定義精確的錯誤型別，省去手寫重複的程式碼。適合函式庫——使用者能 `match` 你的錯誤
- **`anyhow`**：完全不用定義錯誤型別，所有錯誤統一處理。適合應用程式——只需要報告錯誤，不需要讓別人程式化處理

兩者可以搭配使用：函式庫用 `thiserror` 定義錯誤，應用程式用 `anyhow` 統一接收。

## 範例程式碼

```rust,editable
// 這個範例展示 anyhow 的用法
# extern crate anyhow;
#
use anyhow::{Context, Result};
use std::fs;

fn read_config(path: &str) -> Result<(String, i32)> {
    let content = fs::read_to_string(path)
        .context("無法讀取設定檔")?;

    let mut lines = content.lines();

    let name = lines.next()
        .context("設定檔是空的")?
        .to_string();

    let value = lines.next()
        .context("缺少第二行")?
        .trim()
        .parse::<i32>()
        .context("第二行不是有效的數字")?;

    Ok((name, value))
}

fn main() -> Result<()> {
    let (name, value) = read_config("config.txt")?;
    println!("名稱：{}，值：{}", name, value);
    Ok(())
}
```

## 重點整理

- `thiserror`：用 `derive` macro 自動生成 `Display`、`Error`、`From`，適合函式庫
- `#[error("...")]` 生成 `Display`，`#[from]` 生成 `From`
- `anyhow`：通用錯誤型別，不用定義錯誤 `enum`，適合應用程式
- `.context("...")` 幫錯誤加上額外說明
- 函式庫用 `thiserror`，應用程式用 `anyhow`，兩者可以搭配
