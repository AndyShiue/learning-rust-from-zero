# The `_` Wildcard

## Goal of This Episode

Learn to use `_` to ignore values you don't care about, and to build a default arm in a `match`.

## Concept

Sometimes in a `match` we only care about a few cases and want to "ignore" the rest. Rust offers `_` (the underscore) as a **wildcard** — it matches any value without binding it to a variable.

The two most common uses:

**1. The default arm: `_ => ...`**

Placed at the end of a `match`, it means "every other case goes here":

```rust,editable
fn main() {
    let score = 95;
    match score {
        100 => println!("Perfect score!"),
        _ => println!("Not a perfect score"),
    }
}
```

**2. Ignoring a value at some position**

In a tuple or `enum` pattern, use `_` to hold a position you don't need:

```rust,editable
fn main() {
    let point = (5, 5);
    match point {
        (0, _) => println!("On the y-axis"), // Don't care about the second value
        (_, 0) => println!("On the x-axis"), // Don't care about the first value
        (_, _) => println!("Somewhere else"),
    }
}
```

## Example Code

```rust,editable
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn main() {
    // _ as the default arm
    let dir = Direction::Left;

    match dir {
        Direction::Up => println!("Going up"),
        _ => println!("Not up (maybe down, left, or right)"),
    }

    // _ ignoring a value inside a tuple
    let record = ("Alice", 95, 'A');

    match record {
        (name, _, _) => println!("The name is {}", name),
    }

    // Mixed usage
    let data = (1, Direction::Up);

    match data {
        (_, Direction::Up) => println!("The direction is up (whatever the number)"),
        (id, _) => println!("Number {} (direction isn't up)", id),
    }

    // _ as the default on an i32
    let score = 87;

    match score {
        100 => println!("Perfect score!"),
        0 => println!("Zero..."),
        _ => println!("Scored {} points", score),
    }
}
```

## Recap

- `_` is the wildcard: it matches any value without binding a variable.
- `_ => ...` at the end of a `match` is the "default arm," handling every unlisted case.
- Use `_` in patterns to ignore fields you don't need.
- With `_`, a `match` no longer has to spell out every variant.
