# `const fn`

## 本集目標

學會用 `const fn` 定義編譯期也能執行的函數，以及 `const { }` 區塊。

## 概念說明

### 問題：想用函數算 `const` 的值

第二章學了 `const`——編譯期常數。但 `const` 的值只能用簡單的表達式：

```rust,noplayground
const MAX: i32 = 100;        // OK
const DOUBLE: i32 = MAX * 2; // OK
#
# fn main() {}
```

如果你想用一個函數來算呢？

```rust,compile_fail
fn square(x: i32) -> i32 { x * x }
const VALUE: i32 = square(5); // 編譯錯誤！一般函數不能在編譯期執行
#
# fn main() {}
```

### `const fn`

在函數前面加上 `const`，它就變成編譯期也能執行的函數：

```rust,noplayground
const fn square(x: i32) -> i32 { x * x }
const VALUE: i32 = square(5); // OK！編譯期算出 25
#
# fn main() {}
```

`const fn` 不是「只能在編譯期用」——它在執行期也能正常呼叫，就像普通函數一樣。它只是多了一個能力：**可以在編譯期執行**。

```rust
const fn max(a: i32, b: i32) -> i32 {
    if a > b { a } else { b }
}

const BIGGER: i32 = max(10, 20); // 編譯期：20

fn main() {
    let x = max(3, 7); // 執行期：也能用，就是普通函數
    println!("{}", x);
    println!("{}", BIGGER);
}
```

### 限制

`const fn` 裡面不能做所有事情。基本原則是：**編譯器必須能在自己內部模擬執行這段程式碼**。

能做的：
- 算術、比較、邏輯運算
- `if`、`match`、`loop`、`while`、`for`
- `let` 綁定（包括 `let mut`）
- 建立 tuple、`struct`、`enum`
- 呼叫其他 `const fn`
- `panic!`（編譯期 panic 會變成編譯錯誤）

不能做的：
- 呼叫非 `const` 的函數
- 輸入 / 輸出（`println!` 等）
- 與作業系統互動
- inline assembly

Rust 每個版本都在放寬限制，能在 `const fn` 裡做的事越來越多。

### `const` 區塊

`const { ... }` 可以在任何地方插入一段編譯期運算，不需要定義 `const` 變數或 `const fn`：

```rust
fn main() {
    let x = const { 1 + 2 + 3 };
    println!("{}", x); // 6，在編譯期就算好了
}
```

這在需要「就地」做編譯期運算的時候很方便，不用另外定義一個 `const`。

## 範例程式碼

```rust
const fn factorial(n: u64) -> u64 {
    if n <= 1 {
        1
    } else {
        n * factorial(n - 1)
    }
}

const fn clamp(value: i32, min: i32, max: i32) -> i32 {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}

const FACT_10: u64 = factorial(10);
const CLAMPED: i32 = clamp(150, 0, 100);

fn main() {
    println!("10! = {}", FACT_10);
    println!("clamp(150, 0, 100) = {}", CLAMPED);

    // 執行期也能呼叫
    let n = factorial(5);
    println!("5! = {}", n);

    // const 區塊
    let size = const { std::mem::size_of::<[i32; 100]>() };
    println!("100 個 i32 的大小：{} bytes", size);
}
```

## 重點整理

- `const fn` 可以在編譯期執行，也可以在執行期執行
- 主要用來初始化 `const` 的值
- 限制：不能呼叫非 `const fn`、不能做輸入輸出，但限制逐版放寬
- `const { ... }` 區塊可以在任何地方插入編譯期運算
