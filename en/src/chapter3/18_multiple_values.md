# Multiple Values with `|`

## Goal of This Episode

Learn to match several possible values in one `match` arm.

## Concept

Sometimes you want several values to run the same code. For instance, Saturday and Sunday are both days off — no need for two separate arms.

Rust uses `|` (the pipe symbol) to mean "or":

```rust,editable
fn main() {
    let day = 1;
    match day {
        6 | 7 => println!("Day off"),
        _ => println!("Workday"),
    }
}
```

`6 | 7` means "6 or 7." You can chain as many values as you like with `|`:

```rust,editable
fn main() {
    let n = 3;
    match n {
        1 | 2 | 3 => println!("Top three"),
        _ => println!("Other"),
    }
}
```

It works with `enum`s too:

```rust,editable
enum Color {
    Red,
    Green,
    Blue,
}

fn main() {
    let color = Color::Red;
    match color {
        Color::Red | Color::Blue => println!("Warm or cool color"),
        Color::Green => println!("Green"),
    }
}
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
    // Matching multiple numbers
    let month = 7;

    match month {
        3 | 4 | 5 => println!("Spring"),
        6 | 7 | 8 => println!("Summer"),
        9 | 10 | 11 => println!("Autumn"),
        12 | 1 | 2 => println!("Winter"),
        _ => println!("Invalid month"),
    }

    // Matching multiple enum variants
    let s = Season::Autumn;

    let is_hot = match s {
        Season::Summer => true,
        Season::Spring | Season::Autumn | Season::Winter => false,
    };
    println!("Is the weather hot? {}", is_hot);

    // Combining range patterns with |
    let ch = '5';

    match ch {
        'a'..='z' | 'A'..='Z' => println!("A letter"),
        '0'..='9' => println!("A digit"),
        ' ' | '\t' | '\n' => println!("Whitespace"),
        _ => println!("Other"),
    }
}
```

## Recap

- In `match`, `|` means "or," letting one arm match multiple values.
- Syntax: `pattern1 | pattern2 | pattern3 => ...`.
- Works with `enum` variants.
- Works with range patterns too: `'a'..='z' | 'A'..='Z'`.
- When several values need the same handling, `|` beats writing multiple arms.
