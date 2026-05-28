# tuple

## 本集目標

用 tuple 把多個不同型別的值組合成一個，並學會怎麼取出裡面的值。

## 正文

到目前為止，我們一個變數只能存一個值。但如果我想把「一個整數、一個小數、一個布林值」綁在一起呢？這就是 **tuple**（元組）的用途。

### 建立 tuple

```rust,editable
fn main() {
    let t = (1, 3.14, true);
    println!("{}", t.0); // 1
    println!("{}", t.1); // 3.14
    println!("{}", t.2); // true
}
```

用小括號 `()` 把值包起來，用逗號隔開，就是一個 tuple 了。

要取裡面的值，用**點加索引**：`t.0`、`t.1`、`t.2`。注意索引從 0 開始喔！

### unit type — 空的 tuple

Rust 有一個特殊的 tuple，裡面什麼都沒有：

```rust,editable
fn main() {
    let _u: () = ();
}
```

這個 `()` 叫做 **unit type**（單元型別）。它是「只有一個值的型別」。它的值也是寫成 `()`。

### 標型別

如果你想明確寫出 tuple 的型別：

```rust,editable
fn main() {
    let t: (i32, f64, bool) = (1, 3.14, true);
    println!("{} {} {}", t.0, t.1, t.2);
}
```

每個位置的型別都要對應上。

### 單元素 tuple — 別忘了逗號！

如果你想建立一個只有一個元素的 tuple，要記得加逗號：

```rust,editable
fn main() {
    let not_a_tuple = (5);     // 這只是數字 5，加了括號而已
    let a_tuple = (5,);        // 這才是 tuple！注意逗號

    println!("{}", a_tuple.0); // 5
}
```

`(5)` 只是一個被括號包住的數字，不是 tuple。`(5,)` 才是。那個逗號很重要！

型別也是一樣的寫法：

```rust,editable
fn main() {
    let t: (i32,) = (5,);
    println!("{}", t.0);
}
```

`(i32)` 只是 `i32` 加了括號，`(i32,)` 才是單元素 tuple 的型別。

### 修改 tuple 裡面的值

如果 tuple 用 `let mut` 宣告，就可以修改裡面的值：

```rust,editable
fn main() {
    let mut t = (1, 2, 3, 4);
    println!("修改前：{}", t.1); // 2
    t.1 = 99;
    println!("修改後：{}", t.1); // 99
}
```

跟其他 `mut` 變數一樣——沒有 `mut` 就不能改。

## 重點整理

- tuple 用 `()` 把不同型別的值打包在一起
- 用 `t.0`、`t.1`、`t.2`……取值（索引從 0 開始）
- `()` 是 unit type，代表「沒有有意義的值」
- 單元素 tuple 要加逗號：`(5,)` 才是 tuple，`(5)` 只是數字
- `let mut` 的 tuple 可以用 `t.0 = 新值` 修改裡面的值
