# 函數參數

## 本集目標

幫函數加上參數，讓它能接收外部傳進來的資料。

## 正文

上一集的 `greet` 函數每次都只能印一樣的東西，有點無聊。如果我們想讓函數更靈活——比如「你告訴我兩個數字，我幫你加起來」——就需要**參數**（parameter）。

### 加上參數

```rust,editable
fn add(a: i32, b: i32) {
    println!("{} + {} = {}", a, b, a + b);
}

fn main() {
    add(3, 4);
    add(10, 20);
}
```

語法拆解：

- `a: i32` → 第一個參數叫 `a`，型別是 `i32`
- `b: i32` → 第二個參數叫 `b`，型別也是 `i32`
- 參數之間用逗號隔開

呼叫的時候，`add(3, 4)` 就是把 3 傳給 `a`、4 傳給 `b`。

### 參數一定要標型別

在 Rust 裡，函數的參數**一定要標型別**，不能偷懶：

```rust,compile_fail
fn add_v1(a, b) {           // ❌ 編譯錯誤！沒標型別
    println!("{}", a + b);
}

fn add_v2(a: i32, b: i32) { // ✅ 一定要標
    println!("{}", a + b);
}
#
# fn main() {}
```

「可是 `let x = 5;` 不是可以不標嗎？」

沒錯，`let` 可以讓編譯器自己推斷。但函數參數不行——因為函數是你的「對外介面」，Rust 希望介面要清清楚楚的，不要搞得模模糊糊。

### 多個參數、不同型別

參數可以有不同的型別：

```rust,editable
fn describe(x: i32, is_positive: bool) {
    println!("{} 是正數嗎？{}", x, is_positive);
}

fn main() {
    describe(5, true);
    describe(-3, false);
}
```

### 一個參數也行

```rust,editable
fn double(x: i32) {
    println!("{} 的兩倍是 {}", x, x * 2);
}

fn main() {
    double(5);
    double(100);
}
```

## 重點整理

- 函數參數寫在小括號裡：`fn 名字(參數: 型別)`
- 多個參數用逗號隔開
- **參數一定要標型別**，這是 Rust 的硬性規定
- 呼叫時傳入對應的值就好
