# 泛型 `impl`

## 本集目標

學會為泛型 `struct` 實作方法，理解 `impl<T>` 語法中兩個 `T` 的含義。

## 概念說明

第二集我們定義了泛型 `struct` `Pair<T>`。這集要幫它 `impl`。

回想第 3 章，`impl` `struct` 是這樣寫的：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn sum(&self) -> i32 {
        self.x + self.y
    }
}
#
# fn main() {}
```

那泛型 `struct` 呢？

### `impl<T>` 的語法

```rust,noplayground
# #[derive(Debug)]
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
impl<T> Pair<T> {
    fn new(first: T, second: T) -> Pair<T> {
        Pair { first, second }
    }
}
#
# fn main() {}
```

注意這裡有**兩個** `T` 出現在不同位置，它們的角色不一樣：

1. `impl<T>` 的 `<T>`：**宣告**一個型別參數 `T`。告訴 Rust「接下來我要用一個叫 `T` 的型別參數」
2. `Pair<T>` 的 `<T>`：**使用**剛才宣告的 `T`。告訴 Rust「我要幫的是 `Pair<T>` 這個型別」

換句話說：`impl<T>` 宣告 `T`，然後把 `T` 傳給 `Pair<T>`——「對於任何型別 `T`，幫 `Pair<T>` 實作以下方法」。

如果你只寫 `impl Pair<T>` 而不加 `impl<T>`，Rust 會以為 `T` 是一個具體的型別名稱（就像 `i32` 或 `String` 一樣），然後找不到叫 `T` 的型別就報錯。

反過來，如果你寫 `impl Pair<i32>`（不需要 `impl<T>`），那就是只幫 `Pair<i32>` 這一種加方法，`Pair<String>` 或其他的都不會有。

### 方法裡使用 `T`

宣告了 `T` 之後，在整個 `impl` 區塊裡都可以使用它：

```rust,noplayground
# #[derive(Debug)]
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
impl<T> Pair<T> {
    fn new(first: T, second: T) -> Pair<T> {
        Pair { first, second }
    }

    fn first(&self) -> &T {
        &self.first
    }
}
#
# fn main() {}
```

### 實作 `trait` 也是一樣

第 4 章教 `trait` 的時候，我們幫具體型別實作了 `trait`，像 `impl Greet for Cat`。如果你想幫一個泛型型別實作 `trait`，語法也是一樣——在 `impl` 後面加上 `<T>` 來宣告型別參數：

```rust,noplayground
# trait SomeTrait {}
#
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
impl<T> SomeTrait for Pair<T> {
    // ...
}
#
# fn main() {}
```

一樣是「對於任何型別 T，幫 `Pair<T>` 實作這個 `trait`」。

## 範例程式碼

```rust,editable
#[derive(Debug)]
struct Pair<T> {
    first: T,
    second: T,
}

impl<T> Pair<T> {
    // associated function
    fn new(first: T, second: T) -> Pair<T> {
        Pair { first, second }
    }

    // method：回傳 first 的參考
    fn first(&self) -> &T {
        &self.first
    }

    // method：回傳 second 的參考
    fn second(&self) -> &T {
        &self.second
    }
}

fn main() {
    let p = Pair::new(10, 20);
    println!("first = {}", p.first());
    println!("second = {}", p.second());
    println!("{:?}", p);

    let q = Pair::new("hello", "world");
    println!("first = {}", q.first());
    println!("second = {}", q.second());
}
```

## 重點整理

- 為泛型 `struct` 實作方法時，寫 `impl<T> Pair<T> { ... }`
- `impl<T>` 的 `<T>` 是**宣告** `T`，`Pair<T>` 的 `<T>` 是**使用** `T`
- 結論：`impl<T>` 宣告 `T`，然後把 `T` 傳給 `Pair<T>`
- 宣告之後，整個 `impl` 區塊裡的方法都可以使用 `T`
- 幫泛型型別實作 `trait` 語法類似：`impl<T> SomeTrait for Pair<T> { ... }`
