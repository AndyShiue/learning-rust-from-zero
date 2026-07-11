# `catch_unwind`

## Goal of This Episode

Learn to intercept panics with `catch_unwind`, and understand when it should be used.

## Concept

### Basic Usage

Normally, an uncaught panic eventually terminates the current thread. `catch_unwind` lets you put a boundary around a closure and catch a panic that leaves it:

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

If the closure returns normally, you get `Ok(value)`; if it panics, you get `Err`, and the program can continue afterward.

You may still see a panic message in the terminal even when the panic is caught. The important point is that the program continues and `catch_unwind` returns `Err`.

### Why Catch a Panic?

One special use is at an FFI boundary. Suppose a Rust function is exposed to C with `extern "C"`. If a panic escapes this function, the whole program automatically terminates. This is not undefined behavior, and you do not need `catch_unwind` if terminating is acceptable.

If you would rather return an error code to C, use `catch_unwind` inside the Rust function and turn `Err` into that error code. The example at the end of this episode demonstrates this pattern.

### `UnwindSafe`

`catch_unwind` requires its closure to be `UnwindSafe`. The reason is simple: a panic may interrupt a modification halfway through, and the program might continue using that half-updated data after catching it.

`&mut T` does not pass this check. If a closure modifies data through a mutable reference and then panics, the data outside the closure may be left half-updated.

Most shared references, such as `&i32` and `&String`, pass the check—but not every `&T` does. For example, `&Cell<T>` and `&RefCell<T>` do not, because `Cell` and `RefCell` allow modification through a shared reference.

`UnwindSafe` is only a reminder to think about the state left behind after a panic. It does not prove that the data is logically correct.

### `AssertUnwindSafe`

If you have considered the possible state and know how to handle it, `AssertUnwindSafe` lets you explicitly ask Rust to accept the closure:

```rust,editable
use std::panic::{catch_unwind, AssertUnwindSafe};

fn main() {
    let mut data = vec![1, 2, 3];
    let original_len = data.len();

    let result = catch_unwind(AssertUnwindSafe(|| {
        data.push(4);
        panic!("the update stopped halfway");
    }));

    if result.is_err() {
        data.truncate(original_len);
    }

    println!("{:?}", data); // [1, 2, 3]
}
```

`AssertUnwindSafe` does not repair the data for you. It only tells Rust that you accept responsibility for checking or restoring the state afterward.

### `panic = "abort"`

`Cargo.toml` can set:

```toml
[profile.release]
panic = "abort"
```

Under this setting, a panic immediately terminates the whole program. `catch_unwind` cannot catch it.

### Not Ordinary Error Handling

`catch_unwind` is not a general-purpose `try`/`catch`. Expected failures should use `Result`. Use `catch_unwind` only when you deliberately need to contain a panic, such as returning an error code from an FFI function instead of terminating the program.

## Example Code

```rust,editable
use std::panic;

// Simulates code called by an FFI function that we cannot fully control.
fn library_task(mode: i32) -> i32 {
    if mode == 0 {
        panic!("library task panicked");
    }
    100 / mode
}

extern "C" fn ffi_entry(mode: i32) -> i32 {
    match panic::catch_unwind(|| library_task(mode)) {
        Ok(value) => value,
        Err(_) => -1, // Turn the panic into an error code
    }
}

fn main() {
    println!("success: {}", ffi_entry(4)); // 25
    println!("failure: {}", ffi_entry(0)); // -1; the program continues
}
```

Here the panic is caught inside `ffi_entry`, so it never escapes the `extern "C"` function. The function returns `-1` normally instead.

## Recap

- `catch_unwind` runs a closure and returns `Ok(value)` or `Err`.
- A caught panic may still print a message, but the program can continue.
- A panic escaping an `extern "C"` Rust function automatically terminates the whole program; catch it first only when you want a different result, such as an error code.
- `&mut T` does not pass the `UnwindSafe` check. Most shared references do, but `&Cell<T>` and `&RefCell<T>` are exceptions.
- `AssertUnwindSafe` asks Rust to accept your judgment; handling half-updated data is still your responsibility.
- Under `panic = "abort"`, `catch_unwind` cannot catch a panic.
- Use `Result` for expected failures, not `catch_unwind`.

Congratulations on finishing the advanced standard library chapter! 🎉 This chapter toured practical tools from the standard library and the community — from `AsRef`, sorting, and collections, to I/O, string methods, and error handling, all the way to `catch_unwind`. In the next chapter, we enter the world of async!
