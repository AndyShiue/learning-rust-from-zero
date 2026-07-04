# `catch_unwind`

## Goal of This Episode

Learn to intercept panics with `catch_unwind`.

## Concept

### Motivation

Normally a panic aborts the current thread outright. But at an **FFI boundary**, a panic must not propagate up into C — that's undefined behavior (the advanced language features chapter mentioned FFI). `catch_unwind` lets you stop a panic on the Rust side so it never crosses the language boundary.

### Basic Usage

```rust,editable
use std::panic;

fn main() {
    let result = panic::catch_unwind(|| {
        println!("running normally");
        42
    });
    println!("{:?}", result); // Ok(42)

    let result = panic::catch_unwind(|| {
        panic!("something went wrong!");
    });
    println!("{:?}", result); // Err(...)
}
```

`catch_unwind` takes a closure; if the closure returns normally you get `Ok(value)`, and if it panics you get `Err`.

### `UnwindSafe`

`catch_unwind` requires the closure to be `UnwindSafe`. Why? Because at the moment of a panic, the closure's operations may be half-done, leaving data in an inconsistent state — the same reasoning as poisoning in the multithreading chapter.

`&mut T` is not `UnwindSafe`: if you panic halfway through modifying data via `&mut`, that data may be half-baked after the catch. Immutable things like `&T` and `i32` are `UnwindSafe`.

### `AssertUnwindSafe`

If you're sure it's fine, wrap it in `AssertUnwindSafe` to bypass the check:

```rust,noplayground
use std::panic::{catch_unwind, AssertUnwindSafe};

fn main() {
    let mut data = vec![1, 2, 3];
    let result = catch_unwind(AssertUnwindSafe(|| {
        data.push(4);
    }));
}
```

This is in the same spirit as poisoning or `unsafe` — you take responsibility for correctness yourself.

### `panic = "abort"`

`Cargo.toml` can set `panic = "abort"`, which makes a panic terminate the program immediately without any cleanup (including `drop`s). Under this setting `catch_unwind` is useless — the panic simply ends the program; there's nothing to catch.

```toml
[profile.release]
panic = "abort"
```

### A Caution

`catch_unwind` is not for ordinary error handling — that's `Result`'s job. `catch_unwind` is only for the special scenarios above.

## Example Code

```rust,editable
use std::panic;

fn might_fail(x: i32) -> i32 {
    if x == 0 {
        panic!("can't be zero!");
    }
    100 / x
}

fn main() {
    let inputs = vec![10, 5, 0, 2];

    for x in inputs {
        let result = panic::catch_unwind(|| might_fail(x));
        match result {
            Ok(val) => println!("100 / {} = {}", x, val),
            Err(_) => println!("panicked while handling {}, skipping", x),
        }
    }

    println!("the program keeps running");
}
```

## Recap

- `catch_unwind` intercepts panics, returning `Ok(value)` or `Err`.
- Its main use: FFI boundaries, keeping panics from crossing into another language.
- `UnwindSafe`: `&mut T` isn't `UnwindSafe` (the data may be half-baked).
- `AssertUnwindSafe`: manually vouch for safety and bypass the `UnwindSafe` check.
- Under `panic = "abort"`, `catch_unwind` has no effect.
- Don't use `catch_unwind` for ordinary error handling — that's `Result`'s job.

Congratulations on finishing the advanced standard library chapter! 🎉 This chapter toured practical tools from the standard library and the community — from `AsRef`, sorting, and collections, to I/O, string methods, and error handling, all the way to `catch_unwind`. In the next chapter, we enter the world of async!
