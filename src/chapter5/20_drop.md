# `Drop`

## 本集目標

學會用 `Drop` `trait` 定義值離開作用域時的清理行為，以及手動提前釋放資源。

## 概念說明

到目前為止，我們知道值離開作用域就不能用了。但其實 Rust 在背後還做了一件事——值離開作用域時，Rust 會自動**丟棄**（`drop`）它，釋放它佔用的資源（包括記憶體）。大部分時候你不需要在意這件事，但有時候你想在值被丟棄的那一刻做一些額外的事情，比如印一條訊息、關閉檔案、清理暫存等。

### `Drop` `trait`

`Drop` `trait` 讓你自訂「被丟棄時要做什麼」：

```rust,noplayground
# struct MyType { name: String }
#
impl Drop for MyType {
    fn drop(&mut self) {
        println!("MyType 被丟棄了！");
    }
}
#
# fn main() {}
```

Rust 會在值離開作用域時**自動呼叫** `drop`。你不能手動呼叫 `x.drop()`——Rust 禁止這樣做，因為值被 `drop` 之後又被自動 `drop` 一次會出問題。

### 手動提前釋放

如果你想提前釋放一個值，用 `drop()`：

```rust
# struct MyType { name: String }
#
# impl Drop for MyType {
#     fn drop(&mut self) {
#         println!("MyType 被丟棄了！");
#     }
# }
#
# fn main() {
    let x = MyType { name: String::from("小明") };
    drop(x); // 提前丟棄
    // x 不能再用了
# }
```

`drop` 是一個函數（不是 method），它會取走值的所有權，然後讓值離開作用域，觸發 `Drop`。

### 有 `Drop` 的型別不能部分 move

這是一個重要的限制。如果一個 `struct` 實作了 `Drop`，你就不能從它的欄位 move 出值：

```rust,compile_fail
# #![allow(unused_variables)]
#
struct Resource {
    name: String,
    id: i32,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("釋放 {}", self.name);
    }
}

fn main() {
    let r = Resource { name: String::from("A"), id: 1 };
    let n = r.name; // 編譯錯誤！不能部分 move
}
```

為什麼？因為 `drop` 需要完整的 `self`。如果你把 `name` move 走了，`drop` 執行時 `self.name` 就不存在了——這不安全。所以 Rust 禁止有 `Drop` 的型別做部分 move。

## 範例程式碼

```rust
struct Resource {
    name: String,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("釋放資源：{}", self.name);
    }
}

fn main() {
    let a = Resource { name: String::from("資料庫連線") };
    let b = Resource { name: String::from("檔案處理器") };

    println!("建立了兩個資源");

    // 手動提前釋放 a
    drop(a);
    println!("a 已經被提前釋放了");

    // a 不能再用了
    // println!("{}", a.name); // 編譯錯誤！

    println!("接下來 b 會在 main 結束時自動釋放");

    // 作用域示範
    {
        let c = Resource { name: String::from("暫時的資源") };
        println!("c 在這個作用域裡");
    } // c 在這裡被自動 drop

    println!("c 已經被釋放了，b 還在");
} // b 在這裡被自動 drop
```

## 重點整理

- `Drop` `trait` 讓你自訂值離開作用域時的清理行為
- Rust 在值離開作用域時**自動呼叫** `.drop()`，不能手動呼叫
- 想提前釋放，用 `drop(value)`
- **有 `Drop` 的型別不能部分 move**——因為 `drop` 需要完整的 `self`
