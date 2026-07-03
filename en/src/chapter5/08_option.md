# `Option<T>`

## Goal of This Episode

Meet the most important generic enum in Rust's standard library — `Option<T>` — and understand how it replaces null and prevents runtime errors.

## Concept

### The Problem with null

In some programming languages, any variable can be null (empty). This causes a classic problem: you assume a variable has a value, use it, and the program blows up at runtime — the "null pointer exception." Tony Hoare, null's inventor, even called it his "billion-dollar mistake."

Rust's solution is simple: **there is no null.**

In its place stands a generic enum: `Option<T>`.

### The Definition of `Option`

`Option<T>` looks like this (the standard library defines it for you):

```rust,noplayground
enum Option<T> {
    Some(T),
    None,
}
#
# fn main() {}
```

Doesn't it look a lot like the `Maybe<T>` we wrote ourselves in Episode 3? Exactly! Same concept:

- `Some(T)` means "there's a value of type `T`."
- `None` means "no value."

### Forced Handling of `None`

The brilliance of `Option`: the compiler **forces** you to handle the "no value" case. You can't use an `Option<i32>` directly as an `i32` — you must first check whether it's `Some` or `None`.

That's where `match` comes in:

```rust,noplayground
# fn main() {
#     let maybe_value = Some("bruh");
    match maybe_value {
        Some(v) => println!("There's a value: {}", v),
        None => println!("No value"),
    }
# }
```

### No Full Path Needed for `Option`

Because `Option`, `Some`, and `None` are so commonly used, Rust brings them into every file by default. So there's no need to write `Option::Some(42)` — just `Some(42)`.

### The Zero-cost Secret: Niche Optimization

A fun bit of trivia: `Option<&T>` occupies exactly as much memory as a plain reference `&T`!

Since a reference `&T` can never be null, Rust cleverly uses null in memory to represent `None` — no extra space needed. This is called **niche optimization**: exploiting a type's "impossible values" to squeeze in extra information.

## Example Code

```rust,editable
// Find the first even number in a slice; return None if there isn't one
fn find_even(numbers: &[i32]) -> Option<i32> {
    for n in numbers {
        if n % 2 == 0 {
            return Some(*n);
        }
    }
    None
}

fn main() {
    let nums = vec![1, 3, 5, 8, 11];
    let result = find_even(&nums);

    // Extracting the Option's value with match
    match result {
        Some(n) => println!("Found an even number: {}", n),
        None => println!("No even numbers"),
    }

    let odds = vec![1, 3, 5, 7];
    let result2 = find_even(&odds);

    match result2 {
        Some(n) => println!("Found an even number: {}", n),
        None => println!("No even numbers"),
    }
}
```

## Recap

- `Option<T>` is Rust's generic `enum` for "possibly no value," replacing other languages' null.
- `Some(T)` means a value exists; `None` means it doesn't.
- The compiler forces you to handle the `None` case — no null pointer exceptions at runtime.
- `Option`, `Some`, and `None` are so common Rust imports them by default; no extra path needed.
- Niche optimization: `Option<&T>` is the same size as `&T` — zero extra cost.
