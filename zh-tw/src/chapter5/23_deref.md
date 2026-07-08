# Deref

## 本集目標

理解 `Deref` `trait`、`DerefMut` `trait` 和 Rust 的 `deref` coercion，以及智慧指標為什麼常常能當成它們裡面的值來用。

## 概念說明

### 對 `Rc` 使用 `*`

到目前為止，我們的 `*` 幾乎都用在一般的參考（`&T`）上。但 `*` 也能用在某些智慧指標上：

```rust,editable
use std::rc::Rc;

fn main() {
    let value = Rc::new(42);
    let number: i32 = *value;

    println!("{}", number); // 42
}
```

`Rc<i32>` 不是 `i32`，但 Rust 能用這把鑰匙觸及裡面的 `i32`。這裡 `i32` 是 `Copy`，所以把 `*value` 指定給 `number` 會產生出另一個 `i32` 值。

如果內部的值不是 `Copy`——例如 `String`——就沒辦法這樣把它搬出來，正如你從第 4 章的借用行為會預期的：

```rust,compile_fail
use std::rc::Rc;

fn main() {
    let text = Rc::new(String::from("hello"));
    let moved: String = *text; // 編譯錯誤！
}
```

可能還有其他 `Rc` 值開著同一份 heap 資料。把裡面的 `String` 搬走，那些 `Rc` 值的鑰匙就只能開到一個空保險箱了，所以 Rust 禁止這麼做。

### `Deref` `trait`

這背後的機制是 `Deref` `trait`。目前我們還不需要它的精確定義；重要的概念更簡單：

`Deref` 告訴 Rust 怎麼**穿過**一個值去借用。例如，穿過 `Rc<i32>` 可以借用到裡面的 `i32`，產生一個 `&i32`。

那個參考正是重點。`Deref` 給 Rust 的是一個指向內部值的**參考**；它本身並不交出內部值的所有權。

`Rc<T>` 和 `Box<T>` 都實作了 `Deref`。像這樣本職就是作為某個內部值的鑰匙——管理它，並讓 Rust 能透過 `Deref` 觸及它——的型別，我們常稱為**智慧指標（smart pointer）**。其他一些標準庫型別（像 `String` 和 `Vec<T>`）雖然也實作了 `Deref`，但當鑰匙並不是它們的本職；本集聚焦在智慧指標上。

### `*v` 背後發生了什麼

對一個實作了 `Deref` 的型別使用 `*` 時，好用的心智模型是：

```rust,ignore
*v
// 大致上：穿過 v 借用，然後沿著那個參考走過去
```

以剛才的 `Rc<i32>` 為例：

```rust,ignore
let value = Rc::new(42);

*value
// 大致上：
// 穿過 value 借用，得到 &i32
// 然後沿著那個 &i32 走過去
```

因為 `i32` 是 `Copy`，這能產生出另一個 `i32` 值。如果內部的值不是 `Copy`（像 `String`），一般的 `Deref` 沒辦法讓你把它搬出來。

### `deref` coercion

**`deref` coercion** 是 Rust 在需要時自動透過 `Deref` 轉換參考型別的機制。

例如，這個函數要的是 `&i32`：

```rust,editable
use std::rc::Rc;

fn show(n: &i32) {
    println!("{}", n);
}

fn main() {
    let value = Rc::new(42);

    show(&value); // &Rc<i32> 自動變成 &i32
}
```

`show` 需要 `&i32`，但 `&value` 是 `&Rc<i32>`。因為 `Rc<i32>` 實作的 `Deref` 讓 Rust 能借用到內部的 `i32`，Rust 就能轉換：

```rust,ignore
&Rc<i32> -> &i32
```

這個轉換發生在參考層面，沒有任何所有權被移動。

`deref` coercion 也可以連鎖：

```rust,editable
use std::rc::Rc;

fn show(n: &i32) {
    println!("{}", n);
}

fn main() {
    let value = Rc::new(Box::new(42));

    show(&value); // &Rc<Box<i32>> -> &Box<i32> -> &i32
}
```

Rust 先穿過 `Rc`，再穿過 `Box`，直到參考型別符合函數要的為止。

### method call 的自動解參考

method call 有它自己的自動解參考行為。當你用 `.` 呼叫方法時，Rust 會先試外層的型別；在那裡找不到對應的方法，就往內走一層再試一次。

例如：

```rust,editable
use std::rc::Rc;

fn main() {
    let numbers = Rc::new(vec![10, 20, 30]);

    println!("{}", numbers.len()); // 呼叫 Vec<i32> 的 .len()
}
```

`Rc<Vec<i32>>` 自己沒有定義 `.len()`，但 `Vec<i32>` 有。Rust 能用 `Rc` 這把鑰匙，借用到內部的 `Vec<i32>`，再對它呼叫 `.len()`。

有多層包裝時，Rust 能一次往內走一層：

```rust,ignore
let numbers = Rc::new(Box::new(vec![10, 20, 30]));

numbers.len()
// Rust 能穿過 Rc、再穿過 Box，找到 Vec 的 .len()
```

這就是為什麼智慧指標常常讓人感覺就像它們裡面的值：method call 能自動穿過智慧指標去借用。

### `DerefMut`

`DerefMut` 是 `Deref` 的可變版本。它告訴 Rust 怎麼**可變地**穿過一個值去借用：從一個可變的智慧指標，借到指向內部值的可變參考。

`Rc<T>` 沒有實作 `DerefMut`，因為可能還有其他 `Rc` 值開著同一份 heap 資料。一般的 `Rc<T>` 提供的是共享的讀取，不是不受限制的可變存取。`Rc<T>` 無法證明自己是這份 heap 資料唯一的鑰匙；如果允許 `DerefMut`，同一份 heap 資料就可能同時出現好幾個 `&mut T`。

`Box<T>` 就不同了：一把鑰匙、沒有計數器，所以可變的 `Box<T>` 能提供對內部值的可變存取：

```rust,editable
fn main() {
    let mut text = Box::new(String::from("hello"));

    text.push_str(" world");
    println!("{}", text);

    *text = String::from("replaced");
    println!("{}", text);
}
```

`.push_str()` 的呼叫可變地借用了內部的 `String`；透過 `*text` 的賦值則把內部的 `String` 整個換掉。兩者都是 `DerefMut` 的正常行為：Rust 穿過 `Box` 拿到一個 `&mut String`。

### 方法同名時的優先順序

Rust 從外往內找方法。外層智慧指標自身的方法，優先於內層型別的方法。

一個常見的例子是 `.clone()`。`Rc` 自己有 `.clone()` 方法：替同一份 heap 資料多建立一個 `Rc`，並增加參考計數。內部的值可能也有自己的 `.clone()` 方法。

直接呼叫 `.clone()` 得到的是另一個 `Rc`：

```rust,noplayground
use std::rc::Rc;

fn main() {
    let a = Rc::new(String::from("hello"));
    let b = a.clone(); // Rc 的 .clone()：增加計數，不會建立新的 String
}
```

如果要的是內層 `String` 自己的 `.clone()`，就明確寫出來：

```rust,noplayground
# use std::rc::Rc;
#
# fn main() {
#     let a = Rc::new(String::from("hello"));
    let c = (*a).clone(); // String 的 .clone()：建立一個新的 String
# }
```

### `Box<T>` 的一項特權

上面把 `Deref` 一律當成「穿過智慧指標去借用」，這是正確的通用模型。

`Box<T>` 多了一項額外能力：當你**擁有**這個 `Box<T>` 時，Rust 允許你用 `*box_value` 把裡面的 `T` 搬出來：

```rust,editable
fn main() {
    let boxed = Box::new(String::from("owned"));
    let text: String = *boxed; // OK：把 String 從 Box 裡搬出來

    println!("{}", text);
}
```

這是 `Box<T>` 專屬的特殊待遇，**不是**一般 `Deref` 型別做得到的事：

```rust,compile_fail
use std::rc::Rc;

fn main() {
    let shared = Rc::new(String::from("shared"));
    let text: String = *shared; // 編譯錯誤！
}
```

所以通用規則保持簡單：`Deref` 讓 Rust 穿過一個值去借用；用 `*` 把非 `Copy` 的值搬出來，是 `Box<T>` 專屬的特殊能力。

## 範例程式碼

```rust,editable
use std::rc::Rc;

fn show(n: &i32) {
    println!("值：{}", n);
}

fn main() {
    // Rc<i32>：* 觸及那個 i32。因為 i32 是 Copy，這會產生出另一個 i32 值。
    let shared = Rc::new(42);
    let number: i32 = *shared;
    println!("number：{}", number);

    // deref coercion：&Rc<i32> -> &i32
    show(&shared);

    // deref coercion 可以連鎖：&Rc<Box<i32>> -> &Box<i32> -> &i32
    let nested = Rc::new(Box::new(99));
    show(&nested);

    // method call 自動解參考：Rc<Vec<i32>> 能呼叫 Vec<i32> 的方法。
    let numbers = Rc::new(vec![10, 20, 30]);
    println!("長度：{}", numbers.len());

    // DerefMut：Box<String> 能可變地借用內部的 String。
    let mut text = Box::new(String::from("hello"));
    text.push_str(" world");
    println!("{}", text);

    *text = String::from("replaced");
    println!("{}", text);

    // 方法同名的優先順序：Rc 的 .clone() 勝過 String 的 .clone()。
    let a = Rc::new(String::from("shared"));
    let b = a.clone();    // Rc 的 .clone()：增加計數
    let c = (*a).clone(); // String 的 .clone()：建立一個新的 String
    println!("a = {}, b = {}, c = {}", a, b, c);
    println!("Rc 計數 = {}", Rc::strong_count(&a)); // 2，不是 3

    // Box<T> 的特權：擁有 Box 就能把 T 搬出來。
    let boxed = Box::new(String::from("owned"));
    let owned: String = *boxed;
    println!("從 Box 搬出來：{}", owned);
}
```

## 重點整理

- `Deref` 的主軸是「穿過一個值去借用」：它讓 Rust 拿到指向內部值的參考。
- 對 `Deref` 型別使用 `*v`，就是「先借用，再沿著參考走過去」；之後能複製、改寫還是 move，由內部值的型別和這個運算式的用法決定。
- `deref` coercion 會自動把 `&Rc<i32>` 這類參考轉成 `&i32`，而且可以連鎖穿過多層。
- method call 的自動解參考讓智慧指標能呼叫內部值的方法。
- `DerefMut` 提供對內部值的可變存取；`Box<T>` 支援，`Rc<T>` 不支援。
- 方法同名時外層優先——`Rc` 的 `.clone()` 會先於內部值的 `.clone()` 被選中。
- 用 `*box_value` 把非 `Copy` 的值搬出來是 `Box<T>` 專屬的特殊待遇，不是一般 `Deref` 的行為。
