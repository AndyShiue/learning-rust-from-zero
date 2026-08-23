# Associated `const`s

## Goal of This Episode

Learn to define constants inside `trait`s and `impl`s.

## Concept

### Associated `const` in a `trait`

Besides methods and associated types, a `trait` can also define constants:

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

The implementation must specify the value. To use it, write `Type::CONST`:

```rust,editable
trait HasLimit {
    const LIMIT: i32;
}

impl HasLimit for u8 {
    const LIMIT: i32 = 255;
}

impl HasLimit for i8 {
    const LIMIT: i32 = 127;
}
fn main() {
    println!("u8: {}", u8::LIMIT); // 255
    println!("i8: {}", i8::LIMIT); // 127
}
```

### Associated `const`s Can Have Defaults

Just like a `trait`'s default methods, an associated `const` can have a default value:

```rust,editable
trait Config {
    const TIMEOUT: u64 = 30;
    const RETRIES: u32 = 3;
}

struct MyApp;

impl Config for MyApp {
    const TIMEOUT: u64 = 60; // override the default
    // RETRIES uses the default of 3
}

fn main() {}
```

### Associated `const` in an `impl`

An associated `const` doesn't have to live in a `trait` — you can also define type-bound constants directly in an `impl` block:

```rust,editable
struct Circle;

impl Circle {
    const PI: f64 = 3.14159265358979;
}

fn main() {
    println!("PI = {}", Circle::PI);
}
```

Just like an associated function, you access it with `::`.

## Example Code

```rust,editable
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

// associated const in an impl
struct Grid;

impl Grid {
    const WIDTH: usize = 80;
    const HEIGHT: usize = 24;
    const TOTAL: usize = Self::WIDTH * Self::HEIGHT;
}

fn main() {
    let p = Percentage;
    println!("is 50 in range? {}", p.is_in_range(50));
    println!("is 150 in range? {}", p.is_in_range(150));

    println!("temperature range: {} ~ {}", Temperature::LOWER, Temperature::UPPER);

    println!("Grid size: {}x{} = {}", Grid::WIDTH, Grid::HEIGHT, Grid::TOTAL);
}
```

## Recap

- A `trait` can define `const NAME: Type;`, with the value given in the `impl`.
- An associated `const` can have a default value, which the `impl` may override.
- An `impl` block (outside any `trait`) can also define associated `const`s, accessed as `Type::CONST`.
