# 轉換與過濾

## 本集目標

學會迭代器最常用的轉換與過濾方法，以及如何用鏈式呼叫組合出強大的資料管道。

## 概念說明

### `.map(f)` —— 轉換每個元素

`map` 對每個元素套用閉包，產出轉換後的新元素：

```rust,noplayground
# fn main() {
    let doubled: Vec<i32> = vec![1, 2, 3].iter().map(|x| x * 2).collect();
    // [2, 4, 6]
# }
```

注意！`.iter()` 產出 `&T`，所以閉包的參數是 `&i32`。如果不想處理參考，可以搭配 `.copied()`（等等會講）。

### `.flat_map(f)` —— `map` + `flatten`

`flat_map` 等於先 `map` 再 `flatten`（上一集學的）。每個元素經過閉包轉換成一個迭代器，然後全部攤平：

```rust,noplayground
# fn main() {
    let words = vec!["abc", "de", "f"];
    let chars: Vec<char> = words.iter().flat_map(|s| s.chars()).collect();
    // ['a', 'b', 'c', 'd', 'e', 'f']
# }
```

還記得第 7 集 `Option` 和 `Result` 的 `and_then` 嗎？`flat_map` 在迭代器上做的事情本質上一樣——「轉換，但因為轉換結果本身也是容器，就攤平」。

### `.filter(pred)` —— 過濾元素

`filter` 只保留閉包回傳 `true` 的元素：

```rust,noplayground
# fn main() {
    let evens: Vec<&i32> = vec![1, 2, 3, 4, 5].iter().filter(|&&x| x % 2 == 0).collect();
    // [&2, &4]
# }
```

`filter` 的閉包接收 `&&T`（因為 `.iter()` 已經是 `&T`，`filter` 再借用一次就是 `&&T`）。這是初學者常被搞混的地方，但寫多了就習慣了。

### `.copied()` 和 `.cloned()`

當迭代器產出參考（`&T`）但你想要值（`T`）時，可以用這兩個方法把每個元素逐個複製出來：

- `.copied()` —— 要求 `T: Copy`，對每個 `&T` 做 copy 得到 `T`
- `.cloned()` —— 要求 `T: Clone`，對每個 `&T` 呼叫 `.clone()` 得到 `T`

```rust,noplayground
# fn main() {
    let numbers = vec![1, 2, 3];
    let owned: Vec<i32> = numbers.iter().copied().collect();
    // 從 &i32 變成 i32
# }
```

`.copied()` 常搭配 `.filter()` 一起用，可以避免 `&&T` 的困擾：

```rust,noplayground
# fn main() {
    let evens: Vec<i32> = vec![1, 2, 3, 4, 5]
        .iter()
        .copied()
        .filter(|x| x % 2 == 0)
        .collect();
    // [2, 4]，乾淨多了！
# }
```

### `.rev()` —— 反轉迭代順序

```rust,noplayground
# fn main() {
    let reversed: Vec<i32> = (1..=5).into_iter().rev().collect();
    // [5, 4, 3, 2, 1]
# }
```

`.rev()` 需要迭代器實作 `DoubleEndedIterator` `trait`——也就是說，它必須能從兩端取元素。`Vec`、陣列等都支援，但像 `from_fn` 產出的迭代器就不支援（因為沒有「尾端」的概念）。

### 鏈式呼叫的威力

迭代器的方法可以自由串接，形成資料處理管道：

```rust,noplayground
# fn main() {
#     let names = vec!["Andy", "Bob", "Cindy", "David"];
    let result: Vec<String> = names
        .iter()
        .enumerate()
        .filter(|(_, name)| name.len() > 3)
        .map(|(i, name)| format!("#{}: {}", i + 1, name))
        .collect();
# }
```

每一步都做一件小事，串在一起就能做很複雜的操作。而且因為迭代器是惰性的（下一集會講），中間不會產生額外的 `Vec`。

## 範例程式碼

```rust,editable
fn main() {
    let scores = vec![55, 82, 91, 47, 73, 88, 69, 95];

    // map —— 每個分數加 5 分（加分調整）
    let adjusted: Vec<i32> = scores.iter().map(|s| s + 5).collect();
    println!("加分後：{:?}", adjusted);

    // flat_map —— 每個字拆成字元
    let words = vec!["Rust", "好棒"];
    let all_chars: Vec<char> = words.iter().flat_map(|w| w.chars()).collect();
    println!("所有字元：{:?}", all_chars);

    // flat_map 類似 and_then —— 解析成功的留下，失敗的丟掉
    let inputs = vec!["42", "not_a_number", "7"];
    let parsed: Vec<i32> = inputs.iter().flat_map(|s| s.parse::<i32>()).collect();
    println!("成功解析的：{:?}", parsed);

    // filter —— 篩出及格的
    let passing: Vec<i32> = scores.iter().copied().filter(|&s| s >= 60).collect();
    println!("及格的：{:?}", passing);

    // copied —— 從 &i32 變成 i32
    let max_score: Option<i32> = scores.iter().copied().max();
    println!("\n最高分：{:?}", max_score);

    // cloned —— 從 &String 變成 String
    let names = vec![String::from("Alice"), String::from("Bob")];
    let cloned_names: Vec<String> = names.iter().cloned().collect();
    println!("cloned: {:?}", cloned_names);
    println!("原本還在：{:?}", names);

    // rev —— 反轉
    let countdown: Vec<i32> = (1..=5).into_iter().rev().collect();
    println!("\n倒數：{:?}", countdown);

    // 鏈式組合
    println!("\n--- 鏈式組合 ---");
    let long_words: Vec<&str> = vec!["hi", "hello", "hey", "howdy", "greetings"]
        .into_iter()
        .filter(|w| w.len() >= 4)
        .collect();
    println!("4 字以上的：{:?}", long_words);

    // filter + map 組合
    let words = vec!["hello", "hi", "hey", "howdy", "greetings"];
    let long_upper: Vec<String> = words
        .iter()
        .filter(|w| w.len() >= 4)
        .map(|w| w.to_uppercase())
        .collect();
    println!("\n4 字以上轉大寫：{:?}", long_upper);
}
```

## 重點整理

- `.map(f)` 轉換每個元素，`.filter(pred)` 過濾不符合條件的元素
- `.flat_map(f)` = `.map(f)` + `.flatten()`，概念上跟 `Option` / `Result` 的 `and_then` 類似
- `.copied()` 把 `&T` 逐個轉成 `T`（需要 `T: Copy`），`.cloned()` 類似但用 `Clone`
- `.rev()` 反轉迭代順序，需要 `DoubleEndedIterator`
- 這些方法可以自由鏈式呼叫，形成清晰的資料處理管道
- 配合 `.copied()` 可以避免 `filter` 中惱人的 `&&T` 問題
