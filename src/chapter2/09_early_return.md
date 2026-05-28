# early `return`

## 本集目標

用 `return` 關鍵字在函數中途就把值回傳出去，不用等到最後一行。

## 正文

上一集我們學到：函數最後一行不加分號就是回傳值。但有時候你想在函數**中間**就回傳——遇到某個條件就提前結束。這時候就要用 `return` 關鍵字。

### 基本範例：絕對值

```rust,editable
fn abs(x: i32) -> i32 {
    if x >= 0 {
        return x; // 如果 x 是正數或零，直接回傳
    }
    -x            // 走到這裡代表 x 是負數，回傳 -x
}

fn main() {
    println!("abs(5) = {}", abs(5));
    println!("abs(-3) = {}", abs(-3));
    println!("abs(0) = {}", abs(0));
}
```

注意看：

- `return x;` → 用 `return` 關鍵字，**要加分號**
- 最後一行 `-x` → 不加分號，這是「自然回傳」

### `return` vs 不加分號

兩種回傳方式的比較：

```rust,noplayground
// 方式一：用 return（通常用在「提前離開」）
fn abs_v1(x: i32) -> i32 {
    if x >= 0 {
        return x;
    }
    -x
}

// 方式二：純粹用表達式（整個 if-else 就是回傳值）
fn abs_v2(x: i32) -> i32 {
    if x >= 0 {
        x
    } else {
        -x
    }
}
#
# fn main() {}
```

兩種都對！Rust 社群的慣例是：

- **有「我想要提前離開」的意思時用 return**（方式一）
- **其他時候都用表達式**（方式二）

### 實用場景：提前擋掉不合法的輸入

```rust,editable
fn divide(a: f64, b: f64) -> f64 {
    if b == 0.0 {
        println!("錯誤：不能除以零！");
        return 0.0; // 提前離開
    }

    // 這邊可能又做了很多其他事情......

    a / b
}

fn main() {
    println!("{}", divide(10.0, 3.0));
    println!("{}", divide(10.0, 0.0));
}
```

這種「先檢查、不對就提前走人」的寫法叫做 **guard clause**（守衛子句），在實務中非常常見。

### 回傳 () 的 return

如果函數回傳 `()`（例如沒有寫 `-> 型別`），`return` 後面不用寫值：

```rust,editable
fn check_age(age: i32) {
    if age < 0 {
        println!("年齡不能是負數！");
        return; // 等同於 return ();
    }
    println!("你的年齡是 {}", age);
}

fn main() {
    check_age(25);
    check_age(-3);
}
```

`return;` 是 `return ();` 的簡寫——因為回傳的是 `()`（unit type），省略不寫更簡潔。

### 不要到處用 `return`

雖然每個回傳值都寫 `return` 也能跑，但在 Rust 裡這不是好習慣：

```rust,noplayground
// 不太 Rust 的寫法
fn add_v1(a: i32, b: i32) -> i32 {
    return a + b; // 可以跑，但沒必要
}

// Rust 慣用寫法
fn add_v2(a: i32, b: i32) -> i32 {
    a + b         // 最後一行直接當回傳值
}
#
# fn main() {}
```

`return` 留給「提前離開」的場景就好。

## 重點整理

- `return 值;` 可以在函數中途提前回傳（記得加分號）
- 最後一行不加分號的自然回傳是 Rust 的慣用寫法
- `return` 最常用在 guard clause：先檢查條件，不對就提前走人
- 回傳 `()` 的函數裡，`return;` 是 `return ();` 的簡寫
- 不要每個回傳值都寫 `return`，只在需要提前離開時才用