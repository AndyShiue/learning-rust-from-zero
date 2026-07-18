# `cargo test`

## Goal of This Episode

Learn to write tests with `#[test]`, verify results with the `assert!` family of macros, and run tests with `cargo test`.

## Concept

### Why Write Tests?

Once code is written, how do you know it's right? Run it by hand? Then you'll be running it again after every change. **Automated tests** let you write once and verify at any time — one command tells you whether anything broke.

### The Simplest Test

Add `#[test]` above a function, and it becomes a test function:

```rust,noplayground
#[test]
fn it_works() {
    assert_eq!(2 + 2, 4);
}
#
# fn main() {}
```

Run `cargo test`, and Rust automatically finds and executes every function marked `#[test]`. If a test function panics, that test counts as failed.

### The `assert` Family of Macros

- `assert!(condition)` — panics if `condition` is `false`.
- `assert_eq!(left, right)` — panics if `left != right`.
- `assert_ne!(left, right)` — panics if `left == right`.

On failure, `assert_eq!` and `assert_ne!` print both values in `Debug` format, so you can see exactly what went wrong.

The `assert!` family isn't only for tests — you can check conditions in ordinary code with them too. But beware: `assert!` runs in **both** debug and release mode; even a shipped program panics when the condition fails. If you want checks only during development, automatically removed for release, use `debug_assert!`, `debug_assert_eq!`, `debug_assert_ne!` — the compiler ignores them entirely in release mode.

Inside **tests**, though, plain `assert!` is fine — tests run on debug builds by default anyway.

### Testing an Expected Panic

Sometimes you want the opposite: confirming a piece of code **does** panic — say, accessing an out-of-range index. Use `#[should_panic]`:

```rust,noplayground
#[test]
#[should_panic]
fn test_out_of_bounds() {
    let v = vec![1, 2, 3];
    let _ = v[10]; // This panics
}
#
# fn main() {}
```

If the function panics, the test passes; if it **doesn't**, the test fails instead.

The `expected` parameter can require the panic message to contain a given string, ensuring the panic happened for the right reason:

```rust,noplayground
#[test]
#[should_panic(expected = "index out of bounds")]
fn test_out_of_bounds_message() {
    let v = vec![1, 2, 3];
    let _ = v[10];
}
#
# fn main() {}
```

### The Idiomatic Test `mod` Structure

Last episode introduced `use super::*;` — tests use it most of all. The convention is a test `mod` at the bottom of the file:

```rust,noplayground
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn multiply(a: i32, b: i32) -> i32 {
    a * b
}
#
# fn main() {}

#[cfg(test)]
mod tests {
    use super::*; // Bring in everything from the parent mod

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_multiply() {
        assert_eq!(multiply(3, 4), 12);
    }
}
```

Key points:

- `#[cfg(test)]` tells the compiler: this `mod` **compiles only when running tests**. Shipped programs contain no test code.
- `mod tests` is an ordinary `mod`; `tests` is just the customary name.
- `use super::*;` brings in everything from the parent `mod` (the file's outermost level), so tests can call `add`, `multiply`, and friends directly.

### `cargo test`

```bash
cargo test
```

This command:

1. Compiles your code (tests included).
2. Executes every `#[test]` function.
3. Reports which passed and which failed.

### Testing Private Functions

Since `mod tests` is a child of the surrounding `mod`, Rust's privacy rules let it access private items declared in its parent. Tests can therefore test **private functions** directly, no `pub` needed.

## Example Code

```rust,editable
fn is_even(n: i32) -> bool {
    n % 2 == 0
}

fn abs(n: i32) -> i32 {
    if n >= 0 { n } else { -n }
}

fn clamp(value: i32, min: i32, max: i32) -> i32 {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_even() {
        assert!(is_even(4));
        assert!(!is_even(7));
        assert!(is_even(0));
    }

    #[test]
    fn test_abs() {
        assert_eq!(abs(5), 5);
        assert_eq!(abs(-3), 3);
        assert_eq!(abs(0), 0);
    }

    #[test]
    fn test_clamp() {
        assert_eq!(clamp(5, 0, 10), 5);   // Within range; unchanged
        assert_eq!(clamp(-3, 0, 10), 0);  // Below the floor; becomes min
        assert_eq!(clamp(15, 0, 10), 10); // Above the ceiling; becomes max
    }

    #[test]
    fn test_not_equal() {
        assert_ne!(abs(-5), -5); // abs(-5) should be 5, not -5
    }

    // Testing an expected panic
    #[test]
    #[should_panic(expected = "already borrowed")]
    fn test_refcell_double_borrow() {
        use std::cell::RefCell;
        let cell = RefCell::new(42);
        let _r = cell.borrow();
        let _w = cell.borrow_mut(); // An immutable borrow exists; this panics
    }
}

fn main() {
    // main can stay empty — tests run via cargo test
    println!("Run the tests with cargo test!");
}
```

## Recap

- `#[test]` marks test functions; `cargo test` finds and runs them all automatically.
- `assert!(condition)`, `assert_eq!(a, b)`, `assert_ne!(a, b)` verify results (running in both debug and release).
- `debug_assert!`, `debug_assert_eq!`, `debug_assert_ne!` run only in debug mode, ignored in release.
- `#[should_panic]` tests expected panics; add `expected = "..."` to check the panic message.
- `#[cfg(test)]` compiles the test `mod` only during testing.
- `use super::*;` imports everything from the parent `mod` — the test idiom.
- Tests can exercise private functions directly (the test `mod` being a child `mod`).
