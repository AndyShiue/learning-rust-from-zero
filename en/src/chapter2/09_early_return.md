# Early `return`

## Goal of This Episode

Use the `return` keyword to send a value back partway through a function, without waiting for the last line.

## Main Text

Last episode we learned that a function's final line without a semicolon is the return value. But sometimes you want to return **in the middle** of a function — bailing out early when some condition is met. That's what the `return` keyword is for.

### Basic Example: Absolute Value

```rust,editable
fn abs(x: i32) -> i32 {
    if x >= 0 {
        return x; // If x is positive or zero, return immediately
    }
    -x            // Reaching here means x is negative; return -x
}

fn main() {
    println!("abs(5) = {}", abs(5));
    println!("abs(-3) = {}", abs(-3));
    println!("abs(0) = {}", abs(0));
}
```

Look closely:

- `return x;` → uses the `return` keyword, **with a semicolon**.
- The last line `-x` → no semicolon; that's the "natural return."

### `return` vs No Semicolon

Comparing the two ways to return:

```rust,noplayground
// Way 1: using return (usually for "leaving early")
fn abs_v1(x: i32) -> i32 {
    if x >= 0 {
        return x;
    }
    -x
}

// Way 2: pure expressions (the whole if-else is the return value)
fn abs_v2(x: i32) -> i32 {
    if x >= 0 {
        x
    } else {
        -x
    }
}
#
# fn main() {}
```

Both are correct! The Rust community's convention:

- **Use `return` when you mean "I want to leave early"** (Way 1).
- **Use expressions the rest of the time** (Way 2).

### A Practical Scenario: Blocking Invalid Input Early

```rust,editable
fn divide(a: f64, b: f64) -> f64 {
    if b == 0.0 {
        println!("Error: can't divide by zero!");
        return 0.0; // Leave early
    }

    // Possibly lots of other work here......

    a / b
}

fn main() {
    println!("{}", divide(10.0, 3.0));
    println!("{}", divide(10.0, 0.0));
}
```

This "check first, bail out if something's wrong" style is called a **guard clause**, and it's extremely common in practice.

### `return` for Functions Returning `()`

If the function returns `()` (e.g., no `-> type` written), `return` doesn't need a value after it:

```rust,editable
fn check_age(age: i32) {
    if age < 0 {
        println!("Age can't be negative!");
        return; // Same as return ();
    }
    println!("Your age is {}", age);
}

fn main() {
    check_age(25);
    check_age(-3);
}
```

`return;` is shorthand for `return ();` — since what's returned is `()` (the unit type), leaving it out is cleaner.

### Don't Use `return` Everywhere

Writing `return` for every return value does run, but in Rust it's not good style:

```rust,noplayground
// Not very Rust-y
fn add_v1(a: i32, b: i32) -> i32 {
    return a + b; // Runs, but unnecessary
}

// Idiomatic Rust
fn add_v2(a: i32, b: i32) -> i32 {
    a + b         // The last line serves as the return value
}
#
# fn main() {}
```

Save `return` for the "leaving early" scenarios.

## Recap

- `return value;` returns early from the middle of a function (remember the semicolon).
- The natural, semicolon-less return on the last line is idiomatic Rust.
- `return` is most often used in guard clauses: check a condition and bail out early if it's wrong.
- In functions returning `()`, `return;` is shorthand for `return ();`.
- Don't write `return` for every return value — only when leaving early.
