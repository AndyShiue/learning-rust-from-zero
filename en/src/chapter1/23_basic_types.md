# Types (the Basics)

## Goal of This Episode

Meet Rust's basic types.

## Main Text

Until now, when we wrote `let x = 5;` we never said anything about what "type" `x` is. Today let's formally meet the concept of types.

### What Is a Type?

A type tells Rust: "Here's what kind of thing this variable holds."

Is it an integer? A decimal? Text? Or `true` / `false`? Different types represent different kinds of data.

### Annotating Types by Hand

You can specify a type by adding `: type` after the variable name:

```rust,editable
fn main() {
    let x: i32 = 5;
    let negative: i32 = -10;
    let y: f64 = 3.14;
    let z: bool = true;

    println!("x = {}", x);
    println!("negative = {}", negative);
    println!("y = {}", y);
    println!("z = {}", z);
}
```

- `i32` → an integer (32-bit).
- `f64` → a floating-point number (64-bit), used for values that can have a fractional part, such as `3.14` or `0.5`.
- `bool` → a boolean, which is only ever `true` or `false`.

### Then Why Didn't We Annotate Before?

Because Rust is smart! It looks at the value you provide and **infers** the type automatically:

```rust,noplayground
# fn main() {
    let x = 5;    // Rust figures out: this is an i32
    let y = 3.14; // Rust figures out: this is an f64
    let z = true; // Rust figures out: this is a bool
# }
```

This is called **type inference**. Most of the time, Rust can work it out on its own and you don't need to annotate.

## Recap

- Three basic types: `i32` (integer), `f64` (floating-point number), `bool` (boolean).
- Rust has **type inference**; most of the time you don't need to annotate types by hand.
- When needed, specify a type manually with `let x: i32 = 5;`.
