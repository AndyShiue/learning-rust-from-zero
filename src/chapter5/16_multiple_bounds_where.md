# 多個 `trait` bound 與 `where`

## 本集目標

學會用 `+` 組合多個 `trait` bound，以及用 `where` 子句讓複雜的 bound 更好讀。

## 概念說明

第 13 集我們學了 `T: Clone`，要求 `T` 必須實作 `Clone`。但如果你想同時要求 `T` 實作多個 `trait` 呢？

### 多個 `trait` bound

用 `+` 把多個 `trait` bound 串起來：

```rust,noplayground
fn show_clone<T: Clone + std::fmt::Display>(x: &T) {
    let cloned = x.clone();
    println!("原始：{}", x);
    println!("克隆：{}", cloned);
}
#
# fn main() {}
```

`T: Clone + Display` 表示 `T` 必須同時實作 `Clone` 和 `Display`。

### `where` 子句

當 `trait` bound 很長的時候，寫在 `<>` 裡面會很擠。Rust 提供 `where` 子句，放在函數簽名後面：

```rust,noplayground
fn show_clone<T>(x: &T)
where
    T: Clone + std::fmt::Display,
{
    let cloned = x.clone();
    println!("原始：{}", x);
    println!("克隆：{}", cloned);
}
#
# fn main() {}
```

兩種寫法完全等價，只是 `where` 比較好讀。

### `where` 比角括號更靈活

`where` 子句的冒號前面不只能放 `T`，還能放更複雜的東西。比如一個 tuple 型別：

```rust,noplayground
fn clone_pair<T, U>(pair: &(T, U)) -> (T, U)
where
    (T, U): Clone,
{
    pair.clone()
}
#
# fn main() {}
```

`(T, U): Clone` 要求 tuple `(T, U)` 能被 `clone`。這種寫法只能出現在 `where` 子句裡，不能放在 `<>` 裡——這就是 `where` 更靈活的地方。

## 範例程式碼

```rust,editable
use std::fmt::Display;

// 多個 trait bound：Clone + Display
// clone 一份，印出原始值，然後回傳複製品
fn clone_and_show<T: Clone + Display>(x: &T) -> T {
    println!("複製了：{}", x);
    x.clone()
}

// 用 where 子句：有時候比較好讀
fn show_pair<T, U>(a: &T, b: &U)
where
    T: Display,
    U: Display,
{
    println!("a = {}, b = {}", a, b);
}

fn main() {
    // 多個 trait bound
    let cloned = clone_and_show(&42);
    println!("拿到的複製品：{}", cloned);

    let cloned2 = clone_and_show(&String::from("hello"));
    println!("拿到的複製品：{}", cloned2);

    // where 子句
    show_pair(&10, &"world");
}
```

## `where` 還能用在哪裡

`where` 不只能用在函數上。其他很多會用到泛型的地方也都能用 `where`，例如 `impl` 區塊：

```rust,ignore
impl<T> Pair<T>
where
    T: Clone + Display,
{
    // 方法定義
}
```

此外，`where` 也能出現在 `struct`、`enum` 和 `trait` 的定義上。目前知道就好了，之後需要用到的時候自然會想起來。

## 重點整理

- 用 `+` 組合多個 `trait` bound：`T: Clone + Display`
- `where` 子句是另一種寫 `trait` bound 的方式，更好讀
- `where` 比角括號更靈活，冒號前面可以放 tuple 等複雜型別（如 `(T, U): Clone`）
- `where` 不只能用在函數上，`impl`、`struct`、`enum`、`trait` 等能用泛型的地方都能用
