# 聚合

## 本集目標

學會用迭代器的聚合方法把一整個序列「摺疊」成一個值。

## 概念說明

### 什麼是聚合？

前幾集我們學了怎麼建立迭代器、怎麼 `collect` 成集合。但有時候你不需要一個集合，你要的是一個**單一的值**——總和、最大值、個數⋯⋯這就是聚合（aggregation）。

### `.count()` —— 數有幾個

```rust,noplayground
# fn main() {
    let names = vec!["Alice", "Bob", "Charlie"];
    let count = names.iter().count(); // 3
# }
```

### `.sum()` 和 `.product()`

```rust,noplayground
# fn main() {
    let total: i32 = (1..=10).into_iter().sum();         // 55
    let factorial: i64 = (1..=10).into_iter().product(); // 3628800
# }
```

跟 `.collect()` 一樣，`.sum()` 和 `.product()` 需要你指定回傳型別，通常用型別標註解決。

### `.min()` 和 `.max()`

```rust,noplayground
# fn main() {
    let v = vec![3, 1, 4, 1, 5, 9, 2, 6];
    let smallest = v.iter().min(); // Some(&1)
    let largest = v.iter().max();  // Some(&9)
# }
```

回傳 `Option`，因為迭代器可能是空的（空的就回傳 `None`）。

### `.fold(init, f)` —— 最通用的聚合

`fold` 是所有聚合方法的「老大」。它的型別：

```rust,ignore
fn fold<B>(self, init: B, f: impl FnMut(B, Self::Item) -> B) -> B;
```

接受一個初始值 `init`（型別 `B`）和一個閉包，每一步把「累積值」和「當前元素」組合成新的累積值：

```rust,noplayground
# fn main() {
    let sum = (1..=5).into_iter().fold(0, |acc, x| acc + x);
    // 步驟：0+1=1, 1+2=3, 3+3=6, 6+4=10, 10+5=15
# }
```

其實本集介紹的其他方法都能用 `fold` 實作：

```rust,noplayground
# fn main() {
    // count = fold 從 0 開始，每次 +1
    let count = (1..=5).into_iter().fold(0, |acc, _x| acc + 1);

    // sum = fold 從 0 開始，每次加上元素
    let sum = (1..=5).into_iter().fold(0, |acc, x| acc + x);

    // product = fold 從 1 開始，每次乘上元素
    let product = (1..=5).into_iter().fold(1, |acc, x| acc * x);

    // min / max 的實作留給底下的 reduce 做——用 fold 的話不太自然
# }
```

`fold` 還能做更靈活的事情。想把數字串成字串？想同時追蹤多個值？都可以：

```rust,noplayground
# fn main() {
    let text = (1..=5).into_iter().fold(String::new(), |mut acc, x| {
        if !acc.is_empty() {
            acc.push_str(", ");
        }
        acc.push_str(&x.to_string());
        acc
    });
    // "1, 2, 3, 4, 5"
# }
```

### `.reduce(f)` —— 沒有初始值的 `fold`

`reduce` 跟 `fold` 很像，但它用第一個元素當初始值：

```rust,noplayground
# fn main() {
    let product = vec![2, 3, 4].into_iter().reduce(|acc, x| acc * x);
    // Some(24)：2*3=6, 6*4=24
# }
```

因為可能沒有第一個元素（迭代器是空的），所以 `reduce` 回傳 `Option`。

用 `reduce` 實作 `min` 和 `max` 就很自然：

```rust,noplayground
# fn main() {
    let min = vec![3, 1, 4, 1, 5].into_iter()
        .reduce(|a, b| if a < b { a } else { b });
    // Some(1)

    let max = vec![3, 1, 4, 1, 5].into_iter()
        .reduce(|a, b| if a > b { a } else { b });
    // Some(5)
# }
```

因為 `reduce` 本身就回傳 `Option`，空迭代器自動得到 `None`—— `fold` 需要特別處理空迭代器的情形。

## 範例程式碼

```rust,editable
fn main() {
    let scores = vec![85, 92, 78, 95, 88, 76, 91];

    // .count()
    let total = scores.iter().count();
    println!("總共 {} 個分數", total);

    // .sum()
    let sum: i32 = scores.iter().sum();
    println!("總分：{}", sum);

    // .min() / .max()
    let min = scores.iter().min();
    let max = scores.iter().max();
    println!("最低分：{:?}，最高分：{:?}", min, max);

    // .product()
    let factorial: i64 = (1..=10).into_iter().product();
    println!("\n10! = {}", factorial);

    // .fold() —— 計算平均分
    let (count2, sum2) = scores.iter().fold((0, 0), |(c, s), &score| {
        (c + 1, s + score)
    });
    println!("\n用 fold 算平均：{} / {} = {}", sum2, count2, sum2 / count2);

    // .fold() —— 把數字串成字串
    let nums = vec![1, 2, 3, 4, 5];
    let formatted = nums.iter().fold(String::new(), |mut acc, &n| {
        if !acc.is_empty() {
            acc.push_str(" → ");
        }
        acc.push_str(&n.to_string());
        acc
    });
    println!("連接：{}", formatted);

    // .reduce() —— 找最長的字串
    let words = vec!["cat", "elephant", "dog", "hippopotamus"];
    let longest = words
        .iter()
        .reduce(|a, b| if a.len() >= b.len() { a } else { b });
    println!("\n最長的字：{:?}", longest);

    // .reduce() 回傳 Option（空迭代器的情況）
    let empty: Vec<i32> = vec![];
    let result = empty.into_iter().reduce(|a, b| a + b);
    println!("空 Vec 的 reduce：{:?}", result);
}
```

## 重點整理

- `.count()` 計算元素個數
- `.sum()` 和 `.product()` 計算總和與乘積，需要標註回傳型別
- `.min()` 和 `.max()` 回傳 `Option`，因為迭代器可能是空的
- `.fold(init, |acc, x| ...)` 是最通用的聚合——用初始值和閉包逐步累積
- `.reduce(|acc, x| ...)` 類似 `fold` 但用第一個元素當初始值，回傳 `Option`
- 聚合方法會消耗整個迭代器，產出一個單一的值
