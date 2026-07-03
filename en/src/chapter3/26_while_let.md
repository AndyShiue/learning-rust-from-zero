# `while let`

## Goal of This Episode

Learn to use `while let` to keep pattern matching in a loop until the pattern no longer fits.

## Concept

Last episode we learned `if let` — "if it matches, run once." `while let` is "as long as it matches, keep running" — the loop version of `if let`.

Syntax:

```rust,ignore
while let pattern = value {
    // Loop body
}
```

Before each iteration, Rust checks "does the value fit the pattern?" If yes, keep going; if not, stop.

To demonstrate `while let`, we'll use a custom `enum` to simulate a "maybe there's a value, maybe we're done" situation:

```rust,noplayground
enum Step {
    Value(i32),
    Done,
}
#
# fn main() {}
```

## Example Code

```rust,editable
enum Step {
    Value(i32),
    Done,
}

fn get_step(index: i32) -> Step {
    if index < 5 {
        Step::Value(index * 10)
    } else {
        Step::Done
    }
}

fn main() {
    let mut i = 0;

    // while let: keep going as long as get_step returns Value
    while let Step::Value(v) = get_step(i) {
        println!("Step {}, value = {}", i, v);
        i += 1;
    }
    println!("Done! Ran {} steps in total", i);

    println!();

    // Another example: a countdown
    let mut count = 5;

    // Simulating a countdown with a custom enum
    while let Countdown::Tick(n) = get_countdown(count) {
        println!("Counting down {}...", n);
        count -= 1;
    }
    println!("Liftoff! 🚀");
}

enum Countdown {
    Tick(i32),
    Launch,
}

fn get_countdown(n: i32) -> Countdown {
    if n > 0 {
        Countdown::Tick(n)
    } else {
        Countdown::Launch
    }
}
```

## Recap

- `while let pattern = value { ... }` is the loop version of `if let`.
- As long as the value fits the pattern, the loop keeps running.
- When the value no longer fits, the loop ends automatically.
