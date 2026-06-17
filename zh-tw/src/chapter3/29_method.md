# method

## 本集目標

學會用 `self` 定義 method（方法），讓函數可以用 `.` 在值上面呼叫。

## 概念說明

上一集學了 associated function，它是用 `::` 呼叫的，和「型別」相關。但有時候我們想對一個**已經存在的值**做操作，比如「算出這個 `Point` 的 `x + y`」。

這就是 **method**（方法）——參數列表的第一個位置放 `self`，代表「呼叫這個方法的那個值本身」：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn sum(self) -> i32 {
        self.x + self.y
    }
}
#
# fn main() {}
```

呼叫的時候用 `.` 而不是 `::`：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# impl Point {
#     fn new(x: i32, y: i32) -> Point {
#         Point { x, y }
#     }
#
#     fn sum(self) -> i32 {
#         self.x + self.y
#     }
# }
# fn main() {
    let p = Point::new(3, 7);
    let s = p.sum(); // 用 . 呼叫 method
# }
```

注意：呼叫 `p.sum()` 的時候，**不需要再手動傳入 `self`**。`.` 前面的 `p` 會自動變成方法裡的 `self`。所以雖然定義時寫了 `fn sum(self)`，呼叫時只要寫 `p.sum()` 而不是 `p.sum(p)`。

### method 可以有其他參數

method 除了 `self` 之外，還可以有一個或更多其他的參數——就跟一般函數一樣：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn add(self, other: Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}
#
# fn main() {}
```

呼叫時，`self` 由 `.` 前面的值自動帶入，你只需要傳其他的參數：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# impl Point {
#     fn new(x: i32, y: i32) -> Point {
#         Point { x, y }
#     }
#
#     fn add(self, other: Point) -> Point {
#         Point {
#             x: self.x + other.x,
#             y: self.y + other.y,
#         }
#     }
# }
#
# fn main() {
    let p1 = Point::new(1, 2);
    let p2 = Point::new(3, 4);
    let p3 = p1.add(p2); // p1 是 self，p2 是 other
# }
```

### associated function vs method 的差別：

- associated function：沒有 `self`，用 `::` 呼叫 → `Point::new(3, 7)`
- method：第一個參數是 `self`，用 `.` 呼叫 → `p.sum()`

## 範例程式碼

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    // associated function（沒有 self）
    fn new(x: i32, y: i32) -> Point {
        Point { x, y }
    }

    // method（第一個參數是 self）
    fn sum(self) -> i32 {
        self.x + self.y
    }

    // method 可以有 self 之外的參數
    fn add(self, other: Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }

    // 另一個 method
    fn is_origin(self) -> bool {
        self.x == 0 && self.y == 0
    }
}

enum Direction {
    Up,
    Down,
    Left,
    Right,
}

impl Direction {
    // enum 也可以有 method
    fn is_horizontal(self) -> bool {
        match self {
            Direction::Left => true,
            Direction::Right => true,
            Direction::Up => false,
            Direction::Down => false,
        }
    }
}

fn main() {
    let p = Point::new(3, 7); // :: 呼叫 associated function
    let s = p.sum();          // . 呼叫 method
    println!("3 + 7 = {}", s);

    // method 帶其他參數
    let a = Point::new(1, 2);
    let b = Point::new(10, 20);
    let c = a.add(b); // a 是 self，b 是 other
    println!("相加後：({}, {})", c.x, c.y);

    let origin = Point::new(0, 0);
    println!("是原點嗎？{}", origin.is_origin());

    // enum 的 method
    let dir = Direction::Left;
    let horizontal = dir.is_horizontal();
    println!("是水平方向嗎？{}", horizontal);
}
```

## 重點整理

- method 的第一個參數是 `self`，代表值本身
- method 用 `.` 呼叫：`p.sum()`，`.` 前面的值自動成為 `self`，不需要手動傳入
- method 除了 `self` 還可以有其他參數：`fn add(self, other: Point) -> Point`，呼叫時括號內只寫 `self` 以外的參數
- `struct` 和 `enum` 都可以有 method
