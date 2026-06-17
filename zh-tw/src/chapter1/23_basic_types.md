# 型別（基礎）

## 本集目標

認識 Rust 的基本型別。

## 正文

到現在為止，我們寫 `let x = 5;` 的時候都沒有特別說 `x` 是什麼「型別」。今天來正式認識一下型別是什麼。

### 什麼是型別？

型別就是在告訴 Rust：「這個變數裡面放的是什麼東西。」

是整數？小數？文字？還是 `true` / `false`？不同的型別代表不同的資料。

### 手動標註型別

你可以在變數名稱後面加上 `: 型別` 來指定：

```rust,editable
fn main() {
    let x: i32 = 5;
    let negative: i32 = -10;
    let y: f64 = 3.14;
    let z: bool = true;

    println!("x = {}", x);
    println!("negative = {}", negative);
    println!("y = {}", y);
    println!("z = {}", z);
}
```

- `i32` → 整數（integer，32 位元）
- `f64` → 浮點數（float，64 位元），就是帶小數點的數字
- `bool` → 布林值，只有 `true` 和 `false`

### 那之前為什麼不用標？

因為 Rust 很聰明！它會看你給的值，自動**推斷**型別：

```rust,noplayground
# fn main() {
    let x = 5;    // Rust 自動判斷：這是 i32
    let y = 3.14; // Rust 自動判斷：這是 f64
    let z = true; // Rust 自動判斷：這是 bool
# }
```

這叫做**型別推斷**（type inference）。大部分的時候 Rust 都能自己搞定，你不用特別標。

## 重點整理

- 三個基本型別：`i32`（整數）、`f64`（浮點數）、`bool`（布林值）
- Rust 有**型別推斷**，大部分時候不用手動標註型別
- 需要時可以用 `let x: i32 = 5;` 手動指定型別
