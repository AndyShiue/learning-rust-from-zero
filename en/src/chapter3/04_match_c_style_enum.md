# `match` on C-style `enum`s

## Goal of This Episode

Learn to use `match` to run different code based on an `enum`'s value, and understand the idea of "exhaustiveness."

## Concept

Last episode we defined an `enum` but couldn't do different things based on its value. Time to learn `match` — Rust's most powerful **pattern matching** tool.

The basic syntax of `match`:

```rust,ignore
match variable {
    pattern1 => do something,
    pattern2 => do something else,
    pattern3 => do a third thing,
}
```

Each line is called an "arm." Rust checks from top to bottom and runs the code for the first pattern that matches.

**The most important rule: `match` must exhaustively cover every possible value.** If your `enum` has three variants, you must handle all three. Leave one out, and the compiler reports an error. This is Rust catching bugs for you — making sure you never forget to handle a case.

As with `struct`s and `enum`s, the last arm of a `match` can take a trailing comma. The Rust community convention is to include it.

## Example Code

```rust,editable
enum Color {
    Red,
    Green,
    Blue,
}

fn main() {
    let c = Color::Green;

    match c {
        Color::Red => println!("Red"),
        Color::Green => println!("Green"),
        Color::Blue => println!("Blue"),
    }

    // One more example
    let light = Color::Red;

    match light {
        Color::Red => println!("Stop!"),
        Color::Green => println!("Go!"),
        Color::Blue => println!("This traffic light is a bit odd..."),
    }
}
```

## Recap

- `match` compares a value against patterns and runs the corresponding arm.
- Each arm separates the pattern from the code with `=>`.
- **`match` must cover every variant** — missing one fails compilation.
- Arms are checked top to bottom; the first match runs.
- `match` is the most fundamental way Rust handles `enum`s.
