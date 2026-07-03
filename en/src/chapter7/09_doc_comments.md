# Doc Comments

## Goal of This Episode

Learn to write documentation comments, understand that documentation examples are tests (doctests), and generate professional HTML docs with `cargo doc`.

## Concept

Rust treats documentation as a first-class citizen of the language — not squeezed out by external tools, but built into the syntax. Better still: the example code in your docs gets executed as tests by `cargo test`, so Rust documentation examples never silently go stale.

### `///` Item Doc Comments

Three slashes `///` document **the item that follows** (a function, `struct`, `enum`, `trait`, etc.):

```rust,noplayground
/// Computes the greatest common divisor of two integers.
///
/// Uses the Euclidean algorithm, with O(log(min(a, b))) efficiency.
///
/// # Examples
///
/// ```
/// use my_math_lib::gcd;
///
/// let result = gcd(12, 8);
/// assert_eq!(result, 4);
/// ```
pub fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        let temp = b;
        b = a % b;
        a = temp;
    }
    a
}
#
# fn main() {}
```

`///` supports full **Markdown syntax** — headings, bold, code blocks, lists, all of it.

### `//!` `mod`/Crate-level Docs

Two slashes plus a bang, `//!`, documents **the item containing it**, usually placed at the very top of a file:

```rust,noplayground
//! # Math Library
//!
//! This library provides basic mathematical functions.
//!
//! ## Features
//!
//! - Basic arithmetic
//! - Greatest common divisor computation
//! - Exponentiation

pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
#
# fn main() {}
```

At the top of `lib.rs` it documents the whole crate; at the top of some `mod`'s file, that `mod`.

### The Customary Documentation Sections

The Rust community has some conventional section names:

- `# Examples` — usage examples (the most important one!)
- `# Panics` — under what circumstances it panics.
- `# Errors` — if it returns a `Result`, when it's an `Err`.

### Documentation Examples Are Tests (doctests)

Here's the point. The code blocks under `# Examples` aren't just for reading — **`cargo test` extracts, compiles, and runs every documentation example**. These are **doctests**. The `cargo test` from Episode 6 actually runs all doctests in addition to `#[test]` functions.

Each documentation example compiles as a **standalone little program** — it lives **outside** your library, like a program written by one of your library's users. So the example must say `use my_math_lib::gcd;`, exactly as a real user would. Forget the `use` and the doctest fails to compile — and **a compile failure counts as a test failure**. Incidentally, examples don't need `fn main()`; rustdoc wraps one around automatically.

This design yields something beautiful: **the examples are always right**. Rename a function or change its signature while forgetting the docs, and `cargo test` throws the error in your face at once. In many languages, doc examples silently rot as the code evolves; in Rust, a rotten example blocks your tests.

One caveat: only a **library crate**'s doctests execute. Doc comments in a binary crate still generate documentation, but their examples **won't** run as tests.

### `cargo doc`

With doc comments written, one command produces beautiful HTML documentation:

```bash
cargo doc --open
```

This:

1. Compiles your crate (without running it).
2. Generates HTML docs from every `///` and `//!`.
3. Opens them in your browser automatically.

The generated docs are exactly what you see on docs.rs.

## Example Code

A complete example this time. Assuming `Cargo.toml`'s `[package]` has `name = "temperature"`, here's `src/lib.rs`:

```rust,noplayground
//! # Temperature Conversion Tools
//!
//! Provides conversion functions between Celsius and Fahrenheit.

/// Celsius to Fahrenheit.
///
/// # Formula
///
/// `F = C × 9/5 + 32`
///
/// # Examples
///
/// ```
/// use temperature::celsius_to_fahrenheit;
///
/// let f = celsius_to_fahrenheit(100.0);
/// assert!((f - 212.0).abs() < 0.001);
/// ```
pub fn celsius_to_fahrenheit(c: f64) -> f64 {
    c * 9.0 / 5.0 + 32.0
}

/// Fahrenheit to Celsius.
///
/// # Formula
///
/// `C = (F - 32) × 5/9`
///
/// # Examples
///
/// ```
/// use temperature::fahrenheit_to_celsius;
///
/// let c = fahrenheit_to_celsius(32.0);
/// assert!((c - 0.0).abs() < 0.001);
/// ```
pub fn fahrenheit_to_celsius(f: f64) -> f64 {
    (f - 32.0) * 5.0 / 9.0
}

/// A representation of temperature.
///
/// Supports both Celsius and Fahrenheit units.
pub enum Temperature {
    /// A Celsius temperature
    Celsius(f64),
    /// A Fahrenheit temperature
    Fahrenheit(f64),
}

impl Temperature {
    /// Converts any temperature to Celsius.
    ///
    /// # Examples
    ///
    /// ```
    /// use temperature::Temperature;
    ///
    /// let body = Temperature::Fahrenheit(98.6);
    /// assert!((body.to_celsius() - 37.0).abs() < 0.001);
    /// ```
    pub fn to_celsius(&self) -> f64 {
        match self {
            Temperature::Celsius(c) => *c,
            Temperature::Fahrenheit(f) => fahrenheit_to_celsius(*f),
        }
    }

    /// Converts any temperature to Fahrenheit.
    pub fn to_fahrenheit(&self) -> f64 {
        match self {
            Temperature::Celsius(c) => celsius_to_fahrenheit(*c),
            Temperature::Fahrenheit(f) => *f,
        }
    }
}
#
# fn main() {}
```

## Recap

- `///` documents the item that follows (`fn`, `struct`, `enum`, etc.).
- `//!` documents the containing item (`mod`, crate), usually at the file's top.
- Doc comments support full Markdown syntax.
- `# Examples` is the most important section — a good example beats a thousand words.
- **Documentation examples are doctests**: `cargo test` compiles and runs every one; compile failures and `assert` failures both count as test failures.
- Doctests compile as a "library user," so examples must write `use your_crate::...`.
- Doctests run only for library crates.
- `cargo doc --open` generates and opens HTML docs in one step.
- The docs you see on docs.rs are produced by this very mechanism.
