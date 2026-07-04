# Block Expressions

## Goal of This Episode

Learn to create block expressions with curly braces `{}`, running several lines of code inside and returning a value.

## Concept

In Rust, a pair of curly braces `{}` isn't just a scope — it's also an **expression** in its own right, capable of returning a value. The rule is simple: if the last line inside the block has no semicolon, that line's value is the whole block's return value.

```rust,editable
fn main() {
    let x = {
        let y = 5;
        y + 1 // No semicolon → this is the block's return value
    };
    // x is now 6
}
```

This concept is especially useful in `match`. Our `match` arms so far were all one-liners, but if you want to do several things in one arm, use a block:

```rust,noplayground
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn describe_color() -> &'static str {
#     let c = Color::Red;
    match c {
        Color::Red => {
            println!("It's red!");
            "red"
        }
        // ...
#         _ => "",
    }
# }
#
# fn main() {}
```

Inside the block you can declare variables and do calculations; the last line without a semicolon is the return value.

Note: if a `match` arm uses a block `{}`, the comma after it can be omitted. The `}` is already an unambiguous end marker, so Rust doesn't need the comma as a separator. But if the arm is a single line (no block), the comma can't be dropped.

```rust,noplayground
# enum Season {
#     Spring,
#     Summer,
#     Autumn,
#     Winter,
# }
#
# fn describe_season() -> &'static str {
#     let s = Season::Summer;
    match s {
        Season::Summer => {
            println!("So hot!");
            "a scorching summer"
        } // ← No comma; OK
        Season::Autumn => "a cool autumn", // ← Single-line arm; comma required
        // ...
#         _ => "",
    }
# }
#
# fn main() {}
```

## Example Code

```rust,editable
enum Season {
    Spring,
    Summer,
    Autumn,
    Winter,
}

fn main() {
    // Basic use of a block expression
    let result = {
        let a = 10;
        let b = 20;
        a + b // Last line without a semicolon → the return value
    };
    println!("result = {}", result);

    // Using a block in a match arm
    let s = Season::Summer;

    let description = match s {
        Season::Spring => {
            let temp = 22;
            println!("Spring is in the air");
            if temp > 20 {
                "a warm spring"
            } else {
                "a still-chilly spring"
            }
        }
        Season::Summer => {
            println!("So hot!");
            "a scorching summer"
        }
        Season::Autumn => "a cool autumn",
        Season::Winter => "a cold winter",
    };
    println!("{}", description);
}
```

## Recap

- A `{}` block is itself an expression; the last line without a semicolon is its return value.
- `let x = { ... };` runs multiple lines inside the block and assigns the result to x.
- A `match` arm can use `=> { ... }` to run multiple lines, and no comma is needed after the block.
- Variables declared inside a block only live within the block (scope).
- Block expressions are extremely common in Rust, and they are an important foundational concept to understand.
