# 字串方法

## 本集目標

認識 `&str` 和 `String` 上最常用的方法，以及 Rust 字串與 UTF-8 的關係。

## 概念說明

讀寫檔案的時候，拿到的內容通常是字串，你會需要各種方法來處理它——搜尋、分割、修剪、替換等等。之前我們用過 `.trim()`、`.parse()` 和 `.char()`，但 `&str` 和 `String` 上其實有非常多實用的方法。這集介紹最常用的幾個。

### 搜尋

```rust,noplayground
# fn main() {
    let s = "hello, world!";

    s.contains("world");    // true
    s.starts_with("hello"); // true
    s.ends_with("!");       // true
    s.find("world");        // Some(7)，回傳第一次出現的位置（byte index）
# }
```

### 修剪與替換

```rust,noplayground
# fn main() {
    "  hello  ".trim();       // "hello"
    "  hello  ".trim_start(); // "hello  "
    "  hello  ".trim_end();   // "  hello"

    "hello world".replace("world", "Rust"); // "hello Rust"
# }
```

### 分割

```rust,noplayground
# fn main() {
    let parts: Vec<&str> = "a,b,c".split(',').collect();
    // ["a", "b", "c"]

    let words: Vec<&str> = "hello  world".split_whitespace().collect();
    // ["hello", "world"]
# }
```

`split` 回傳迭代器，通常搭配 `collect` 使用。

### 逐字元走訪

```rust,editable
# fn main() {
    for c in "hello".chars() {
        println!("{}", c);
    }
# }
```

`.chars()` 回傳 Unicode 字元的迭代器。也有 `.bytes()` 回傳原始 byte。

### 大小寫

```rust,noplayground
# fn main() {
    "Hello".to_uppercase(); // "HELLO"
    "Hello".to_lowercase(); // "hello"
# }
```

### `len` 是 byte 數

```rust,noplayground
# fn main() {
    "hello".len();         // 5
    "hello".is_empty();    // false
    "hello".repeat(3);     // "hellohellohello"

    // 注意：len() 回傳的是 byte 數，不是字元數
    "你好".len();           // 6（UTF-8 byte 數）
    "你好".chars().count(); // 2（字元數）
# }
```

## 範例程式碼

```rust,editable
fn main() {
    let sentence = "  Hello, Rust World!  ";

    // 修剪空白
    let trimmed = sentence.trim();
    println!("修剪後：'{}'", trimmed);

    // 搜尋
    println!("包含 Rust：{}", trimmed.contains("Rust"));
    println!("Rust 的位置：{:?}", trimmed.find("Rust"));

    // 分割
    let words: Vec<&str> = trimmed.split_whitespace().collect();
    println!("字數：{}", words.len());
    for word in &words {
        println!("  {}", word);
    }

    // 替換
    let replaced = trimmed.replace("Rust", "世界");
    println!("替換後：{}", replaced);

    // UTF-8
    let chinese = "你好世界";
    println!("byte 數：{}", chinese.len());         // 12
    println!("字元數：{}", chinese.chars().count()); // 4

    for (i, c) in chinese.chars().enumerate() {
        println!("第 {} 個字元：{}", i + 1, c);
    }
}
```

## 重點整理

- `contains`、`starts_with`、`ends_with`、`find`：搜尋
- `trim`、`trim_start`、`trim_end`：修剪空白
- `replace`：替換
- `split`、`split_whitespace`：分割，回傳迭代器
- `chars`：逐字元走訪；`bytes`：逐 byte 走訪
- `len` 回傳 byte 數，字元數要用 `.chars().count()`
