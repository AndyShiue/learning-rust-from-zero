# `let` 解構 `struct`

## 本集目標

學會用 `let` 直接把 `struct` 的欄位拆開，分別賦值給變數。

## 概念說明

上一集學了 `let` 解構 tuple，現在來解構 `struct`。概念完全一樣——用 `let` 把 `struct` 的欄位一次拆開：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
#     let p = Point { x: 6, y: 7 };
    let Point { x, y } = p;
# }
```

這一行會把 `p.x` 的值放進變數 `x`，`p.y` 的值放進變數 `y`。這裡用的是 field shorthand（第 11 集學的），所以 `x` 既是欄位名也是變數名。

如果你想要的變數名和欄位名不同，可以用 `欄位名: 變數名` 的寫法：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
#     let p = Point { x: 6, y: 7 };
    let Point { x: px, y: py } = p;
    // 現在變數叫 px 和 py
# }
```

之前學的 `..` 也可以用，只取你需要的欄位：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
#     let p = Point { x: 6, y: 7 };
    let Point { x, .. } = p;
    // 只取 x，忽略其他欄位
# }
```

tuple `struct` 也可以解構，用法跟 tuple pattern 幾乎一樣，只是前面要加上型別名稱：

```rust
struct Pair(i32, i32);

fn main() {
    let p = Pair(1, 2);
    let Pair(a, b) = p;
}
```

## 範例程式碼

```rust
struct Point {
    x: i32,
    y: i32,
}

struct Rectangle {
    x: i32,
    y: i32,
    width: i32,
    height: i32,
}

fn main() {
    let p = Point { x: 5, y: 10 };

    // let 解構 struct（用 field shorthand）
    let Point { x, y } = p;
    println!("x = {}, y = {}", x, y);

    // 用不同的變數名
    let p2 = Point { x: 3, y: 7 };
    let Point { x: px, y: py } = p2;
    println!("px = {}, py = {}", px, py);

    // 搭配 .. 只取部分欄位
    let rect = Rectangle { x: 0, y: 0, width: 100, height: 50 };
    let Rectangle { width, height, .. } = rect;
    println!("寬 {}，高 {}", width, height);
    let area = width * height;
    println!("面積 = {}", area);
}
```

## 重點整理

- `let Point { x, y } = p;` 把 `struct` 的欄位拆成個別變數
- `..` 可以忽略不需要的欄位
- tuple `struct` 也能解構：`let Pair(a, b) = p;`
- `let` 解構在取出 `struct` 資料時非常方便
