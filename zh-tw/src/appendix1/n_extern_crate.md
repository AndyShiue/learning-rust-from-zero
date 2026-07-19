# `extern crate`

## 本集目標

了解 `extern crate` 和 `use` 的差別，以及為什麼本教學的部分範例仍然會寫 `extern crate`。

> 本集是**第 7 章**的補充。

## 正文

第 7 章介紹過如何用 Cargo 加入外部 `crate`。例如要使用 `rand`，先執行：

```bash
cargo add rand
```

Cargo 會把 `rand` 加進 `Cargo.toml`。在新版 Rust 中，這樣就可以直接從程式裡使用它：

```rust,noplayground
# extern crate rand;
#
use rand::RngExt;

fn main() {
    let mut rng = rand::rng();
    let n = rng.random_range(1..=100);
    println!("{}", n);
}
```

一般的 Cargo 專案不需要再寫 `extern crate rand;`。

### `extern crate` 做了什麼？

`extern crate` 會明確告訴編譯器要載入某個外部 `crate`：

```rust,ignore
extern crate rand;
```

不過，它不會下載或安裝 `rand`，也不能取代 `Cargo.toml` 裡的 dependency。外部 `crate` 還是必須先由 Cargo 或其他建置工具準備好。

### `extern crate` 和 `use` 不一樣

下面兩行的工作不同：

```rust,ignore
extern crate rand;

use rand::RngExt;
```

- `extern crate rand;` 明確載入 `rand` 這個外部 `crate`。
- `use rand::RngExt;` 把 `rand` 裡的 `RngExt` `trait` 引入目前的作用域。

也就是說，`extern crate` 處理的是外部 `crate` 本身，`use` 處理的是程式裡名稱的使用方式。

### 用 `as` 替外部 `crate` 取別名

`extern crate` 也可以在載入外部 `crate` 時，替它建立一個在目前作用域中使用的名稱：

```rust,ignore
extern crate rand as random;
```

這個語法的一般形式是：

```rust,ignore
extern crate a as b;
```

其中：

- `a` 是外部 `crate` 的名稱。
- `b` 是這項宣告在目前作用域中建立的名稱。

例如，替 `rand` 取名為 `random` 之後，就可以透過 `random` 使用它：

```rust,editable
extern crate rand as random;

use random::RngExt;

fn main() {
    let mut rng = random::rng();
    let n = rng.random_range(1..=100);
    println!("{}", n);
}
```

不過，在新版 Rust 的一般 Cargo 專案中，如果目的只是替名稱取別名，通常直接使用第 7 章介紹過的 `use ... as ...` 即可：

```rust,ignore
use rand as random;
```

雖然兩種語法都使用 `as`，用途仍然不同：`extern crate rand as random;` 明確載入外部 `crate`，並建立名稱 `random`；`use rand as random;` 則是替已經可以使用的 `rand` 建立別名。

### 為什麼本教學仍然使用它？

你可能已經在本教學的範例中看過：

```rust,ignore
extern crate rand;
```

這不代表新版 Rust 的一般 Cargo 專案仍然需要這樣寫。**本教學加入 `extern crate`，是為了通過內部測試。**

本教學使用 `mdbook test`，自動編譯並測試書中的 Rust 程式碼。測試前會先把範例需要的外部 `crate` 編譯好，再使用 `-L` 告訴測試工具要去哪個資料夾尋找這些編譯結果。

但 `-L` 只提供搜尋路徑，不會像 Cargo 一樣替每個 dependency 傳入完整的資訊。因此，範例需要用 `extern crate rand;` 明確告訴編譯器要載入 `rand`，內部測試才能找到並使用它。

這是本教學測試方式的特殊需求，不是新版 Rust 的一般寫法。如果你把範例複製到自己的 Cargo 專案，而且已經用 `cargo add rand` 加入 dependency，通常可以刪除 `extern crate rand;`。

## 重點整理

- `extern crate name;` 會明確告訴編譯器載入某個外部 `crate`。
- `extern crate a as b;` 會明確載入外部 `crate` `a`，並在目前作用域中替它建立名稱 `b`；新版 Rust 若只需要別名，通常使用 `use a as b;`。
- `extern crate` 不會下載套件，也不能取代 `Cargo.toml` 裡的 dependency。
- `extern crate` 和 `use` 的用途不同：前者處理外部 `crate`，後者把名稱引入作用域。
- 新版 Rust 的一般 Cargo 專案通常不需要寫 `extern crate`。
- 本教學加入 `extern crate`，是為了讓使用 `mdbook test -L` 的內部測試能找到外部 `crate`。
