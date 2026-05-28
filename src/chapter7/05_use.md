# `use`

## 本集目標

學會用 `use` 簡化路徑，理解 Rust 的路徑解析規則和各種匯入方式。

## 概念說明

在前面我們已經初步接觸過 `use`，這裡要把所有用法和路徑規則講完整。

### 為什麼需要 `use`

每次呼叫都寫完整路徑很累：

```rust,ignore
# fn main() {
    let sum = crate::math::basic::add(1, 2);
    let diff = crate::math::basic::subtract(5, 3);
# }
```

用 `use` 把路徑帶進來，之後就能直接用短名稱：

```rust,ignore
use crate::math::basic::add;
use crate::math::basic::subtract;

fn main() {
    let sum = add(1, 2);
    let diff = subtract(5, 3);
}
```

### 絕對路徑 vs 相對路徑

Rust 有兩種路徑起點：

**絕對路徑**——從 crate root 開始：

```rust,ignore
use crate::math::add; // 自己這個 crate 裡的 math mod
```

**相對路徑**——從當前 mod 的位置開始：

```rust,ignore
use math::add; // 當前 mod 底下的 math 子 mod
```

### 外部 crate 的路徑

在 `Cargo.toml` 加了外部 crate 後，直接用 crate 名稱作為路徑開頭：

```rust,ignore
use std::collections::HashMap;
use rand::Rng;
#
# fn main() {}
```

`std` 是 Rust 的**標準函式庫（standard library）**——Rust 內建的一組工具，包含我們已經用過的 `Vec`、`String`、`Option`、`Result`、`println!` 等等，以及更多像是檔案操作、網路、集合等功能。你不需要在 Cargo.toml 加 dependency 就能用它，因為每個 Rust 程式都會自動連結 `std`。使用時路徑寫法跟外部 crate 一樣——`std::collections::HashMap`、`std::fmt::Display` 等。不只 `std` 會被自動連結，`std` 中的 **prelude** 更會被自動引入——也就是說，`Vec`、`String`、`Option`、`Result`、`Clone`、`Copy` 等最常用的型別和 trait，不用寫 `use` 就能直接用。這就是為什麼我們在最前面好幾章沒寫 `use` 也能用這些東西。

如果你想明確強調「這是外部 crate」，可以用 `::` 開頭：

```rust,ignore,mdbook-runnable
use ::rand::Rng;  // 明確表示 rand 是外部 crate，不是本地 mod
#
# fn main() {}
```

這在你的 crate 裡也有一個叫 `rand` 的 `mod` 時特別有用，可以避免歧義。

### super:: 和 self::

- `super::`：往上一層，指向**父 `mod`**
- `self::`：指向**當前 `mod`**（通常省略，但有時在 `use` 中有用）

```rust,noplayground
mod outer {
    pub fn greet() -> String {
        String::from("Hello from outer")
    }

    pub mod inner {
        pub fn call_parent() -> String {
            super::greet() // 呼叫父 mod 的 greet
        }
    }
}
#
# fn main() {}
```

### 一次 `use` 多個東西

匯入同一個路徑底下的多個東西，可以用大括號合併：

```rust,noplayground
use std::io::{self, Read, Write};
// 等同於：
// use std::io;
// use std::io::Read;
// use std::io::Write;
#
# fn main() {}
```

`self` 在這裡代表 `std::io` 本身，所以你既匯入了 `io` 這個 `mod`，也匯入了裡面的 `Read` 和 `Write`。

### `use` ... `as`（別名）

如果兩個不同地方有同名的東西，可以用 `as` 取別名：

```rust,noplayground
use std::fmt::Result as FmtResult;
use std::io::Result as IoResult;

fn format_something() -> FmtResult {
    Ok(())
}

fn read_something() -> IoResult<()> {
    Ok(())
}
#
# fn main() {}
```

### `use` 的名字衝突

如果你 `use` 了兩個同名的東西到同一個作用域，Rust 會直接報錯：

```rust,compile_fail
mod a {
    pub fn hello() -> &'static str { "from a" }
}

mod b {
    pub fn hello() -> &'static str { "from b" }
}

use a::hello;
use b::hello; // 編譯錯誤！hello 已經被定義了
```

這時候就用 `as` 取別名來解決。

但如果是**不同作用域**，內層的 `use` 會遮蔽（shadow）外層的——就像 `let` 的 shadowing：

```rust,editable
# mod a {
#     pub fn hello() -> &'static str { "from a" }
# }
#
# mod b {
#     pub fn hello() -> &'static str { "from b" }
# }
#
use a::hello;

fn main() {
    println!("{}", hello());     // "from a"

    {
        use b::hello;            // 在這個作用域裡 shadow 了外面的 hello
        println!("{}", hello()); // "from b"
    }

    println!("{}", hello());     // "from a"（回到外層）
}
```

### glob import（星號匯入）

`*` 會把 mod 底下所有 `pub` 的東西全部帶進來：

```rust,noplayground
use std::collections::*; // HashMap, HashSet, BTreeMap... 全部可用
#
# fn main() {}
```

**一般不推薦**在正式程式碼裡用，因為不清楚到底帶了什麼進來，容易衝突。但在**測試**裡很常見——`use super::*;` 可以把父 `mod` 的所有東西帶進測試 `mod`。下一集我們會教怎麼用 `cargo test` 寫測試，到時候就會看到這個用法。

### `use` `enum` variant

`use` 不只能匯入 `mod` 底下的東西，也能匯入 `enum` 的 variant：

```rust,noplayground
use std::cmp::Ordering::{Less, Equal, Greater};

fn compare(a: i32, b: i32) {
    match a.cmp(&b) {
        Less => println!("小於"),
        Equal => println!("相等"),
        Greater => println!("大於"),
    }
}
#
# fn main() {}
```

不用每次都寫 `Ordering::Less`，直接用 `Less` 就好。這在 `match` 很多 variant 的時候特別方便。

## 範例程式碼

```rust,editable
mod math {
    pub mod basic {
        pub fn add(a: i32, b: i32) -> i32 {
            a + b
        }

        pub fn subtract(a: i32, b: i32) -> i32 {
            a - b
        }
    }

    pub mod advanced {
        pub fn power(base: i32, exp: u32) -> i32 {
            let mut result = 1;
            for _ in 0..exp {
                result *= base;
            }
            result
        }

        pub fn factorial(n: u64) -> u64 {
            let mut result: u64 = 1;
            for i in 1..=n {
                result *= i;
            }
            result
        }
    }
}

// 各種 use 的方式
use math::basic::add;
use math::basic::subtract;
use math::advanced::{power, factorial};

fn main() {
    println!("3 + 5 = {}", add(3, 5));
    println!("10 - 4 = {}", subtract(10, 4));
    println!("2 ^ 10 = {}", power(2, 10));
    println!("10! = {}", factorial(10));
}
```

## 重點整理

- `use` 將路徑帶入作用域，讓你不必每次寫完整路徑
- 絕對路徑用 `crate::` 開頭，相對路徑從當前 `mod` 位置開始
- 外部 crate 直接用名稱開頭；加 `::` 前綴可以明確標記為外部 crate
- `std` 是標準函式庫，不用加 dependency 就能用，prelude 也在裡面
- `super::` 指向父 `mod`，`self::` 指向當前 `mod`
- `use a::b::{self, X, Y};` 一次 `use` 多個東西
- `use X as Alias;` 取別名，解決名字衝突
- 同作用域 `use` 同名會報錯；不同作用域會 shadow（內層遮蔽外層）
- `use something::*;` 星號匯入——測試裡常用，正式程式碼少用
- `enum` 的 variant 也可以被 `use`