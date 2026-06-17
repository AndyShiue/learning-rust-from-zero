# `trait` bound

## 本集目標

學會用 `trait` bound 限制泛型參數的能力，以及用條件式 `impl` 為符合條件的型別加方法。

## 概念說明

第一集學泛型函數的時候，我們寫了 `fn first<T>(a: T, b: T) -> T`。但如果你想在泛型函數裡 `clone` 一個值呢？

```rust,compile_fail
fn duplicate<T>(x: &T) -> (T, T) {
    (x.clone(), x.clone()) // 編譯錯誤！
}
#
# fn main() {}
```

編譯器會報錯：「不是所有 `T` 都有 `clone()` 方法。」

這很合理——`T` 可以是任何型別，萬一有個型別沒有實作 `Clone` 呢？

### `trait` bound：限制 `T` 的能力

解法是加上 **`trait` bound**，告訴 Rust「`T` 必須實作 `Clone`」：

```rust,editable
fn duplicate<T: Clone>(x: &T) -> (T, T) {
    (x.clone(), x.clone())
}

fn main() {}
```

`T: Clone` 的意思是「`T` 必須實作 `Clone` `trait`」。這樣 Rust 就知道 `x.clone()` 一定可以呼叫。

### 到處都能加 `trait` bound

`trait` bound 不只能用在函數上。幾乎所有有泛型參數的地方都能加——`struct`、`enum`、`impl` 定義裡都可以：

```rust,noplayground
struct Wrapper<T: Clone> {
    value: T,
}
#
# fn main() {}
```

### 條件式 `impl`

其中最實用的是在 `impl` 區塊上加 `trait` bound。這叫做**條件式 impl**——只有當型別參數符合某些條件時，才提供特定的方法。

```rust,noplayground
# #[derive(Debug)]
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
impl<T: Clone> Pair<T> {
    fn to_tuple(&self) -> (T, T) {
        (self.first.clone(), self.second.clone())
    }
}
#
# fn main() {}
```

這段的意思是：只有當 `T` 實作了 `Clone` 的時候，`Pair<T>` 才有 `to_tuple` 方法。

### 實際效果

```rust,compile_fail
# #[derive(Debug)]
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
# impl<T: Clone> Pair<T> {
#     fn new(first: T, second: T) -> Pair<T> {
#         Pair { first, second }
#     }
#
#     fn to_tuple(&self) -> (T, T) {
#         (self.first.clone(), self.second.clone())
#     }
# }
# fn main() {
    let p1 = Pair::new(1, 2); // i32 有 Clone
    let t = p1.to_tuple();    // 可以呼叫 ✓

    let p2 = Pair::new(Pair::new(1, 2), Pair::new(3, 4)); // Pair 沒有 derive Clone
    p2.to_tuple(); // 編譯錯誤！Pair<i32> 沒有實作 Clone
# }
```

`Pair<Pair<i32>>` 不能呼叫 `to_tuple()`，因為 `Pair<i32>` 沒有實作 `Clone`（我們沒有幫它 `derive` `Clone`）。

## 範例程式碼

```rust,editable
#[derive(Debug)]
struct Pair<T> {
    first: T,
    second: T,
}

// 所有 Pair<T> 都有 new
impl<T> Pair<T> {
    fn new(first: T, second: T) -> Pair<T> {
        Pair { first, second }
    }
}

// 只有 T: Clone 的 Pair<T> 才有 to_tuple
impl<T: Clone> Pair<T> {
    fn to_tuple(&self) -> (T, T) {
        (self.first.clone(), self.second.clone())
    }
}

// 泛型函數 + trait bound
fn duplicate<T: Clone>(x: &T) -> (T, T) {
    (x.clone(), x.clone())
}

fn main() {
    // i32 有 Clone，所以 Pair<i32> 有 to_tuple
    let p = Pair::new(10, 20);
    let t = p.to_tuple();
    println!("{:?}", t);

    // 泛型函數也可以用
    let pair = duplicate(&42);
    println!("{:?}", pair);

    let pair2 = duplicate(&String::from("hello"));
    println!("{:?}", pair2);

    // Pair<Pair<i32>> 不能呼叫 to_tuple
    // 因為 Pair<i32> 沒有 derive Clone
    let nested = Pair::new(Pair::new(1, 2), Pair::new(3, 4));
    println!("{:?}", nested);
    // nested.to_tuple(); // 編譯錯誤！Pair<i32> 沒有實作 Clone
}
```

## 重點整理

- `trait` bound `T: Clone` 限制 `T` 必須實作特定 `trait`
- `trait` bound 可以加在函數、`struct`、`enum`、`impl` 等各種泛型參數上
- 沒有 `trait` `bound` 的話，泛型函數或方法不能假設 `T` 有任何能力
- 條件式 `impl`：`impl<T: Clone> Pair<T> { ... }` 只在 `T` 符合條件時提供方法
