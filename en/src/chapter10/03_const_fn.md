# `const fn`

## Goal of This Episode

Learn to use `const fn` to define functions that can also run at compile time, plus the `const { }` block.

## Concept

### The Problem: Computing a `const` Value with a Function

Chapter 2 covered `const` — compile-time constants. But a `const`'s value can only use simple expressions:

```rust,noplayground
const MAX: i32 = 100;        // OK
const DOUBLE: i32 = MAX * 2; // OK
#
# fn main() {}
```

What if you want to compute it with a function?

```rust,compile_fail
fn square(x: i32) -> i32 { x * x }
const VALUE: i32 = square(5); // compile error! ordinary functions can't run at compile time
#
# fn main() {}
```

### `const fn`

Put `const` in front of a function and it becomes a function that can also run at compile time:

```rust,noplayground
const fn square(x: i32) -> i32 { x * x }
const VALUE: i32 = square(5); // OK! 25 is computed at compile time
#
# fn main() {}
```

A `const fn` is not "compile-time only" — it can be called at runtime just fine, like a regular function. It just has one extra ability: **it can run at compile time**.

```rust,editable
const fn max(a: i32, b: i32) -> i32 {
    if a > b { a } else { b }
}

const BIGGER: i32 = max(10, 20); // compile time: 20

fn main() {
    let x = max(3, 7); // runtime: works too, just a regular function
    println!("{}", x);
    println!("{}", BIGGER);
}
```

### Restrictions

You can't do everything inside a `const fn`. The basic principle: **the compiler must be able to simulate running this code inside itself**.

What you can do:
- Arithmetic, comparison, and logical operations
- `if`, `match`, `loop`, `while`, `for`.
- `let` bindings (including `let mut`).
- Creating tuples, `struct`s, `enum`s.
- Calling other `const fn`s.
- `panic!` (a compile-time panic becomes a compile error).

What you can't do:
- Call non-`const` functions.
- Input/output (`println!` and the like).
- Interact with the operating system
- inline assembly

Every Rust release relaxes the restrictions a little more; the list of things you can do in a `const fn` keeps growing.

### `const` Blocks

`const { ... }` lets you insert a piece of compile-time computation anywhere, without defining a `const` variable or a `const fn`:

```rust,editable
fn main() {
    let x = const { 1 + 2 + 3 };
    println!("{}", x); // 6, computed at compile time
}
```

This is handy when you want compile-time computation "in place," without defining a separate `const`.

## Example Code

```rust,editable
const fn factorial(n: u64) -> u64 {
    if n <= 1 {
        1
    } else {
        n * factorial(n - 1)
    }
}

const fn clamp(value: i32, min: i32, max: i32) -> i32 {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}

const FACT_10: u64 = factorial(10);
const CLAMPED: i32 = clamp(150, 0, 100);

fn main() {
    println!("10! = {}", FACT_10);
    println!("clamp(150, 0, 100) = {}", CLAMPED);

    // callable at runtime too
    let n = factorial(5);
    println!("5! = {}", n);

    // const block
    let size = const { std::mem::size_of::<[i32; 100]>() };
    println!("size of 100 i32s: {} bytes", size);
}
```

## Recap

- A `const fn` can run at compile time and at runtime.
- Its main use is initializing `const` values.
- Restrictions: it can't call non-`const fn`s or do I/O, but the restrictions loosen with each release.
- A `const { ... }` block inserts compile-time computation anywhere.
