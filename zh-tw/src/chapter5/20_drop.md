# `Drop`

## 本集目標

學會用 `drop(value)` 提前丟棄值，理解 Rust 會自動丟棄值所擁有的內容，並用 `Drop` `trait` 在內部值被丟棄前執行額外動作。

## 概念說明

### 用 `drop(value)` 提前丟棄值

值通常會在離開作用域時被 Rust 自動丟棄。如果不想等到作用域結束，可以呼叫 `drop(value)` 提前丟棄它：

```rust,editable
fn main() {
    let message = String::from("hello");
    println!("{}", message);

    drop(message);
    println!("message 已經被丟棄");

    // println!("{}", message); // 編譯錯誤！message 的值已經被 move
}
```

`drop` 是 prelude 提供的普通函數，不需要額外 `use`。它會取得傳入值的所有權，因此 `drop(message)` 之後不能再使用原本的值。

更精確地說，被丟棄的是 `message` 綁定的**值**，不是變數名稱本身。變數原本的作用域並沒有縮短，只是它的值已經被 move 給 `drop`，接著被丟棄。

### 內部值也會被自動丟棄

丟棄一個值時，Rust 也會繼續丟棄這個值所擁有的欄位或元素：

```rust,editable
struct Message {
    title: String,
    body: String,
}

fn main() {
    let message = Message {
        title: String::from("問候"),
        body: String::from("你好！"),
    };

    drop(message);
}
```

這裡只需要丟棄 `message`，Rust 就會自動丟棄裡面的 `title` 和 `body`。同樣的機制也適用於 tuple、`enum`、陣列和 `Vec` 等型別所擁有的值，不需要自己逐一清理。

### 用 `Drop` 在丟棄前執行額外動作

有時候，在 Rust 自動丟棄內部值之前，我們想先做一些事情，例如關閉連線、歸還資源或印出紀錄。這時可以為型別實作 `Drop` `trait`：

```rust,noplayground
# struct Resource {
#     name: String,
# }
#
impl Drop for Resource {
    fn drop(&mut self) {
        println!("釋放資源：{}", self.name);
    }
}
#
# fn main() {}
```

當 `Resource` 被丟棄時，Rust 會先執行 `Drop` 的 `.drop()` 方法，之後再自動丟棄它的欄位。這個方法是丟棄過程中的額外動作，不會取代 Rust 對內部值的自動處理。

雖然 `Drop` 的 `.drop()` 方法和 `drop(value)` 函數都叫作 `drop`，但兩者的用法不同：

- `drop(value)` 是可以主動呼叫的普通函數，用來提前丟棄值。
- `Drop` 的 `.drop()` 方法由 Rust 在丟棄值時自動執行，不能寫成 `value.drop()` 主動呼叫。

為什麼不能手動呼叫 `value.drop()`？因為這個方法只取得 `&mut self`，不會取得值的所有權。如果允許手動呼叫，值在呼叫後仍然存在；等它之後真的被丟棄時，Rust 又會執行一次相同的方法，可能重複釋放同一份資源。因此 Rust 直接禁止這種寫法。

`drop(value)` 不一樣：它會取得值的所有權，呼叫後原本的值不能再使用。這能讓 Rust 提前完成整個丟棄過程，而不會留下稍後還要再次丟棄的值。

## 範例程式碼

```rust,editable
struct Resource {
    name: String,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("釋放資源：{}", self.name);
    }
}

struct Worker {
    name: String,
    resource: Resource,
}

impl Drop for Worker {
    fn drop(&mut self) {
        println!(
            "停止工作者：{}（接著會釋放 {}）",
            self.name,
            self.resource.name,
        );
    }
}

fn main() {
    let worker = Worker {
        name: String::from("下載器"),
        resource: Resource {
            name: String::from("網路連線"),
        },
    };

    println!("工作者執行中");
    drop(worker);
    println!("工作者已被提前丟棄");

    {
        let temporary = Resource {
            name: String::from("暫存檔"),
        };
        println!("暫時資源使用中：{}", temporary.name);
    } // temporary 在這裡被自動丟棄
}
```

## 實作 `Drop` 的型別不能部分 move

如果一個型別實作了 `Drop`，就不能從它的欄位 move 出值：

```rust,compile_fail
struct Resource {
    name: String,
    id: i32,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("釋放 {}（編號 {}）", self.name, self.id);
    }
}

fn main() {
    let resource = Resource {
        name: String::from("資料庫連線"),
        id: 1,
    };

    let name = resource.name; // 編譯錯誤！不能部分 move
}
```

`Drop` 的 `.drop()` 方法會取得完整的 `&mut self`，因此可能存取任何欄位。如果允許先把 `name` move 出去，之後執行這個方法時，`resource` 就不再完整，所以 Rust 禁止這種操作。

如果某個欄位本身又是一個 `struct`，從更內層的欄位 move 出值也一樣會讓外層值不完整，因此同樣不允許。

限制的是從欄位 **move** 出值；以下操作仍然可以：

- move 整個 `resource`。
- 借用欄位，例如 `&resource.name`。
- 複製有實作 `Copy` 的欄位，例如 `resource.id`。

## 重點整理

- Rust 會在值離開作用域時自動丟棄它。
- `drop(value)` 取得值的所有權，讓你在作用域結束前提前丟棄它。
- 外層值被丟棄時，它所擁有的內部值也會被自動丟棄。
- `Drop` 的 `.drop()` 方法讓你在內部值被丟棄前執行額外動作；它由 Rust 自動執行，不能直接呼叫。
- 實作 `Drop` 的型別不能部分 move，但仍然可以 move 整個值、借用欄位或複製 `Copy` 欄位。
