# Tuple Patterns

## Goal of This Episode

Learn to destructure ordinary tuples and tuple `struct`s inside a `match`.

## Concept

Episode 9 covered destructuring `enum` variants in `match`. But it's not just `enum`s — we can use `match` to destructure ordinary tuples too!

```rust,editable
fn main() {
    let point = (3, 7);

    match point {
        (0, 0) => println!("The origin"),
        (x, 0) => println!("On the x-axis, x = {}", x),
        (0, y) => println!("On the y-axis, y = {}", y),
        (x, y) => println!("At ({}, {})", x, y),
    }
}
```

`match` compares top to bottom:

- `(0, 0)` → matches only when both values are 0.
- `(x, 0)` → the second value is 0, the first is anything (captured as `x`).
- `(0, y)` → the first value is 0, the second is anything.
- `(x, y)` → matches everything (the last arm acts as the "default").

Just like Episode 10, patterns can mix "fixed values" and "variables." Fixed values do the comparing; variables catch the data.

## Example Code

```rust,editable
fn main() {
    let point = (2, 0);

    match point {
        (0, 0) => println!("The origin"),
        (x, 0) => println!("On the x-axis, x = {}", x),
        (0, y) => println!("On the y-axis, y = {}", y),
        (x, y) => println!("An ordinary point ({}, {})", x, y),
    }

    // Simple classification with match and tuples
    let score = (85, 90);

    match score {
        (100, 100) => println!("Double perfect score!"),
        (a, b) => {
            println!("Literature {}, math {}", a, b);
            let total = a + b;
            println!("Total {}", total);
        }
    }
}
```

## Tuple `struct`s Work the Same Way

Remember the tuple `struct` from Episode 2? Its pattern matching works exactly like ordinary tuples:

```rust,editable
struct Point(i32, i32);

fn main() {
    let p = Point(3, 0);

    match p {
        Point(0, 0) => println!("The origin"),
        Point(x, 0) => println!("On the x-axis, x = {}", x),
        Point(0, y) => println!("On the y-axis, y = {}", y),
        Point(x, y) => println!("At ({}, {})", x, y),
    }
}
```

The only difference is the type name in front of the pattern, `Point(...)`, whereas ordinary tuples are written directly as `(...)`.

## Recap

- Ordinary tuples can be `match`ed too.
- Tuple `struct`s pattern-match the same way, just with the type name in front: `Point(x, y)`.
