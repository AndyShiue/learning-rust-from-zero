# Short-circuiting of `&&` and `||`

## Goal of This Episode

Understand that `&&` and `||` don't necessarily evaluate both sides — sometimes the left side alone settles the result.

> This episode supplements **Chapter 1**.

## Concept

Chapter 1 taught `&&` (and) and `||` (or). One detail went unmentioned: they **short-circuit** (short-circuit evaluation).

### `&&`'s Short Circuit

If `&&`'s left side is `false`, the right side never runs — whatever it is, the overall result must be `false`:

```rust,editable
fn main() {
    let x = 0;
    // The left side x != 0 is false, so the right side 10 / x never runs
    // If it did run, 10 / 0 would panic!
    if x != 0 && 10 / x > 2 {
        println!("Greater than 2");
    }
}
```

### `||`'s Short Circuit

If `||`'s left side is `true`, the right side never runs — whatever it is, the overall result must be `true`:

```rust,editable
fn check() -> bool {
    println!("check was called");
    true
}

fn main() {
    // The left side is already true; check() is never called
    if true || check() {
        println!("The result is true");
    }
    // Only "The result is true" prints — never "check was called"
}
```

### Why Know This

Most of the time you needn't think about short-circuiting. But when the right-hand expression has **side effects** (printing, modifying variables) or **can fail** (dividing by zero), knowing the right side may never run becomes important.

## Example Code

```rust,editable
fn is_even(n: i32) -> bool {
    println!("  Checking whether {} is even", n);
    n % 2 == 0
}

fn is_positive(n: i32) -> bool {
    println!("  Checking whether {} is positive", n);
    n > 0
}

fn main() {
    // &&: a false left side means the right is never looked at
    println!("--- && short-circuiting ---");
    let n = -3;
    if is_even(n) && is_positive(n) {
        println!("{} is a positive even number", n);
    } else {
        println!("{} is not a positive even number", n);
    }
    // is_even(-3) returns false; is_positive is never called

    // ||: a true left side means the right is never looked at
    println!("\n--- || short-circuiting ---");
    let n = 4;
    if is_even(n) || is_positive(n) {
        println!("{} is even or positive", n);
    }
    // is_even(4) returns true; is_positive is never called

    // A practical scenario: avoiding division by zero
    println!("\n--- A practical scenario ---");
    let divisor = 0;
    if divisor != 0 && 100 / divisor > 10 {
        println!("The quotient exceeds 10");
    } else {
        println!("The divisor is zero, or the quotient doesn't exceed 10");
    }
}
```

## Recap

- `&&`: a `false` left side skips the right; the whole result is immediately `false`.
- `||`: a `true` left side skips the right; the whole result is immediately `true`.
- This is called short-circuit evaluation.
- It matters most when the right side has side effects or can fail.
