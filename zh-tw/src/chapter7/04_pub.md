# `pub` 可見性

## 本集目標

完整理解 Rust 的可見性規則，掌握 `pub` 的各種用法。

## 概念說明

第 2 集提到 `mod` 裡的東西預設是私有的，這一集我們來把可見性規則講清楚。

### 預設私有

Rust 的哲學是**預設封閉**——所有東西一開始都是私有的，你必須明確地用 `pub` 開放。這跟有些語言預設公開的設計完全相反。

```rust,compile_fail
mod secrets {
    fn hidden() {
        // 外面看不到我
    }

    pub fn visible() {
        // 外面可以呼叫我
        hidden(); // 同 mod 內可以互相呼叫
    }
}

fn main() {
    secrets::visible(); // OK
    secrets::hidden();  // 編譯錯誤！hidden 是私有的
}
```

你可能會好奇：`fn main()` 和 `mod secrets` 都沒加 `pub`，為什麼 `main` 能看到 `secrets`？因為它們都定義在根 `mod` 裡——同一個 `mod` 的成員互相看得到，不需要 `pub`。`pub` 是用來讓**其他 `mod`** 看到你的東西的。

### `pub fn`

函數加 `pub` 就對外公開，沒什麼好說的。

### `pub struct` —— 欄位要個別標記

`struct` 加 `pub` 只是讓這個**型別**公開，欄位還是私有的！每個欄位要**個別**加 `pub`：

```rust,compile_fail
mod user {
    pub struct Profile {
        pub name: String,  // 外部可讀寫
        pub email: String, // 外部可讀寫
        age: u32,          // 私有！外部看不到
    }

    impl Profile {
        pub fn new(name: String, email: String, age: u32) -> Profile {
            Profile { name, email, age }
        }

        pub fn age(&self) -> u32 {
            self.age // 透過方法公開唯讀存取
        }
    }
}

fn main() {
    let p = user::Profile::new(
        String::from("Yaju"),
        String::from("yaju@senpai.com"),
        24,
    );
    println!("名字：{}", p.name);  // OK，name 是 pub
    println!("年齡：{}", p.age()); // OK，透過方法存取
    println!("{}", p.age);         // 編譯錯誤！age 欄位是私有的
}
```

這個設計很重要——它讓你可以控制哪些欄位要暴露、哪些要隱藏。如果 `struct` 有任何私有欄位，外部就無法直接用 `StructName { ... }` 建構，必須透過你提供的建構函數。

tuple `struct` 也一樣——欄位預設是私有的，要個別加 `pub`：

```rust,compile_fail
# #![allow(unused_variables)]
#
mod geometry {
    pub struct Point(pub f64, pub f64); // 兩個欄位都公開
    pub struct Id(u64);                 // 欄位是私有的！
}

fn main() {
    let p = geometry::Point(1.0, 2.0); // OK，欄位都是 pub
    println!("x = {}", p.0);

    let id = geometry::Id(42); // 編譯錯誤！Id 的欄位是私有的
}
```

### `pub enum` —— variants 自動公開

`enum` 跟 `struct` 不一樣：只要 `enum` 本身是 `pub`，所有 variants 都**自動公開**。

```rust,editable
mod status {
    pub enum Color {
        Red,
        Green,
        Blue,
    }
}

fn main() {
    let c = status::Color::Red;  // 所有 variant 都可用
    match c {
        status::Color::Red => println!("紅色"),
        status::Color::Green => println!("綠色"),
        status::Color::Blue => println!("藍色"),
    }
}
```

這很合理——如果你公開了一個 `enum` 但藏了某些 variant，別人根本沒辦法正確 `match`，那還不如不公開。

### `pub trait` 和 `impl`

`trait` 加 `pub` 後，裡面的 `fn` **不用也不能**個別加 `pub`——它們的可見性自動跟著 `trait` 走。如果 `trait` 是公開的，裡面的 `fn` 就是公開的；如果 `trait` 是私有的，裡面的 `fn` 就是私有的。這很合理：`trait` 是一個「契約」，如果你公開了這個契約，契約裡的所有條款當然也要公開，不然別人怎麼實作？

```rust,editable
mod animal {
    pub trait Speak {
        fn speak(&self); // 不用加 pub，跟著 trait 走
    }

    pub struct Dog;

    impl Speak for Dog {
        fn speak(&self) {
            println!("汪！");
        }
    }
}

fn main() {
    use animal::Speak; // trait 要在作用域內才能呼叫它的方法
    let d = animal::Dog;
    d.speak();
}
```

注意 `use animal::Speak;` 這行——即使 `Dog` 已經實作了 `Speak`，你還是要把 `Speak` `trait` 引入作用域才能呼叫它的方法。如果拿掉這行，`d.speak()` 會編譯錯誤。這是 Rust 的規則：**`trait` 的方法只有在 `trait` 被 `use` 進來之後才能呼叫。**

```rust,compile_fail
mod animal {
    pub trait Speak {
        fn speak(&self); // 不用加 pub，跟著 trait 走
    }

    pub struct Dog;

    impl Speak for Dog {
        fn speak(&self) {
            println!("汪！");
        }
    }
}

fn main() {
    // 沒有 use animal::Speak;
    let d = animal::Dog;
    d.speak(); // 編譯錯誤！Speak 不在作用域內
}
```

`impl` 區塊本身**不需要也不能加 `pub`**。對於 `impl Type`（不是 `impl Trait for Type`），裡面的 `fn` 各自用 `pub` 控制可見性：

```rust,noplayground
mod shapes {
    pub struct Circle {
        pub radius: f64,
    }

    impl Circle {
        pub fn area(&self) -> f64 {
            std::f64::consts::PI * self.radius * self.radius
        }

        // 這是私有方法，只有 mod 內部能用
        fn internal_check(&self) -> bool {
            self.radius > 0.0
        }
    }
}
#
# fn main() {}
```

### `pub(crate)`、`pub(super)`、`pub(in path)`

有時候你不想完全公開，但又想讓 crate 內部的其他 `mod` 使用。Rust 提供了精細的控制：

- `pub(crate)`：整個 crate 內部可見，但外部（別的 crate）看不到
- `pub(super)`：只有父 `mod` 可見
- `pub(in crate::some::path)`：只對指定的 `mod` 路徑可見——最精細的控制

```rust,compile_fail
mod database {
    // 整個 crate 內部都能呼叫，但如果這是 library，
    // 使用你 library 的人看不到這個函數
    pub(crate) fn connect() -> String {
        String::from("connected")
    }

    // 注意 queries 本身是 pub——如果這個 mod 不是 pub，
    // 那裡面的東西即使標了 pub(super) 也沒用，
    // 因為外面根本看不到這個 mod，更別說裡面的東西了。
    pub mod queries {
        // 只有 database mod（父 mod）能看到
        pub(super) fn raw_query() -> String {
            String::from("SELECT * FROM users")
        }

        pub fn safe_query() -> String {
            let raw = raw_query(); // 同 mod 內可以呼叫
            format!("SAFE: {}", raw)
        }
    }
}

// pub(in path) 的例子
mod app {
    pub mod api {
        pub mod internal {
            // 只有 app::api 能看到這個函數
            pub(in crate::app::api) fn secret_key() -> &'static str {
                "super-secret"
            }
        }

        pub fn get_key() -> &'static str {
            internal::secret_key() // OK，我們在 app::api 裡
        }
    }
}

// app::api::internal::secret_key() 在這裡看不到
// 因為 pub(in crate::app::api) 限制了只有 app::api 能存取

// 注意：pub(in path) 的 path 必須是「包含你的」mod（從你往外數的某一層）。
// 如果你寫了一個跟你無關的 mod 路徑，例如：
//     pub(in crate::some_unrelated_mod) fn foo() {}
// 編譯器會直接報錯——你不能對一個「不包含你」的 mod 開放可見性。

fn main() {
    let conn = database::connect();          // OK，我們在同一個 crate
    let q = database::queries::safe_query(); // OK，pub
    println!("{}, {}", conn, q);
    database::queries::raw_query();          // 編譯錯誤！pub(super) 只給父 mod
}
```

## 重點整理

- Rust **預設一切私有**，必須明確加 `pub` 才公開
- `pub struct` 只公開型別名稱，每個欄位需要**個別**加 `pub`（tuple `struct` 也一樣）
- 有私有欄位的 `struct` 無法從外部直接建構，必須提供建構函數
- `pub enum` 的所有 variants **自動公開**
- `impl Trait for T` 裡的 `fn` 可見性跟著 `trait` 走，不加 `pub`；`impl T` 裡的 `fn` 各自用 `pub` 控制
- `pub(crate)`：crate 內部可見，外部不可見
- `pub(super)`：只有父 `mod` 可見
- `pub(in path)`：只對指定的 `mod` 路徑可見
