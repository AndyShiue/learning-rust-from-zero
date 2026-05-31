# `for` 迴圈解構

## 本集目標

學會在 `for` 迴圈的變數位置直接解構 tuple 或 `struct`。

## 概念說明

我們已經學過 `let` 可以解構 tuple 和 `struct`。其實 `for` 迴圈的變數位置也可以——同樣的解構語法直接寫上去就行。

走訪一個裝著 tuple 的陣列：

```rust,editable
# fn main() {
    let pairs = [(1, "one"), (2, "two"), (3, "three")];

    for (num, name) in pairs {
        println!("{} = {}", num, name);
    }
# }
```

`(num, name)` 就是模式，陣列裡的每個元素都是 tuple，迴圈會把它拆開分別給 `num` 和 `name`。

走訪 `struct` 也一樣：

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let points = [
        Point { x: 0, y: 0 },
        Point { x: 1, y: 2 },
        Point { x: 3, y: 4 },
    ];

    for Point { x, y } in points {
        println!("({}, {})", x, y);
    }
}
```

把這想成是 `let` 解構和 `for` 迴圈的結合：每次迴圈拿出一個元素時，就用 `let` 解構的語法把它拆開。

## 範例程式碼

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    // 走訪 tuple 陣列並解構
    let scores = [("Alice", 85), ("Bob", 92), ("Carol", 78)];
    for (name, score) in scores {
        println!("{}: {}", name, score);
    }

    // 走訪 struct 陣列並解構
    let points = [
        Point { x: 0, y: 0 },
        Point { x: 3, y: 4 },
        Point { x: -1, y: 2 },
    ];
    for Point { x, y } in points {
        println!("({}, {})", x, y);
    }

    // 用 .. 忽略不要的欄位
    let more_points = [
        Point { x: 1, y: 10 },
        Point { x: 2, y: 20 },
    ];
    for Point { x, .. } in more_points {
        println!("x = {}", x);
    }
}
```

## 重點整理

- `for` 迴圈的變數位置可以直接寫解構模式
- 走訪 tuple 的陣列：`for (a, b) in pairs`
- 走訪 `struct` 的陣列：`for Point { x, y } in points`
