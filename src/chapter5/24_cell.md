# `Cell<T>`

## 本集目標

學會用 `Cell<T>` 在不可變參考的情況下修改值，理解它的限制。

## 概念說明

第 4 章學了借用規則：要嘛一個 `&mut`，要嘛多個 `&`，不能同時。這很安全，但有時候你在只有 `&`（不可變參考）的情況下，還是想修改值。

### `Cell` 的概念

`Cell<T>` 提供一種「繞過借用規則」的方式——它用 `.get()` 取值、`.set(v)` 設值，**不需要可變參考**。

```rust,editable
use std::cell::Cell;

fn main() {
    let x = Cell::new(42);
    x.set(100);              // 不需要 mut！
    println!("{}", x.get()); // 100
}
```

但 `Cell` 有一個重要的限制：

### `T` 必須是 `Copy`

`Cell<T>` 的 `.get()` 會把值**複製一份**出來（不是借用）。所以 `T` 必須實作 `Copy`。

你不能用 `Cell<String>`，因為 `String` 不是 `Copy`。只能用 `Copy` 的型別（`i32`、`f64`、`bool` 等）。

### 為什麼不要用 mut？

有些情況下你不方便拿到 `&mut`。比如一個 `struct` 被多處共享參考（`&self`），但你想修改裡面的某個計數器。`Cell` 就很適合這種場景。

### `Rc` 就是用 `Cell` 實作的

上一集學的 `Rc<T>` 需要一個參考計數器——每次 `clone` 時計數 +1，`drop` 時計數 -1。但 `Rc` 對外只提供 `&self`（不可變參考），計數器卻需要被修改。怎麼辦？答案就是用 `Cell`！`Rc` 內部的計數器就是 `Cell<usize>`，所以即使只有 `&self` 也能更新計數。

## 範例程式碼

```rust,editable
use std::cell::Cell;

struct Counter {
    count: Cell<i32>,
    name: String,
}

impl Counter {
    fn new(name: String) -> Counter {
        Counter {
            count: Cell::new(0),
            name,
        }
    }

    // 注意：只需要 &self，不需要 &mut self
    fn increment(&self) {
        let current = self.count.get();
        self.count.set(current + 1);
    }

    fn get_count(&self) -> i32 {
        self.count.get()
    }
}

fn main() {
    // 基本用法
    let x = Cell::new(42);
    println!("原始值：{}", x.get());

    x.set(100);
    println!("修改後：{}", x.get());

    // 在 struct 裡使用 Cell
    let counter = Counter::new(String::from("訪問次數"));

    // 只有 &counter（不可變參考），但可以修改 count
    counter.increment();
    counter.increment();
    counter.increment();

    println!("{} 的計數：{}", counter.name, counter.get_count());
}
```

## 重點整理

- `Cell<T>` 讓你在不需要 `&mut` 的情況下修改值
- `.get()` 複製值出來，`.set(v)` 寫入新值
- **T 必須是 `Copy`**——因為 `get` 是複製，不是借用
- 適合用在「只有 `&self` 但想修改某個欄位」的場景
