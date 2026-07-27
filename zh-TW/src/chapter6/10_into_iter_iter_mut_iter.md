# `into_iter` / `iter_mut` / `iter`

## 本集目標

搞懂三種迭代模式的差別——消耗、可變借用、借用——以及它們和所有權系統的關係。

## 概念說明

### 三種迭代方式

前面提到過 `for x in v` 和 `for x in &v` 的差別。今天來補完整個概念，正式介紹 `Vec` 提供的三個迭代方法：

| 方法 | 產出型別 | 語意 | `Vec` 之後還能用嗎？ |
|------|---------|------|-------------------|
| `.into_iter()` | `T` | 消耗整個集合 | ✗ 不行 |
| `.iter_mut()` | `&mut T` | 可變借用每個元素 | ✓ 可以（已修改） |
| `.iter()` | `&T` | 借用每個元素 | ✓ 可以 |

### `.into_iter()` —— 拿走一切

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

### `.iter_mut()` —— 借來改改

```rust,editable
fn main() {
    let mut scores = vec![60, 70, 80];
    for score in scores.iter_mut() {
        *score += 10; // score 是 &mut i32
    }
    println!("{:?}", scores); // [70, 80, 90]
}
```

`.iter_mut()` 回傳一個產出 `&mut T` 的迭代器，讓你可以原地修改每個元素。

### `.iter()` —— 只是看看

```rust,editable
fn main() {
    let names = vec![String::from("Alice"), String::from("Bob")];
    for name in names.iter() {
        println!("{}", name); // name 是 &String
    }
    println!("names 還在：{:?}", names); // 沒問題，只是借用
}
```

`.iter()` 回傳 `&T` 的迭代器。集合本身不受影響，用完還在。

### 對應關係

這三種方法其實對應第 4 章學的三種所有權操作：

| 所有權概念 | 迭代方法 | for 簡寫 |
|-----------|---------|-----------|
| `T`（移動所有權） | `.into_iter()` | `for x in v` |
| `&mut T`（可變借用） | `.iter_mut()` | `for x in &mut v` |
| `&T`（借用） | `.iter()` | `for x in &v` |

### 背後的 `IntoIterator`

上一集學到 `for x in something` 會呼叫 `something.into_iter()`。那三種 `for` 迴圈是怎麼運作的？

其實是因為 `Vec<T>`、`&mut Vec<T>`、`&Vec<T>` 分別實作了 `IntoIterator`：

```rust,ignore
impl<T> IntoIterator for Vec<T> {
    type Item = T;
    fn into_iter(self) -> ... { /* 消耗 Vec，產出 T */ }
}

impl<'a, T> IntoIterator for &'a mut Vec<T> {
    type Item = &'a mut T;
    fn into_iter(self) -> ... { /* 等同於 .iter_mut()，產出 &mut T */ }
}

impl<'a, T> IntoIterator for &'a Vec<T> {
    type Item = &'a T;
    fn into_iter(self) -> ... { /* 等同於 .iter()，產出 &T */ }
}
```

所以 `for x in v`、`for x in &mut v`、`for x in &v`，其實會分別走到 `Vec<T>`、`&mut Vec<T>`、`&Vec<T>` 的 `IntoIterator` 實作，最終拿到 `T`、`&mut T`、`&T`。

大部分集合型別（`Vec`、陣列等）都遵循這個模式——為自己、`&mut self`、`&self` 三種各實作一次 `IntoIterator`。

### 選哪一個？

- 需要拿走元素的所有權 → `.into_iter()`。
- 需要原地修改 → `.iter_mut()`。
- 只需要讀取 → `.iter()`（最常用）。

選擇剛好能提供所需存取方式的迭代方法。

## 範例程式碼

```rust,editable
fn main() {
    // .into_iter() —— 消耗所有權
    let words = vec![
        String::from("hello"),
        String::from("world"),
    ];
    println!("--- .into_iter()（消耗） ---");
    for word in words.into_iter() {
        println!("拿到了：{}", word); // word 是 String（擁有所有權）
    }
    // println!("{:?}", words); // 編譯錯誤！words 被消耗了

    // .iter_mut() —— 可變借用，原地修改
    let mut prices = vec![100, 200, 300];
    println!("\n--- .iter_mut()（修改） ---");
    println!("打折前：{:?}", prices);
    for price in prices.iter_mut() {
        *price = *price * 8 / 10; // 打八折
    }
    println!("打折後：{:?}", prices);

    // .iter() —— 借用
    let animals = vec![
        String::from("貓"),
        String::from("狗"),
        String::from("兔子"),
    ];

    println!("\n--- .iter()（借用） ---");
    for animal in animals.iter() {
        println!("動物：{}", animal);
    }
    println!("animals 還在：{:?}", animals);

    // 簡寫版的對應
    println!("\n--- 簡寫版 ---");
    let owned = vec![1, 2, 3];

    // for x in owned 等於 for x in owned.into_iter()
    for x in owned {
        print!("{} ", x);
    }
    println!("← owned（消耗）");
    // owned 已經不能用了

    let mut mutable = vec![1, 2, 3];
    // for x in &mut mutable 等於 for x in mutable.iter_mut()
    for x in &mut mutable {
        *x *= 10;
    }
    println!("{:?} ← &mut mutable（可變借用）", mutable);

    let borrowed = vec![1, 2, 3];
    // for x in &borrowed 等於 for x in borrowed.iter()
    for x in &borrowed {
        print!("{} ", x);
    }
    println!("← &borrowed（借用）");
    println!("borrowed 還在：{:?}", borrowed);
}
```

## 重點整理

- `.into_iter()` 產出 `T`，消耗整個集合，拿走所有權。
- `.iter_mut()` 產出 `&mut T`，可以原地修改元素。
- `.iter()` 產出 `&T`，借用元素，集合不受影響。
- `for x in v` = `.into_iter()`，`for x in &mut v` = `.iter_mut()`，`for x in &v` = `.iter()`。
- 選擇剛好能提供所需存取方式的迭代方法——要消耗就 `.into_iter()`，要改就 `.iter_mut()`，只讀就 `.iter()`。
