# iter / into_iter / iter_mut

## 本集目標
搞懂三種迭代模式的差別——借用、消耗、可變借用——以及它們和所有權系統的關係。

## 概念說明

### 三種迭代方式

前面提到過 `for x in &v` 和 `for x in v` 的差別。今天來正式介紹 Vec 提供的三個方法：

| 方法 | 產出型別 | 語意 | Vec 之後還能用嗎？ |
|------|---------|------|-------------------|
| `.iter()` | `&T` | 借用每個元素 | ✓ 可以 |
| `.into_iter()` | `T` | 消耗整個集合 | ✗ 不行 |
| `.iter_mut()` | `&mut T` | 可變借用每個元素 | ✓ 可以（已修改） |

### .iter() —— 只是看看

```rust
# fn main() {
    let names = vec![String::from("Alice"), String::from("Bob")];
    for name in names.iter() {
        println!("{}", name); // name 是 &String
    }
    println!("names 還在：{:?}", names); // 沒問題，只是借用
# }
```

`.iter()` 回傳 `&T` 的迭代器。集合本身不受影響，用完還在。

### .into_iter() —— 拿走一切

```rust,compile_fail
# fn main() {
    let names = vec![String::from("Alice"), String::from("Bob")];
    for name in names.into_iter() {
        println!("{}", name); // name 是 String（擁有所有權）
    }
    println!("{:?}", names); // 編譯錯誤！names 被消耗了
# }
```

`.into_iter()` 把每個元素的所有權交出來。集合本身被消耗，之後不能再用。

其實 `for name in names` 就等於 `for name in names.into_iter()`。

### .iter_mut() —— 借來改改

```rust
# fn main() {
    let mut scores = vec![60, 70, 80];
    for score in scores.iter_mut() {
        *score += 10;  // score 是 &mut i32
    }
    println!("{:?}", scores);  // [70, 80, 90]
# }
```

`.iter_mut()` 回傳 `&mut T`，讓你可以原地修改每個元素。

### 對應關係

這三種方法其實對應第四章學的三種所有權操作：

| 所有權概念 | 迭代方法 | for 簡寫 |
|-----------|---------|-----------|
| `&T`（共享借用） | `.iter()` | `for x in &v` |
| `T`（移動所有權） | `.into_iter()` | `for x in v` |
| `&mut T`（可變借用） | `.iter_mut()` | `for x in &mut v` |

### 背後的 IntoIterator

上一集學到 `for x in something` 會呼叫 `something.into_iter()`。那三種 for 迴圈是怎麼運作的？

其實是因為 `Vec<T>`、`&Vec<T>`、`&mut Vec<T>` 分別實作了 `IntoIterator`：

```rust,ignore
impl<T> IntoIterator for Vec<T> {
    type Item = T;
    fn into_iter(self) -> ... { /* 消耗 Vec，產出 T */ }
}

impl<'a, T> IntoIterator for &'a Vec<T> {
    type Item = &'a T;
    fn into_iter(self) -> ... { /* 等同於 .iter()，產出 &T */ }
}

impl<'a, T> IntoIterator for &'a mut Vec<T> {
    type Item = &'a mut T;
    fn into_iter(self) -> ... { /* 等同於 .iter_mut()，產出 &mut T */ }
}
```

所以 `for x in &v` 其實是對 `&v`（型別是 `&Vec<T>`）呼叫 `into_iter()`，走到 `&Vec<T>` 的那個 impl，最終拿到 `&T`。

大部分集合型別（Vec、String、陣列等）都遵循這個模式——為自己、`&self`、`&mut self` 三種各實作一次 `IntoIterator`。

### 選哪一個？

- 只需要讀取 → `.iter()`（最常用）
- 需要拿走元素的所有權 → `.into_iter()`
- 需要原地修改 → `.iter_mut()`

原則就是所有權的原則：不要拿你不需要的權限。

## 範例程式碼

```rust
fn main() {
    // .iter() —— 只讀借用
    let animals = vec![
        String::from("貓"),
        String::from("狗"),
        String::from("兔子"),
    ];

    println!("--- .iter()（借用） ---");
    for animal in animals.iter() {
        println!("動物：{}", animal);
    }
    println!("animals 還在：{:?}", animals);

    // .iter_mut() —— 可變借用，原地修改
    let mut prices = vec![100, 200, 300];
    println!("\n--- .iter_mut()（修改） ---");
    println!("打折前：{:?}", prices);
    for price in prices.iter_mut() {
        *price = *price * 8 / 10; // 打八折
    }
    println!("打折後：{:?}", prices);

    // .into_iter() —— 消耗所有權
    let words = vec![
        String::from("hello"),
        String::from("world"),
    ];
    println!("\n--- .into_iter()（消耗） ---");
    for word in words.into_iter() {
        println!("拿到了：{}", word); // word 是 String（擁有所有權）
    }
    // println!("{:?}", words); // 編譯錯誤！words 被消耗了

    // 簡寫版的對應
    println!("\n--- 簡寫版 ---");
    let nums = vec![1, 2, 3];

    // for x in &nums 等於 for x in nums.iter()
    for x in &nums {
        print!("{} ", x);
    }
    println!("← &nums（借用）");

    // for x in nums 等於 for x in nums.into_iter()
    for x in nums {
        print!("{} ", x);
    }
    println!("← nums（消耗）");
    // nums 已經不能用了
}
```

## 重點整理
- `.iter()` 產出 `&T`，借用元素，集合不受影響
- `.into_iter()` 產出 `T`，消耗整個集合，拿走所有權
- `.iter_mut()` 產出 `&mut T`，可以原地修改元素
- `for x in &v` = `.iter()`，`for x in v` = `.into_iter()`，`for x in &mut v` = `.iter_mut()`
- 選擇原則：不要拿超過需要的權限——只讀就 `.iter()`，要改就 `.iter_mut()`，要消耗就 `.into_iter()`
