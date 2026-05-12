# `static` 變數

## 本集目標

了解 `static` 和 `const` 的差別，以及為什麼幾乎不該用 `static mut`。

## 概念說明

### `static` vs `const`

第二章學了 `const`——編譯期常數，值被直接嵌進使用它的地方。`static` 看起來很像，但有一個根本差異：**`static` 變數有固定的記憶體位址**。

```rust,noplayground
static GREETING: &str = "Hello, world!";
static MAX_SIZE: usize = 1024;
#
# fn main() {}
```

| | `const` | `static` |
|--|--|--|
| 記憶體 | 沒有固定位址，值嵌進使用的地方 | 有固定位址，整個程式共用一份 |
| 取位址 | 不能取 `&` | 可以取 `&`，保證永遠合法 |

大部分情況 `const` 就夠了。需要固定記憶體位址（例如傳給 C 函數）的時候才用 `static`。

### static mut

Rust 允許可變的 `static`——但讀寫都需要 `unsafe`：

```rust,noplayground
static mut COUNTER: i32 = 0;

fn increment() {
    unsafe { COUNTER += 1; }
}
#
# fn main() {}
```

為什麼需要 `unsafe`？因為 `static` 是全域共享的，多個執行緒同時讀寫就是資料競爭。

**`static mut` 幾乎永遠不該用。** 現代 Rust 有更好的替代：

- 簡單的計數器 → `AtomicI32`、`AtomicBool`
- 複雜的可變全域狀態 → `Mutex<T>`（搭配 `static`）
- 延遲初始化 → `LazyLock`（下一集教）

## 範例程式碼

```rust
use std::sync::atomic::{AtomicI32, Ordering};

// const：值嵌進使用的地方
const MAX: i32 = 100;

// static：有固定位址
static GREETING: &str = "Hello!";

// 用 atomic 取代 static mut
static COUNTER: AtomicI32 = AtomicI32::new(0);

fn increment() {
    COUNTER.fetch_add(1, Ordering::Relaxed);
}

fn main() {
    println!("{}", GREETING);
    println!("MAX = {}", MAX);

    increment();
    increment();
    increment();
    println!("COUNTER = {}", COUNTER.load(Ordering::Relaxed));
}
```

## 重點整理

- `static` 有固定記憶體位址，整個程式共用一份
- `const` 沒有固定位址，值被嵌入使用的地方；大部分情況用 `const` 就好
- `static mut` 讀寫都需要 `unsafe`，幾乎永遠不該用
- 替代方案：`AtomicXxx`、`Mutex<T>`、`LazyLock`
