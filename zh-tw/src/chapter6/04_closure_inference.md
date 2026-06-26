# 閉包種類的推斷

## 本集目標

理解 Rust 如何根據閉包體的內容，自動推斷一個閉包是 `FnOnce`、`FnMut` 還是 `Fn`。

## 正文

上一集我們手動用 `struct` 模擬了三種閉包，對應 `self`、`&mut self`、`&self`。但你寫閉包的時候從來不需要告訴 Rust「這是 `FnOnce`」或「這是 `FnMut`」——Rust 會自動判斷。

### 推斷規則

Rust 看的是**閉包體裡面對捕捉變數做了什麼**：

1. **如果閉包體裡 move 了捕捉的變數**（例如 `let s = captured_string;`）→ 這個閉包是 **`FnOnce`**，因為 move 走了就沒了，只能呼叫一次
2. **如果閉包體裡修改了捕捉的變數**（例如 `count += 1;`）→ 這個閉包是 **`FnMut`**，可以多次呼叫但需要 `&mut`
3. **如果閉包體只讀取捕捉的變數**（例如 `println!("{}", name);`）→ 這個閉包是 **`Fn`**，只需要 `&self`

Rust 會選**能接受最多種使用方式的那個**——如果只讀取，就給 `Fn`（因為 `Fn` 的閉包也能當 `FnMut` 和 `FnOnce` 用）。如果有修改，就變成 `FnMut`。如果有 move，就變成 `FnOnce`。

### 範例對照

```rust,noplayground
# fn main() {
    let name = String::from("Alice");

    // 只讀取 name → Fn
    let greet = || println!("Hi, {}!", name);

    // 修改 count → FnMut
    let mut count = 0;
    let mut increment = || { count += 1; };

    // move name → FnOnce
    let consume = || { let s = name; };
# }
```

你不需要寫任何標記——Rust 看閉包體就知道了。

### 捕捉多個變數時怎麼辦？

一個閉包可能同時捕捉多個變數，而且對每個變數的用法不同：

```rust,noplayground
# fn main() {
    let name = String::from("Alice");
    let mut count = 0;
    let closure = || {
        count += 1;           // 修改 count → 需要 &mut
        println!("{}", name); // 只讀取 name → 只需要 &
    };
# }
```

想像成 `struct` 的話，這個閉包的匿名 `struct` 會有兩個欄位：`count`（需要 `&mut`）和 `name`（只需要 `&`）。但呼叫閉包時只有一個 `self`——而 `&mut self` 裡面可以做 `&` 的操作，反過來不行——所以整個閉包是 `FnMut`（`&mut self`）。就像一個 method 接收 `&mut self`，但裡面不一定每個欄位都要改：

```rust,noplayground
struct Data<'a> {
    count: &'a mut i32,
    name: &'a String,
}

impl<'a> Data<'a> {
    fn increment_and_greet(&mut self) {
        *self.count += 1;                  // 修改 count
        println!("Hello, {}!", self.name); // 只讀取 name
    }
}
#
# fn main() {}
```

閉包也是同樣的道理。

同理，`FnOnce` 的 `self` 裡面的值當然也能取 `&` 或 `&mut`——擁有一個值就包含了可以借用它。

### 如果沒有捕捉任何變數呢？

沒有捕捉變數的閉包自動是 `Fn`，因為它不需要存取任何外部狀態：

```rust,noplayground
# fn main() {
    let add_one = |x: i32| x + 1; // Fn
# }
```

第 2 集提到的「不捕捉變數的閉包可以轉成函數指標」也是因為這個原因——它連匿名 `struct` 都不需要。

## 重點整理

- Rust 根據閉包體的內容自動推斷閉包的種類：move → `FnOnce`、修改 → `FnMut`、只讀 → `Fn`
- 不需要手動標記，編譯器會自動選擇能接受最多種使用方式的閉包
- 沒有捕捉變數的閉包是 `Fn`，也可以轉成函數指標
- `Fn` 的閉包可以傳給 `FnMut` 和 `FnOnce`；`FnMut` 可以傳給 `FnOnce`；反過來不行
