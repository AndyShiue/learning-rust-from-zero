# 大寫 `Self`

## 本集目標

學會用大寫 `Self` 作為「目前正在 `impl` 的型別」的別名，讓程式碼更簡潔。

## 概念說明

上一集我們在 `impl` 裡面寫了這樣的程式碼：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn new(x: i32, y: i32) -> Point {
        Point { x, y }
    }
}
#
# fn main() {}
```

注意到 `Point` 這個名字出現了三次：`impl Point`、`-> Point`、`Point { x, y }`。如果型別名很長（例如 `Rectangle`），一直重複寫就很囉嗦。

Rust 提供了大寫 `Self`（注意 S 是大寫的！），它在 `impl` 區塊裡面代表「目前正在 `impl` 的型別」。所以上面的程式碼可以改成：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn new(x: i32, y: i32) -> Self {
        Self { x, y }
    }
}
#
# fn main() {}
```

`Self` 就是 `Point` 的別名。這樣寫有兩個好處：

1. 更簡潔，尤其是型別名很長的時候
2. 如果之後改了型別名，`impl` 裡面不用每個地方都改

**注意區分：**

- 小寫 `self`：代表「這個值本身」（method 的第一個參數）
- 大寫 `Self`：代表「目前的型別」

## 範例程式碼

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    // 用 Self 代替 Point
    fn new(x: i32, y: i32) -> Self {
        Self { x, y }
    }

    fn origin() -> Self {
        Self { x: 0, y: 0 }
    }

    // method 裡也可以用 Self
    fn flip(self) -> Self {
        Self { x: self.y, y: self.x }
    }

    fn sum(self) -> i32 {
        self.x + self.y
    }
}

// enum 也可以用 Self
enum Light {
    Red,
    Yellow,
    Green,
}

impl Light {
    fn next(self) -> Self {
        match self {
            Self::Red => Self::Green,
            Self::Green => Self::Yellow,
            Self::Yellow => Self::Red,
        }
    }

    fn is_stop(self) -> bool {
        match self {
            Self::Red => true,
            Self::Yellow => true,
            Self::Green => false,
        }
    }
}

fn main() {
    // struct 使用 Self
    let p = Point::new(3, 7);
    println!("原始：({}, {})", p.x, p.y);

    let p2 = Point::new(3, 7);
    let flipped = p2.flip();
    println!("翻轉：({}, {})", flipped.x, flipped.y);

    let p3 = Point::origin();
    println!("原點：({}, {})", p3.x, p3.y);

    // enum 使用 Self
    let light = Light::Red;
    let stop = light.is_stop();
    println!("需要停嗎？{}", stop);

    let light2 = Light::Red;
    let next_light = light2.next();
    let stop2 = next_light.is_stop();
    println!("下一個燈需要停嗎？{}", stop2);
}
```

## 重點整理

- 大寫 `Self` 在 `impl` 區塊裡代表「目前的型別」
- `Self` 可以用在回傳型別 `-> Self`、建構值 `Self { ... }`、以及 `enum` variant `Self::Red`
- 小寫 `self` = 值本身，大寫 `Self` = 型別本身
- `struct` 和 `enum` 的 `impl` 裡都可以用 `Self`
- 使用 `Self` 讓程式碼更簡潔，也更容易維護

恭喜你完成了第 3 章！🎉 這一章你學會了 `struct`、`enum`、pattern matching（`match`、`if let`、`while let`、`let...else...`）、解構、associated function 和 method。你現在已經能用 Rust 的型別系統來組織資料和行為了。下一章我們要進入 Rust 最核心也最獨特的概念——所有權（ownership）！
