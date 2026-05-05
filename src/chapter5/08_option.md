# `Option<T>`

## 本集目標
認識 Rust 標準庫最重要的泛型 enum——`Option<T>`，理解它如何取代 null 並防止 runtime 錯誤。

## 概念說明

### null 的問題

在某些程式語言裡，任何變數都可能是 `null`（空值）。這導致一個經典問題：你以為變數有值，用了它，結果 runtime 炸掉——「null pointer exception」。null 的發明者 Tony Hoare 甚至稱它為「十億美金的錯誤」。

Rust 的解法很簡單：**沒有 null。**

取而代之的是一個泛型 enum：`Option<T>`。

### Option 的定義

`Option<T>` 長這樣（標準庫已經幫你定義好了）：

```rust,no_run
enum Option<T> {
    Some(T),
    None,
}
#
# fn main() {}
```

看起來是不是很像第 3 集我們自己寫的 `Maybe<T>`？沒錯！概念完全一樣：

- `Some(T)` 表示「有一個 `T` 型別的值」
- `None` 表示「沒有值」

### 強制處理 None

`Option` 的厲害之處在於：編譯器**強制**你處理「沒有值」的情況。你不能直接把 `Option<i32>` 當成 `i32` 來用，必須先檢查它到底是 `Some` 還是 `None`。

這就是用 `match` 的時候了：

```rust,no_run
# fn main() {
#     let maybe_value = Some("bruh");
    match maybe_value {
        Some(v) => println!("有值：{}", v),
        None => println!("沒有值"),
    }
# }
```

### Option 不用寫完整路徑

因為 `Option`、`Some`、`None` 實在太常用了，Rust 預設就把它們引入到每個檔案裡。所以你不需要寫 `Option::Some(42)`，直接寫 `Some(42)` 就好。

### 零成本的秘密：niche optimization

一個有趣的小知識：`Option<&T>` 和普通的參考 `&T` 佔用一樣大的記憶體！

因為參考 `&T` 不可能是 null，所以 Rust 在記憶體中聰明地用 null 來代表 `None`，不需要額外的空間。這叫做 **niche optimization**——利用型別中「不可能出現的值」來塞額外的資訊。

## 範例程式碼

```rust
// 在切片中找到第一個偶數，找不到就回傳 None
fn find_even(numbers: &[i32]) -> Option<i32> {
    for n in numbers {
        if n % 2 == 0 {
            return Some(*n);
        }
    }
    None
}

fn main() {
    let nums = vec![1, 3, 5, 8, 11];
    let result = find_even(&nums);

    // 用 match 取出 Option 的值
    match result {
        Some(n) => println!("找到偶數：{}", n),
        None => println!("沒有偶數"),
    }

    let odds = vec![1, 3, 5, 7];
    let result2 = find_even(&odds);

    match result2 {
        Some(n) => println!("找到偶數：{}", n),
        None => println!("沒有偶數"),
    }
}
```

## 重點整理
- `Option<T>` 是 Rust 用來表達「可能沒有值」的泛型 enum，取代了其他語言的 null
- `Some(T)` 表示有值，`None` 表示沒有值
- 編譯器強制你處理 `None` 的情況，runtime 不會有 null pointer exception
- `Option`、`Some`、`None` 太常用，Rust 預設就引入了，不需要額外路徑
- niche optimization：`Option<&T>` 和 `&T` 大小相同，零額外成本
