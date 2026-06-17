# `const` generics

## 本集目標

學會用常數值作為泛型參數，處理任意長度的陣列。

## 概念說明

### 問題：想寫處理任意長度陣列的函數

`[i32; 3]` 和 `[i32; 5]` 是不同型別——長度是型別的一部分。如果你想寫一個函數印出任意長度的陣列，難道每個長度都要寫一個？

### `const` generics

泛型參數不只能是型別，也能是**常數值**：

```rust,editable
fn print_array<const N: usize>(arr: [i32; N]) {
    for x in arr {
        println!("{}", x);
    }
}

fn main() {
    print_array([1, 2, 3]);        // N = 3
    print_array([10, 20, 30, 40]); // N = 4
}
```

`<const N: usize>` 宣告一個常數泛型參數 `N`，型別是 `usize`。跟型別參數 `<T>` 一樣，編譯器會為每個不同的 `N` 生成一份程式碼。

### 跟 slice 的差別

你可能會想：傳 `&[i32]` 不就好了？確實，如果只是要讀取一串資料，slice 更靈活。但 `const` generics 能做到 slice 做不到的事：

**回傳固定長度的陣列：**

```rust,noplayground
fn zeros<const N: usize>() -> [i32; N] {
    [0; N]
}

fn main() {
    let a: [i32; 3] = zeros();
    let b: [i32; 10] = zeros();
}
```

slice 沒辦法回傳 `[T]`（DST），但 `[T; N]` 可以。

**在型別層面保證長度：**

```rust,noplayground
fn add_arrays<const N: usize>(a: [i32; N], b: [i32; N]) -> [i32; N] {
    let mut result = [0; N];
    for i in 0..N {
        result[i] = a[i] + b[i];
    }
    result
}
#
# fn main() {}
```

兩個參數的長度在編譯期就保證一致。slice 做不到。

### 用在 struct 上

```rust,noplayground
struct Matrix<const ROWS: usize, const COLS: usize> {
    data: [[f64; COLS]; ROWS],
}
#
# fn main() {}
```

### 表達式語法

如果 `const` generic 的位置不是簡單的字面值或路徑，要用 `{}` 包起來：

```rust,noplayground
fn example<const N: usize>() -> [i32; N] { [0; N] }

fn main() {
    let a = example::<3>();         // 字面值，不用 {}
    let b = example::<{ 1 + 2 }>(); // 表達式，要用 {}
}
```

### 搭配 `const fn`

前面學的 `const fn` 也能當 `const` generic 的值：

```rust,noplayground
const fn double(n: usize) -> usize { n * 2 }

fn zeros<const N: usize>() -> [i32; N] { [0; N] }

fn main() {
    let c = zeros::<{ double(3) }>(); // [i32; 6]，const fn 當值
}
```

## 範例程式碼

```rust,editable
fn sum<const N: usize>(arr: [i32; N]) -> i32 {
    let mut total = 0;
    for i in 0..N {
        total += arr[i];
    }
    total
}

fn filled<T: Copy, const N: usize>(value: T) -> [T; N] {
    [value; N]
}

fn main() {
    println!("sum([1, 2, 3]) = {}", sum([1, 2, 3]));
    println!("sum([10, 20]) = {}", sum([10, 20]));

    let ones: [i32; 5] = filled(1);
    println!("{:?}", ones);

    let hellos: [&str; 3] = filled("hello");
    println!("{:?}", hellos);

    // 表達式語法
    let zeros: [i32; { 2 + 3 }] = filled(0);
    println!("{:?}", zeros);
}
```

## 重點整理

- 泛型參數可以是常數值：`<const N: usize>`
- 最常見的用途：處理任意長度的陣列 `[T; N]`
- 跟 slice 的差別：`const` generics 能回傳固定長度陣列、在型別層面保證長度
- 表達式要用 `{}` 包：`Foo::<{ 1 + 2 }>`
- 可以搭配 `const fn` 使用
