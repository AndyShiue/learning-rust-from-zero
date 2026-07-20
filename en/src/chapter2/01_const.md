# `const`

## Goal of This Episode

Declare a never-changing constant with `const`, and understand how it differs from `let`.

## Main Text

In Chapter 1 we learned to declare variables with `let`. Today let's meet its good friend — `const`.

`const` means "constant," as in: **this value never changes, and it's already determined at compile time.**

Here's the syntax:

```rust,editable
fn main() {
    const MAX_SCORE: i32 = 100;
    println!("The highest score is: {}", MAX_SCORE);
}
```

Looks a lot like `let`, right? But there are several important differences:

### Difference 1: `const` Must Have a Type Annotation

```rust,editable
fn main() {
    const MAX_SCORE: i32 = 100; // ✅ The : i32 is required
    let max_score = 100;        // ✅ let can omit it; the compiler infers it
}
```

With `const`, you can't lazily skip the type — the compiler will complain.

### Difference 2: The Naming Convention Is ALL CAPS with Underscores

```rust,editable
fn main() {
    const MAX_SCORE: i32 = 100;    // ✅ All caps, separated by underscores
    const PI_VALUE: f64 = 3.14159; // ✅ Like this
    const maxScore: i32 = 100;     // ⚠️ Compiles, but the compiler will warn you
}
```

This is the Rust community convention: constants use `SCREAMING_SNAKE_CASE`. Your program still runs if you don't follow it, but the compiler will grumble.

### Difference 3: `const` Can't Take `mut`

```rust,compile_fail
# #![allow(unused)]
#
# fn main() {
    const mut MAX: i32 = 100; // ❌ No such thing exists
    let mut x = 5;            // ✅ This is fine
# }
```

A constant is a constant — unchangeable means unchangeable. There's no such contradiction as a "mutable constant."

### Difference 4: `const` Can Live Outside `fn`

```rust,editable
const MAX_PLAYERS: i32 = 10;

fn main() {
    println!("At most {} players", MAX_PLAYERS);
}
```

`const` can be declared at the outermost level of a program; `let` cannot.

### When to Use `const`?

When you have a value that's **fixed and unchanging**, and you already know what it is while writing the program, use `const`. For example:

```rust,noplayground
const TAX_RATE: f64 = 0.05;
const MAX_RETRY: i32 = 3;
#
# fn main() {}
```

## Recap

- `const` declares a compile-time constant whose value never changes.
- The type annotation is mandatory (can't be omitted).
- The naming convention is all caps with underscores, like `MAX_SCORE`.
- No `mut` allowed.
- It can be placed outside `fn` so other parts of the program can use it.
