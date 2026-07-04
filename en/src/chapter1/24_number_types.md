# Types (Numbers in Detail)

## Goal of This Episode

Get to know all of Rust's numeric types, plus how numeric suffixes work.

## Main Text

Last episode we briefly met `i32` and `f64`. Today let's go through all of Rust's numeric types.

### Integer Types

Rust's integer types come in **signed** (can be negative) and **unsigned** (only positive and zero) flavors:

| Signed | Unsigned | Bits | Range (signed) |
|------|------|--------|-------------|
| `i8` | `u8` | 8 | -128 ~ 127 |
| `i16` | `u16` | 16 | -32,768 ~ 32,767 |
| `i32` | `u32` | 32 | roughly ±2.1 billion |
| `i64` | `u64` | 64 | enormous |
| `i128` | `u128` | 128 | astronomical |
| `isize` | `usize` | system-dependent | 64 bits on a 64-bit system |

- `i` = integer, `u` = unsigned.
- The number says how many bits are used for storage — more bits means bigger numbers can be stored.
- The size of `isize` and `usize` depends on whether your system is 32-bit or 64-bit (nearly everything is 64-bit these days).

**For everyday use, `i32` is enough.** When in doubt, use `i32`.

### Floating-point Types

Floating-point numbers are used for values that can have a fractional part. Rust has two floating-point types:

| Type | Precision |
|------|--------|
| `f32` | single precision (about 7 significant digits) |
| `f64` | double precision (about 15 significant digits) |

**For everyday use, `f64` is enough.** It's also Rust's default floating-point type.

### Floating-point Arithmetic

Back in Episode 5, when we covered arithmetic, we used integers throughout. Floating-point numbers work with `+` `-` `*` `/` `%` too, but there's one important difference — **floating-point division can produce a fractional result**:

```rust,editable
fn main() {
    let a = 10.0;
    let b = 3.0;
    println!("{}", a / b); // 3.3333333333333335
    println!("{}", a % b); // 1.0
}
```

Remember how `10 / 3` in Episode 5 gave `3` (integer division truncates)? Floating-point doesn't truncate: `10.0 / 3.0` gives `3.3333...`.

That said, floating-point has one classic pitfall — **precision issues**:

```rust,editable
fn main() {
    println!("{}", 0.1 + 0.2); // 0.30000000000000004
}
```

`0.1 + 0.2` is not `0.3`! This isn't a bug in Rust — it's a floating-point precision limitation shared by every programming language. Computers store decimals in binary, and some decimal fractions simply can't be represented exactly. Just knowing this exists is enough; don't worry about it too much.

### How Does Rust Infer Numeric Types?

When you write `let x = 5;`, Rust treats it as `i32` by default.
When you write `let y = 3.14;`, Rust treats it as `f64` by default.

But Rust doesn't just look at the number itself — it also infers the type from **how you use the variable**. Sometimes, based on context, Rust will infer an integer type other than `i32`. This will become clearer when we run into it later.

**Fundamentally though: integers default to `i32`, and floating-point numbers default to `f64`.**

### Numeric Suffixes (Literal Suffixes)

If you want to specify a type, besides `let x: i64 = 5;` there's an even more concise way — append the type name directly to the number:

```rust,editable
fn main() {
    let a = 5i32;      // i32
    let b = 5u8;       // u8
    let c = 3.14f64;   // f64
    let d = 2.0f32;    // f32
    let e = 100000i64; // i64

    println!("{} {} {} {} {}", a, b, c, d, e);
}
```

`5i32` means "the number 5, with type `i32`." No space between the number and the type — they're joined directly.

### A Small Reminder

Numbers of different types **can't be mixed in arithmetic directly**:

```rust,compile_fail
fn main() {
    let a: i32 = 5;
    let b: i64 = 10;
    println!("{}", a + b); // ❌ Compile error! i32 and i64 can't be added directly
}
```

This is a safety-minded design: Rust generally doesn't convert types for you automatically.

## Recap

- Integers come in signed (`i8`-`i128`) and unsigned (`u8`-`u128`); `i32` is enough for everyday use.
- The size of `isize` and `usize` depends on the system (64 bits on 64-bit systems).
- Floating-point types are `f32` and `f64`; use `f64` day-to-day (Rust's default).
- Numeric suffixes (like `5i32`, `3.14f64`) specify the type directly.
- Floating-point division can produce fractional results, but has precision issues (`0.1 + 0.2 ≠ 0.3`).
- Rust generally doesn't convert types for you automatically.
