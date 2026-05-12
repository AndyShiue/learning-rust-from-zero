# `union`

## 本集目標

認識 `union`——所有欄位共享同一塊記憶體。

## 概念說明

### 什麼是 `union`

`struct` 的每個欄位各佔一塊記憶體。`union` 不一樣——**所有欄位共享同一塊記憶體**：

```rust,noplayground
union IntOrFloat {
    i: i32,
    f: f32,
}
#
# fn main() {}
```

`IntOrFloat` 的大小是最大欄位的大小（4 bytes）。`i` 和 `f` 佔的是同一塊記憶體——寫入 `i` 會覆蓋 `f` 的內容。

### 寫入不需要 `unsafe`，讀取需要

```rust,noplayground
# union IntOrFloat {
#     i: i32,
#     f: f32,
# }
#
# fn main() {
    let u = IntOrFloat { i: 42 };
    let value = unsafe { u.i }; // 讀取需要 unsafe
# }
```

為什麼讀取需要 `unsafe`？因為 Rust 不知道你上次寫入的是哪個欄位。如果你用 `i` 寫入 42，再用 `f` 讀出來，Rust 會把那 4 bytes 當成 `f32` 解讀——得到一個無意義的浮點數。

### 跟 `enum` 的差別

| | `enum` | `union` |
|--|--|--|
| 知道目前是哪個 variant | 有 discriminant | 不知道，你自己追蹤 |
| 讀取 | 安全 | 需要 `unsafe` |
| 大小 | 最大 variant + discriminant | 最大欄位（沒有額外開銷） |

### 用途：FFI

`union` 在純 Rust 裡幾乎用不到——`enum` 更安全也更好用。`union` 存在的主要原因是跟 C 語言互動：C 有 `union`，你需要 Rust 版的 `union` 來對應它的記憶體佈局。

## 範例程式碼

```rust
union Value {
    integer: i64,
    float: f64,
    boolean: bool,
}

fn main() {
    let v = Value { integer: 42 };

    // 讀取需要 unsafe
    unsafe {
        println!("integer: {}", v.integer);
        // 同一塊記憶體用不同型別解讀
        println!("float: {}", v.float); // 無意義的值
    }

    // 寫入不需要 unsafe
    let v2 = Value { float: 3.14 };
    unsafe {
        println!("float: {}", v2.float);
    }

    // union 的大小 = 最大欄位的大小
    println!("size: {} bytes", std::mem::size_of::<Value>()); // 8
}
```

## 重點整理

- `union` 的所有欄位共享同一塊記憶體
- 寫入不需要 `unsafe`，讀取需要——因為 Rust 不知道裡面存的是哪個欄位
- 跟 `enum` 不同：`union` 沒有 discriminant，不追蹤目前是哪個 variant
- 主要用途是 FFI（跟 C 語言的 `union` 對應）
