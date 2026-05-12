# attribute 總覽

## 本集目標

整理 Rust 常見的 attribute，理解 outer 和 inner 的差別。

## 概念說明

### outer vs inner

- **outer attribute** `#[...]`：放在項目的上面，修飾那個項目
- **inner attribute** `#![...]`：放在項目的裡面（通常是檔案開頭），修飾包含它的整個項目

```rust,noplayground
#![allow(dead_code)] // inner：修飾整個 mod

#[derive(Debug)]     // outer：修飾下面的 struct
struct Point { x: i32, y: i32 }
#
# fn main() {}
```

差一個驚嘆號 `!`。

### derive

```rust,noplayground
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
struct Color(u8, u8, u8);
#
# fn main() {}
```

### 警告控制

```rust,ignore
#[allow(dead_code)]        // 不警告未使用的程式碼
#[allow(unused_variables)] // 不警告未使用的變數
#[warn(missing_docs)]      // 開啟「缺少文件」的警告
#[deny(unsafe_code)]       // 把「使用 unsafe」升級成錯誤
```

### 條件編譯

```rust,ignore
#[cfg(target_os = "windows")]
fn windows_only() { /* ... */ }

#[cfg(test)]
mod tests { /* ... */ }
```

### 測試

```rust,noplayground
#[test]
fn test_add() { assert_eq!(1 + 1, 2); }

#[test]
#[should_panic]
fn test_panic() { panic!("故意的"); }

#[test]
#[ignore]
fn slow_test() { /* 暫時跳過 */ }
#
# fn main() {}
```

### 效能提示

呼叫函數的時候，程式需要跳到函數的位置去執行，跑完再跳回來。**`inline`** 是一種最佳化：編譯器把函數的程式碼直接「貼」到呼叫的地方，省掉跳來跳去的開銷。

```rust,ignore
#[inline]         // 建議編譯器 inline 這個函數
#[inline(always)] // 強制 inline
#[inline(never)]  // 禁止 inline
```

大部分時候不需要手動寫——編譯器會自己判斷。只有在跨 crate 呼叫的小函數、或效能很關鍵的地方才需要。

### 記憶體佈局

Rust 的編譯器會自由調整 `struct` 欄位在記憶體裡的排列順序和對齊方式來節省空間。但如果你要跟 C 語言互動，C 的 `struct` 有固定的排列規則，`#[repr(C)]` 就是告訴 Rust「用 C 的規則排列」：

```rust,ignore
#[repr(C)]  // 用 C 語言的記憶體佈局
#[repr(u8)] // enum 底層型別（上一集學過）
```

### 其他常用

`#[must_use]` 標記在函數或型別上，如果呼叫者拿到回傳值卻沒有使用，編譯器會警告。`Result` 就有 `#[must_use]`——這就是為什麼你不處理 `Result` 的時候會看到警告。

```rust,noplayground
#[must_use]
fn compute() -> i32 { 42 }

fn main() {
    compute(); // 警告：回傳值沒有被使用
    let _ = compute(); // OK：用 let _ 明確忽略
}
```

```rust,ignore
#[non_exhaustive] // 告訴其他 crate 這個 enum / struct 未來可能加新的東西
#[deprecated]     // 標記已棄用
#[deprecated(since = "2.0", note = "請用 new_function")]
```

### doc comment 是 attribute 的簡寫

```rust,ignore
/// 這是一個函數
fn foo() {}

// 等同於
#[doc = "這是一個函數"]
fn foo() {}
```

`///` 只是 `#[doc = "..."]` 的簡寫。同理，`//!` 是 `#![doc = "..."]` 的簡寫——用在檔案開頭，為整個 `mod` 或 crate 寫說明文件。

## 範例程式碼

```rust
#![allow(dead_code)]

#[derive(Debug, Clone, PartialEq)]
struct Config {
    name: String,
    value: i32,
}

#[must_use]
fn create_config(name: &str, value: i32) -> Config {
    Config { name: String::from(name), value }
}

#[deprecated(note = "請用 create_config")]
fn make_config() -> Config {
    create_config("default", 0)
}

#[cfg(target_os = "linux")]
fn linux_only() {
    println!("只在 Linux 上執行");
}

fn main() {
    let c = create_config("test", 42);
    println!("{:?}", c);
}
```

## 重點整理

- `#[...]`（outer）修飾下面的項目，`#![...]`（inner）修飾包含它的項目
- `#[derive(...)]`：自動實作 `trait`
- `#[allow/warn/deny(...)]`：控制警告
- `#[cfg(...)]`：條件編譯
- `#[test]` / `#[should_panic]` / `#[ignore]`：測試相關
- `#[must_use]`：忽略回傳值時警告
- `#[deprecated]`：標記已棄用
- `///` 是 `#[doc = "..."]` 的簡寫，`//!` 是 `#![doc = "..."]` 的簡寫
