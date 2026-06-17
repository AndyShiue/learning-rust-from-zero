# `union`

## 本集目標

認識 `union`——所有欄位共享同一塊記憶體。

## 概念說明

### 什麼是 `union`

`struct` 的每個欄位各佔一塊記憶體。`union` 不一樣——**所有欄位共享同一塊記憶體**：

```rust,noplayground
union IntOrBool {
    i: i32,
    b: bool,
}
#
# fn main() {}
```

`IntOrBool` 的大小是最大欄位的大小（4 bytes）。`i` 和 `b` 佔的是同一塊記憶體——寫入 `i` 會覆蓋 `b` 的內容。

### 寫入不需要 `unsafe`，讀取需要

```rust,noplayground
# union IntOrBool {
#     i: i32,
#     b: bool,
# }
#
# fn main() {
    let u = IntOrBool { i: 1 };
    let value = unsafe { u.i }; // 讀取需要 unsafe
# }
```

為什麼讀取需要 `unsafe`？因為 Rust 不知道你上次寫入的是哪個欄位。`bool` 在記憶體中**必須是 0 或 1**。如果你用 `i` 寫入 42，再用 `b` 讀出來，那塊記憶體的內容是 42——對 `bool` 來說不是有效的值，這是**未定義行為**。讀取 union 欄位時，你必須自己保證記憶體裡的內容對你要讀的型別是有效的——編譯器檢查不了這件事，所以要 `unsafe`。

### 跟 `enum` 的差別

| | `enum` | `union` |
|--|--|--|
| 知道目前是哪個 variant | 有 discriminant | 不知道，你自己追蹤 |
| 讀取 | 安全 | 需要 `unsafe` |
| 大小 | 最大 variant + discriminant | 最大欄位（沒有額外開銷） |

### 用途：FFI

`union` 在純 Rust 裡幾乎用不到——`enum` 更安全也更好用。`union` 存在的主要原因是跟 C 語言互動：C 有 `union`，你需要 Rust 版的 `union` 來對應它的記憶體佈局。

## 範例程式碼

```rust,editable
union IntOrBool {
    i: i32,
    b: bool,
}

fn main() {
    // 寫入不需要 unsafe
    let u = IntOrBool { b: true };

    // 讀取需要 unsafe
    unsafe {
        // 寫 b 讀 b，沒問題
        println!("b = {}", u.b);
    }

    let v = IntOrBool { i: 42 };
    unsafe {
        println!("i = {}", v.i);
        // 千萬不要這樣做：
        // println!("b = {}", v.b);
        // bool 必須是 0 或 1，但這塊記憶體是 42 → 未定義行為！
    }

    // union 的大小 = 最大欄位的大小
    println!("size: {} bytes", std::mem::size_of::<IntOrBool>()); // 4
}
```

## 重點整理

- `union` 的所有欄位共享同一塊記憶體
- 寫入不需要 `unsafe`，讀取需要——因為 Rust 不知道裡面存的是哪個欄位
- 讀取時你必須保證記憶體內容對該型別有效——`bool` 必須是 0 或 1，寫入 42 後讀 `b` 是未定義行為
- 跟 `enum` 不同：`union` 沒有 discriminant，不追蹤目前是哪個 variant
- 主要用途是 FFI（跟 C 語言的 `union` 對應）
