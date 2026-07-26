# Arithmetic Operators

## Goal of This Episode

Learn to add, subtract, multiply, divide, and take remainders in Rust.

## Main Text

Today we're doing math! Don't worry — it's just arithmetic.

### The Four Basic Operations

First, create two variables:

```rust,editable
fn main() {
    let a = 10;
    let b = 3;

    println!("{} + {} = {}", a, b, a + b); // 13
    println!("{} - {} = {}", a, b, a - b); // 7
    println!("{} * {} = {}", a, b, a * b); // 30
    println!("{} / {} = {}", a, b, a / b); // 3
    println!("{} % {} = {}", a, b, a % b); // 1
}
```

### Wait — How Is 10 / 3 Equal to 3?

Good question! Because `a` and `b` are both integers, Rust performs **integer division**: everything after the decimal point simply gets chopped off. 10 divided by 3 is 3.333..., and chopping off the decimals gives 3.

### What Is `%`?

`%` is the **remainder** operator (the modulo operation). 10 divided by 3 is 3 with a remainder of 1, so `10 % 3` is `1`.

You can think of it as: "How many 3s fit inside 10? Three of them, with 1 left over." That leftover is the remainder.

### Using Multiple `{}`s

Did you notice? We put three `{}`s inside `println!`:

```rust,editable
fn main() {
    let a = 10;
    let b = 3;
    println!("{} + {} = {}", a, b, a + b);
}
```

Rust fills in the values in order:
- The first `{}` → the value of `a` (10).
- The second `{}` → the value of `b` (3).
- The third `{}` → the value of `a + b` (13).

The number of `{}`s matches the number of values that follow, and the order must line up.

## Recap

- The five arithmetic operators: `+` (addition), `-` (subtraction), `*` (multiplication), `/` (division), `%` (remainder).
- Integer division discards the decimal part (`10 / 3` is `3`, not `3.333`).
- `%` takes the remainder: `10 % 3` is the `1` left over after dividing 10 by 3.
- `println!` can contain multiple `{}`s, matched in order with the values that follow.
