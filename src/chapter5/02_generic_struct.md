# 泛型 `struct`

## 本集目標

學會定義帶型別參數的 `struct`，讓同一個結構可以存放不同型別的資料。

## 概念說明

上一集我們學了泛型函數。其實 `struct` 也可以有型別參數！

回想一下，`Vec<i32>` 和 `Vec<String>` 就是同一個 `struct` 定義，只是裡面放的型別不同。我們也可以自己定義這樣的泛型 `struct`。

### 定義泛型 `struct`

```rust,noplayground
struct Pair<T> {
    first: T,
    second: T,
}
#
# fn main() {}
```

這裡的 `<T>` 寫在 `struct` 名稱後面，表示「`Pair` 有一個型別參數 `T`」。`first` 和 `second` 的型別都是 `T`，所以它們必須是同一種型別。

使用的時候：

```rust,noplayground
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
# fn main() {   
    let p = Pair { first: 1, second: 2 };       // T = i32
    let q = Pair { first: "hi", second: "yo" }; // T = &str
# }
```

### 多個型別參數

如果你希望 `first` 和 `second` 可以是不同型別，就用兩個型別參數：

```rust,noplayground
struct MixedPair<T, U> {
    first: T,
    second: U,
}
#
# fn main() {}
```

這和上一集的 `make_pair<T, U>` 概念一模一樣。

## 範例程式碼

```rust,editable
// 兩個欄位必須同型別
#[derive(Debug)]
struct Pair<T> {
    first: T,
    second: T,
}

// 兩個欄位可以不同型別
#[derive(Debug)]
struct MixedPair<T, U> {
    first: T,
    second: U,
}

fn main() {
    let int_pair = Pair { first: 10, second: 20 };
    println!("{:?}", int_pair);

    let str_pair = Pair { first: "hello", second: "world" };
    println!("{:?}", str_pair);

    // Pair<T> 的兩個欄位必須同型別，以下會編譯錯誤：
    // let bad = Pair { first: 42, second: "oops" };

    let mixed = MixedPair { first: 42, second: "answer" };
    println!("{:?}", mixed);
}
```

## 重點整理

- `struct` 可以用 `<T>` 宣告型別參數，讓同一個定義適用於不同型別
- `Pair<T>` 的兩個欄位都是 `T`，所以必須同型別
- 需要不同型別時，用多個型別參數：`MixedPair<T, U>`
- 和泛型函數一樣，Rust 會根據使用方式自動推斷型別參數
