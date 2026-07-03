# `match` as an Expression

## Goal of This Episode

Learn to use `match` as an expression, so it returns a value.

## Concept

Remember from Chapter 1 that `if` can be an expression?

```rust,editable
fn main() {
    let condition = true;
    let x = if condition { 1 } else { 2 };
}
```

`match` can too! You can put a whole `match` on the right side of a `let`, with each arm returning a value:

```rust,editable
enum Color {
    Red,
    Green,
    Blue,
}

fn main() {
    let c = Color::Red;
    let msg = match c {
        Color::Red => "red",
        Color::Green => "green",
        Color::Blue => "blue",
    };
}
```

Note the semicolon `;` at the very end — the whole `let msg = match ... { ... };` is one `let` statement.

The values returned by all the arms must have matching types. If the first arm returns `&str`, every other arm must return `&str` too.

## Example Code

```rust,editable
enum Season {
    Spring,
    Summer,
    Autumn,
    Winter,
}

fn main() {
    // match as an expression, returning &str
    let season = Season::Autumn;
    let name = match season {
        Season::Spring => "spring",
        Season::Summer => "summer",
        Season::Autumn => "autumn",
        Season::Winter => "winter",
    };
    println!("It's {} now", name);

    // Another example: match returning i32
    let weather = Season::Summer;
    let temp = match weather {
        Season::Spring => 22,
        Season::Summer => 35,
        Season::Autumn => 18,
        Season::Winter => 8,
    };
    println!("About {} degrees", temp);
}
```

## Recap

- `match` can be an expression; the whole `match` returns a value.
- Usage: `let x = match ... { ... };` (don't forget the final semicolon).
- All arms must return values of matching types.
- Same idea as the `if` expression — lots of things in Rust are expressions.
