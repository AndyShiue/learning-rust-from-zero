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
    print_length("hello");            // &str
    print_length(String::from("hi")); // String
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

### 為什麼 `AsRef` 用 `impl AsRef<T>` 但 `AsMut` 用 `&mut impl AsMut<T>`？

`AsRef` 的 `as_ref` 只需要 `&self`，所以把值傳進來完全沒問題——函數內部借用一下就好，呼叫端的值不受影響（如果是 `Copy` 的話），或者你本來就打算把值 move 進來。

但 `AsMut` 不一樣。如果你寫 `fn foo(buf: impl AsMut<[u8]>)`，值會被 move 進來——呼叫端用完就沒了。你都特地傳 `&mut` 了，就是想改完之後繼續用，所以參數寫成 `&mut impl AsMut<[u8]>`，借用它的可變參考就好，不需要 move。

那你可能會想：「`&mut Vec<u8>` 又不是 `Vec<u8>`，為什麼 `&mut Vec<u8>` 能當成 `AsMut<[u8]>` 用？」答案是標準庫有這個 blanket implementation：

```rust,ignore
impl<T, U> AsMut<U> for &mut T
where
    T: AsMut<U> + ?Sized,
    U: ?Sized,
{ ... }
```

意思是：如果 `T` 實作了 `AsMut<U>`，那 `&mut T` 也自動實作 `AsMut<U>`。所以 `&mut Vec<u8>` 能直接當 `AsMut<[u8]>` 用。

### 跟 `Deref` 的差別

`Deref` 是自動的——編譯器幫你加 `*`，你不用寫任何東西。`AsRef` 是手動呼叫 `.as_ref()`。

更重要的差別：每個型別只能有一個 `Deref` 目標（`String` `deref` 成 `str`），但可以實作多個 `AsRef`（`String` 同時是 `AsRef<str>` 和 `AsRef<[u8]>`）。`AsMut` 同理。

### 什麼時候用

寫函數參數想泛化接受多種型別的時候，用 `impl AsRef<T>` 和 `&mut impl AsMut<T>`。標準庫到處都在用。

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
    // AsRef<str>：接受 &str 和 String
    describe("hello");
    describe(String::from("你好"));

    // AsRef<[u8]>：接受 Vec<u8>、String 等
    count_bytes(vec![1, 2, 3]);
    count_bytes(String::from("hi"));
}
```

## 重點整理

- `AsRef<T>`：便宜地借用成 `&T`，用 `.as_ref()` 呼叫
- `AsMut<T>`：便宜地借用成 `&mut T`，用 `.as_mut()` 呼叫
- `AsRef` 參數用 `impl AsRef<T>`（傳值），`AsMut` 參數用 `&mut impl AsMut<T>`（借用，改完呼叫端還能繼續用）
- `&mut T` 之所以能當 `impl AsMut<U>` 用，是因為標準庫的 blanket implementation
- 一個型別可以實作多個 `AsRef` / `AsMut`（`Deref` / `DerefMut` 只能一個目標）
- 標準庫大量使用
