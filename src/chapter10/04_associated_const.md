# associated `const`

## 本集目標

學會在 `trait` 和 `impl` 裡定義常數。

## 概念說明

### `trait` 裡的 associated `const`

除了方法和 associated type，`trait` 裡也能定義常數：

```rust,noplayground
trait HasLimit {
    const LIMIT: i32;
}

impl HasLimit for u8 {
    const LIMIT: i32 = 255;
}

impl HasLimit for i8 {
    const LIMIT: i32 = 127;
}
#
# fn main() {}
```

實作的時候必須指定值。使用時用 `Type::CONST` 的語法：

```rust
# trait HasLimit {
#     const LIMIT: i32;
# }
#
# impl HasLimit for u8 {
#     const LIMIT: i32 = 255;
# }
#
# impl HasLimit for i8 {
#     const LIMIT: i32 = 127;
# }
# fn main() {
    println!("u8：{}", <u8 as HasLimit>::LIMIT); // 255
    println!("i8：{}", <i8 as HasLimit>::LIMIT); // 127
# }
```

### associated `const` 可以有預設值

跟 `trait` 的預設方法一樣，associated `const` 也能有預設值：

```rust
trait Config {
    const TIMEOUT: u64 = 30;
    const RETRIES: u32 = 3;
}

struct MyApp;

impl Config for MyApp {
    const TIMEOUT: u64 = 60; // 覆蓋預設
    // RETRIES 用預設值 3
}
#
# fn main() {}
```

### `impl` 裡的 associated `const`

associated `const` 不一定要在 `trait` 裡——你也可以直接在 `impl` 區塊裡定義跟型別綁定的常數：

```rust
struct Circle;

impl Circle {
    const PI: f64 = 3.14159265358979;
}

fn main() {
    println!("PI = {}", Circle::PI);
}
```

這就像 associated function 一樣，用 `::` 存取。

## 範例程式碼

```rust
trait Bounded {
    const LOWER: i32;
    const UPPER: i32;

    fn is_in_range(&self, value: i32) -> bool {
        value >= Self::LOWER && value <= Self::UPPER
    }
}

struct Percentage;

impl Bounded for Percentage {
    const LOWER: i32 = 0;
    const UPPER: i32 = 100;
}

struct Temperature;

impl Bounded for Temperature {
    const LOWER: i32 = -273;
    const UPPER: i32 = 1000;
}

// impl 裡的 associated const
struct Grid;

impl Grid {
    const WIDTH: usize = 80;
    const HEIGHT: usize = 24;
    const TOTAL: usize = Self::WIDTH * Self::HEIGHT;
}

fn main() {
    let p = Percentage;
    println!("50 在範圍內？{}", p.is_in_range(50));
    println!("150 在範圍內？{}", p.is_in_range(150));

    println!("溫度範圍：{} ~ {}", Temperature::LOWER, Temperature::UPPER);

    println!("Grid 大小：{}x{} = {}", Grid::WIDTH, Grid::HEIGHT, Grid::TOTAL);
}
```

## 重點整理

- `trait` 裡可以定義 `const NAME: Type;`，`impl` 時指定值
- associated `const` 可以有預設值，`impl` 時可以覆蓋
- `impl` 區塊（不在 `trait` 裡）也能定義 associated `const`，用 `Type::CONST` 存取
