# `HashSet<T>`

## 本集目標

學會用 `HashSet` 處理集合運算。

## 概念說明

### 動機

`HashMap` 存的是 key-value 對，但有時候你只關心「有沒有」而不關心對應的值——例如追蹤哪些使用者已經上線、哪些單字出現過。這時候用 `HashSet`。

### 本質

`HashSet` 其實就是只有 key 沒有 value 的 `HashMap`。所以元素一樣要求 `Eq + Hash`。

### 基本操作

```rust,editable
use std::collections::HashSet;

fn main() {
    let mut fruits = HashSet::new();
    fruits.insert("apple");
    fruits.insert("banana");
    fruits.insert("apple"); // 重複，不會加進去

    println!("{}", fruits.contains("apple")); // true
    println!("{}", fruits.len());             // 2

    fruits.remove("banana");
}
```

### 從迭代器建立

```rust,editable
use std::collections::HashSet;

fn main() {
    let nums: HashSet<i32> = vec![1, 2, 3, 2, 1].into_iter().collect();
    println!("{:?}", nums); // {1, 2, 3}，自動去掉重複
}
```

### 集合運算

這是 `HashSet` 最有用的地方：

```rust,noplayground
use std::collections::HashSet;

fn main() {
    let a: HashSet<i32> = [1, 2, 3].into_iter().collect();
    let b: HashSet<i32> = [2, 3, 4].into_iter().collect();

    // 交集：兩邊都有的
    let intersection: HashSet<_> = a.intersection(&b).copied().collect();
    // {2, 3}

    // 聯集：合在一起
    let union_set: HashSet<_> = a.union(&b).copied().collect();
    // {1, 2, 3, 4}

    // 差集：a 有但 b 沒有的
    let diff: HashSet<_> = a.difference(&b).copied().collect();
    // {1}

    // 對稱差集：只在其中一邊的
    let sym_diff: HashSet<_> = a.symmetric_difference(&b).copied().collect();
    // {1, 4}
}
```

### 運算子

進階語言功能那章學了運算子重載——`HashSet` 就用了這個功能。你可以用 `&` `|` `-` `^` 對兩個 `HashSet` 的參考做集合運算：

```rust,noplayground
# use std::collections::HashSet;
#
# fn main() {
#     let a: HashSet<i32> = [1, 2, 3].into_iter().collect();
#     let b: HashSet<i32> = [2, 3, 4].into_iter().collect();
    let intersection = &a & &b; // 交集
    let union_set    = &a | &b; // 聯集
    let diff         = &a - &b; // 差集
    let sym_diff     = &a ^ &b; // 對稱差集
# }
```

### 其他關係

```rust,editable
# use std::collections::HashSet;
#
# fn main() {
    let small: HashSet<i32> = [1, 2].into_iter().collect();
    let big: HashSet<i32> = [1, 2, 3, 4].into_iter().collect();

    println!("{}", small.is_subset(&big));   // true
    println!("{}", big.is_superset(&small)); // true
    println!("{}", small.is_disjoint(&big)); // false（有交集）
# }
```

### 走訪

跟 `HashMap` 一樣，走訪順序不固定：

```rust,noplayground
# use std::collections::HashSet;
#
# fn main() {
#     let fruits = HashSet::<&str>::new();
    for fruit in &fruits {
        println!("{}", fruit);
    }
# }
```

## 範例程式碼

```rust,editable
use std::collections::HashSet;

fn main() {
    let class_a: HashSet<&str> = ["Alice", "Bob", "Charlie", "Dave"].into_iter().collect();
    let class_b: HashSet<&str> = ["Charlie", "Dave", "Eve", "Frank"].into_iter().collect();

    println!("A 班：{:?}", class_a);
    println!("B 班：{:?}", class_b);

    // 兩班都有的人
    let both = &class_a & &class_b;
    println!("都有：{:?}", both);

    // 全部的人
    let all = &class_a | &class_b;
    println!("全部：{:?}", all);

    // 只在 A 班的人
    let only_a = &class_a - &class_b;
    println!("只在 A：{:?}", only_a);

    // 去掉重複
    let words = vec!["hello", "world", "hello", "rust", "world"];
    let unique: HashSet<_> = words.into_iter().collect();
    println!("不重複的字：{:?}", unique);
}
```

## 重點整理

- `HashSet<T>` 是只有 key 的 `HashMap`，元素不重複
- 元素必須實作 `Eq + Hash`
- `insert` 加入、`contains` 檢查、`remove` 移除
- 集合運算：`intersection`（交集）、`union`（聯集）、`difference`（差集）、`symmetric_difference`（對稱差集）
- 也可以用運算子：`&`（交集）、`|`（聯集）、`-`（差集）、`^`（對稱差集）
- `is_subset`、`is_superset`、`is_disjoint` 判斷其他關係
