# Format Strings in Depth

## Goal of This Episode

Learn `println!`'s assorted formatting tricks: the variable-capture shorthand, positional parameters, width, precision control, alignment, and base display.

> This episode supplements **Chapter 2**.

## Concept

We've been printing with `println!("{}", x)` all along, but Rust's format strings are far more powerful. This episode covers the most-used tricks without covering everything — for the full formatting syntax, see [the official documentation](https://doc.rust-lang.org/std/fmt/).

### The Variable-capture Shorthand

You can write a variable's name straight into the `{}`:

```rust,editable
fn main() {
    let name = "Andy";
    println!("{name}"); // Equivalent to println!("{}", name)
}
```

This can be more convenient than writing `{}` and matching variables afterward, especially with many variables. Note only variable names go inside — no expressions (`"{x + 1}"` won't work).

### Positional Parameters

`{}` matches the following arguments in order by default, but you can write a number in the braces to name which argument explicitly (counting from 0):

```rust,editable
fn main() {
    println!("{0} {1}", "hel", "lo"); // hel lo
    println!("{1} {0}", "hel", "lo"); // lo hel
}
```

The same argument can be reused without passing it twice:

```rust,editable
fn main() {
    println!("{0}, {0}!", "wait"); // wait, wait!
}
```

When is this useful? Most commonly when one value appears several times in the string, or when you want to reorder the output without reordering the arguments.

### Decimal Precision

Control the digits after the decimal point with `:.N`:

```rust,editable
fn main() {
    let pi = 3.14159265;
    println!("{pi:.2}"); // Prints 3.14
}
```

### Width

Specify a minimum width with `:N` — shortfalls get padded with spaces:

```rust,editable
fn main() {
    let x = 42;
    println!("{x:5}"); // "   42" (width 5, right-aligned, space-padded)
}
```

### Alignment

Control right, left, and center alignment explicitly with `:>N`, `:<N`, `:^N`:

```rust,editable
fn main() {
    let name = "Andy";
    println!("[{name:>10}]"); // Right-aligned, width 10
    println!("[{name:<10}]"); // Left-aligned
    println!("[{name:^10}]"); // Centered
}
```

### The Fill Character

Padding defaults to spaces, but another character can be specified:

```rust,editable
fn main() {
    let id = 42;
    println!("{id:0>5}"); // Prints 00042 (padded with 0s)
}
```

### Base Display

`:b`, `:x`, `:o` display numbers in binary, hexadecimal, and octal respectively:

```rust,editable
fn main() {
    let n = 255;
    println!("{n:b}"); // 11111111
    println!("{n:x}"); // ff
    println!("{n:o}"); // 377
}
```

These formats combine — e.g. `{:0>8b}` is "binary, zero-padded to 8 digits."

### Escaping Braces

To print a literal `{` or `}` in a format string, use `{{` and `}}`:

```rust,editable
fn main() {
    println!("These are braces: {{}}"); // Prints: These are braces: {}
}
```

## Example Code

```rust,editable
fn main() {
    let name = "Ming";
    let score = 87.5678;

    // The variable-capture shorthand
    println!("Student: {name}");
    println!("Score: {score}");

    // Positional parameters: reordering, reuse
    println!("{1}'s score is {0}", score, name);
    println!("{0}! {0}! {0}!", "Go");

    // Decimal precision
    println!("Rounded to two places: {score:.2}");

    // Width
    println!("[{name:10}]"); // Strings left-align by default
    let x = 42;
    println!("[{x:10}]");    // Numbers right-align by default

    // Alignment
    println!("[{name:>10}]"); // Right
    println!("[{name:<10}]"); // Left
    println!("[{name:^10}]"); // Centered

    // Zero padding
    let id = 42;
    println!("ID: {id:0>5}");

    // Base display
    let value = 255;
    println!("Decimal: {value}");
    println!("Binary: {value:b}");
    println!("Hexadecimal: {value:x}");
    println!("Octal: {value:o}");

    // Combo: zero-pad + right-align + width 2 + hexadecimal
    let byte = 10;
    println!("0x{byte:0>2x}"); // Prints 0x0a

    // Combo: zero-pad + right-align + width 8 + binary
    println!("{byte:0>8b}"); // Prints 00001010

    // Printing braces themselves takes {{ and }}
    println!("Here's a brace pair: {{}}"); // Prints: Here's a brace pair: {}
}
```

## Recap

- `println!("{x}")` puts the variable name right in the braces — variables only, no expressions.
- `{0}`, `{1}` pick arguments by number (from 0); the same argument can be reused.
- `{:.2}` controls digits after the decimal point.
- `{:5}` sets a minimum width.
- `{:>10}`, `{:<10}`, `{:^10}` align right, left, and center.
- `{:0>5}` pads with `0` to width 5.
- `{:b}`, `{:x}`, `{:o}` display in binary, hexadecimal, octal.
- Format options combine, e.g. `{:0>8b}` = zero-pad + right + width 8 + binary.
- Print literal `{` and `}` by escaping as `{{` and `}}`.
