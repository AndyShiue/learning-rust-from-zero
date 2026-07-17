# `@` Bindings

## Goal of This Episode

Learn to use `@` to bind the matching value to a variable while matching a pattern.

## Concept

We have already learned range patterns: `0..=100` matches values from 0 through 100. Now suppose the `SetVolume` variant of a `Command` carries a volume. We want to check that volume's range and print its exact value inside the arm:

```rust,editable
enum Command {
    SetVolume(i32),
    SetBrightness(i32),
    Quit,
}

fn main() {
    let command = Command::SetVolume(72);

    match command {
        Command::SetVolume(level @ 0..=100) => {
            println!("Set the volume to {}", level);
        }
        Command::SetVolume(level) => {
            println!("Volume {} is out of range", level);
        }
        Command::SetBrightness(level) => {
            println!("Set the brightness to {}", level);
        }
        Command::Quit => println!("Quit"),
    }
}
```

Inside `Command::SetVolume(level @ 0..=100)`, the range `0..=100` on the right performs the match, while `level` on the left binds the exact volume. When the value is `Command::SetVolume(72)`, the pattern matches and `level` is `72` inside the arm.

This is the syntax of an `@` binding:

```text
variable_name @ pattern
```

The left side creates a binding, and the right side performs the match. After the pattern matches, the variable on the left can be used inside the arm.

`@` can be used with other patterns too, including `|`:

In the example below, the first arm uses `('a' | 'e' | 'i' | 'o' | 'u')` to match a lowercase vowel, then binds the matching character to `key`. When the pattern to the right of `@` uses `|`, that group must be wrapped in parentheses.

The `MouseClick` arm demonstrates an `@` binding inside a field of a `struct` variant. `0..=10` matches the range of the `x` field, and `horizontal` binds the exact coordinate that matched.

## Example Code

```rust,editable
enum Event {
    KeyPress(char),
    MouseClick { x: i32, y: i32 },
    Quit,
}

fn main() {
    let event = Event::MouseClick { x: 6, y: 30 };

    match event {
        Event::KeyPress(key @ ('a' | 'e' | 'i' | 'o' | 'u')) => {
            println!("Pressed the lowercase vowel '{}'", key);
        }
        Event::KeyPress(key @ 'a'..='z') => {
            println!("Pressed another lowercase letter '{}'", key);
        }
        Event::KeyPress(key) => {
            println!("Pressed another key '{}'", key);
        }
        Event::MouseClick {
            x: horizontal @ 0..=10,
            y,
        } => {
            println!("Clicked in the left area: ({}, {})", horizontal, y);
        }
        Event::MouseClick { x, y } => {
            println!("Clicked elsewhere: ({}, {})", x, y);
        }
        Event::Quit => println!("Quit"),
    }
}
```

## Recap

- `variable_name @ pattern` checks the pattern on the right; after a successful match, the actual value is bound to the variable on the left.
- `Command::SetVolume(level @ 0..=100)` both restricts the volume range and captures the exact volume.
- `@` can be used inside nested data such as `enum` variants and `struct` fields.
- `@` works with ranges, `|`, and other patterns. With `|`, write `value @ (pattern1 | pattern2)`.
