# 組合與截取

## 本集目標

學會用 `zip`、`enumerate`、`chain`、`take`、`skip`、`flatten` 來組合和截取迭代器。

## 概念說明

### `.zip(iter)` —— 把兩個迭代器配對

`zip` 把兩個迭代器「拉鍊式」地配對起來，產出 tuple：

```rust,noplayground
# fn main() {
    let names = vec!["Alice", "Bob", "Charlie"];
    let scores = vec![90, 85, 92];
    let paired: Vec<_> = names.iter().zip(scores.iter()).collect();
    // [("Alice", 90), ("Bob", 85), ("Charlie", 92)]
# }
```

如果兩個迭代器長度不同，`zip` 在較短的那個結束時就停止。

### `.enumerate()` —— 帶上索引

```rust,noplayground
# fn main() {
    let names = vec!["Alice", "Bob", "Charlie"];
    for (i, name) in names.iter().enumerate() {
        println!("第 {} 個：{}", i, name);
    }
# }
```

`enumerate` 把每個元素包成 `(index, element)` 的 tuple，索引從 0 開始。

### `.chain(iter)` —— 串接兩個迭代器

`chain` 把兩個迭代器首尾相接：

```rust,noplayground
# fn main() {
    let first = vec![1, 2, 3];
    let second = vec![4, 5, 6];
    let all: Vec<i32> = first.into_iter().chain(second.into_iter()).collect();
    // [1, 2, 3, 4, 5, 6]
# }
```

### `.take(n)` —— 只取前 n 個

```rust,noplayground
# fn main() {
    let first_three: Vec<i32> = (1..=100).into_iter().take(3).collect();
    // [1, 2, 3]
# }
```

### `.skip(n)` —— 跳過前 n 個

```rust,noplayground
# fn main() {
    let after_skip: Vec<i32> = (1..=10).into_iter().skip(7).collect();
    // [8, 9, 10]
# }
```

### `.flatten()` —— 把巢狀結構攤平

如果迭代器的元素本身也是迭代器（或 `Option`、`Vec` 等），`flatten` 可以把它攤平一層：

```rust,noplayground
# fn main() {
    let nested = vec![vec![1, 2], vec![3, 4], vec![5]];
    let flat: Vec<i32> = nested.into_iter().flatten().collect();
    // [1, 2, 3, 4, 5]
# }
```

`Option` 也可以 `flatten`——`Some(value)` 被取出，`None` 被忽略：

```rust,noplayground
# fn main() {
    let options = vec![Some(1), None, Some(3), None, Some(5)];
    let values: Vec<i32> = options.into_iter().flatten().collect();
    // [1, 3, 5]
# }
```

這是因為 `Option` 也實作了 `IntoIterator`。

## 範例程式碼

```rust,editable
fn main() {
    // zip —— 名字和分數配對
    let students = vec!["小明", "小華", "小美"];
    let grades = vec![88, 95, 72];
    println!("--- zip ---");
    for (name, grade) in students.iter().zip(grades.iter()) {
        println!("{}：{} 分", name, grade);
    }

    // enumerate —— 帶索引
    println!("\n--- enumerate ---");
    let fruits = vec!["蘋果", "香蕉", "櫻桃"];
    for (i, fruit) in fruits.iter().enumerate() {
        println!("第 {} 個：{}", i + 1, fruit);
    }

    // chain —— 串接兩個 Vec
    let morning = vec!["開會", "寫報告"];
    let afternoon = vec!["寫程式", "code review"];
    let all_tasks: Vec<&&str> = morning.iter().chain(afternoon.iter()).collect();
    println!("\n今日行程：{:?}", all_tasks);

    // take 和 skip
    let numbers: Vec<i32> = (1..=20).into_iter().collect();
    let first_five: Vec<&i32> = numbers.iter().take(5).collect();
    let last_five: Vec<&i32> = numbers.iter().skip(15).collect();
    println!("\n前 5 個：{:?}", first_five);
    println!("跳過 15 個後：{:?}", last_five);

    // take + skip 組合：取中間的
    let middle: Vec<&i32> = numbers.iter().skip(5).take(5).collect();
    println!("第 6~10 個：{:?}", middle);

    // flatten —— 攤平巢狀 Vec
    let matrix = vec![
        vec![1, 2, 3],
        vec![4, 5, 6],
        vec![7, 8, 9],
    ];
    let flat: Vec<i32> = matrix.into_iter().flatten().collect();
    println!("\n攤平矩陣：{:?}", flat);

    // flatten —— 過濾 Option
    let maybe_values = vec![Some(10), None, Some(30), None, Some(50)];
    let real_values: Vec<i32> = maybe_values.into_iter().flatten().collect();
    println!("有值的：{:?}", real_values);

    // zip + map 組合，下集就會教迭代器的 map
    println!("\n--- zip + map ---");
    let prices = vec![100, 200, 300];
    let quantities = vec![2, 1, 4];
    let grand_total: i32 = prices.iter()
        .zip(quantities.iter())
        .map(|(p, q)| p * q)
        .sum();
    println!("總計：{}", grand_total);
}
```

## 重點整理

- `.zip(iter)` 把兩個迭代器配對成 tuple，以較短的為準
- `.enumerate()` 為每個元素加上從 0 開始的索引
- `.chain(iter)` 把兩個迭代器首尾串接
- `.take(n)` 只取前 n 個元素，`.skip(n)` 跳過前 n 個
- `.flatten()` 把巢狀結構攤平一層（`Vec<Vec<T>>` → `Vec<T>`，也適用於 `Option`）
- 這些方法可以自由組合，打造出強大的資料處理管道
