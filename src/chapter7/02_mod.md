# `mod`

## 本集目標

學會用 `mod` 將程式碼組織成有層次的結構。

## 概念說明

當程式越寫越長，全部塞在一個 `main.rs` 裡面會變得很難維護。這時候我們需要把相關的函數、`struct`、`enum` 分組——在 Rust 裡，這個分組機制就是 **模組（`mod`）**。

### 在同一個檔案裡定義 `mod`

最簡單的用法：直接在檔案裡用 `mod` 關鍵字建立一個區塊。

```rust,noplayground
mod math {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }

    pub fn multiply(a: i32, b: i32) -> i32 {
        a * b
    }
}
#
# fn main() {}
```

要呼叫 mod 裡的函數，用 `::` 路徑語法：

```rust,noplayground
# mod math {
#     pub fn add(a: i32, b: i32) -> i32 {
#         a + b
#     }
#
#     pub fn multiply(a: i32, b: i32) -> i32 {
#         a * b
#     }
# }
#
# fn main() {
    let result = math::add(3, 5);
# }
```

注意那個 `pub`——`mod` 裡的東西**預設是私有的**。如果不加 `pub`，外面就看不到、用不了。關於 `pub` 的完整規則我們在第 4 集會詳細講，這裡先記住：想讓外面用，就加 `pub`。

### 巢狀 `mod`

`mod` 可以一層一層巢狀：

```rust,noplayground
mod math {
    pub mod basic {
        pub fn add(a: i32, b: i32) -> i32 {
            a + b
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
    }
}
#
# fn main() {}
```

呼叫的時候就用完整路徑：

```rust,noplayground
# mod math {
#     pub mod basic {
#         pub fn add(a: i32, b: i32) -> i32 {
#             a + b
#         }
#     }
#
#     pub mod advanced {
#         pub fn power(base: i32, exp: u32) -> i32 {
#             let mut result = 1;
#             for _ in 0..exp {
#                 result *= base;
#             }
#             result
#         }
#     }
# }
#
# fn main() {
    let sum = math::basic::add(2, 3);
    let p = math::advanced::power(2, 10);
# }
```

這就像檔案系統的資料夾結構一樣——`math` 底下有 `basic` 和 `advanced` 兩個子 `mod`。

### `mod` 的預設可見性

一個很重要的觀念：**`mod` 裡的所有項目預設都是私有的**。同一個 `mod` 內部的程式碼可以互相存取，但外部看不到。這是 Rust 用來保護封裝性的設計。我們第 4 集會深入探討。

## 範例程式碼

```rust,editable
mod geometry {
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

    pub mod utils {
        pub fn describe_shape(name: &str, area: f64) {
            println!("{} 的面積是 {}", name, area);
        }
    }
}

fn main() {
    let rect = geometry::Rectangle::new(10.0, 5.0);
    let area = rect.area();
    geometry::utils::describe_shape("長方形", area);
}
```

## 重點整理

- `mod name { ... }` 在同一個檔案裡建立 `mod`
- `mod` 裡的東西用 `mod_name::item` 的路徑語法呼叫
- `mod` 可以巢狀，路徑就越來越長：`a::b::c::func()`
- `mod` 內的所有項目**預設是私有的**，要讓外部使用需加 `pub`
- `mod` 是 Rust 組織程式碼的基本單位，就像資料夾組織檔案一樣
