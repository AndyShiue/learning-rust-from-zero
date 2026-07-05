# `@` Bindings

## Goal of This Episode

Learn to use `@` to bind the matching value to a variable while matching a pattern.

## Concept

We've learned range patterns: `1..=5` matches values from 1 to 5. But there's a problem — after a match succeeds, you can't tell "was it 1, 2, 3, 4, or 5?" You only know it was in the range.

`@` (the at sign) solves this. It lets you store the actual value in a variable at the same time as matching a pattern:

```rust,editable
fn main() {
    let age = 50;
    match age {
        n @ 0..=12 => println!("{} years old — a child", n),
        n @ 13..=19 => println!("{} years old — a teenager", n),
        n => println!("{} years old — an adult", n),
    }
}
```

`n @ 0..=12` means "if the value is between 0 and 12, call it `n`." Now you can range-check and capture the value at once.

## Example Code

```rust,editable
fn main() {
    let age = 15;

    match age {
        n @ 0..=6 => println!("{} years old — preschool", n),
        n @ 7..=12 => println!("{} years old — elementary school", n),
        n @ 13..=15 => println!("{} years old — junior high", n),
        n @ 16..=18 => println!("{} years old — high school", n),
        n => println!("{} years old — an adult", n),
    }

    // With char
    let ch = 'k';

    match ch {
        c @ 'a'..='m' => println!("'{}' is in the first half of the alphabet", c),
        c @ 'n'..='z' => println!("'{}' is in the second half of the alphabet", c),
        c => println!("'{}' isn't a lowercase letter", c),
    }

    // A more practical example: HTTP status codes
    let status = 404;

    match status {
        code @ 200..=299 => println!("Success! Status code: {}", code),
        code @ 300..=399 => println!("Redirect, status code: {}", code),
        code @ 400..=499 => println!("Client error, status code: {}", code),
        code @ 500..=599 => println!("Server error, status code: {}", code),
        code => println!("Unknown status code: {}", code),
    }
}
```

## `@` Isn't Limited to Ranges

`@` can pair with any pattern, not just ranges. For instance, with `|` (multiple values):

```rust,editable
fn main() {
    let day = 6;

    match day {
        d @ (1 | 3 | 5 | 7) => println!("Day {} — a rest day", d),
        d @ (2 | 4 | 6) => println!("Day {} — a workday", d),
        d => println!("Day {} — not a valid day", d),
    }
}
```

`d @ (1 | 3 | 5 | 7)` means "if the value is 1, 3, 5, or 7, call it `d`." Note that the `|` part must be wrapped in parentheses.

## Recap

- `n @ 1..=5` binds the value to the variable `n` while matching the range.
- Syntax: `variable_name @ pattern`.
- `@` can pair with any pattern, not just ranges: `d @ (1 | 3 | 5 | 7)` works too.
- Without `@`, you only know the value fit the pattern — not what it actually was.
- The idea of `@`: "store the value that fits this pattern under this name."
