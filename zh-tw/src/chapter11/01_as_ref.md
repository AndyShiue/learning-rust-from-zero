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
    print_length(&text);
    println!("{text}"); // 仍然可以使用
}
```

標準庫已經幫很多型別實作了 `AsRef`：

- `String: AsRef<str>`
- `String: AsRef<[u8]>`
- `Vec<T>: AsRef<[T]>`

### `AsMut`

`AsMut<T>` 是可變版本，借用成 `&mut T`：

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

### 誰擁有傳入的參數？

`AsRef` 和 `AsMut` 只描述一個型別能提供哪種參考，不會決定函數是否取得參數的所有權。所有權關係取決於參數型別，以及呼叫者實際傳入什麼。

雖然 `s: impl AsRef<str>` 是傳值參數，但 `impl AsRef<str>` 代表的實際型別本身也可以是參考。在 `print_length(&text)` 中，該型別是 `&String`，所以函數只會收到參考，之後仍然可以使用 `text`。因此，當呼叫者想保留一個值時，通常會傳入 `&value`。

我們也可以將參數寫成 `s: &impl AsRef<str>`，強制呼叫者只能借用。不過，`s: impl AsRef<str>` 更有彈性：呼叫者可以傳入參考以保留原本的值，也可以在不再需要某個值時直接交出所有權。

使用 `AsMut` 參數的函數通常是想修改呼叫者原本擁有的值，而不會想拿走該值的所有權。因此，`fill_zeros` 在參數外層加上 `&mut`，要求呼叫者提供可變借用。外層的 `&mut` 決定函數如何接收 buffer，`AsMut<[u8]>` 則表示該 buffer 能提供一個 `&mut [u8]`。在 `fill_zeros(&mut v)` 中，`impl AsMut<[u8]>` 代表 `Vec<u8>`，而 `buf.as_mut()` 會產生迴圈所需的可變切片。

### 跟 `Deref` 的差別

`Deref` 是在 `deref` coercion 和 method call 這些地方被自動使用的：Rust 幫你穿過值去借用。`AsRef` 則是手動呼叫 `.as_ref()`。

更重要的差別：每個型別只能有一個 `Deref` 目標（`String` 的 target 是 `str`），但可以實作多個 `AsRef`（`String` 同時是 `AsRef<str>` 和 `AsRef<[u8]>`）。`AsMut` 同理。

### 什麼時候用

當函數需要用同一種方式借用多種輸入型別時，可以使用 `AsRef<T>` 或 `AsMut<T>`。通常，`AsRef` 參數會寫成 `impl AsRef<T>`，`AsMut` 參數則會寫成 `&mut impl AsMut<T>`。前者讓呼叫者能傳入擁有的值或參考，後者則能修改呼叫者現有的值而不取得所有權。只有當函數刻意需要不同的所有權關係時，才使用其他形式。

## 範例程式碼

```rust,editable
fn describe(s: impl AsRef<str>) {
    let s = s.as_ref();
    println!("「{}」有 {} 個字元", s, s.chars().count());
}

fn count_bytes(data: impl AsRef<[u8]>) {
    println!("共 {} bytes", data.as_ref().len());
}

fn main() {
    let message = String::from("你好");
    describe(&message);
    println!("原始內容：{message}");

    let numbers = vec![1, 2, 3];
    count_bytes(&numbers);
    println!("原始內容：{numbers:?}");
}
```

## 重點整理

- `AsRef<T>`：便宜地借用成 `&T`，用 `.as_ref()` 呼叫。
- `AsMut<T>`：便宜地借用成 `&mut T`，用 `.as_mut()` 呼叫。
- `AsRef` 和 `AsMut` 不決定所有權；所有權由參數型別和呼叫者傳入的引數決定。
- 傳值的 `impl AsRef<T>` 參數仍然可以接收參考，讓呼叫者保留原本的值。
- `AsMut` 參數通常會在外層加上 `&mut`，修改呼叫者現有的值而不取得所有權。
- 一個型別可以實作多個 `AsRef` / `AsMut`（`Deref` / `DerefMut` 只能一個目標）。
- 標準庫大量使用。
