# `match` Guards

## Goal of This Episode

Learn to add extra conditional checks (guards) to `match` arms.

## Concept

Sometimes pattern matching alone isn't enough — you need extra conditions on top. Say you want a `match` that tells odd numbers from even ones. That can't be expressed with range patterns or fixed values, because it needs a computation (`% 2`).

Rust's **`match` guard** lets you append `if condition` after a pattern:

```rust,editable
fn main() {
    let n = 137;
    match n {
        x if x % 2 == 0 => println!("{} is even", x),
        x => println!("{} is odd", x),
    }
}
```

`x if x % 2 == 0` means "first bind the value to `x`, then additionally check whether `x % 2 == 0` holds." The arm runs only when the pattern matches **and** the guard condition is `true`.

Note: guards don't count toward "exhaustiveness." Even if you write guards covering every possibility, Rust may still require a `_` default arm.

## Example Code

```rust,editable
fn main() {
    let n = 8;

    match n {
        x if x % 2 == 0 => println!("{} is even", x),
        x => println!("{} is odd", x),
    }

    // With tuples
    let point = (3, 7);

    match point {
        (x, y) if x == y => println!("On the diagonal: ({}, {})", x, y),
        (x, y) if x > 0 && y > 0 => println!("({}, {}) is in the first quadrant", x, y),
        (x, y) => println!("Some other point ({}, {})", x, y),
    }
}
```

## Recap

- `match` guard: append `if condition` after a pattern for an extra check.
- Syntax: `pattern if condition => ...`.
- The arm runs only when the pattern matches **and** the condition is `true`.
- Guards can use variables bound by the same arm's pattern, as in `x if x > 0 => ...`.
- Guard conditions don't count toward exhaustiveness — you usually still need a `_` default arm.
