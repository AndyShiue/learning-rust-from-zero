# `for` 迴圈的真面目

## 本集目標

揭開 `for` 迴圈的真面目，理解它背後其實是 `IntoIterator` + `while let` 的組合。

## 概念說明

### `for` 迴圈不是魔法

從第 1 章開始我們就在用 `for` 迴圈：

```rust,editable
# fn main() {
    let v = vec![1, 2, 3];
    for x in v {
        println!("{}", x);
    }
# }
```

看起來很簡單對吧？但這背後到底發生了什麼事？

### 迴圈展開

上面的 `for` 迴圈，編譯器其實會轉換成這樣：

```rust,editable
# fn main() {
    let v = vec![1, 2, 3];
    let mut iter = v.into_iter();
    while let Some(x) = iter.next() {
        println!("{}", x);
    }
# }
```

三個步驟：

1. 呼叫 `v.into_iter()` 把 `v` 轉成迭代器
2. 反覆呼叫 `iter.next()`
3. 用 `while let Some(x)` 解構（還記得第 3 章的 `while let` 嗎？），直到拿到 `None` 就結束

### `IntoIterator` `trait`

`IntoIterator` 是一個 `trait`，定義了「如何把自己轉成迭代器」：

```rust,noplayground
trait IntoIterator {
    type Item;
    type IntoIter: Iterator<Item = Self::Item>;
    fn into_iter(self) -> Self::IntoIter;
}
#
# fn main() {}
```

任何實作了 `IntoIterator` 的型別都可以用 `for` 迴圈。`Vec`、陣列、字串切片的 `.chars()`⋯⋯背後都是因為實作了這個 `trait`。

### `Iterator` 也實作了 `IntoIterator`

有個很方便的設計：每個 `Iterator` 都自動實作了 `IntoIterator`（`into_iter()` 直接回傳自己）。所以你可以把迭代器直接丟進 `for`：

```rust,editable
# fn main() {
    let v = vec![1, 2, 3];
    let iter = v.iter(); // 這是一個 Iterator
    for x in iter {      // Iterator 也實作了 IntoIterator
        println!("{}", x);
    }
# }
```

## 範例程式碼

```rust,editable
fn main() {
    // 正常的 for 迴圈
    let fruits = vec!["蘋果", "香蕉", "橘子"];
    println!("--- for 迴圈 ---");
    for fruit in fruits {
        println!("水果：{}", fruit);
    }

    // 手動展開成 while let（完全等價）
    let fruits = vec!["蘋果", "香蕉", "橘子"];
    println!("\n--- 手動展開 ---");
    let mut iter = fruits.into_iter();
    while let Some(fruit) = iter.next() {
        println!("水果：{}", fruit);
    }

    // 自訂迭代器（Iterator 自動實作 IntoIterator，所以能用 for）
    println!("\n--- 自訂 Iterator ---");
    let countdown = Countdown { value: 5 };
    for n in countdown {
        print!("{} ", n);
    }
    println!("發射！");

    // 迭代器本身也可以放進 for
    println!("\n--- Iterator 直接用 for ---");
    let numbers = vec![10, 20, 30, 40, 50];
    for n in numbers.iter() {
        if *n > 20 {
            println!("大於 20 的：{}", n);
        }
    }

    // Range 也實作了 IntoIterator
    println!("\n--- Range ---");
    for i in 1..=5 {
        print!("{} ", i);
    }
    println!();
}

// 自訂迭代器
struct Countdown {
    value: i32,
}

impl Iterator for Countdown {
    type Item = i32;

    fn next(&mut self) -> Option<i32> {
        if self.value > 0 {
            let current = self.value;
            self.value -= 1;
            Some(current)
        } else {
            None
        }
    }
}
```

## 重點整理

- `for x in v` 是簡寫，展開後是 `v.into_iter()` + `while let Some(x) = iter.next()`
- `IntoIterator` `trait` 定義了「如何把自己轉成迭代器」
- 任何實作了 `IntoIterator` 的型別都能用 `for` 迴圈
- 每個 `Iterator` 自動實作了 `IntoIterator`
- 之所以能寫 `for i in 1..5` 或 `for i in 1..=5`，就是因為 range 實作了 `IntoIterator`
