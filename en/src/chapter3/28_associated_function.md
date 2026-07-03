# Associated Functions

## Goal of This Episode

Learn to define associated functions for a `struct` or `enum` with `impl`, and call them with `::`.

## Concept

So far, all our functions have been "standalone" — defined at the top level, unrelated to any type. But often, certain functions are closely tied to a specific type. For example, "create a new `Point`" relates directly to the `Point` type.

Rust uses `impl` blocks to let you "attach" functions to a type:

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

A function defined this way is called an **associated function**, because it's "associated" with the `Point` type. Call it with `::`:

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
# }
#
# fn main() {
    let p = Point::new(3, 7);
# }
```

Does `Point::new` look a little familiar? We used `::` with `enum`s too — like `Color::Red`. It's the same concept: `::` means "something under a type."

The most common use of associated functions is `new` — a "constructor" for creating values of the type.

## Example Code

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    // Associated function: create a new Point
    fn new(x: i32, y: i32) -> Point {
        Point { x, y }
    }

    // Other associated functions can be defined too
    fn origin() -> Point {
        Point { x: 0, y: 0 }
    }
}

// enums can have impl too!
enum Color {
    Red,
    Green,
    Blue,
}

impl Color {
    fn from_number(n: i32) -> Color {
        match n {
            0 => Color::Red,
            1 => Color::Green,
            _ => Color::Blue,
        }
    }
}

fn main() {
    // Calling associated functions with ::
    let p1 = Point::new(3, 7);
    println!("p1 = ({}, {})", p1.x, p1.y);

    let p2 = Point::origin();
    println!("p2 = ({}, {})", p2.x, p2.y);

    // An enum's associated function
    let c = Color::from_number(1);
    match c {
        Color::Red => println!("Red"),
        Color::Green => println!("Green"),
        Color::Blue => println!("Blue"),
    }
}
```

## Recap

- `impl TypeName { ... }` defines associated functions for a type.
- Associated functions are called with `TypeName::function_name()`.
- The most common use is a `new` function serving as a constructor.
- Both `struct`s and `enum`s can have `impl` blocks.
