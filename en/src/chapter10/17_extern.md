# `extern` blocks

## Goal of This Episode

Learn to call C functions and let C call Rust functions. This episode is only a rough tour of FFI. If you want a complete FFI example (from building a C library to calling it from Rust), search for a dedicated tutorial.

## Concept

### What Is FFI

FFI (Foreign Function Interface) is the mechanism that lets different programming languages call each other's functions. Rust can call functions written in C, and C can call functions written in Rust. Since nearly every language can interoperate with C, Rust can talk to most languages by using C as the bridge.

### Calling C Functions

Declare external C functions with an `unsafe extern "C"` block:

```rust,editable
unsafe extern "C" {
    fn abs(x: i32) -> i32;
}

fn main() {
    let result = unsafe { abs(-42) };
    println!("abs(-42) = {}", result);
}
```

Calling an external function requires `unsafe` — Rust has no way to check whether the function on the C side is safe.

Since the Rust 2024 edition, the `extern` block itself also requires `unsafe` — because Rust can't verify that the function signatures you wrote in the declaration (parameter types, return type, etc.) are correct. If a signature doesn't match what's actually on the C side, that's undefined behavior.

### `safe fn`

If you're certain an external function is safe, you can mark it `safe`:

```rust,editable
unsafe extern "C" {
    safe fn abs(x: i32) -> i32; // you guarantee abs is always safe
}

fn main() {
    let result = abs(-42); // callable without unsafe!
    println!("abs(-42) = {}", result);
}
```

### What the `"C"` Means

The `"C"` in `extern "C"` refers to the **ABI** (Application Binary Interface) — how functions are called at the binary level. `"C"` is the most common ABI; nearly every language can interoperate with the C ABI.

### Letting C Call Rust

```rust,noplayground
#[unsafe(no_mangle)]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}
#
# fn main() {}
```

- `extern "C"`: use the C ABI.
- `#[unsafe(no_mangle)]`: don't mangle the function name, so C can find it as `add`. In the 2024 edition, `no_mangle` is an `unsafe` attribute, because it changes how the function is linked, which can affect safety.

### `extern` Blocks Can Declare `static` Variables Too

```rust,noplayground
unsafe extern "C" {
    static errno: i32; // a global variable on the C side
}
#
# fn main() {}
```

## Example Code

```rust,editable
unsafe extern "C" {
    safe fn abs(x: i32) -> i32;
    fn sqrt(x: f64) -> f64;
}

#[unsafe(no_mangle)]
pub extern "C" fn rust_add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    // functions marked safe don't need unsafe
    println!("abs(-10) = {}", abs(-10));

    // unmarked ones do
    let root = unsafe { sqrt(25.0) };
    println!("sqrt(25) = {}", root);

    // Rust's extern "C" functions can also be called directly from Rust
    println!("rust_add(3, 4) = {}", rust_add(3, 4));
}
```

## Recap

- `unsafe extern "C" { ... }` declares external C functions.
- Calling external functions requires `unsafe`, except those marked `safe fn`.
- `"C"` is the ABI — how functions are called at the binary level.
- `#[unsafe(no_mangle)] pub extern "C" fn` lets C call Rust.
