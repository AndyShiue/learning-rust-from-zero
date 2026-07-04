# `static` Variables

## Goal of This Episode

Understand the difference between `static` and `const`, and why you should almost never use `static mut`.

## Concept

### `static` vs `const`

Chapter 2 covered `const` — compile-time constants whose values get embedded directly wherever they're used. `static` looks similar, but there's one fundamental difference: **a `static` variable has a fixed memory address**.

```rust,noplayground
static GREETING: &str = "Hello, world!";
static MAX_SIZE: usize = 1024;
#
# fn main() {}
```

| | `const` | `static` |
|--|--|--|
| Memory | No fixed address; value embedded at use sites | Fixed address; one copy shared by the whole program |
| Taking an address | Can't take `&` | Can take `&`, guaranteed valid forever |

Most of the time `const` is enough. Use `static` only when you need a fixed memory address (e.g. to hand to a C function).

### static mut

Rust allows mutable `static`s — but both reading and writing require `unsafe`:

```rust,noplayground
static mut COUNTER: i32 = 0;

fn increment() {
    unsafe { COUNTER += 1; }
}
#
# fn main() {}
```

Why the `unsafe`? Because a `static` is globally shared — multiple threads reading and writing it at once is a data race.

**`static mut` should almost never be used.** Modern Rust has better alternatives:

- A simple counter → `AtomicI32`, `AtomicBool`.
- Complex mutable global state → `Mutex<T>` (paired with `static`).
- Lazy initialization → `LazyLock` (next episode).

## Example Code

```rust,editable
use std::sync::atomic::{AtomicI32, Ordering};

// const: value embedded at use sites
const MAX: i32 = 100;

// static: has a fixed address
static GREETING: &str = "Hello!";

// atomic instead of static mut
static COUNTER: AtomicI32 = AtomicI32::new(0);

fn increment() {
    COUNTER.fetch_add(1, Ordering::Relaxed);
}

fn main() {
    println!("{}", GREETING);
    println!("MAX = {}", MAX);

    increment();
    increment();
    increment();
    println!("COUNTER = {}", COUNTER.load(Ordering::Relaxed));
}
```

## Recap

- A `static` has a fixed memory address; one copy is shared by the whole program.
- A `const` has no fixed address; its value is embedded at use sites — use `const` most of the time.
- `static mut` requires `unsafe` for both reads and writes and should almost never be used.
- Alternatives: `AtomicXxx`, `Mutex<T>`, `LazyLock`.
