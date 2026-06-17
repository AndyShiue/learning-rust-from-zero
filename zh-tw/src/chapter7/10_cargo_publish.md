# `cargo publish`

## 本集目標

學會將你的 library 發布到 crates.io，讓全世界的 Rust 開發者都能使用。

## 概念說明

到目前為止，我們學會了怎麼組織程式碼、寫文件、使用別人的套件。這一集要反過來——把你自己的套件發布出去。

### 帳號設定

首先，你需要一個 crates.io 的帳號：

1. 到 [crates.io](https://crates.io) 用 GitHub 帳號登入
2. 到帳號設定頁面，產生一個 **API Token**
3. 在終端機執行：

```bash
cargo login
```

按 enter 後，終端機會提示你貼上 token——貼上後再按 enter 就完成了。token 會被存在本機，之後 publish 時自動使用。

### 準備 `Cargo.toml`

發布前，`Cargo.toml` 需要補上一些必要的 metadata：

```toml
[package]
name = "my-awesome-lib"
version = "0.1.0"
edition = "2024"
description = "一個很棒的數學運算 library"
license = "MIT"
repository = "https://github.com/yourname/my-awesome-lib"
readme = "README.md"
keywords = ["math", "utility"]
categories = ["mathematics"]
```

根據[官方文件](https://doc.rust-lang.org/cargo/reference/publishing.html)，發布前應填寫：

- `license`（或 `license-file`）：開源授權條款（如 `MIT`、`Apache-2.0`、`MIT OR Apache-2.0`）
- `description`：一行簡短描述
- `homepage`：專案首頁網址
- `repository`：原始碼倉庫網址
- `readme`：README 檔案路徑

另外建議但非必需：

- `keywords`：搜尋用的關鍵字（最多 5 個）
- `categories`：分類（需符合 crates.io 的分類清單）

### 發布前檢查

發布前可以先用 `cargo package` 檢查有沒有問題：

```bash
cargo package
```

這會模擬打包過程，檢查有沒有缺少必要欄位或其他問題。

### 發布！

一切準備好後：

```bash
cargo publish
```

完成！你的套件現在在 crates.io 上了，任何人都可以 `cargo add my-awesome-lib` 來使用。

### 版本更新流程

套件發布後，如果要更新：

1. 修改程式碼
2. 更新 `Cargo.toml` 裡的 `version`，遵循 [SemVer（語意化版本號）](https://semver.org/)
3. 再次 `cargo publish`

SemVer 的規則：

- **1.0 之前**（`0.x.y`）：整個 API 都被視為不穩定，任何版本都可能有破壞性變更
- **1.0 之後**：
  - bug 修復：`1.0.0` → `1.0.1`（patch）
  - 新增功能（向下相容）：`1.0.1` → `1.1.0`（minor）
  - 破壞性變更：`1.1.0` → `2.0.0`（major）——改第一個數字

**注意**：已發布的版本**無法刪除或覆蓋**。如果發現某個版本有嚴重問題，可以用 `cargo yank` 標記它為不建議使用，但已經在用的人不會受影響：

```bash
cargo yank --version 0.1.0
```

### 發布前最好做的事

- 寫好 `README.md`（這會顯示在 crates.io 套件頁面上）
- 跑過 `cargo test` 確認所有測試通過
- 用 `///` 寫好文件註解（上一集學的）
- 確保有範例程式碼
- 用 `cargo doc --open` 檢查文件看起來沒問題

## 範例程式碼

一個準備好發布的小 library 的完整結構：

```ignore
my-math-lib/
├── Cargo.toml
├── README.md
└── src/
    └── lib.rs
```

**Cargo.toml：**

```toml
[package]
name = "my-math-lib"
version = "0.1.0"
edition = "2024"
description = "Simple math utility functions"
license = "MIT"
homepage = "https://example.com/my-math-lib"
repository = "https://github.com/example/my-math-lib"
readme = "README.md"
keywords = ["math", "utility"]
categories = ["mathematics"]
```

**src/lib.rs：**

```rust,noplayground
//! # My Math Lib
//!
//! 提供簡單好用的數學函數。

/// 計算最大公因數。
///
/// # Examples
///
/// ```
/// use my_math_lib::gcd;
///
/// assert_eq!(gcd(12, 8), 4);
/// ```
pub fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        let temp = b;
        b = a % b;
        a = temp;
    }
    a
}

/// 計算最小公倍數。
///
/// # Examples
///
/// ```
/// use my_math_lib::lcm;
///
/// assert_eq!(lcm(4, 6), 12);
/// ```
pub fn lcm(a: u64, b: u64) -> u64 {
    if a == 0 || b == 0 {
        return 0;
    }
    a / gcd(a, b) * b
}

/// 判斷一個數是否為質數。
///
/// # Examples
///
/// ```
/// use my_math_lib::is_prime;
///
/// assert!(is_prime(7));
/// assert!(!is_prime(4));
/// ```
pub fn is_prime(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    let mut i: u64 = 2;
    while i * i <= n {
        if n % i == 0 {
            return false;
        }
        i += 1;
    }
    true
}
#
# fn main() {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_gcd() {
        assert_eq!(gcd(12, 8), 4);
        assert_eq!(gcd(7, 3), 1);
        assert_eq!(gcd(0, 5), 5);
    }

    #[test]
    fn test_lcm() {
        assert_eq!(lcm(4, 6), 12);
        assert_eq!(lcm(0, 5), 0);
    }

    #[test]
    fn test_is_prime() {
        assert!(!is_prime(0));
        assert!(!is_prime(1));
        assert!(is_prime(2));
        assert!(is_prime(17));
        assert!(!is_prime(15));
    }
}
```

發布指令流程：

```bash
cargo test       # 確認測試通過
cargo doc --open # 檢查文件
cargo package    # 模擬打包
cargo publish    # 正式發布！
```

## 重點整理

- 在 crates.io 用 GitHub 登入，產生 API token 後用 `cargo login` 設定
- `Cargo.toml` 發布前應填寫 `license`、`description`、`homepage`、`repository`、`readme`
- `cargo package` 可以在發布前檢查問題
- `cargo publish` 正式發布到 crates.io
- 更新版本時修改 `version` 欄位，遵循 SemVer（語意化版本號）
- 已發布的版本無法刪除，只能用 `cargo yank` 標記為不建議使用
- 發布前寫好 README、文件註解、測試，是對使用者的基本尊重

恭喜你完成了第 7 章！🎉 到這裡為止，我們已經教完了 Rust 的主要觀念——所有權、借用、泛型、`trait`、生命週期、閉包、迭代器，以及模組系統和套件管理。你現在已經可以獨當一面了。如果你腦中有什麼點子，現在就是動手實作的好時機！

即便如此，Rust 還有很多獨特而強大的功能。後面的章節會繼續介紹那些還沒介紹的重要主題，希望能帶給你對 Rust 更完整、更全面的認識。
