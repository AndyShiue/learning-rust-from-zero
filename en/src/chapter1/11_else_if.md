# `else if`

## Goal of This Episode

Use `else if` to handle multiple condition branches — not just two-way choices, but three-way, four-way, and beyond.

## Main Text

The `if...else...` from last episode only handles "pick one of two." But what if there are more cases? Say, letter grades: A, B, C, F... That's when you need `else if`.

### Example: Letter Grades

```rust,editable
fn main() {
    let score = 85;

    if score >= 90 {
        println!("A");
    } else if score >= 80 {
        println!("B");
    } else if score >= 70 {
        println!("C");
    } else {
        println!("F");
    }
}
```

### How Does It Decide?

Rust goes **from top to bottom**, checking the conditions one by one:

1. `score >= 90`? Is 85 >= 90? No, skip.
2. `score >= 80`? Is 85 >= 80? Yes! Print `"B"`, then stop.
3. Everything after that is never looked at.

This is important: **as soon as one condition holds, all the rest are skipped**.

### Try Other Scores

- `score = 95` → prints `"A"`.
- `score = 73` → prints `"C"`.
- `score = 50` → prints `"F"` (nothing above holds, so it falls through to `else`).

### The Structure

```rust,ignore
if condition1 {
    ...
} else if condition2 {
    ...
} else if condition3 {
    ...
} else {
    ... (when none of the above holds)
}
```

You can have as many `else if`s as you like. The final `else` is optional (though it's usually a good idea to include it, in case some situation slips through).

## Recap

- `else if` handles multiple condition branches — more than just two-way choices.
- Rust checks conditions from top to bottom; the first one that holds gets executed, and all the rest are skipped.
- The final `else` is optional; it handles the case where "none of the above holds."
