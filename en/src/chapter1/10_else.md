# `else`

## Goal of This Episode

Use `else` to make the program do something different when the condition doesn't hold.

## Main Text

When we learned `if`, the program simply did nothing if the condition didn't hold. But often we want to say: "If this, do A; otherwise, do B." That's what `else` is for.

### Basic Usage

```rust,editable
fn main() {
    let x = 2;
    if x > 5 {
        println!("big");
    } else {
        println!("small");
    }
}
```

`x` is 2. Is 2 greater than 5? No, so the `if` block is skipped and the `else` block runs, printing "small".

### Try a Different Value

Change `x` to 8:

```rust,editable
fn main() {
    let x = 8;
    if x > 5 {
        println!("big");
    } else {
        println!("small");
    }
}
```

This time it prints "big", because 8 is greater than 5 — the condition holds, so the `if` side runs.

### In Plain Words

You can think of `if...else...` as:

> **If** the condition holds, do this; **otherwise**, do that.

Exactly one side will run — never both, and never neither.

## Recap

- `else` follows an `if` and handles what to do when the condition doesn't hold.
- `if...else...` is an either-or: exactly one side runs, never both and never neither.
