# `use` bound

## 本集目標

理解 return-position `impl Trait` 的隱藏型別會捕捉哪些泛型參數，學會用 `use<...>` 明確限制捕捉集合。

> 本集是**第 5 章 `impl Trait` 與生命週期**的補充。

## 概念說明

第 5 章看過在回傳位置使用 `impl Trait`：

```rust,noplayground
fn numbers() -> impl Iterator<Item = i32> {
    [1, 2, 3].into_iter()
}
#
# fn main() {}
```

呼叫者看到的 `impl Iterator<Item = i32>` 是一個 **opaque type**（不透明型別）：介面刻意不公開它的具體身分。函數體替它選定的具體型別則稱為 **hidden type**（隱藏型別）；本例的 hidden type 是 `std::array::IntoIter<i32, 3>`。Hidden type 本身不一定沒有名稱，只是被 opaque return type 隱藏起來。

如果函數帶有泛型參數，隱藏型別能不能使用那些參數？這就是「捕捉」要回答的問題。

### 隱藏型別確實借用了參數

```rust,editable
fn words<'a>(text: &'a str) -> impl Iterator<Item = &'a str> {
    text.split_whitespace()
}

fn main() {
    let text = String::from("Rust lifetime capture");

    for word in words(&text) {
        println!("{word}");
    }
}
```

真正回傳的是 `SplitWhitespace<'a>`，裡面保存對 `text` 的參考。因此隱藏型別必須能使用，也就是**捕捉** `'a`。

在 Rust 2024 edition 中，回傳位置的 `impl Trait` 預設會捕捉作用域內所有可用的 lifetime、型別與 `const` 泛型參數。

### 捕捉得比實際需要更多

但「允許捕捉」會反映在呼叫端的借用檢查上。即使目前的隱藏型別根本沒有使用某個參數，公開簽名若允許它捕捉，呼叫者就必須按照「可能有捕捉」來使用回傳值：

```rust,compile_fail
fn greeting<'a>(_name: &'a str) -> impl Fn() {
    || println!("哈囉！")
}

fn main() {
    let name = String::from("小明");
    let greet = greeting(&name);

    drop(name);
    greet();
}
```

閉包其實完全沒用到 `name`，但在 Rust 2024 的預設規則下，`impl Fn()` 被允許捕捉 `'a`。因此只看函數簽名的呼叫端會保守地認為 `greet` 可能仍借用 `name`，不讓我們先 `drop(name)`。

### `use<...>` 指定捕捉集合

`use<...>` bound 可以精確列出隱藏型別允許捕捉的泛型參數：

```rust,editable
fn greeting<'a>(_name: &'a str) -> impl Fn() + use<> {
    || println!("哈囉！")
}

fn main() {
    let name = String::from("小明");
    let greet = greeting(&name);

    drop(name);
    greet();
}
```

`use<>` 裡是空的，表示隱藏型別不允許捕捉任何泛型參數。現在簽名明確保證 `greet` 與 `'a` 無關，呼叫端就能先釋放 `name`。

這裡的 `use` 和匯入名稱的 `use std::...` 完全不同。它出現在 `impl Trait` 的 bound 列表中，工作是列出捕捉集合。

### 需要捕捉時要列出來

若隱藏型別真的使用了 `'a`，卻寫成 `use<>`，函數本身就無法通過編譯：

```rust,compile_fail
fn text_length<'a>(text: &'a str) -> impl Fn() -> usize + use<> {
    move || text.len()
}
#
# fn main() {}
```

閉包保存了 `text`，所以隱藏型別使用 `'a`。把 `'a` 加進捕捉集合即可：

```rust,editable
fn text_length<'a>(text: &'a str) -> impl Fn() -> usize + use<'a> {
    move || text.len()
}

fn main() {
    let text = String::from("被捕捉的資料");
    let get_length = text_length(&text);
    println!("{}", get_length());
}
```

`use<'a>` 表示隱藏型別可以使用 `'a`。這次 `get_length` 確實借用 `text`，所以它存在期間不能先釋放 `text`。

### 型別與 `const` 泛型也能捕捉

`use<...>` 不只放生命週期，也能放型別參數、`const` 參數，以及 method 中的 `Self`：

```rust,editable
fn repeat<T, const N: usize>(value: T) -> impl Iterator<Item = T> + use<T, N>
where
    T: Clone,
{
    std::iter::repeat_n(value, N)
}

fn main() {
    let values: Vec<_> = repeat::<_, 3>(String::from("Rust")).collect();
    println!("{values:?}");
}
```

目前一個 `impl Trait` 最多只能有一組 `use<...>`，而且作用域內的型別與 `const` 泛型參數都必須列入。此外，如果回傳型別的其他部分已經用到某段生命週期，也要把它列進 `use<...>`。例如 `impl Iterator<Item = &'a str> + use<'a>` 中，`Item = &'a str` 已經用到 `'a`，所以不能改寫成 `use<>`。清單中的生命週期要寫在型別與 `const` 泛型參數之前。若清單不完整或順序不對，編譯器會直接指出問題。

### 什麼時候值得寫？

一般函數若確實回傳借用參數的迭代器、閉包或 `Future`，預設捕捉通常正合需要，不必每次都寫 `use<...>`。

當函數**接受一個帶生命週期的參數，但回傳值實際上與它無關**，預設捕捉可能讓呼叫端認為回傳值仍持有參考，因而延後釋放原本的值。這時 `use<>` 能把 API 的承諾說得更精準，也讓呼叫端更早使用或釋放原本的值。

## 範例程式碼

```rust,editable
fn borrowed_words<'a>(
    text: &'a str,
) -> impl Iterator<Item = &'a str> + use<'a> {
    text.split_whitespace()
}

fn fixed_numbers<'a>(
    _label: &'a str,
) -> impl Iterator<Item = i32> + use<> {
    [1, 2, 3].into_iter()
}

fn main() {
    let text = String::from("一 二 三");
    let words: Vec<_> = borrowed_words(&text).collect();
    println!("借用文字：{words:?}");

    let label = String::from("不會被迭代器使用");
    let numbers = fixed_numbers(&label);

    // use<> 保證 numbers 沒捕捉 label 的生命週期。
    drop(label);
    println!("固定數字：{:?}", numbers.collect::<Vec<_>>());
}
```

## 重點整理

- return-position `impl Trait` 在介面上是 opaque type，背後則有一個由函數體決定的隱藏具體型別。
- 捕捉某個泛型參數，表示隱藏型別被允許使用它。
- Rust 2024 edition 預設捕捉作用域內所有 lifetime、型別與 `const` 泛型參數。
- `impl Trait + use<'a, T, N>` 可以精確列出允許捕捉的參數；`use<>` 表示不捕捉任何參數。
- 若隱藏型別真的使用未列入的參數，函數本身會編譯失敗。
- 精確排除不必要的生命週期捕捉，可以避免呼叫端參考的生命週期被保守地延長。
