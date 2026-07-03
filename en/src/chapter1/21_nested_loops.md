# Nested Loops

## Goal of This Episode

Put a loop inside a loop — use nested loops to print the multiplication table.

## Main Text

Last episode we learned the `for` loop. Today we'll try something more advanced — putting one loop **inside another loop**.

### What Are Nested Loops?

"Nested" means "one layer inside another," like Russian nesting dolls. Each time the outer loop runs once, the inner loop runs through a complete round.

### The Multiplication Table

Let's take on a challenge: print the 9×9 multiplication table with nested loops:

```rust,editable
fn main() {
    for i in 1..=9 {
        for j in 1..=9 {
            print!("{} x {} = {}   ", i, j, i * j);
        }
        println!(); // New line
    }
}
```

### How Does It Work?

1. The outer loop runs `i` from 1 to 9.
2. When `i = 1`, the inner loop runs `j` from 1 to 9 → printing 1×1, 1×2, ... 1×9.
3. After the inner loop finishes, `println!()` starts a new line.
4. The outer loop moves to `i = 2`, and the inner loop runs 1 to 9 again → printing 2×1, 2×2, ... 2×9.
5. And so on...

### `print!` vs `println!`

We used something new here: `print!`. It's a lot like `println!`, except that `print!` **doesn't start a new line** after printing, whereas `println!` does.

### Visualizing It

One outer-loop iteration = one row:

```ignore
i=1 → [j=1, j=2, j=3, ... j=9] → new line
i=2 → [j=1, j=2, j=3, ... j=9] → new line
...
i=9 → [j=1, j=2, j=3, ... j=9] → new line
```

### `break` Only Exits the Innermost Layer

Using `break` inside nested loops only exits the **innermost** loop — the outer one keeps going:

```rust,editable
fn main() {
    for i in 1..=3 {
        for j in 1..=3 {
            if j == 2 {
                break; // Only exits the inner loop
            }
            println!("i={}, j={}", i, j);
        }
    }
}
```

Each time `j` reaches 2 it `break`s, but the outer `i` still runs through 1, 2, 3.

### Loop Labels: Breaking Out of a Specific Layer

What if you want to jump straight out of the outer loop? Use a **loop label**:

```rust,editable
fn main() {
    'outer: for i in 1..=3 {
        for j in 1..=3 {
            if j == 2 {
                break 'outer; // Exits the outer loop
            }
            println!("i={}, j={}", i, j);
        }
    }
    println!("Done!");
}
```

`'outer:` is a **label**, placed in front of a loop. `break 'outer` says "exit the loop labeled `'outer`." Note that label names start with `'` (a single quote).

## Recap

- Nested loops are loops inside loops: each outer iteration runs the inner loop through a full round.
- The difference between `print!` and `println!`: `print!` doesn't start a new line.
- In nested loops, `break` only exits the innermost loop.
- Use a loop label (`'outer:` + `break 'outer`) to break out of a specific outer loop.
