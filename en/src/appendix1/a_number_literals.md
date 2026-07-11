# Number Literal Formats

## Goal of This Episode

Learn underscore separators, different bases, type suffixes, and the various ways of writing floating-point literals.

> This episode supplements **Chapter 1**.

## Concept

Chapter 1 taught basic number notation like `42` and `3.14`. But Rust's numeric literals actually come in many forms, making your numbers more readable and more precise.

### Underscore Separators

With a big number, which reads better — `1000000` or `1_000_000`? Rust lets you insert underscores `_` anywhere in a numeric literal; the compiler simply ignores them:

```rust,noplayground
# fn main() {
    let million = 1_000_000;
    let weird_but_legal = 1_00_00_00; // Legal, but don't write this
# }
```

### Different Bases

Beyond decimal, Rust supports three base prefixes:

- `0x` — hexadecimal (e.g. `0xff` = 255)
- `0b` — binary (e.g. `0b1010` = 10)
- `0o` — octal (e.g. `0o77` = 63)

Especially practical for bitwise operations, color values, and the like. Underscores combine with bases too: `0b1111_0000`.

### Type Suffixes

You can append the type directly to a number:

```rust,noplayground
# fn main() {
    let byte = 0xFFu8;      // Hexadecimal + u8
    let big = 1_000_000i64; // Underscores + i64
    let pi = 3.14f32;       // Float + f32
# }
```

Without a suffix, integers default to `i32` and floats to `f64`.

### Floating-point Literals

Floats can be written several ways:

```rust,noplayground
# fn main() {
    let a = 3.14;        // An ordinary decimal, defaulting to f64
    let b = 3.14f32;     // Specifying f32
    let c = 1.0e10;      // Scientific notation: 1.0 × 10^10
    let d = 2.5E-3;      // Scientific notation: 2.5 × 10^-3 = 0.0025
    let e = 1_234.567_8; // Underscores work in floats too
# }
```

## Example Code

```rust,editable
fn main() {
    // Underscore separators
    let population = 23_000_000;
    println!("Taiwan's population is roughly {}", population);

    // Hexadecimal
    let hex_color = 0xFF5733;
    println!("Color value: {}", hex_color);

    // Binary
    let bits = 0b1010_1100;
    println!("Bit value: {}", bits);

    // Octal
    let octal = 0o755;
    println!("Octal 0o755 = {}", octal);

    // Type suffixes
    let byte_max = 0xFFu8;
    println!("u8's maximum: {}", byte_max);

    // Floats
    let pi = 3.14_159_265f64;
    println!("Pi is roughly {}", pi);

    // Scientific notation
    let speed_of_light = 3.0e8;
    println!("The speed of light is roughly {} m/s", speed_of_light);

    let tiny = 1.6e-19;
    println!("The electron charge is roughly {} C", tiny);
}
```

## Recap

- `_` can go anywhere in a numeric literal to aid reading; the compiler ignores it.
- `0x` hexadecimal, `0b` binary, `0o` octal.
- Type suffixes like `u8`, `i64`, `f32` attach directly to numbers.
- Floats support scientific notation (`1.0e10`, `2.5E-3`).
