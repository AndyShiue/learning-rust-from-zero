# `struct`s / `enum`s inside `fn`s

## Goal of This Episode

Learn that "items" like `fn`, `struct`, and `enum` can be defined inside functions, and the fundamental ordering difference between them and `let` bindings.

> This episode supplements **Chapter 3**.

## Concept

You're probably used to defining `struct`s and `enum`s outside `fn main()`, but putting them inside is perfectly legal too:

```rust,editable
fn main() {
    struct Point {
        x: i32,
        y: i32,
    }
    let p = Point { x: 1, y: 2 };
    println!("{}", p.x);
}
```

This code compiles just fine.

### The Limitation: Visible Only within That Function

A type defined inside a function is visible only to that `fn`. Other functions can't use it. So by convention, type definitions still go outside — unless you're sure the type is used in just one `fn`.

### The Important Difference: Items Aren't Order-sensitive

Here's a point many don't know. In Rust, **items** — including `fn`, `struct`, `enum`, `trait`, `impl`, and so on — **are unaffected by definition order**. They can be used before they are defined:

```rust,editable
fn main() {
    let p = Point { x: 1, y: 2 }; // Used first
    println!("{}", p.x);

    struct Point {                // Defined later
        x: i32,
        y: i32,
    }
}
```

Completely unlike `let`! A `let` binding must appear before its use, or the compiler errors. But item definitions are "globally visible" (within their scope), regardless of which line they sit on.

### Why Is It Like This?

Because items are static definitions settled at compile time. The compiler scans all items first, builds the full type information, and only then processes runtime statements like `let`.

## Example Code

```rust,editable
fn main() {
    // Called first, defined later — perfectly legal
    greet();

    // The struct used first, defined later
    let p = Point { x: 3.0, y: 4.0 };
    println!("Coordinates: ({}, {})", p.x, p.y);

    // The enum used first, defined later
    let color = Color::Red;
    describe(color);

    // These items are all defined after their use
    struct Point {
        x: f64,
        y: f64,
    }

    enum Color {
        Red,
        Green,
        Blue,
    }

    fn describe(c: Color) {
        match c {
            Color::Red => println!("Red"),
            Color::Green => println!("Green"),
            Color::Blue => println!("Blue"),
        }
    }

    fn greet() {
        println!("Hi there!");
    }

    // But let bindings must precede their use!
    // Uncommenting the following fails to compile:
    // println!("{}", not_yet);
    let not_yet = 42;
    println!("A let binding must be declared first: {}", not_yet);
}
```

## Recap

- Items like `struct`, `enum`, and `fn` can legally be defined inside functions.
- An item defined inside an `fn` is visible only to that `fn` (scope restriction).
- Type definitions conventionally still go outside `fn`s, unless a single `fn` uses them.
- **Items are unaffected by definition order** — they can be used either before or after their definitions.
- **`let` bindings must appear before use** — the fundamental difference between items and `let`.
- The reason: items are compile-time static definitions; the compiler scans all items before handling runtime code.
