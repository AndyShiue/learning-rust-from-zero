# `let else`

## Goal of This Episode

Learn to use `let...else...` to bail out early when a pattern doesn't match, writing flatter code.

## Concept

### The Flip Side of `if let`

Last episode was `while let`, and before that `if let` — "if the match succeeds, do something." But sometimes you want the reverse: "if the match **fails**, leave early; if it succeeds, keep going."

Suppose we have this `enum`:

```rust,noplayground
enum Color {
    Red,
    Green,
    Blue,
    Custom(i32, i32, i32),
}
#
# fn main() {}
```

Written with `if let`:

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
#     Custom(i32, i32, i32),
# }
#
fn describe(color: Color) {
    if let Color::Custom(r, g, b) = color {
        println!("Custom color: {} {} {}", r, g, b);
    } else {
        println!("Not a custom color; ending");
        return;
    }
    // We'd like to use r, g, b here... but they're already out of scope!
}
#
# fn main() {}
```

`r`, `g`, and `b` live only inside the `if let`'s `{}` — the code afterward can't touch them.

### The `let...else...` Syntax

`let...else...` makes the bound variables live in the code that follows, rather than only inside `{}`:

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
#     Custom(i32, i32, i32),
# }
#
fn describe(color: Color) {
    let Color::Custom(r, g, b) = color else {
        println!("Not a custom color; ending");
        return;
    };
    // r, g, b are directly usable here!
    println!("Red: {}, green: {}, blue: {}", r, g, b);
}
#
# fn main() {}
```

Meaning:

1. Try to match `color` against the pattern.
2. On success, `r`, `g`, `b` are bound and the program continues downward.
3. On failure, the code inside `else` runs.

### The `else` Must Leave

The `else` block can't just "do a bit of work and continue" — it must make the program leave the current flow. Legal options include:

- `return` — leave the function
- `break` — leave the loop
- `continue` — skip to the loop's next iteration

Why? Because if the pattern doesn't match, the variables were never bound. If the program kept running after the `else`, those variables would be undefined — and Rust doesn't allow that.

### Comparison with `if let`

- `if let`: enter the `{}` block only on a successful match; bound variables live only inside.
- `let...else...`: leave on a failed match; bound variables live in all the code that follows.

`let...else...` keeps code flatter — no extra level of indentation.

## Example Code

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

fn print_circle_info(shape: Shape) {
    let Shape::Circle(radius) = shape else {
        println!("Not a circle; skipping");
        return;
    };
    // radius is directly usable here
    println!("Circle, radius = {}", radius);
}

fn main() {
    print_circle_info(Shape::Circle(3.14));
    print_circle_info(Shape::Rectangle(10, 20));

    // With continue inside a loop
    let shapes = [
        Shape::Rectangle(3, 4),
        Shape::Circle(1.0),
        Shape::Rectangle(5, 6),
        Shape::Circle(2.5),
    ];

    println!("\nPrinting only the circles:");
    for shape in shapes {
        let Shape::Circle(r) = shape else {
            continue;  // Not a circle; skip this round
        };
        println!("Radius: {}", r);
    }
}
```

## Recap

- `let pattern = expr else { return / break / continue };` leaves early when the match fails.
- The `else` must exit the current flow (`return` / `break` / `continue`).
- On a successful match, the bound variables remain usable in the code that follows.
- Better suited than `if let` to "fail → leave, succeed → continue" scenarios — the code stays flatter.
