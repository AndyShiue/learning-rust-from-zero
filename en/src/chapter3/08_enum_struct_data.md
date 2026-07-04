# `enum` with `struct` Variants

## Goal of This Episode

Learn to give `enum` variants named fields, `struct`-style.

## Concept

Last episode's tuple variants had unnamed fields, distinguished by position. But if a variant carries a lot of data, having no names makes things easy to mix up.

Rust lets you write variants in a style similar to named-field `struct`s, giving every field a name:

```rust,noplayground
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: i32, height: i32 },
}
#
# fn main() {}
```

Creating a value works just like creating a `struct`:

```rust,noplayground
# enum Shape {
#     Circle { radius: f64 },
#     Rectangle { width: i32, height: i32 },
# }
#
# fn main() {
    let s = Shape::Circle { radius: 5.0 };
    let r = Shape::Rectangle { width: 10, height: 20 };
# }
```

Within a single `enum`, some variants can use the tuple form, some the `struct` form, and some can carry nothing at all — mixing and matching is completely fine.

## Example Code

```rust,editable
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: i32, height: i32 },
    Dot, // A data-free variant can be mixed in too
}

fn main() {
    let s1 = Shape::Circle { radius: 5.0 };
    let s2 = Shape::Rectangle { width: 10, height: 20 };
    let s3 = Shape::Dot;

    // We can't extract the fields directly yet
    // Episode 10 covers extracting struct-variant data with match
    println!("All three shapes created!");

    // A more everyday example
    let event = Event::Click { x: 100, y: 200 };
    println!("Event created!");
}

enum Event {
    Click { x: i32, y: i32 },
    KeyPress(char), // The tuple form mixes in fine
    Quit,           // Carrying nothing works too
}
```

## Recap

- Variants can carry named fields in `struct` form: `Circle { radius: f64 }`.
- Create a value: `Shape::Circle { radius: 5.0 }`.
- One enum can mix and match: tuple-form variants, `struct`-form variants, and data-free ones.
- The `struct` form's advantage: named fields sometimes make the code easier to read.
- Extracting field data requires `match` (coming in Episode 10).
