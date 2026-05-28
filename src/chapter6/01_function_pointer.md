# 函數指標

## 本集目標

認識函數指標（function pointer）型別，學會把函數名稱當成值來傳遞和儲存。

## 概念說明

在 Rust 裡，函數不只能被呼叫——還能像值一樣被傳來傳去、存進變數、放進 `Vec`。要做到這件事，我們需要認識**函數指標**（function pointer）型別。

### 函數指標的寫法

假設你有一個函數：

```rust,noplayground
fn add_one(x: i32) -> i32 {
    x + 1
}
#
# fn main() {}
```

這個函數的函數指標型別是 `fn(i32) -> i32`。注意這裡的 `fn` 是小寫的——它代表函數指標型別，不是定義函數的關鍵字。

### 把函數存進變數

你可以把函數名稱直接賦值給一個變數：

```rust,noplayground
# fn add_one(x: i32) -> i32 {
#     x + 1
# }
#
# fn main() {
    let f: fn(i32) -> i32 = add_one;
# }
```

之後就能用 `f(10)` 來呼叫它，效果跟直接呼叫 `add_one(10)` 一樣。

### 把函數當參數傳遞

函數指標最常用的場景之一，就是「把一個函數傳給另一個函數」：

```rust,noplayground
fn apply(f: fn(i32) -> i32, value: i32) -> i32 {
    f(value)
}
#
# fn main() {}
```

這讓 `apply` 可以接受任何簽名為 `fn(i32) -> i32` 的函數，非常靈活。

### 多個參數和不同回傳型別

函數指標的型別由參數和回傳值決定：

- 沒有參數、沒有回傳值：`fn()`
- 兩個參數：`fn(i32, i32) -> i32`
- 回傳 `String`：`fn(&str) -> String`

### 函數指標 vs 下一集的閉包

函數指標 `fn(...) -> ...` 是一個具體的型別，大小固定。但它有一個限制——函數體沒辦法使用呼叫處的區域變數。下一集會介紹閉包（closure），它能做到這件事。

## 範例程式碼

```rust,editable
fn add_one(x: i32) -> i32 {
    x + 1
}

fn double(x: i32) -> i32 {
    x * 2
}

fn apply(f: fn(i32) -> i32, value: i32) -> i32 {
    f(value)
}

fn pick_function(use_double: bool) -> fn(i32) -> i32 {
    if use_double {
        double
    } else {
        add_one
    }
}

fn main() {
    // 把函數存進變數
    let f: fn(i32) -> i32 = add_one;
    println!("f(5) = {}", f(5));

    // 把函數當參數傳遞
    println!("apply(add_one, 10) = {}", apply(add_one, 10));
    println!("apply(double, 10) = {}", apply(double, 10));

    // 函數也可以當回傳值
    let chosen = pick_function(true);
    println!("chosen(7) = {}", chosen(7));

    let chosen2 = pick_function(false);
    println!("chosen2(7) = {}", chosen2(7));

    // 把函數放進 Vec 裡
    let operations: Vec<fn(i32) -> i32> = vec![add_one, double];
    for op in &operations {
        println!("op(3) = {}", op(3));
    }
}
```

## 重點整理

- 函數指標型別寫作 `fn(參數型別) -> 回傳型別`，注意是小寫 `fn`
- 函數名稱可以直接當成值，賦值給變數或傳遞給其他函數，也可以存進 `Vec` 等容器
- 函數指標的限制：沒辦法使用呼叫處的區域變數。下一集的閉包能做到這件事
