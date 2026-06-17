# `const`

## 本集目標

用 `const` 宣告一個永遠不會變的常數，並了解它和 `let` 的差別。

## 正文

第 1 章我們學了 `let` 來宣告變數，今天來認識它的好朋友——`const`。

`const` 就是「常數」，意思是：**這個值從頭到尾都不會變，而且在編譯的時候就已經決定好了。**

來看語法：

```rust,editable
fn main() {
    const MAX_SCORE: i32 = 100;
    println!("最高分是：{}", MAX_SCORE);
}
```

看起來跟 `let` 很像對吧？但有幾個重要的差別：

### 差別一：`const` 一定要標型別

```rust,editable
fn main() {
    const MAX_SCORE: i32 = 100; // ✅ 一定要寫 : i32
    let max_score = 100;        // ✅ let 可以省略，編譯器會自己推
}
```

用 `const` 的時候，你不能偷懶不寫型別，編譯器會跟你抱怨。

### 差別二：命名慣例是全大寫加底線

```rust,editable
fn main() {
    const MAX_SCORE: i32 = 100;    // ✅ 全大寫，用底線分隔
    const PI_VALUE: f64 = 3.14159; // ✅ 這樣
    const maxScore: i32 = 100;     // ⚠️ 可以編譯，但編譯器會警告你
}
```

這是 Rust 社群的慣例：常數用 `SCREAMING_SNAKE_CASE`（全大寫蛇形命名）。不遵守的話程式還是能跑，但編譯器會碎碎念。

### 差別三：`const` 不能用 `mut`

```rust,compile_fail
# #![allow(unused)]
#
# fn main() {
    const mut MAX: i32 = 100; // ❌ 不存在這種東西
    let mut x = 5;            // ✅ 這個可以
# }
```

常數就是常數，不能變就是不能變，沒有「可變的常數」這種矛盾的東西。

### 差別四：`const` 可以放在 `fn` 外面

```rust,editable
const MAX_PLAYERS: i32 = 10;

fn main() {
    println!("最多 {} 位玩家", MAX_PLAYERS);
}
```

`let` 只能放在 `fn` 裡面，但 `const` 可以放在最外層，讓整個程式都能用到。

### 什麼時候用 `const`？

當你有一個值是**固定不變**的，而且你在寫程式的時候就知道它是多少，就用 `const`。比如：

```rust,noplayground
const TAX_RATE: f64 = 0.05;
const MAX_RETRY: i32 = 3;
#
# fn main() {}
```

## 重點整理

- `const` 宣告編譯期常數，值永遠不會變
- 一定要標型別（不能省略）
- 命名慣例是全大寫加底線，像 `MAX_SCORE`
- 不能加 `mut`
- 可以放在函數外面，讓整個程式都能用
