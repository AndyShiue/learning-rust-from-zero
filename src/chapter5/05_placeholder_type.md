# placeholder type `_`

## 本集目標

學會用 `_` 在型別標注中讓編譯器推斷部分型別。

## 概念說明

上一集學了 turbofish，可以手動指定所有型別參數。但有時候你只想指定一部分，剩下的讓 Rust 自己推斷。這時候就用 `_` 作為型別層級的萬用字元。

### `_` 當型別佔位符

看這個例子：

```rust,editable
# fn main() {
    let v: Vec<_> = vec![1, 2, 3];
# }
```

這裡我們告訴 Rust「這是一個 `Vec`」，但裡面的元素型別用 `_` 表示「你自己推斷吧」。Rust 看到 `1, 2, 3` 是整數，就推斷 `_` = `i32`。

turbofish 裡也可以用 `_`：

```rust,ignore
# fn main() {
    let v = Vec::<_>::new();
# }
```

不過這樣寫其實和直接寫 `Vec::new()` 讓 Rust 全部推斷沒什麼差別。`_` 更常用在你需要指定外層型別、但內層型別讓 Rust 推斷的情況。

### 什麼時候有用？

當型別有多個參數，你只想標注一部分的時候。`_` 的威力在型別越複雜時越明顯——之後學到更多標準庫型別時會自然體會到。

## 範例程式碼

```rust,editable
fn main() {
    // 用 _ 讓 Rust 推斷 Vec 的元素型別
    let v: Vec<_> = vec![1, 2, 3];
    println!("{:?}", v);

    // turbofish 裡也能用 _
    let v2 = Vec::<_>::new(); // 和 Vec::new() 一樣，_ 讓 Rust 推斷
    let v2: Vec<i32> = v2;    // 之後透過使用方式確定型別
    println!("{:?}", v2);

    // 比較：完全不標型別 vs 用 _ 部分標注
    let a = vec![true, false]; // Rust 全部推斷：Vec<bool>
    let b: Vec<_> = vec![true, false]; // 告訴 Rust 是 Vec，元素型別自己推斷
    println!("{:?}", a);
    println!("{:?}", b);
}
```

## 重點整理

- `_` 可以在型別標注中當佔位符，讓 Rust 推斷該位置的型別
- 適合用在「外層型別我知道，內層讓 Rust 推斷」的情況
- turbofish 和 `let` 標注都可以使用 `_`

