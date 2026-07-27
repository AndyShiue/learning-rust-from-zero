# `AsRef<T>` / `AsMut<T>`

## 本集目標

學會用 `AsRef` 和 `AsMut` 讓函數接受多種型別。

## 概念說明

### 動機

假設你寫了一個函數接受 `&str`：

```rust,noplayground
fn print_length(s: &str) {
    println!("長度：{}", s.len());
}
#
# fn main() {}
```

呼叫者手上有 `String`，因為 `Deref` 的關係，`&String` 會自動轉成 `&str`，所以沒問題。但如果你想寫一個函數，讓它同時接受 `String`、`&str`、甚至其他型別呢？

### `AsRef`

`AsRef<T>` `trait` 表示「我能便宜地借用成 `&T`」：

```rust,editable
fn print_length(s: impl AsRef<str>) {
    println!("長度：{}", s.as_ref().len());
}

fn main() {
    let text = String::from("hello");

    print_length("嗨");                  // &str
    print_length(&text);
    print_length(String::from("你好"));  // String

    println!("{text}"); // 仍然可以使用
}
```

標準庫已經幫很多型別實作了 `AsRef`：

- `String: AsRef<str>`
- `String: AsRef<[u8]>`
- `Vec<T>: AsRef<[T]>`

### `AsMut`

`AsMut<T>` 是可變版本，借用成 `&mut T`：

一般來說，我們使用 `AsMut` 是為了修改呼叫者原本擁有所有權的值，而不是取得該值的所有權。因此，參數通常會寫成 `&mut impl AsMut<T>`，而不是 `impl AsMut<T>`。

```rust,editable
fn fill_zeros(buf: &mut impl AsMut<[u8]>) {
    for byte in buf.as_mut() {
        *byte = 0;
    }
}

fn main() {
    let mut v = vec![1, 2, 3];
    fill_zeros(&mut v);
    println!("{:?}", v); // [0, 0, 0]
}
```

### 所有權與使用時機

`AsRef` 和 `AsMut` 只描述一個型別能提供哪種參考，不會決定函數是否取得參數的所有權。所有權關係取決於參數型別，以及呼叫者實際傳入什麼。

雖然 `s: impl AsRef<str>` 是傳值參數，但實際傳入的型別也可以是參考。`print_length(&text)` 只借用 `text`，所以之後仍能使用；如果直接傳入 `text`，則會移動它。這種寫法讓呼叫者自行選擇傳入擁有所有權的值或參考。

在 `fill_zeros` 中，外層的 `&mut` 表示函數只借用 buffer，`AsMut<[u8]>` 則表示該 buffer 能提供一個 `&mut [u8]`。

### 跟 `Deref` 的差別

`Deref` 是在 `deref` coercion 和 method call 這些地方被自動使用的：Rust 幫你穿過值去借用。`AsRef` 則是手動呼叫 `.as_ref()`。

更重要的差別：每個型別只能有一個 `Deref` 目標（`String` 的 target 是 `str`），但可以實作多個 `AsRef`（`String` 同時是 `AsRef<str>` 和 `AsRef<[u8]>`）。`AsMut` 同理。

當函數需要以同一種方式借用多種輸入型別時，就適合使用 `AsRef<T>` 或 `AsMut<T>`。

## 重點整理

- `AsRef<T>` 和 `AsMut<T>` 讓函數將多種輸入型別分別借用成 `&T` 和 `&mut T`。
- `AsRef` / `AsMut` 不決定所有權；`impl AsRef<T>` 可以接收擁有所有權的值或參考，而 `&mut impl AsMut<T>` 會借用並修改原值。
- 轉換時需手動呼叫 `.as_ref()` 或 `.as_mut()`；`Deref` 則可由 Rust 自動使用。
- 一個型別可以實作多個 `AsRef` / `AsMut`，但只能有一個 `Deref` 目標。
