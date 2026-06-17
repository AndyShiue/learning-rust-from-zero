# 函數參數解構

## 本集目標

學會在函數的參數位置直接解構 tuple 或 `struct`。

## 概念說明

我們已經學了在 `let`、`match` 和 `for` 裡解構。其實**函數的參數也可以解構**！

假設你有一個函數，接收一個 tuple `(i32, i32)` 代表座標。與其在函數內再拆開，不如直接在參數位置就拆好：

```rust,noplayground
fn print_point((x, y): (i32, i32)) {
    println!("({}, {})", x, y);
}
#
# fn main() {}
```

注意語法：`(x, y)` 是模式（pattern），`: (i32, i32)` 是型別標註。模式和型別之間用 `:` 分隔。

呼叫的時候和平常一樣，傳一個 tuple 進去：

```rust,editable
fn print_point((x, y): (i32, i32)) {
    println!("({}, {})", x, y);
}
fn main() {
    print_point((3, 7));
}
```

`struct` 也可以在參數位置解構：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
fn print_point_struct(Point { x, y }: Point) {
    println!("({}, {})", x, y);
}
#
# fn main() {}
```

## 範例程式碼

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

// 函數參數解構 tuple
fn add_coordinates((x1, y1): (i32, i32), (x2, y2): (i32, i32)) -> (i32, i32) {
    (x1 + x2, y1 + y2)
}

// 函數參數解構 struct
// 當然這邊你也能選擇用 match
fn describe_point(Point { x, y }: Point) {
    if x == 0 && y == 0 {
        println!("原點");
    } else if x == 0 {
        println!("在 y 軸上，y = {}", y);
    } else if y == 0 {
        println!("在 x 軸上，x = {}", x);
    } else {
        println!("一般的點 ({}, {})", x, y);
    }
}

fn main() {
    // 傳 tuple 給函數
    let a = (1, 2);
    let b = (3, 4);
    let result = add_coordinates(a, b);
    println!("({}, {}) + ({}, {}) = ({}, {})", a.0, a.1, b.0, b.1, result.0, result.1);

    // 傳 struct 給函數
    let p = Point { x: 0, y: 5 };
    describe_point(p);

    let origin = Point { x: 0, y: 0 };
    describe_point(origin);
}
```

## 為什麼 tuple 和 `struct` 能用 `let` 解構？

你可能會好奇：為什麼 tuple 和 `struct` 就可以在 `let`、`for` 和函數參數裡直接解構？

```rust,compile_fail
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# enum Shape {
#     Circle { radius: f64 },
#     Rectangle { width: i32, height: i32 },
# }
#
# fn main() {
#     let p = Point { x: 6, y: 7 };
#     let s = Shape::Circle { radius: 6.7 };
    let (x, y) = (1, 2);    // OK
    let Point { x, y } = p; // OK
    let Shape::Circle { radius } = s; // 不行！
# }
```

答案是：**tuple 和 `struct` 的解構不會失敗**。一個 `(i32, i32)` 一定有兩個值，一個 `Point` 一定有 `x` 和 `y`——沒有其他可能。

但 `enum` 不一樣。一個 `Shape` 可能是 `Circle` 或 `Rectangle`。如果你寫 `let Shape::Circle { radius } = s;`，但 `s` 其實是 `Rectangle` 呢？這就失敗了。Rust 不允許 `let` 裡出現可能失敗的模式。

比對時一定會成功的模式被叫做 **irrefutable pattern**（不可反駁的模式），可能失敗的叫做 **refutable pattern**（可反駁的模式）。`let`、`for` 和函數參數只接受 irrefutable pattern。

還有什麼 irrefutable pattern 呢？

```rust,editable
fn main() {
    let arr = [1, 2, 3];
    let [head, ..] = arr;
    println!("第一個元素是 {}", head);
}
```

`arr` 的型別是 `[i32; 3]`，編譯器看一眼就知道它一定有三個元素，所以 `[head, ..]` 比對一定成功——這也是 irrefutable pattern，所以可以直接用 `let` 解構。反過來，如果今天是切片 `&[i32]`，那就不行了：切片有可能是空的，`[head, ..]` 在切片身上會變成 refutable，`let` 就接不住了。

想處理 refutable pattern？下一集會教 `if let`。

## 重點整理

- 函數參數也可以直接用模式解構：`fn foo((x, y): (i32, i32))`
- tuple 和 `struct` 都可以在參數位置解構
- 呼叫時和平常一樣傳值，解構是函數內部的事
- `let`、`for` 和函數參數只接受不會失敗的模式（irrefutable pattern），所以 tuple 和 `struct` 可以，`enum` 會有問題
