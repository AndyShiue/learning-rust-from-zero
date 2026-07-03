# `enum` with Tuple Variants

## Goal of This Episode

Learn to make `enum` variants carry extra data, tuple-style.

## Concept

In the C-style `enum`s we learned earlier, each variant was just a name carrying no data. But often, different options need to carry different data.

For instance, a "shape" might be a circle or a rectangle. A circle needs a radius; a rectangle needs a width and a height — they need different data. In Rust, you can have each variant carry data:

```rust,noplayground
enum Shape {
    Circle(f64),         // Carries one f64 (the radius)
    Rectangle(i32, i32), // Carries two i32s (width, height)
}
#
# fn main() {}
```

This style looks like appending tuple fields to the variant's name, so it's called a **tuple variant**.

Creating a value looks like calling a function — put the data in the parentheses:

```rust,noplayground
# enum Shape {
#     Circle(f64),
#     Rectangle(i32, i32),
# }
#
# fn main() {
    let s = Shape::Circle(3.14);
    let r = Shape::Rectangle(10, 20);
# }
```

Note: we now know how to create `enum`s that carry data, but to "extract" the data inside, we need `match` — which we'll learn in Episode 9.

## Example Code

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

enum Message {
    Quit,           // No data (just like C-style)
    Echo(i32),      // Carries one i32
    Move(i32, i32), // Carries two i32s
}

fn main() {
    let s1 = Shape::Circle(5.0);
    let s2 = Shape::Rectangle(10, 20);

    let m1 = Message::Quit;
    let m2 = Message::Echo(42);
    let m3 = Message::Move(3, 7);

    // For now, we just create the values
    // Episode 9 covers extracting the data with match
    println!("Shapes and messages created!");

    // Within one enum, different variants can carry different amounts and types of data
    // Some variants can even carry nothing at all (like Message::Quit)
}
```

## Recap

- `enum` variants can carry data: `Circle(f64)` means Circle carries one `f64`.
- Create a data-carrying variant with `Shape::Circle(5.0)`.
- Within one `enum`, different variants can carry different data.
- Some variants carry nothing, some one value, some several — very flexible.
- Extracting a variant's data requires `match` (coming in Episode 9).
