# `Deref` 與自動解參考

## 本集目標

理解 `Deref` `trait` 和 Rust 的自動解參考機制，以及智慧指標為什麼能直接呼叫內部型別的方法。

## 概念說明

### 對智慧指標使用 `*`

到目前為止，我們只對一般的參考（`&T`）用過 `*`。但其實 `*` 也能用在其他型別上：

```rust,editable
# fn main() {
    let b = Box::new(42);
    let val: i32 = *b; // 把值從 Box 裡拿出來
    println!("{}", val); // 42
# }
```

`*b` 得到的是 `Box` 裡面的 `i32`。這之所以能成立，是因為 `Box<T>` 實作了一個叫 `Deref` 的 `trait`。

### `Deref` `trait` 與智慧指標

`Deref` 告訴 Rust：「當你需要解參考我的時候，該怎麼做。」`Box<T>` 和 `Rc<T>` 都實作了 `Deref`。在 Rust 中，我們常常把**實作了 `Deref` 的型別**叫作**智慧指標（smart pointer）**。

### `*v` 背後發生了什麼

當你對一個實作了 `Deref` 的型別使用 `*` 時，Rust 實際上會這樣展開：

```rust,ignore
*v
// 等同於
*(Deref::deref(&v))
```

`Deref::deref` 接收 `&Self`，回傳一個參考（例如 `&T`），然後外面的 `*` 再把這個參考解開，得到 `T` 本身。

以剛才的 `Box<i32>` 為例：

```rust,ignore
let b = Box::new(42);

*b
// 展開為 *(Deref::deref(&b))
// Deref::deref(&b) 回傳 &i32
// 再 * 一次得到 i32
```

所以解參考 `Box<T>` 最終得到的是 `T`。`Rc<T>` 也一樣，解參考 `Rc<T>` 得到 `T`。

### `DerefMut`

`DerefMut` 是 `Deref` 的可變版本。當你對一個可變的智慧指標寫入時，Rust 會用 `DerefMut` 來展開：

```rust,ignore
*v = 新的值
// 等同於
*(DerefMut::deref_mut(&mut v)) = 新的值
```

`DerefMut::deref_mut` 回傳 `&mut T`，外面的 `*` 解開後就能寫入值。例如：

```rust,editable
# fn main() {
    let mut b = Box::new(0);
    *b = 42;
    println!("{}", *b); // 42
# }
```

`Box<T>` 同時實作了 `Deref` 和 `DerefMut`，所以既能讀也能寫。`Rc<T>` 則只實作了 `Deref`，不允許透過 `*` 修改內容。

### `Deref` coercion

**`Deref` coercion** 是 Rust 在需要的時候自動透過 `Deref` 轉換參考型別的機制。這不只發生在 method call，任何需要型別匹配的地方都可能觸發。

例如，一個函數接受 `&i32`，你可以直接傳 `&Box<i32>` 進去，Rust 會自動透過 `Deref` 把 `&Box<i32>` 轉成 `&i32`：

```rust,editable
fn show(val: &i32) {
    println!("{}", val);
}

fn main() {
    let b = Box::new(42);
    show(&b); // deref coercion：&Box<i32> 自動轉成 &i32
}
```

`Deref` coercion 也可以連鎖。例如 `&Box<Box<i32>>` 會先 `deref` 成 `&Box<i32>`，再 `deref` 成 `&i32`。`DerefMut` 同理。

### method call 的自動解參考

method call 有另一套獨立的機制。前面學過 `(&a).method()` 可以簡寫為 `a.method()`——如果 `method` 接收的是 `&self`，Rust 會自動幫你加 `&`。反過來，如果你有一個 `&T` 或智慧指標，而方法定義在 `T` 上，Rust 也會自動幫你加 `*`。

當你用 `.` 呼叫方法時，Rust 會嘗試加 `&`、加 `*`、或兩者組合，一層一層嘗試，直到找到有對應方法的型別。如果 `a` 是 `&Box<i32>`，而你呼叫一個定義在 `i32` 上、接收 `&self` 的方法，Rust 會做 `(&**a).method()`——先 `*a` 得到 `Box<i32>`，再 `*` 得到 `i32`，再 `&` 回去得到 `&i32` 來匹配 `&self`。

來看一些比較簡單的例子：

```rust,ignore
let boxed = Box::new(String::from("hello"));

// 你寫的：
boxed.len()

// Rust 實際上做的：
(*boxed).len()
// *boxed 得到 String，String 有 len()，找到了
```

如果有多層包裝，Rust 會一層一層剝開：

```rust,ignore
let double_boxed = Box::new(Box::new(String::from("hello")));

// 你寫的：
double_boxed.len()

// Rust 實際上做的：
(**double_boxed).len()
// *double_boxed 得到 Box<String>，沒有 len()
// 再 * 一次得到 String，有 len()，找到了
```

`Rc` 也一樣：

```rust,editable
use std::rc::Rc;

fn main() {
    let rc = Rc::new(vec![1, 2, 3]);
    println!("{}", rc.len()); // 自動解參考，呼叫 Vec 的 len()
}
```

### 方法同名時的優先順序

Rust 從外往內找方法：外層智慧指標自身的方法優先於內層型別的方法。

一個常見的例子是 `clone`。`Rc` 本身有 `clone` 方法（增加參考計數），`T` 可能也有 `clone` 方法（深度複製資料）。直接呼叫 `.clone()` 會拿到 `Rc` 的 `clone`：

```rust,noplayground
use std::rc::Rc;

fn main() {
    let a = Rc::new(String::from("hello"));
    let b = a.clone(); // Rc 的 clone，增加參考計數，不複製 String
}
```

如果你想呼叫內層 `String` 的 `clone`，可以明確寫出來：

```rust,noplayground
# use std::rc::Rc;
#
# fn main() {
#     let a = Rc::new(String::from("hello"));
    let c = (*a).clone(); // String 的 clone，真的複製了一份 String
# }
```

## 範例程式碼

```rust,editable
use std::rc::Rc;

fn show(val: &i32) {
    println!("值：{}", val);
}

fn main() {
    // *Box<T> 得到 T（Deref）
    let b = Box::new(42);
    let val: i32 = *b;
    println!("解參考 Box：{}", val);

    // DerefMut：透過 * 寫入值
    let mut b = Box::new(0);
    *b = 42;
    println!("寫入後：{}", *b);

    // deref coercion：&Box<i32> 自動轉成 &i32
    let b = Box::new(99);
    show(&b);

    // 自動解參考：Box<String> 直接呼叫 String 的方法
    let boxed = Box::new(String::from("hello"));
    println!("Box 裡的字串長度：{}", boxed.len());
    // 等同於 (*boxed).len()

    // Rc 也一樣
    let rc = Rc::new(vec![10, 20, 30]);
    println!("Rc 裡的 Vec 長度：{}", rc.len());

    // clone 的優先順序
    let a = Rc::new(String::from("shared"));
    let b = a.clone();       // Rc 的 clone（快，只增加計數）
    let c = (*a).clone();    // String 的 clone（慢，複製整個 String）
    println!("a = {}, b = {}, c = {}", a, b, c);
    println!("Rc 計數 = {}", Rc::strong_count(&a)); // 2，不是 3
}
```

## 重點整理

- 在 Rust 中，實作了 `Deref` 的型別常被稱為智慧指標；`*v` 展開為 `*(Deref::deref(&v))`，所以解參考 `Box<T>` 得到 `T`
- `DerefMut` 是 `Deref` 的可變版本；`*v = 值` 展開為 `*(DerefMut::deref_mut(&mut v)) = 值`
- `Deref` coercion：Rust 在型別不匹配時會自動透過 `Deref` 轉換參考，不限於 method call（如 `&Box<i32>` → `&i32`）
- method call 的自動解參考是獨立的機制：用 `.` 呼叫方法時，Rust 會嘗試加 `&`、加 `*` 或兩者組合來找到對應的方法
- 方法同名時外層優先——`Rc` 的 `clone` 優先於 `String` 的 `clone`
