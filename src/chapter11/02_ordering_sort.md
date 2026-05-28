# `Ordering` 與排序

## 本集目標

認識 `Ordering`、`min`/`max` 系列函數、排序方法，以及 `Reverse` 的原理。

## 概念說明

### `Ordering`

第 5 章學了 `Ord` `trait`，知道實作了 `Ord` 的型別可以比大小。`Ord` 的核心方法是 `cmp`，它比較兩個值，回傳 `std::cmp::Ordering`——一個只有三個值的 `enum`：

```rust,editable
use std::cmp::Ordering;

fn main() {
    match 5.cmp(&3) {
        Ordering::Less => println!("比較小"),
        Ordering::Equal => println!("一樣"),
        Ordering::Greater => println!("比較大"),
    }
}
```

### `min` / `max`

`std::cmp::min(a, b)` 和 `std::cmp::max(a, b)` 回傳兩個值中比較小或大的那個，要求型別實作 `Ord`：

```rust,editable
use std::cmp;

fn main() {
    println!("{}", cmp::min(3, 7)); // 3
    println!("{}", cmp::max(3, 7)); // 7
}
```

### 浮點數的問題

`f64` 沒有實作 `Ord`（第 5 章提過，因為 `NAN` 和任何值比較都是 `false`），所以不能直接用 `cmp::min`。

`f64` 只有 `PartialOrd`，它的方法是 `partial_cmp`，回傳 `Option<Ordering>` 而不是 `Ordering`——因為碰到 `NAN` 的時候沒辦法比大小，只能回傳 `None`。

這時候可以用 `min_by` / `max_by`，自訂比較邏輯：

```rust,editable
use std::cmp;

fn main() {
    let smaller = cmp::min_by(3.0_f64, 2.5, |a, b| {
        a.partial_cmp(b).unwrap() // 如果確定不會碰到 NAN，用 unwrap 取出 Ordering
    });
    println!("{}", smaller); // 2.5

    let bigger = cmp::max_by(3.0_f64, 2.5, |a, b| {
        a.partial_cmp(b).unwrap()
    });
    println!("{}", bigger); // 3.0
}
```

`min_by` / `max_by` 的閉包回傳 `Ordering`，你自己決定怎麼比。

### `min_by_key` / `max_by_key`

根據某個 key 來比較：

```rust,editable
use std::cmp;

fn main() {
    let short = cmp::min_by_key("hello", "hi", |s| s.len());
    println!("{}", short); // "hi"
}
```

### 排序

`Vec` 和切片提供了幾種排序方法：

```rust,editable
# fn main() {
    let mut nums = vec![3, 1, 4, 1, 5];

    // sort：由小到大，要求 Ord
    nums.sort();
    println!("{:?}", nums); // [1, 1, 3, 4, 5]

    // sort_by：自訂比較，傳入閉包回傳 Ordering
    nums.sort_by(|a, b| b.cmp(a));
    println!("{:?}", nums); // [5, 4, 3, 1, 1]

    // sort_by_key：根據 key 排序
    let mut words = vec!["banana", "apple", "fig"];
    words.sort_by_key(|w| w.len());
    println!("{:?}", words); // ["fig", "apple", "banana"]
# }
```

### `Reverse`

`std::cmp::Reverse` 可以把排序順序反過來：

```rust,editable
use std::cmp::Reverse;

fn main() {
    let mut nums = vec![3, 1, 4, 1, 5];
    nums.sort_by_key(|&x| Reverse(x));
    println!("{:?}", nums); // [5, 4, 3, 1, 1]
}
```

這是怎麼做到的？`Reverse` 其實就是一個 newtype：

```rust,ignore
pub struct Reverse<T>(pub T);
```

它的 `Ord` 實作把比較順序反了過來：

```rust,ignore
impl<T: Ord> Ord for Reverse<T> {
    fn cmp(&self, other: &Reverse<T>) -> Ordering {
        other.0.cmp(&self.0) // 注意：是 other 跟 self 比，反過來了
    }
}
```

正常的 `5.cmp(&3)` 回傳 `Greater`，但 `Reverse(5).cmp(&Reverse(3))` 內部做的是 `3.cmp(&5)`，回傳 `Less`。`sort_by_key` 用 key 的 `cmp` 來決定順序，key 被 `Reverse` 包住之後比較邏輯就自動反過來了。

比起 `sort_by(|a, b| b.cmp(a))`，`Reverse` 的寫法意圖更清楚。

## 範例程式碼

```rust,editable
use std::cmp::{self, Reverse};

fn main() {
    // min / max
    println!("min(10, 20) = {}", cmp::min(10, 20));
    println!("max(10, 20) = {}", cmp::max(10, 20));

    // 浮點數用 min_by / max_by
    let smaller = cmp::min_by(1.5_f64, 2.3, |a, b| {
        a.partial_cmp(b).unwrap()
    });
    println!("min_by(1.5, 2.3) = {}", smaller);

    // 排序
    let mut scores = vec![85, 92, 78, 95, 88];
    scores.sort();
    println!("由小到大：{:?}", scores);

    scores.sort_by_key(|&s| Reverse(s));
    println!("由大到小：{:?}", scores);

    // 根據字串長度排序
    let mut names = vec!["Alice", "Bob", "Charlie", "Dave"];
    names.sort_by_key(|n| n.len());
    println!("依長度排：{:?}", names);
}
```

## 重點整理

- `Ordering` 有三個值：`Less`、`Equal`、`Greater`
- `cmp::min` / `cmp::max` 取兩者的較小/大值，要求 `Ord`
- `f64` 沒有 `Ord`，用 `min_by` / `max_by` 自訂比較
- `min_by_key` / `max_by_key` 根據 key 比較
- `sort()` 由小到大、`sort_by()` 自訂比較、`sort_by_key()` 根據 key 排序
- `Reverse` 是一個 tuple `struct`，`Ord` 實作把比較反過來，所以排序結果跟著反轉
