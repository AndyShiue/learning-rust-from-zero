# tuple pattern

## 本集目標

學會在 `match` 裡解構一般的 tuple 與 tuple `struct`。

## 概念說明

第 9 集學了怎麼在 `match` 裡解構 `enum` variant。其實不只 `enum`，我們也能用 `match` 解構一般的 tuple！

```rust,editable
# fn main() {
    let point = (3, 7);

    match point {
        (0, 0) => println!("原點"),
        (x, 0) => println!("在 x 軸上，x = {}", x),
        (0, y) => println!("在 y 軸上，y = {}", y),
        (x, y) => println!("在 ({}, {})", x, y),
    }
# }
```

`match` 會從上到下比對：

- `(0, 0)` → 兩個值都是 0 才會符合
- `(x, 0)` → 第二個值是 0，第一個值隨便（取出來叫 `x`）
- `(0, y)` → 第一個值是 0，第二個值隨便
- `(x, y)` → 什麼都會符合（最後一個分支當「預設」）

跟第 10 集學的一樣，模式裡可以混用「固定的值」和「變數」。固定的值用來比對，變數用來接住資料。

## 範例程式碼

```rust,editable
fn main() {
    let point = (2, 0);

    match point {
        (0, 0) => println!("原點"),
        (x, 0) => println!("在 x 軸上，x = {}", x),
        (0, y) => println!("在 y 軸上，y = {}", y),
        (x, y) => println!("一般的點 ({}, {})", x, y),
    }

    // 用 match 搭配 tuple 做簡單的分類
    let score = (85, 90);

    match score {
        (100, 100) => println!("雙滿分！"),
        (a, b) => {
            println!("國文 {}，數學 {}", a, b);
            let total = a + b;
            println!("總分 {}", total);
        }
    }
}
```

## tuple `struct` 也能用同樣的方式

還記得第 2 集學的 tuple `struct` 嗎？它的模式匹配方式和一般 tuple 一模一樣：

```rust,editable
struct Point(i32, i32);

fn main() {
    let p = Point(3, 0);

    match p {
        Point(0, 0) => println!("原點"),
        Point(x, 0) => println!("在 x 軸上，x = {}", x),
        Point(0, y) => println!("在 y 軸上，y = {}", y),
        Point(x, y) => println!("在 ({}, {})", x, y),
    }
}
```

唯一的差別是模式前面要加上型別名稱 `Point(...)`，而普通 tuple 直接寫 `(...)`。

## 重點整理

- 一般的 tuple 也可以拿來 `match`
- tuple `struct` 也能用同樣的方式進行模式匹配，只是前面要加型別名稱：`Point(x, y)`
