# Cargo 與 crates.io

## 本集目標

認識 Cargo 的更多功能以及如何透過 crates.io 使用社群套件。

## 概念說明

我們從第 1 章開始就在用 `cargo new` 和 `cargo run`。其實 `cargo run` 背後做了兩件事：先**編譯**你的程式碼，再**執行**編譯出來的執行檔。如果你只想編譯但不執行，可以用 `cargo build`——它只會產生執行檔，放在 `target/debug/` 資料夾裡。

這一集我們來多認識一些 Cargo 的功能，特別是怎麼引入外部套件。

### debug build vs release build

`cargo build` 和 `cargo run` 預設跑的是 **debug 模式**——編譯快但執行慢（沒有最佳化）。當你要發布程式的時候，加上 `--release`：

```bash
cargo build --release
```

這會產生最佳化過的執行檔，放在 `target/release/` 而不是 `target/debug/`。差異可以非常大——有些程式 release 版本跑起來快好幾倍。

### Cargo.toml

每個 Rust 專案的根目錄都有 `Cargo.toml`。TOML 是一種設定檔格式，設計得讓人好讀好寫。

一個典型的 `Cargo.toml` 長這樣：

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2024"

[dependencies]
```

- `[package]`：專案的基本資訊（名稱、版本、Rust edition）
- `[dependencies]`：這個專案用到的外部套件

其中 `edition` 是 Rust 的**版本號**——但不是 Rust 編譯器的版本，而是**語言規格的版本**。Rust 每隔幾年會發布一個新的 edition（2015、2018、2021、2024），每次可能會微調一些語法或預設行為。不同 edition 的 crate 可以互相搭配使用，所以不用擔心相容性問題。`cargo new` 會自動幫你設成最新的 edition。

### 加入外部套件

想用別人寫好的套件？最簡單的方式：

```bash
cargo add rand
```

這會自動在 `Cargo.toml` 的 `[dependencies]` 加上類似這樣的一行：

```toml
[dependencies]
rand = "0.10"
```

實際加上的版本號取決於你執行 `cargo add` 時的最新版本，不一定和這裡寫的一樣。

### crates.io

[crates.io](https://crates.io) 是 Rust 的官方套件庫。你可以在上面搜尋套件、看下載數、閱讀文件。每個套件頁面都會有：

- 使用說明和版本歷史
- 連結到 [docs.rs](https://docs.rs) 的自動產生文件
- 下載數（可以當作套件熱門程度的參考）

### 依賴的版本語意

在 `[dependencies]` 裡指定外部套件的版本時，有不同的寫法：

- `"^1.0"`（或直接寫 `"1.0"`）：相容 `1.x.y` 的任何版本，但不會升到 `2.0`
- `"=1.0.0"`：鎖定**剛好**這個版本
- `">=1.2, <1.5"`：指定範圍

大多數時候用預設的 `^` 就好，Cargo 會幫你選合適的版本。更多細節可以參考[官方文件](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html)。

### Cargo features

有些套件提供可選功能，用 `features` 開啟：

```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] }
```

這樣就能用 `serde` 的 `#[derive(Serialize, Deserialize)]`，而不需要的功能不會被編譯進來。

## 範例程式碼

用 `rand` 套件產生隨機數：

```rust,editable
// 先執行：cargo add rand
extern crate rand;

use rand::RngExt;

fn main() {
    let mut rng = rand::rng();

    let n: u32 = rng.random_range(1..=100);
    println!("隨機數字：{}", n);

    let coin: bool = rng.random();
    if coin {
        println!("正面！");
    } else {
        println!("反面！");
    }
}
```

## 重點整理

- `cargo build --release` 產生最佳化的執行檔，適合發布
- `Cargo.toml` 用 TOML 格式，`[package]` 記專案資訊，`[dependencies]` 記外部套件
- `edition` 是 Rust 語言規格的版本（2015、2018、2021、2024），不同 edition 的 crate 可以互相搭配
- `cargo add <套件名>` 是加入外部套件最快的方式
- [crates.io](https://crates.io) 是 Rust 的官方套件庫，[docs.rs](https://docs.rs) 提供自動產生的文件
- 版本號 `"1.0"` 等同 `"^1.0"`，允許相容升級；`"=1.0.0"` 鎖定精確版本
- `features` 可以開啟套件的可選功能
