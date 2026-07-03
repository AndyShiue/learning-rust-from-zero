# Range Patterns

## Goal of This Episode

Learn to match numeric values with ranges inside a `match`.

## Concept

When we learned `match`, we compared values one at a time. But what if you want to match "any number between 1 and 5"? Surely not five separate arms.

Rust offers the **range pattern**, letting you match against ranges in a `match`:

```rust,editable
fn main() {
    let score = 12;
    match score {
        1..=5 => println!("Low score"),
        _ => {}
    }
}
```

`1..=5` means 1, 2, 3, 4, 5 (both ends included). This `..=` means much the same as the `for i in 0..=5` from Chapter 1.

Besides `..=` (end included), you can use `..` (end excluded):

```rust,editable
fn main() {
    let score = 65;
    match score {
        0..50 => println!("Failing"),   // 0 through 49
        50..=100 => println!("Passing"), // 50 through 100 (inclusive)
        _ => {}
    }
}
```

### Careful: Don't Confuse the Two Kinds of `..`!

Last episode's `..` and this episode's `..` look identical but mean completely different things:

- **Last episode**: `Point { x, .. }` → ignore remaining fields; `..` means "I don't care about the rest."
- **This episode**: `0..50` → a numeric range; `..` means "from one number to another."

The Rust compiler tells them apart from context and never confuses them. But as a beginner, take care to distinguish the two.

### One-sided Ranges

Range patterns also support writing just one side:

```rust,editable
fn main() {
    let temperature = 25;
    match temperature {
        ..0 => println!("Below zero"),   // Less than 0
        0..=30 => println!("Ordinary"),  // 0 through 30
        31.. => println!("Very hot"),    // 31 and up
    }
}
```

### `char` Works Too

Range patterns aren't just for numbers — they work on `char` too:

```rust,editable
fn main() {
    let c = '哼';
    match c {
        'a'..='z' => println!("A lowercase English letter"),
        'A'..='Z' => println!("An uppercase English letter"),
        '0'..='9' => println!("A digit"),
        _ => println!("Some other character"),
    }
}
```

## Example Code

```rust,editable
fn main() {
    // Grading scores with range patterns
    let score = 78;

    match score {
        90..=100 => println!("A"),
        80..90 => println!("B"),
        70..80 => println!("C"),
        60..70 => println!("D"),
        0..60 => println!("F"),
        _ => println!("Score out of range"),
    }

    // One-sided ranges
    let temperature = -5;

    match temperature {
        ..0 => println!("Below zero — freezing!"),
        0..=35 => println!("Tolerable"),
        36.. => println!("Too hot!"),
    }

    // Range patterns on char
    let c = 'G';

    match c {
        'a'..='z' => println!("'{}' is a lowercase letter", c),
        'A'..='Z' => println!("'{}' is an uppercase letter", c),
        '0'..='9' => println!("'{}' is a digit", c),
        _ => println!("'{}' is some other character", c),
    }
}
```

## Recap

- `..` and `..=` work not only in `for` loops but also as patterns.
- `1..=5` → both ends included (1, 2, 3, 4, 5).
- `0..50` → start included, end excluded (0 through 49).
- `..0` → less than 0; `31..` → 31 and up (one-sided ranges).
- `char` supports range patterns too: `'a'..='z'`.
- This `..` is a "numeric range" — a different thing from last episode's field-ignoring `..`; don't mix them up.
