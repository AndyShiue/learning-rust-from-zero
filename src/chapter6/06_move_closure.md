# `move` 閉包

## 本集目標

學會用 `move` 關鍵字強制閉包以 move 方式捕捉外部變數，理解它為什麼能解決生命週期問題。

## 概念說明

### 預設的捕捉行為

Rust 的閉包很聰明，會自動選擇「最輕量」的捕捉方式：

- 如果只讀取變數 → 用 `&T`（借用）
- 如果需要修改 → 用 `&mut T`（可變借用）
- 如果需要消耗 → 用 `T`（move）

大部分時候這很好用。但有些情況下，借用會造成生命週期的問題。

### 問題場景：回傳閉包

假設你想寫一個函數，回傳一個閉包：

```rust,compile_fail
fn make_greeter(name: String) -> impl Fn() {
    || println!("Hello, {}!", name) // 編譯錯誤！
}
#
# fn main() {}
```

為什麼錯？因為閉包預設用借用的方式捕捉 `name`（`&name`），但 `name` 是函數的局部變數，函數結束後就被丟掉了。閉包裡的借用就變成了懸垂參考——第 4 章的老朋友。

### move 關鍵字

加上 `move` 就解決了：

```rust,editable
fn make_greeter(name: String) -> impl Fn() {
    move || println!("Hello, {}!", name)
}
#
# fn main() {}
```

`move` 告訴 Rust：「不要用借用，把所有捕捉的變數都**搬進**閉包裡。」這樣 `name` 就歸閉包所有了，不管原本的作用域怎麼結束，閉包都能繼續用 `name`。

### move 閉包的匿名 struct

回想前幾集——閉包是匿名 `struct`。沒有 `move` 的時候，`struct` 的欄位可能是參考（`&T` 或 `&mut T`）；加了 `move` 之後，**所有欄位都變成擁有所有權的值**（`T`）：

```rust,noplayground
# fn main() {
    // 沒有 move：閉包借用 name，struct 裡存的是參考
    let name = String::from("Alice");
    let greet = || println!("{}", name);
    // name 還能用，因為閉包只是借用

    // 有 move：name 被搬進 struct，閉包擁有它
    let name = String::from("Alice");
    let greet = move || println!("{}", name);
    // name 不能再用了，已經被搬進閉包裡
# }
```

因為所有欄位都是擁有所有權的，這個 `struct` 不借用任何東西，所以沒有 lifetime 的問題——可以安全地從函數回傳、存進 `struct`。

### `move` 不影響閉包是哪種 `Fn` `trait`

很多人會搞混：`move` 閉包不代表它是 `FnOnce`！

`move` 只影響**怎麼捕捉**，不影響**怎麼使用**：

```rust,editable
# fn main() {
    let name = String::from("Alice");
    let greet = move || println!("Hello, {}!", name);
    // name 被 move 進閉包了，但閉包只是「讀取」name
    // 所以這個閉包是 Fn，可以多次呼叫
    greet();
    greet();
# }
```

### 閉包自動實作的 `trait`

閉包能不能 `clone` 或 copy，取決於它捕捉的變數——跟 tuple 類似，如果裡面的東西都能 copy，整體就能 copy：

- 所有捕捉的變數都是 `Copy` → 閉包也是 `Copy`
- 所有捕捉的變數都是 `Clone` → 閉包也是 `Clone`
- 其他某些 `trait` 也是同理

```rust,editable
# fn main() {
    let x = 42;
    let f = move || x + 1; // x 是 i32（Copy），所以 f 也是 Copy
    let g = f; // Copy 了 f
    println!("{}", f()); // f 還能用
    println!("{}", g());
# }
```

## 範例程式碼

```rust,editable
// 回傳閉包時，通常需要 move
fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

fn make_counter(start: i32) -> impl FnMut() -> i32 {
    let mut count = start;
    move || {
        count += 1;
        count
    }
}

fn main() {
    // move 讓閉包擁有捕捉的值，可以安全回傳
    let add_five = make_adder(5);
    println!("10 + 5 = {}", add_five(10));
    println!("20 + 5 = {}", add_five(20));

    // move + FnMut：閉包擁有 count，並且每次修改它
    let mut counter = make_counter(0);
    println!("計數：{}", counter());
    println!("計數：{}", counter());
    println!("計數：{}", counter());

    // move 不代表 FnOnce
    let name = String::from("Bob");
    let greet = move || {
        println!("Hi, {}!", name); // 只是讀取 name，所以是 Fn
    };
    greet();
    greet(); // 可以多次呼叫，不是 FnOnce

    // 捕捉 Copy 型別的閉包可以 Copy
    let factor = 3;
    let multiply = move |x: i32| x * factor;
    let multiply_copy = multiply; // Copy 了
    println!("multiply(4) = {}", multiply(4)); // 原本的還能用
    println!("multiply_copy(4) = {}", multiply_copy(4));

    // 捕捉 String（非 Copy）的 move 閉包不能 Copy
    let label = String::from("result");
    let show = move |x: i32| {
        println!("{}: {}", label, x);
    };
    // let show2 = show; // 這會 move show，不是 Copy
    show(42);
}
```

## 重點整理

- `move` 強制閉包獲得所有捕捉變數的所有權，不依賴外部借用，適合需要長壽命的場景
- 回傳閉包時通常需要 `move`，避免懸垂參考
- `move` **不影響**閉包是 `Fn` / `FnMut` / `FnOnce`——那取決於閉包**怎麼使用**捕捉的值
- 閉包能否 `clone` / copy 取決於捕捉的變數是否全為 `Clone` / `Copy`
