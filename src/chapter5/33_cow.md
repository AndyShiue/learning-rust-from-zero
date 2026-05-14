# `Cow<'a, B>`

## 本集目標

學會使用 `Cow<'a, str>` 實現「能借就借，需要時才 `clone`」的彈性策略。

## 概念說明

有些函數有時候可以直接回傳借用的資料，有時候又需要回傳擁有的資料。

### 舉個例子

假設你有一個函數，幫字串加上問候語。如果字串已經有「你好」開頭，直接回傳原字串就好（借用）。如果沒有，就要建一個新的字串（擁有）。

回傳型別是 `&str` 還是 `String`？兩個都不完全對。

### `Cow` 來拯救

`Cow` 的全名是 **`Clone` on write**（寫入時才複製）。它定義在 `std::borrow` 模組裡。來看它的定義（省略了一些我們還沒學的部分）：

```rust,noplayground
enum Cow<'a, B>
where
    B: 'a + ToOwned,
{
    Borrowed(&'a B),
    Owned(B::Owned), // ToOwned 的 associated type
}
#
# fn main() {}
```

一行一行看：

- **`'a`**：生命週期參數，代表借用資料的壽命
- **`B: 'a`**：lifetime bound（前幾集學的），`B` 裡面的參考必須活得過 `'a`
- **`B: ToOwned`**：`trait` bound，`B` 必須實作 `ToOwned`
- **`Borrowed(&'a B)`**：借用的版本，存一個 `&'a B`
- **`Owned(...)`**：擁有所有權的版本，型別由 `ToOwned` 的 associated type `Owned` 決定

`ToOwned` 是一個 `trait`，它有一個 associated type `Owned`，代表「擁有所有權版本的型別」。

對 `str` 來說：
- `str` 實作了 `ToOwned`，`type Owned = String`
- 所以 `Cow<'a, str>` = `Borrowed(&'a str)` 或 `Owned(String)`

對 `[T]` 來說：
- `[T]` 實作了 `ToOwned`，`type Owned = Vec<T>`
- 所以 `Cow<'a, [T]>` = `Borrowed(&'a [T])` 或 `Owned(Vec<T>)`

### `Cow` 實作了 `Deref`

這是使用 `Cow` 時最關鍵的一點：`Cow<'a, B>` 實作了 `Deref<Target = B>`。也就是說，不管裡面是 `Borrowed(&str)` 還是 `Owned(String)`，你都可以直接把 `Cow<'_, str>` 當成 `&str` 來用——呼叫 `&str` 的所有方法、傳給接受 `&str` 的函數，完全不用管它實際上是借用還是擁有。

```rust
# use std::borrow::Cow;
#
# fn main() {
    let cow: Cow<'_, str> = Cow::Owned(String::from("hello"));
    // 直接當 &str 用，Deref 自動處理
    println!("長度：{}", cow.len());
    println!("大寫：{}", cow.to_uppercase());
# }
```

因為有 `Deref`，呼叫端通常不需要在意裡面到底是借用還是擁有——直接當 `&str` 用就好。

### 常用方法

- **`to_mut()`**：如果是 `Borrowed`，先 `clone` 成 `Owned`，然後回傳可變參考。如果已經是 `Owned`，直接回傳它的可變參考。這就是「寫入時才複製」的核心
- **`into_owned()`**：不管是 `Borrowed` 還是 `Owned`，都轉成擁有所有權的值。`Borrowed` 會 `clone` 一份，`Owned` 則直接拿走

## 範例程式碼

```rust
use std::borrow::Cow;

// 如果字串已經是「你好」開頭，直接借用回傳
// 否則建立新的 String
fn ensure_greeting(s: &str) -> Cow<'_, str> {
    if s.starts_with("你好") {
        // 不需要修改，直接借用
        Cow::Borrowed(s)
    } else {
        // 需要修改，建立新字串
        let mut greeting = String::from("你好，");
        greeting.push_str(s);
        Cow::Owned(greeting)
    }
}

fn main() {
    // 已經有「你好」開頭 → 借用，不花成本
    let s1 = "你好世界";
    let result1 = ensure_greeting(s1);
    println!("{}", result1);

    // 沒有「你好」開頭 → 建立新字串
    let s2 = "Rust";
    let result2 = ensure_greeting(s2);
    println!("{}", result2);

    // 可以判斷是借用還是擁有
    match ensure_greeting(s1) {
        Cow::Borrowed(s) => println!("借用的：{}", s),
        Cow::Owned(s) => println!("擁有的：{}", s),
    }

    match ensure_greeting(s2) {
        Cow::Borrowed(s) => println!("借用的：{}", s),
        Cow::Owned(s) => println!("擁有的：{}", s),
    }

    // to_mut：寫入時才複製
    let mut cow: Cow<'_, str> = Cow::Borrowed("hello");
    // 現在是 Borrowed，呼叫 to_mut 會先 clone 成 Owned
    cow.to_mut().push_str(" world");
    println!("{}", cow); // "hello world"

    // into_owned：轉成擁有的 String
    let cow2: Cow<'_, str> = Cow::Borrowed("bye");
    let owned: String = cow2.into_owned();
    println!("{}", owned);
}
```

## 重點整理

- `Cow<'a, str>` 可以是借用（`&str`）或擁有（`String`），視情況而定
- `Cow` 利用 `ToOwned` `trait` 的 associated type 來決定擁有版本的型別（`str` → `String`、`[T]` → `Vec<T>`）
- `Cow` 實作了 `Deref`，`Cow<'a, str>` 不管是 `Borrowed` 還是 `Owned` 都能直接當 `&str` 用——這是它最大的優點
- `to_mut()`：寫入時才複製（Borrowed → `clone` 成 `Owned` → 回傳可變參考）
- `into_owned()`：不管哪種都轉成擁有所有權的值
- 適合用在「大部分時候不修改，偶爾需要修改」的場景

恭喜你完成了第五章！🎉 這一章的內容非常紮實——從泛型、`trait` bound、生命週期，到 `Box`、`Rc` 等智慧指標與 `Deref` 機制，再到 `Cell`、`RefCell` 的 interior mutability，以及 `Display`、associated type、`Cow`。這些是 Rust 型別系統最強大的武器，也是讀懂標準庫原始碼的基礎。下一章我們將進入閉包與迭代器——Rust 最優雅的函數式程式設計風格！
