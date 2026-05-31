# DST 簡介

## 本集目標

理解什麼是動態大小型別（DST），以及 `Sized`、`?Sized` 在泛型中的意義。

> 本集是**第 5 章**的補充。

## 概念說明

（本集提到的指標大小以 64 位元系統為準——現在絕大多數電腦都是 64 位元。）

在 Rust 的型別系統裡，大部分型別的大小在編譯期就已知——`i32` 是 4 bytes、`bool` 是 1 byte、`(i32, i32)` 是 8 bytes。但有些型別的大小**在編譯期是未知的**，這就是 **DST（Dynamically Sized Types）**，動態大小型別。

### 常見的 DST

你其實已經見過它們了：

- **`str`**：字串切片的「內容」型別。`"hello"` 是 5 bytes，`"哈囉"` 是 6 bytes，長度不固定
- **`[T]`**：陣列切片的「內容」型別。`[i32]` 可能是 3 個元素也可能是 100 個

因為大小不固定，你**不能**直接把它們當作值使用：

```rust,compile_fail
fn main() {
    let s: str = "hello";       // 編譯錯誤！
    let arr: [i32] = [1, 2, 3]; // 編譯錯誤！
}
```

### 怎麼用？靠指標！

DST 必須藏在某種指標後面：

- `&str`、`&[T]` — 參考
- `Box<str>`、`Box<[T]>` — 指向 heap 的指標

這些指標是所謂的**胖指標（fat pointer）**——它們不只存一個位址，還多存了一個長度資訊：

```ignore
一般指標：[位址]       （8 bytes）
胖指標：　[位址][長度] （16 bytes）
```

所以 `&str` 實際上佔 16 bytes：8 bytes 指向字串資料，8 bytes 記錄長度。

### `Sized` `trait`

Rust 有一個特殊的 trait 叫 `Sized`，表示「這個型別的大小在編譯期已知」。**絕大多數型別都自動實作了 `Sized`**。

而且——這是很多人不知道的——**泛型參數預設有 `Sized` bound**：

```rust,ignore
fn print_it<T>(val: T) { ... }
// 其實等同於
fn print_it<T: Sized>(val: T) { ... }
```

這很合理，因為如果 `T` 的大小未知，函數根本不知道要在 stack 上分配多少空間。

### `?Sized`：放寬限制

有時候你希望泛型參數可以接受 DST，這時候用 `?Sized` 來放寬限制：

```rust,ignore
fn print_it<T: ?Sized>(val: &T) { ... }
//                     ^^^^^^^ 注意：必須透過參考
```

`?Sized` 的意思是「`T` 可以是 `Sized`，也可以不是」。但因為大小可能未知，你通常只能透過參考或智慧指標來使用 `T`。

### `trait` 裡的 `Self` 預設是 `?Sized`

前面說泛型參數 `T` 預設有 `Sized` bound。但 `trait` 裡的 `Self` 是個例外——它預設是 `?Sized` 的，也就是說 `Self` 不一定是 `Sized`。

還記得第 4 章第 8 集介紹的 `Clone` 嗎？它的方法是 `fn clone(&self) -> Self`——直接回傳 `Self`。由於 `Self` 預設可能不是 `Sized`，而回傳的型別必須有已知大小，所以 `Clone` 實際上的定義是：

```rust,noplayground
trait Clone: Sized {
    fn clone(&self) -> Self;
}
#
# fn main() {}
```

### 回頭看第 5 章的 `Cow`

第 5 章最後一集教 `Cow` 的時候，我們用的也是簡化版的定義：

```rust,noplayground
// 第 5 章提供的簡化版
pub enum Cow<'a, B>
where
    B: 'a + ToOwned,
{
    Borrowed(&'a B),
    Owned(B::Owned),
}
#
# fn main() {}
```

如果你試過要把 `str` 或 `[T]` 放進 `Cow`——例如寫 `Cow<'_, str>`——你會發現編譯不過。因為泛型參數 `B` 預設要求 `Sized`，而 `str` 不是 `Sized`。

加上 `?Sized` 就能解決：

```rust,noplayground
pub enum Cow<'a, B>
where
    B: 'a + ToOwned + ?Sized,
{
    Borrowed(&'a B),
    Owned(B::Owned),
}
#
# fn main() {}
```

`Borrowed(&'a B)` 裡的 `B` 已經在參考後面，所以即使 `B` 是 DST 也沒問題——胖指標會幫你搞定。

### `&mut [T]` 與 `&mut str`

DST 也可以拿可變參考。`&mut [T]` 很實用——你可以修改切片裡的元素：

```rust,noplayground
# fn main() {
    let mut arr = [1, 2, 3, 4, 5];
    let slice: &mut [i32] = &mut arr[1..4];
    slice[0] = 99;  // arr 變成 [1, 99, 3, 4, 5]
# }
```

但 `&mut str` 就很沒用了。雖然語法上合法，但你幾乎做不了什麼。原因是：

**首先，`&mut str` 和 `&mut [T]` 一樣不能改長度。** `str` 是 DST，`&mut str` 是一個胖指標（位址 + 長度），長度是參考的一部分。`&mut str` 只是借用——你不擁有那塊記憶體的配置權，沒辦法讓它變大或變小。想想 `&'static mut str`：它指向的是程式檔案裡的唯讀區段，你不可能讓那塊記憶體變大。要改長度只能透過擁有記憶體的 `String`。

**再來，連改內容都受限。** UTF-8 編碼裡，一個字元可能佔 1~4 bytes：

- `'a'` → 1 byte
- `'é'` → 2 bytes
- `'哈'` → 3 bytes

假設你有 `"哈囉"`（6 bytes），想把 `'哈'` 改成 `'a'`——`'a'` 只有 1 byte，但 `'哈'` 佔了 3 bytes，你沒辦法就地替換，因為長度不同。如果硬改了第一個 byte 卻沒處理後面的，UTF-8 的多 byte 序列就斷了。而 Rust 的 `str` 保證內容一定是合法的 UTF-8，破壞這個保證會導致未定義行為。

所以標準庫裡 `&mut str` 上的方法少得可憐，基本上只有 `make_ascii_uppercase()` 和 `make_ascii_lowercase()` 這類「不會改變 byte 長度」的操作（ASCII 字母的大小寫轉換剛好是 1 byte 對 1 byte）。要修改字串，還是用 `String` 吧。

### DST 與 `Deref`

第 5 章也介紹了 `Deref` `trait`。`String` 和 `Vec<T>` 也實作了 `Deref`，它們解參考得到的正是 DST：

- `String` 實作了 `Deref`，`Deref::deref(&String)` 回傳 `&str`
- `Vec<T>` 實作了 `Deref`，`Deref::deref(&Vec<T>)` 回傳 `&[T]`

也就是說解參考 `String` 得到的是 `str`，解參考 `Vec<T>` 得到的是 `[T]`。雖然 DST 沒辦法直接放在變數裡，但 `deref` coercion 發生在**參考的層級**：`&String` 轉成 `&str`，`&Vec<T>` 轉成 `&[T]`。轉換的結果就是一個胖指標，帶著位址和長度，不需要知道 DST 的實際大小。

這就是為什麼一個接受 `&str` 的函數可以直接傳 `&String` 進去，接受 `&[T]` 的函數可以直接傳 `&Vec<T>` 進去——背後的機制正是 DST + `Deref` 的組合。

### 看不懂指標？

如果你對「指標」、「胖指標」、「位址」這些概念的理解還是很模糊，別擔心——下一章的第一集會正式介紹指標到底是什麼。

## 範例程式碼

```rust,editable
use std::fmt::Display;

// 預設：T 必須是 Sized
fn print_sized<T: Display>(val: T) {
    println!("Sized 值：{}", val);
}

// 放寬：T 可以是 DST，但必須透過參考
fn print_unsized<T: Display + ?Sized>(val: &T) {
    println!("可能是 DST：{}", val);
}

// 展示 64 位元電腦上的胖指標大小
fn show_pointer_sizes() {
    use std::mem::size_of;

    println!("--- 指標大小比較 ---");
    println!("&i32     = {} bytes", size_of::<&i32>());     // 8
    println!("&[i32]   = {} bytes", size_of::<&[i32]>());   // 16（胖指標）
    println!("&str     = {} bytes", size_of::<&str>());     // 16（胖指標）
    println!("Box<i32> = {} bytes", size_of::<Box<i32>>()); // 8
    println!("Box<str> = {} bytes", size_of::<Box<str>>()); // 16（胖指標）
}

fn main() {
    // Sized 值：一般型別
    print_sized(42);
    print_sized(String::from("hello"));

    // ?Sized：可以接受 &str（str 是 DST）
    print_unsized("hello");                // T = str（DST）
    print_unsized(&42);                    // T = i32（Sized，也可以）
    print_unsized(&String::from("world")); // T = String（Sized）

    // &str 和 &[T] 是胖指標
    show_pointer_sizes();

    // str 和 [T] 不能直接當值用
    // let s: str = *"hello";    // 編譯錯誤！
    // let a: [i32] = *&[1,2,3]; // 編譯錯誤！

    // 但透過參考就沒問題
    let s: &str = "hello";
    let a: &[i32] = &[1, 2, 3];
    println!("\n&str = {}", s);
    println!("&[i32] 長度 = {}", a.len());

    // Box<str> 也可以
    let boxed: Box<str> = String::from("boxed string").into_boxed_str();
    println!("Box<str> = {}", boxed);
}
```

## 重點整理

- **DST（Dynamically Sized Types）**：大小在編譯期未知的型別，如 `str`、`[T]`
- DST 不能直接當值使用，必須透過指標：`&str`、`&[T]`、`Box<str>` 等
- 指向 DST 的指標是**胖指標（fat pointer）**：位址 + 長度，在 64 位元電腦上佔 16 bytes
- **`Sized`**：表示型別大小在編譯期已知；泛型參數預設有 `T: Sized` bound
- **`?Sized`**：放寬限制，讓泛型參數可以接受 DST（但必須透過參考使用）
- `trait` 裡的 `Self` 預設是 `?Sized`；如果方法需要回傳 `Self`，要在 `trait` 上加 `: Sized`（如 `Clone: Sized`）
- `Cow<'a, B>` 中的 `B: ?Sized` 就是為了讓 `B` 可以是 `str` 或 `[T]` 等 DST
- `String` 和 `Vec<T>` 的 `Deref` 分別得到 DST `str` 和 `[T]`，`deref` coercion 讓 `&String` → `&str`、`&Vec<T>` → `&[T]` 成為可能
