# 其他集合簡介

## 本集目標

認識 `BTreeMap`、`BTreeSet` 和 `VecDeque`。

## 概念說明

`HashMap` 和 `HashSet` 是最常用的集合，但標準庫還有其他選擇。

### `BTreeMap`

跟 `HashMap` 的差別：key 是**有序**的。走訪的時候會按照 key 的排序順序，不是隨機順序：

```rust,editable
use std::collections::BTreeMap;

fn main() {
    let mut scores = BTreeMap::new();
    scores.insert("Charlie", 70);
    scores.insert("Alice", 90);
    scores.insert("Bob", 85);

    for (name, score) in &scores {
        println!("{}: {}", name, score);
    }
    // 一定按字母順序：Alice, Bob, Charlie
}
```

代價是 key 必須實作 `Ord`（而不是 `Hash + Eq`）。查詢速度方面，`HashMap` 不管資料量多大幾乎是固定的，`BTreeMap` 資料越多會稍微慢一點，但還是很快。

### `BTreeSet`

`BTreeSet` 就是只有 key 的 `BTreeMap`，跟 `HashSet` 對 `HashMap` 的關係一樣。元素有序，走訪時按順序輸出：

```rust,editable
use std::collections::BTreeSet;

fn main() {
    let mut set = BTreeSet::new();
    set.insert(3);
    set.insert(1);
    set.insert(2);

    for x in &set {
        print!("{} ", x);
    }
    // 1 2 3
}
```

`HashSet` 的集合運算（交集、聯集等）`BTreeSet` 也都有。

### 什麼時候用哪個

- 不在乎順序 → `HashMap` / `HashSet`（比較快）
- 需要按某種順序走訪、或需要找最小/最大的 key → `BTreeMap` / `BTreeSet`

### `VecDeque`

`Vec` 只能在尾巴高效地 `push` / `pop`。如果在頭 `insert` 或 `remove`，要把後面所有元素往後搬一格，資料越多越慢。

`VecDeque`（雙端佇列）在頭和尾都能高效操作，不管資料量多大速度都是固定的：

```rust,editable
use std::collections::VecDeque;

fn main() {
    let mut deque = VecDeque::new();
    deque.push_back(1);
    deque.push_back(2);
    deque.push_front(0);

    println!("{:?}", deque); // [0, 1, 2]

    deque.pop_front(); // 拿掉 0
    deque.pop_back();  // 拿掉 2
    println!("{:?}", deque); // [1]
}
```

### 什麼時候用 `VecDeque`

需要先進先出（FIFO）的佇列，或需要頻繁在頭尾操作的時候。如果只在尾巴操作，`Vec` 就夠了。

## 範例程式碼

```rust,editable
use std::collections::{BTreeMap, VecDeque};

fn main() {
    // BTreeMap：有序的 key-value
    let mut scores = BTreeMap::new();
    scores.insert("Charlie", 70);
    scores.insert("Alice", 90);
    scores.insert("Bob", 85);
    scores.insert("Dave", 60);

    // 一定按字母順序印出
    for (name, score) in &scores {
        println!("{}: {}", name, score);
    }

    // VecDeque：雙端佇列
    let mut queue = VecDeque::new();
    queue.push_back("第一個");
    queue.push_back("第二個");
    queue.push_back("第三個");

    // 從前面拿，先進先出
    while let Some(item) = queue.pop_front() {
        println!("處理：{}", item);
    }
}
```

## 重點整理

- `BTreeMap`：有序的 `HashMap`，key 必須實作 `Ord`
- `BTreeSet`：有序的 `HashSet`，元素必須實作 `Ord`
- 需要排序走訪用 `BTree` 系列，不需要就用 `Hash` 系列（比較快）
- `VecDeque`：雙端佇列，頭尾操作都很快
- `Vec` 只在尾巴操作快，頭部操作慢（要搬移所有元素）
