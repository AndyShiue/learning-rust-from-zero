# `while`

## Goal of This Episode

Rewrite the countdown with a `while` loop, and compare it to the `loop` + `break` version.

## Main Text

Last episode we built a countdown with `loop` + `break`. Today we'll learn another kind of loop — `while` — which makes the same logic cleaner to write.

### Rewriting the Countdown with `while`

```rust,editable
fn main() {
    let mut count = 5;
    while count > 0 {
        println!("{}", count);
        count -= 1;
    }
    println!("Liftoff!");
}
```

Exactly the same result!

### Comparing with `loop` + `break`

Last episode's version:

```rust,editable
fn main() {
    let mut count = 5;
    loop {
        if count == 0 {
            println!("Liftoff!");
            break;
        }
        println!("{}", count);
        count -= 1;
    }
}
```

The `while` version:

```rust,editable
fn main() {
    let mut count = 5;
    while count > 0 {
        println!("{}", count);
        count -= 1;
    }
    println!("Liftoff!");
}
```

See the difference? `while` merges the "condition check" and the "loop" into one. No need to write your own `if` and `break` — just tell `while`: "As long as this condition holds, keep going."

### `while` in Plain Words

> **While** the condition holds, keep doing what's inside the curly braces.

`while count > 0` → as long as `count` is greater than 0, keep running. Once `count` hits 0, the condition no longer holds, and it stops automatically.

### When to Use `loop`, and When `while`?

- **`while`**: You know whether to continue before the loop iteration starts (check the condition first, then decide whether to run).
- **`loop` + `break`**: You can only decide whether to stop somewhere in the middle of the loop.

Both get the job done — it's just that `while` is more concise in many situations.

## Recap

- A `while` loop keeps running as long as the condition holds, and stops automatically when it doesn't.
- More concise than `loop` + `break`; good for when you know whether to continue before each iteration.
- `loop` + `break` suits cases where the stopping decision happens mid-loop.
