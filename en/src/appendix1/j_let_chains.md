# `let` Chains

## Goal of This Episode

Meet `let` chains — stringing together multiple `let`s and boolean conditions with `&&` inside `if` and `while` conditions.

> This episode supplements **Chapter 3**.

## Concept

### The Problem: Nested `if let`

Chapter 3 taught `if let`. But needing several pattern matches in a row means nested `if let`s:

```rust,editable
enum Wrapper {
    Value(i32),
    Empty,
}

fn get_a() -> Wrapper { Wrapper::Value(10) }
fn get_b(x: i32) -> Wrapper { Wrapper::Value(x + 1) }

fn main() {
    if let Wrapper::Value(a) = get_a() {
        if a > 0 {
            if let Wrapper::Value(b) = get_b(a) {
                println!("a = {}, b = {}", a, b);
            }
        }
    }
}
```

Every extra condition adds a level of indentation, and the code sinks deeper and deeper.

### `let` Chains Flatten It

You can string multiple `let`s and boolean conditions into one `if` with `&&`:

```rust,editable
enum Wrapper {
    Value(i32),
    Empty,
}

fn get_a() -> Wrapper { Wrapper::Value(10) }
fn get_b(x: i32) -> Wrapper { Wrapper::Value(x + 1) }

fn main() {
    if let Wrapper::Value(a) = get_a()
        && a > 0
        && let Wrapper::Value(b) = get_b(a)
    {
        println!("a = {}, b = {}", a, b);
    }
}
```

The `&&`-chained conditions are checked left to right in order. Variables bound by earlier `let`s are usable in later conditions (like `a` above). If any condition fails, the rest don't run — just like `&&`'s short-circuiting.

### Works in `while` Too

```rust,ignore
while let Some(item) = next_item()
    && item.value > 0
{
    // ...
}
```

## Example Code

```rust,editable
enum Command {
    Run { speed: i32 },
    Stop,
}

fn get_command() -> Command {
    Command::Run { speed: 5 }
}

fn get_boost() -> Command {
    Command::Run { speed: 3 }
}

fn main() {
    // The nested style
    if let Command::Run { speed: s } = get_command() {
        if s > 0 {
            if let Command::Run { speed: boost } = get_boost() {
                println!("Nested: speed {} + boost {} = {}", s, boost, s + boost);
            }
        }
    }

    // The let-chains style — same logic, flatter
    if let Command::Run { speed: s } = get_command()
        && s > 0
        && let Command::Run { speed: boost } = get_boost()
    {
        println!("Flat: speed {} + boost {} = {}", s, boost, s + boost);
    }
}
```

## Recap

- `let` chains string multiple `let`s and boolean conditions together with `&&` inside `if` and `while`.
- They replace nested `if let`, flattening the code.
- Variables bound earlier are usable later.
- Consistent with `&&` short-circuiting: an earlier failure stops the rest.
