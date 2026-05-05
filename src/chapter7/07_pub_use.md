# pub use

## 本集目標

學會用 `pub use` 重新匯出（re-export）內部項目，讓使用者不需要知道你的 mod 結構。

## 概念說明

假設你寫了一個 library，內部結構長這樣：

```ignore
src/
├── lib.rs
├── math.rs
└── math/
    ├── basic.rs
    └── advanced.rs
```

如果不做任何處理，使用你 library 的人得寫：

```rust,ignore
use your_crate::math::basic::add;
use your_crate::math::advanced::power;
```

這很麻煩——使用者根本不在意你內部怎麼分資料夾，他只想用 `add` 和 `power`。

### pub use 的魔法

`pub use` 把內部的東西「重新匯出（re-export）」到當前 mod，讓外部可以用更短的路徑存取：

```rust,ignore
// lib.rs
mod math;

// 重新匯出，讓使用者不需要知道 math::basic:: 的路徑
pub use math::basic::add;
pub use math::advanced::power;
```

現在使用你 library 的人只需要：

```rust,ignore
use your_crate::add;
use your_crate::power;
```

乾淨多了。

注意：`pub use` 只能匯出**本來就是 pub 的東西**。如果你試圖 `pub use` 一個 private 的 item，編譯器會報錯——你不能把別人藏起來的東西公開出去。

### re-export 其他 crate 的東西

`pub use` 不只能匯出自己 mod 的內容，也能匯出**其他 crate** 的東西：

```rust,ignore
// lib.rs
pub use rand::Rng; // 使用者 use your_crate::Rng 就好，不用自己加 rand 依賴
#
# fn main() {}
```

這在 library 設計裡很常見——你的 library 依賴了某個 crate，但你想讓使用者透過你的 crate 就能用到那些型別，不用自己在 `Cargo.toml` 加依賴。

### 分層 re-export

你也可以在中間層的 mod 做 re-export，建立更有層次的公開 API：

```rust,ignore
// math.rs
pub mod basic;
pub mod advanced;

// 把常用的函數提升到 math 層級
pub use basic::add;
pub use basic::subtract;
pub use advanced::power;
```

這樣外部可以用 `your_crate::math::add`，不需要知道 `basic` 這一層。

### re-export 的好處

1. **簡化公開 API**：使用者不需要知道你的內部結構，用更短的路徑存取
2. **自由重構**：你可以隨意改內部的 mod 結構，只要 `pub use` 保持不變，使用者的程式碼不會壞

### 實際案例

很多知名的 Rust library 都大量使用 re-export。比如你寫 `use std::io::Read;`，其實 `Read` 可能定義在更深層的地方，只是被 re-export 到 `std::io` 了。

## 範例程式碼

```rust
mod shapes {
    pub mod circle {
        pub struct Circle {
            pub radius: f64,
        }

        impl Circle {
            pub fn new(radius: f64) -> Circle {
                Circle { radius }
            }

            pub fn area(&self) -> f64 {
                std::f64::consts::PI * self.radius * self.radius
            }
        }
    }

    pub mod rectangle {
        pub struct Rectangle {
            pub width: f64,
            pub height: f64,
        }

        impl Rectangle {
            pub fn new(width: f64, height: f64) -> Rectangle {
                Rectangle { width, height }
            }

            pub fn area(&self) -> f64 {
                self.width * self.height
            }
        }
    }

    // 重新匯出：使用者不需要知道 circle 和 rectangle 這兩個子 mod
    pub use circle::Circle;
    pub use rectangle::Rectangle;
}

// 直接從 shapes 拿，不需要 shapes::circle::Circle
use shapes::{Circle, Rectangle};

fn main() {
    let c = Circle::new(5.0);
    println!("圓形面積：{}", c.area());

    let r = Rectangle::new(4.0, 6.0);
    println!("長方形面積：{}", r.area());
}
```

## 重點整理

- `pub use path::Item;` 把內部的東西重新匯出，讓外部用更短的路徑存取
- 使用者不需要知道你內部的 mod 結構——你可以自由重構而不影響外部
- 可以匯出自己 mod 的內容，也可以匯出其他 crate 的東西
- library 的 `lib.rs` 常用 `pub use` 把重要型別提升到 crate 頂層
