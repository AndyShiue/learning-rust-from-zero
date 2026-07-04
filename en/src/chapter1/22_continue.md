# `continue`

## Goal of This Episode

Use `continue` to skip certain iterations of a loop.

## Main Text

Earlier we learned that `break` jumps out of a loop. Today it's `continue` — which doesn't exit the loop, but **skips the current iteration and goes straight to the next one**.

### Printing Only Odd Numbers

```rust,editable
fn main() {
    for i in 0..10 {
        if i % 2 == 0 {
            continue;
        }
        println!("{}", i);
    }
}
```

### How Does It Work?

The loop runs `i` from 0 to 9:

- `i = 0` → Is `0 % 2 == 0`? Yes (even), `continue`! Skip it, don't print.
- `i = 1` → Is `1 % 2 == 0`? No (odd), keep going, print 1.
- `i = 2` → Even, `continue`, skip.
- `i = 3` → Odd, print 3.
- ...and so on.

### `break` vs `continue`

- **`break`**: The whole loop ends; no more iterations.
- **`continue`**: Skip this iteration, but the loop continues with the next one.

Like `break`, `continue` only acts on **loops** — it doesn't skip control structures like `if`. In the code above, `continue` skips the current iteration of the `for` loop, not the `if`.

### Another Example

Skip 5 and don't print it:

```rust,editable
fn main() {
    for i in 1..=10 {
        if i == 5 {
            continue;
        }
        println!("{}", i);
    }
}
```

5 gets skipped; everything else prints normally.

### `continue` + Loop Labels

Last episode we learned that `break 'outer` can exit a specific loop layer. `continue` works with labels too:

```rust,editable
fn main() {
    'outer: for i in 1..=3 {
        for j in 1..=3 {
            if j == 2 {
                continue 'outer; // Skip to the outer loop's next iteration
            }
            println!("i={}, j={}", i, j);
        }
    }
}
```

Each time `j` reaches 2, `continue 'outer` jumps straight to the outer loop's next iteration, so `j=2` and `j=3` never get printed.

## Recap

- `continue` skips the current iteration and goes straight to the next one.
- `break` means "stop the whole loop"; `continue` means "skip the current iteration and run the next one."
- Pair it with `if` to selectively skip particular cases.
- `continue 'outer` works with loop labels to skip the current iteration of an outer loop.
