# `use` Basics

## Goal of This Episode

Learn to shorten long paths with `use`, and understand why we could use `Option`, `Vec`, and friends without any `use` before.

## Concept

Rust ships with a great many built-in functions, types, and `trait`s. To organize them, the standard library sorts things into modules. Every type has a full **path** describing which module it lives in, with segments separated by `::` — like `std::string::String` (`String` lives in `std`'s `string` module), `std::vec::Vec`, `std::fmt::Display`. Normally, using a type means writing out its full path.

But strangely, we've been using `Vec`, `String`, `Option`, and `Result` all along without ever writing full paths like `std::vec::Vec`. Why?

Because Rust has a mechanism called the **prelude** — Rust imports the most commonly used functions, types, and `trait`s into every file by default. `Vec`, `String`, `Option`, `Result`, `Some`, `None`, `Ok`, `Err`, plus common `trait`s like `Clone` and `Copy`, are all in the prelude, so no full paths are needed.

But not everything is in the prelude. The `trait` `std::fmt::Display`, for instance, isn't. To use it, you either write the full path — or bring it in with `use`.

### The `use` Syntax

```rust,noplayground
use std::fmt::Display;
#
# fn main() {}
```

This line means: "Bring `std::fmt::Display` into the current scope; from now on, just write `Display`."

`use` brings an existing name into the current scope, which lets you write a shorter path. Without `use`, you write `std::fmt::Display`; with it, just `Display`.

## Example Code

```rust,editable
use std::cmp::max;

fn main() {
    // Without use, the full path is needed:
    println!("The smaller is: {}", std::cmp::min(3, 7));

    // With use, just max will do:
    println!("The larger is: {}", max(3, 7));
    println!("The larger is: {}", max(10, -2));
}
```

`std::cmp::max` and `std::cmp::min` are standard-library functions returning the larger or smaller of two values. They're not in the prelude, so it's either the full path or a `use`.

## Recap

- `use std::fmt::Display;` shortens the long path; afterward, just write `Display`.
- `use` brings an existing name into the current scope, which lets you write a shorter path.
- Rust's compiler imports the prelude's common types and `trait`s by default (`Vec`, `String`, `Option`, `Clone`, etc.).
- Things outside the prelude (like `Display`) need the full path or a `use`.
