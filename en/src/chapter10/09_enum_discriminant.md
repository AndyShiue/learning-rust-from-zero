# `enum` discriminant

## Goal of This Episode

Understand the integer value behind each `enum` variant, and how to customize it.

## Concept

### Every Variant Has an Integer Value

Chapter 3 covered C-style `enum`s. Behind every variant there is an integer, called the **discriminant**. Rust uses it to tell which variant a value currently is.

```rust,noplayground
enum Color {
    Red,   // 0
    Green, // 1
    Blue,  // 2
}
#
# fn main() {}
```

By default it starts at 0 and increments by 1 per variant.

### Getting the Discriminant with `as`

Last episode covered `as`. A C-style `enum` can be converted to an integer with `as` to reveal its discriminant:

```rust,editable
enum Color {
    Red,   // 0
    Green, // 1
    Blue,  // 2
}

fn main() {
    println!("{}", Color::Red as i32);   // 0
    println!("{}", Color::Green as i32); // 1
    println!("{}", Color::Blue as i32);  // 2
}
```

### Custom Discriminants

Specify values manually:

```rust,editable
enum HttpStatus {
    Ok = 200,
    NotFound = 404,
    InternalError = 500,
}

fn main() {
    println!("{}", HttpStatus::NotFound as i32); // 404
}
```

Unspecified variants continue from the previous one +1:

```rust,noplayground
enum Level {
    Low = 1,
    Medium,    // 2
    High,      // 3
    Critical = 10,
    Emergency, // 11
}
```

### Controlling the Underlying Type with `#[repr]`

By default, the underlying type is up to the compiler. Use `#[repr]` to specify it explicitly:

```rust,noplayground
#[repr(u8)]
enum Direction {
    North, // 0_u8
    South, // 1_u8
    East,  // 2_u8
    West,  // 3_u8
}
#
# fn main() {}
```

Common choices include `u8`, `u16`, `u32`, `i32`, and so on.

### `enum`s with Data Have Discriminants Too

An `enum` carrying data also has an internal discriminant to distinguish variants, but you **can't get it with `as`**:

```rust,compile_fail
enum Shape {
    Circle(f64),
    Rectangle(f64, f64),
}

fn main() {
    Shape::Circle(3.0) as i32; // compile error!
}
```

## Example Code

```rust,editable
#[repr(u8)]
enum Command {
    Quit = 0,
    Move = 1,
    Write = 2,
    ChangeColor = 3,
}

enum Season {
    Spring = 1,
    Summer, // 2
    Autumn, // 3
    Winter, // 4
}

fn main() {
    println!("Quit = {}", Command::Quit as u8);
    println!("Write = {}", Command::Write as u8);

    println!("Spring = {}", Season::Spring as i32);
    println!("Winter = {}", Season::Winter as i32);
}
```

## Recap

- Every `enum` variant has an integer discriminant, starting at 0 by default and incrementing.
- A C-style `enum` can be converted to an integer with `as` to see the discriminant.
- Specify values manually with `= number`; unspecified ones continue from the previous +1.
- `#[repr(u8)]` and friends control the underlying type.
- `enum`s with data have discriminants too, but they can't be obtained with `as`.
