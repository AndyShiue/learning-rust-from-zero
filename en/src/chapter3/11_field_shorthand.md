# Field Shorthand

## Goal of This Episode

Learn to simplify `struct` creation and pattern matching with field shorthand.

## Concept

Last episode we wrote `radius: r` in a match, meaning "take the `radius` field out and call it `r`." But what if you want the variable to be called `radius` itself? Following the earlier style you'd write `radius: radius` — the field name and variable name repeated, a bit wordy.

Rust offers a shorthand: if the variable name matches the field name, write it once:

```rust,noplayground
# enum Shape {
#     Circle { radius: f64 },
#     Rectangle { width: i32, height: i32 },
# }
#
# fn main() {
#     let radius = 42.0;
    // Full form
    Shape::Circle { radius: radius };
    // Shorthand (field shorthand)
    Shape::Circle { radius };
# }
```

This shorthand isn't just for `match` — **it works when creating a `struct` too**:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
    let x = 3;
    let y = 7;
    // Full form
    let p = Point { x: x, y: y };
    // Shorthand
    let p = Point { x, y };
# }
```

Whenever the variable name matches the field name, the `: variable_name` part can be dropped.

## Example Code

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

enum Shape {
    Circle { radius: f64 },
    Rectangle { width: i32, height: i32 },
}

fn main() {
    // Field shorthand when creating a struct
    let x = 5;
    let y = 10;
    let p = Point { x, y }; // Same as Point { x: x, y: y }
    println!("The point's coordinates: ({}, {})", p.x, p.y);

    // Works when creating an enum struct variant too
    let radius = 3.5;
    let s = Shape::Circle { radius }; // Same as Shape::Circle { radius: radius }

    // Field shorthand works in match as well
    match s {
        Shape::Circle { radius } => {
            println!("Circle, radius = {}", radius);
        }
        Shape::Rectangle { width, height } => {
            println!("Rectangle {}x{}", width, height);
        }
    }
}
```

## Recap

- When the variable name matches the field name, write it once: `Point { x, y }` equals `Point { x: x, y: y }`.
- This shorthand is called **field shorthand**.
- Usable when creating `struct`s / `enum` variants.
- Usable in `match` patterns too.
- It's very common — real Rust code uses the shorthand all the time.
