# `Unpin` 與 `get_mut`

## 本集目標

搞懂 `Unpin` 是什麼、哪些型別自動是 `Unpin`，以及 `Unpin` 的型別怎麼用 `get_mut` 拿回普通的 `&mut`。

## 概念說明

### `Unpin` 是一個 auto trait

前兩集一直提到 `Unpin`，現在正式介紹它。`Unpin` 的意思是「**這個型別搬了不會壞，所以 `Pin` 對它其實沒什麼好限制的**」。

`Unpin` 是一個 **auto trait**（自動 trait），就像第 9 章的 `Send` / `Sync` 一樣——你不用手動實作，編譯器會自動判斷。規則很簡單：

- 普通手寫的 `Future`，只要欄位都是可以安全 move 的東西，通常就會**自動是 `Unpin`**。我們前面寫的 `Delay`、`Counter`、`JoinAll`、`JoinHandle` 全都是 `Unpin`——這也是為什麼它們的 `poll` 裡都能直接呼叫 `self.get_mut()`。
- 但 `async fn` / `async` block 產生的 `Future`**不能直接假設是 `Unpin`**。因為它可能是自我參照的狀態機（上上集那種），搬了會壞，所以編譯器**不**讓它自動 `Unpin`。

### `Unpin` 的型別可以 `get_mut`

`Pin` 的可變存取（拿回普通的 `&mut T`）是上一集留下來的部分。關鍵方法是 `get_mut`，它的型別大致是：

```rust,ignore
impl<'a, T: ?Sized> Pin<&'a mut T> {
    pub fn get_mut(self) -> &'a mut T
    where
        T: Unpin, // 只有 Unpin 的型別才給用
    { /* ... */ }
}
```

注意那個 `where T: Unpin`。意思是：只有「搬了不會壞」的型別，才能從 `Pin<&mut T>` 拿回普通的 `&mut T`。這很合理——既然搬了不會壞，那 `Pin` 的保護對它就是多餘的，乾脆放行。

對 `Unpin` 的型別來說，`get_mut` 完全沒問題：

```rust,editable
use std::pin::Pin;

struct Counter {
    count: u32,
}

fn main() {
    let mut counter = Counter { count: 0 };
    let pinned: Pin<&mut Counter> = Pin::new(&mut counter);

    // Counter 是 Unpin，所以可以用 get_mut 拿回普通的 &mut Counter
    let normal: &mut Counter = pinned.get_mut();
    normal.count += 1;
    println!("count = {}", normal.count);
}
```

這就是我們之前每個 `poll` 開頭 `let this = self.get_mut();` 能成功的原因——那些型別都是 `Unpin`。

### 不是 `Unpin` 的型別呢

如果一個型別**不是** `Unpin`，`get_mut` 就會被擋下來。我們可以用標準庫的 `PhantomPinned` 標記，手動做出一個 `!Unpin` 的型別來看效果（`async` 狀態機的 `!Unpin` 也是同樣道理）：

```rust,compile_fail
use std::marker::PhantomPinned;
use std::pin::Pin;

struct NotUnpin {
    data: String,
    _pin: PhantomPinned, // 這個標記讓型別退出 Unpin
}

fn main() {
    let mut value = NotUnpin { data: String::from("hi"), _pin: PhantomPinned };
    let pinned = unsafe { Pin::new_unchecked(&mut value) };
    let _normal = pinned.get_mut(); // 編譯錯誤：NotUnpin 不是 Unpin
}
```

編譯器會回報 `the trait Unpin is not implemented`。對這種型別，你只能透過接受 `Pin<&mut Self>` 的方法去操作它（例如自己在 `poll` 裡小心地處理），拿不到那個能隨便搬走它的普通 `&mut T`——這正是 `Pin` 想守住的防線。

### 哪些地方會要求 `Unpin`

整理一下到目前為止看到的、會要求 `Unpin` 的地方：

- `Pin::new`：建立 `Pin` 的安全版本，要求 `Unpin`。
- `Pin::get_mut` / `Pin` 的 `DerefMut`：拿回 `&mut T`，要求 `Unpin`。
- 很多接受 `Future` 的函數或方法（例如某些組合器），會要求傳進去的 `Future` 是 `Unpin`，否則你得先用 `Box::pin` 把它釘在 heap 上（`Box::pin` 出來的 `Pin<Box<T>>` 自己是 `Unpin`），或用下一集要講的 `pin!`。

下一集就來看 `pin!`——一個讓你不必 `Box::pin`、直接在 stack 上釘住 `Future` 的好用工具。

## 重點整理

- `Unpin` 是 auto trait，意思是「搬了不會壞」；編譯器自動判斷，不用手動實作。
- 普通手寫的 `Future`（欄位都可安全 move）通常自動是 `Unpin`；`async fn` / `async` block 的 `Future` 不能假設是 `Unpin`。
- `get_mut`（以及 `Pin` 的可變 `Deref`）要求 `T: Unpin`，才把 `Pin<&mut T>` 變回普通 `&mut T`。
- 我們前面 `poll` 裡的 `self.get_mut()` 能用，正是因為那些型別都是 `Unpin`。
- `!Unpin` 的型別（如含 `PhantomPinned` 或自我參照的 `async` 狀態機）不能 `get_mut`，只能透過 `Pin<&mut Self>` 的方法操作。
