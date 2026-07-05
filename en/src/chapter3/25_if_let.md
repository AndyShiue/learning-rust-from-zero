# `if let`

## Goal of This Episode

Learn to use `if let` to simplify a `match` where you only care about one pattern.

## Concept

Sometimes you only care about one variant of an `enum`, and the rest don't matter. With `match`, you must handle every case, even when you only want to handle one:

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn main() {
#     let c = Color::Blue;
    match c {
        Color::Red => println!("It's red!"),
        _ => {} // Do nothing in every other case
    }
# }
```

That `_ => {}` looks redundant. Rust offers the `if let` syntax to simplify this situation:

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn main() {
#     let c = Color::Blue;
    if let Color::Red = c {
        println!("It's red!");
    }
# }
```

`if let pattern = value` means "if this value fits this pattern, run the code in the braces."

You can add an `else` to handle the non-matching case:

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn main() {
#     let c = Color::Blue;
    if let Color::Red = c {
        println!("It's red!");
    } else {
        println!("Not red");
    }
# }
```

Note: the `=` in `if let` is a single equals sign, not two. This isn't a comparison — it's "pattern matching."

## Example Code

```rust,editable
enum Color {
    Red,
    Green,
    Blue,
}

enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

fn main() {
    let c = Color::Red;

    // Checking whether it's Red with if let
    if let Color::Red = c {
        println!("It's red!");
    }

    // With else
    let c2 = Color::Blue;

    if let Color::Red = c2 {
        println!("It's red!");
    } else {
        println!("Not red");
    }

    // if let can extract a variant's data too
    let s = Shape::Circle(5.0);

    if let Shape::Circle(r) = s {
        println!("It's a circle! Radius = {}", r);
        let area = r * r * 3.14159;
        println!("Area roughly {}", area);
    }

    // If it's not a Circle, the if-let body won't run
    let s2 = Shape::Rectangle(10, 20);

    if let Shape::Circle(r) = s2 {
        println!("This line never runs, because s2 is a Rectangle");
        println!("Radius {}", r);
    } else {
        println!("Not a circle");
    }
}
```

## `if let` Guards

`if let` can also appear in a `match` guard position (the `match` guards from Episode 20). The syntax is `pattern if let pattern2 = expression =>`:

```rust,editable
enum Wrapper {
    Value(i32),
    Empty,
}

fn lookup(key: i32) -> Wrapper {
    if key > 0 { Wrapper::Value(key * 10) } else { Wrapper::Empty }
}

fn main() {
    let items = [1, -2, 3];

    for item in items {
        match item {
            x if let Wrapper::Value(v) = lookup(x) => {
                println!("{} found: {}", x, v);
            }
            x => println!("{} not found", x),
        }
    }
}
```

`x if let Wrapper::Value(v) = lookup(x)` means: first bind the value to `x`, then pattern-match again on the result of `lookup(x)` — the arm applies only when that result is `Wrapper::Value(v)`.

This example could be written with an ordinary `if let` too. But when the logic gets more complex — say the outer `match` is already comparing other patterns and you need to pattern-match another value within one arm — an `if let` guard can sometimes read better than nesting another `if let` inside a `match` arm.

## Recap

- `if let pattern = value { ... }` is shorthand for a `match` with just one arm.
- The braces run only when the value fits the pattern.
- An `else` can handle the non-matching case.
- Patterns can extract data, as in `if let Shape::Circle(r) = s`.
- Compared to `match` + `_ => {}`, `if let` is more concise.
- `if let` also works in `match` guards: `pattern if let pattern2 = expression => ...`.
