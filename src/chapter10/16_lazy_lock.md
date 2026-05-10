# LazyLock

## 本集目標
學會用 `LazyLock` 延遲初始化全域變數。

## 概念說明

`LazyLock` 嚴格來說是標準庫提供的工具，不算語言功能。但因為上一集剛學了 `static`，它又是搭配 `static` 最常用的東西，所以一併在這裡介紹。

### 問題：static 的值必須編譯期確定

`static` 的值必須在編譯期就算出來。空的 `Vec::new()` 可以（因為它是 const fn，不需要配置記憶體），但如果你想要一個**已經有內容**的 Vec 呢？

```rust,compile_fail
// vec! 巨集和 String::from 都需要在執行期配置記憶體
static NAMES: Vec<String> = vec![String::from("Alice"), String::from("Bob")];
```

那怎麼辦？既然沒辦法在編譯期給值，那就**先不給**——等到程式執行時第一次用到的時候再初始化。這就是延遲初始化。

### LazyLock

`std::sync::LazyLock` 就是做這件事的——你給它一個閉包，它會在第一次存取時才執行閉包產生值，之後都用快取的結果：

```rust
use std::sync::LazyLock;

static NAMES: LazyLock<Vec<String>> = LazyLock::new(|| {
    vec![String::from("Alice"), String::from("Bob")]
});

fn main() {
    println!("{:?}", *NAMES); // 第一次：執行閉包
    println!("{}", NAMES[0]); // 之後：直接用快取
}
```

### 為什麼叫 LazyLock

- **Lazy**：不到用的時候不初始化
- **Lock**：內部有鎖，多個執行緒同時存取時只會初始化一次（thread-safe）

## 範例程式碼

```rust
use std::sync::LazyLock;

static NAMES: LazyLock<Vec<String>> = LazyLock::new(|| {
    println!("初始化 NAMES！");
    vec![String::from("Alice"), String::from("Bob"), String::from("Charlie")]
});

fn print_first() {
    println!("第一個名字：{}", NAMES[0]);
}

fn main() {
    println!("程式開始");
    print_first(); // 第一次存取，這時才會初始化
    print_first(); // 第二次存取，直接用快取
    println!("共 {} 個名字", NAMES.len());
}
```

## 重點整理
- `static` 的值必須編譯期確定，但 `Vec`/`String` 等做不到
- `LazyLock` 延遲到第一次存取才初始化，之後用快取
- `LazyLock` 是 thread-safe 的，可以安全地用在 `static`