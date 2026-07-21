# `HashMap<K, V>`

## 本集目標

學會用 `HashMap` 儲存和查詢 key-value 資料。

## 概念說明

### 動機

如果你想用名字查分數、用 ID 查使用者，用 `Vec` 當然也做得到——存一堆 `(名字, 分數)` 的 tuple，要查的時候從頭走訪找到名字相符的那個。但這樣資料越多就越慢。

`HashMap<K, V>` 解決了這個問題。它用 hash 函數縮小 key 可能存放的範圍，通常不用走訪每一筆資料就能找到對應的值。

### 建立與基本操作

```rust,editable
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();
    scores.insert("Alice", 95);
    scores.insert("Bob", 80);

    println!("{:?}", scores.get("Alice")); // Some(&95)
    println!("{:?}", scores.get("Eve"));   // None
}
```

`insert` 放入、`get` 查詢回傳 `Option<&V>`（key 不存在就是 `None`）、`remove` 刪除並回傳 `Option<V>`（key 存在就回傳 `Some(被刪掉的值)`，不存在就回傳 `None`）。

對同一個 key 再 `insert` 會覆蓋舊值。

### 用 `collect` 從迭代器建立

```rust,noplayground
use std::collections::HashMap;

fn main() {
    let scores: HashMap<&str, i32> = vec![("Alice", 95), ("Bob", 80)]
        .into_iter()
        .collect();
}
```

### 走訪

```rust,editable
use std::collections::HashMap;

fn main() {
    let scores: HashMap<&str, i32> = vec![("Alice", 95), ("Bob", 80)]
        .into_iter()
        .collect();
    for (name, score) in &scores {
        println!("{}: {}", name, score);
    }
}
```

注意走訪順序是**不固定**的——每次跑可能不一樣。如果你需要固定順序，用 `BTreeMap`（之後會介紹）。

### `Hash` 是什麼

`HashMap` 要根據 key 快速找到對應的值。它會把 key 丟進一個 **hash 函數**，算出一個稱為 hash value 的數字，再用這個數字決定要從內部表格的哪裡開始找。如果多個 key 指向同一區域，它可能會檢查數個候選位置，直到找到 key 或確認它不在裡面。這樣就不用走訪每一筆已儲存的資料。

所以 key 的型別必須實作 `Hash` `trait`——告訴 Rust 如何把這個型別的值交給 hasher 處理。

### Key 的要求：`Eq + Hash`

Key 除了要 `Hash`，還要 `Eq`。Hash value 只能縮小搜尋範圍，不能唯一識別一個 key。不同的 key 可能指向同一區域，所以 `HashMap` 會用 `==` 確認候選者是不是你要找的 key。

大部分基本型別（整數、`bool`、`char`、`&str`、`String`）都已經實作了 `Eq + Hash`。`f64` 沒有實作 `Eq` 或 `Hash`，所以不能直接當 key（`NaN` 是其中一個原因）。

### 幫自己的型別實作 `Hash`

`Hash` 可以 derive：

```rust,noplayground
use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq, Hash)]
struct Student {
    name: String,
    grade: i32,
}

fn main() {
    let mut map = HashMap::new();
    map.insert(Student { name: String::from("Alice"), grade: 90 }, "優等");
}
```

注意你同時需要 `PartialEq`、`Eq` 和 `Hash`——因為 `Eq: PartialEq`，三個都要。

一般來說，當你 `derive` `PartialEq` 和 `Eq` 的時候，建議也一起 `derive` `Hash`。這不會有額外的代價，但讓你的型別以後需要當 `HashMap` 的 key 的時候不用再回來改。

### `entry` API

「有就不動，沒有才插入」是很常見的需求：

```rust,noplayground
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();
    scores.insert("Alice", 95);

    scores.entry("Alice").or_insert(0); // Alice 已存在，不動
    scores.entry("Eve").or_insert(0);   // Eve 不存在，插入 0
}
```

`or_insert` 回傳 `&mut V`，可以直接修改。這在計數的時候特別好用：

```rust,noplayground
# use std::collections::HashMap;
#
# fn main() {
    let words = vec!["hello", "world", "hello", "rust"];
    let mut counts = HashMap::new();

    for word in words {
        let count = counts.entry(word).or_insert(0);
        *count += 1;
    }
    // {"hello": 2, "world": 1, "rust": 1}
# }
```

### 其他常用方法

`HashMap` 還有一些常用的方法：

- `contains_key(&key)`：檢查 key 是否存在，回傳 `bool`。
- `len()`：回傳有幾組 key-value。
- `is_empty()`：是不是空的。
- `keys()`：所有 key 的迭代器
- `values()`：所有 value 的迭代器

## 範例程式碼

```rust,editable
use std::collections::HashMap;

fn main() {
    // 統計每個字元出現幾次
    let text = "hello world";
    let mut char_counts = HashMap::new();

    for c in text.chars() {
        if c == ' ' { continue; }
        let count = char_counts.entry(c).or_insert(0);
        *count += 1;
    }

    // 印出結果（順序不固定）
    for (ch, count) in &char_counts {
        println!("'{}': {} 次", ch, count);
    }

    // 找出出現最多次的字元
    if let Some((ch, count)) = char_counts.iter().max_by_key(|(_, count)| *count) {
        println!("出現最多的是 '{}'，共 {} 次", ch, count);
    }
}
```

## 重點整理

- `HashMap<K, V>` 利用 hash 按 key 尋找 value，不用走訪每一筆資料。
- `insert` 放入、`get` 查詢（回傳 `Option<&V>`）、`remove` 刪除。
- Key 必須實作 `Eq + Hash`，`Hash` 也可以 `derive`。
- `f64` 不能當 key（沒有 `Eq`）。
- `entry().or_insert()` 是「沒有才插入」的慣用寫法，回傳 `&mut V`。
- 走訪順序不固定。
