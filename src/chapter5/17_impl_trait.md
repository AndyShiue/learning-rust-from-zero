# `impl Trait` 語法

## 本集目標

學會用 `impl Trait` 作為 `trait` bound 的簡寫，理解它在參數和回傳值中的不同含義。

## 概念說明

我們前面學了 `trait` bound：`fn foo<T: Display>(x: &T)`。Rust 還提供了一種更簡潔的寫法：`impl Trait`。

### 參數位置的 `impl Trait`

```rust,noplayground
# use std::fmt::Display;
#
fn show(x: &impl Display) {
    println!("{}", x);
}
#
# fn main() {}
```

這和 `fn show<T: Display>(x: &T)` 完全等價——都是說「`x` 的型別必須實作 `Display`」。只是寫法更簡潔。

### 每個 `impl Trait` 是獨立的型別

重要觀念：參數中的每個 `impl Trait` 代表一個**獨立的**型別。

```rust,noplayground
# use std::fmt::Display;
#
fn show_two(a: &impl Display, b: &impl Display) {
    println!("{} {}", a, b);
}
#
# fn main() {}
```

`a` 和 `b` 可以是**不同的型別**——只要它們都實作了 `Display`。比如 `a` 可以是 `i32`，`b` 可以是 `String`。

如果你要求 `a` 和 `b` **必須是同一個型別**，就要用具名的型別參數：

```rust,noplayground
# use std::fmt::Display;
#
fn show_same<T: Display>(a: &T, b: &T) {
    println!("{} {}", a, b);
}
#
# fn main() {}
```

### 回傳位置的 `impl Trait`

`impl Trait` 也可以用在回傳值：

```rust,noplayground
# use std::fmt::Display;
#
fn greeting() -> impl Display {
    String::from("你好")
}
#
# fn main() {}
```

這表示「我會回傳一個實作了 `Display` 的型別，但不告訴你具體是什麼型別」。呼叫者只知道回傳值可以用 `Display` 的方法（像 `println!("{}", greeting())`），不知道具體是 `String` 還是其他什麼。

## 範例程式碼

```rust,editable
use std::fmt::Display;

// 參數位置的 impl Trait
fn show(x: &impl Display) {
    println!("顯示：{}", x);
}

// 每個 impl Trait 是獨立型別，a 和 b 可以不同型別
fn show_pair(a: &impl Display, b: &impl Display) {
    println!("{} 和 {}", a, b);
}

// 要求同一型別，用泛型
fn show_same<T: Display>(a: &T, b: &T) {
    println!("{} 和 {}", a, b);
}

// 回傳位置的 impl Trait
fn make_greeting(name: &str) -> impl Display {
    let mut s = String::from("你好，");
    s.push_str(name);
    s.push_str("！");
    s
}

fn main() {
    // 參數位置
    show(&42);
    show(&String::from("hello"));

    // 兩個參數可以不同型別
    show_pair(&42, &"hello");

    // 要求同型別
    show_same(&10, &20);
    // show_same(&10, &"hello"); // 編譯錯誤！i32 和 &str 不同型別

    // 回傳 impl Trait
    let greeting = make_greeting("世界");
    println!("{}", greeting);

    // greeting 的型別是 `impl Display`，不是 `String`
    // 所以你不能把它當 String 用：
    // greeting.push_str("!!!"); // 編譯錯誤！impl Display 沒有 push_str 方法
    // 即使我們知道裡面其實是 String，編譯器只認 Display 這個 trait
}
```

## 重點整理

- `fn foo(x: &impl Display)` 是 `fn foo<T: Display>(x: &T)` 的簡寫
- 每個 `impl Trait` 參數代表獨立的型別——兩個 `impl Display` 可以是不同型別
- 要求同型別，用具名的型別參數 `<T: Display>`
- 回傳位置的 `-> impl Trait` 隱藏具體型別，呼叫者只知道它實作了什麼 `trait`
