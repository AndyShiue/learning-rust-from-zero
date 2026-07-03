# `for` + Ranges

## Goal of This Episode

Use a `for` loop together with a range to repeat things, without managing a counter yourself.

## Main Text

In the last two episodes we learned `loop` and `while`, both of which required managing a counter by hand (`count -= 1` and so on). Today we'll learn an even simpler way — the `for` loop.

### `for` + a Range

```rust,editable
fn main() {
    for i in 0..5 {
        println!("{}", i);
    }
}
```

### What Is `0..5`?

`0..5` is called a **range**. It means "starting at 0, up to just before 5." Note: **5 is not included**!

So `0..5` gives the five numbers 0, 1, 2, 3, 4.

You can read `for i in 0..5` as: "Let `i` run from 0 to 4 in order, doing what's inside the curly braces each time."

Notice that `i` here doesn't need a `let` — `for` declares it for you automatically. And `i` is usable anywhere inside the curly braces `{}` that follow the `for`.

### Want to Include the End? Use `0..=5`

```rust,editable
fn main() {
    for i in 0..=5 {
        println!("{}", i);
    }
}
```

`0..=5` has an extra `=`, meaning "including 5."

### Comparison

| Syntax | Meaning | Numbers produced |
|------|------|-----------|
| `0..5` | 0 to 4 | 0, 1, 2, 3, 4 |
| `0..=5` | 0 to 5 | 0, 1, 2, 3, 4, 5 |
| `1..4` | 1 to 3 | 1, 2, 3 |
| `1..=4` | 1 to 4 | 1, 2, 3, 4 |

### `while` and `for` Can Use `break` Too

We learned `break` inside `loop` earlier, but it also works in `while` and `for`. One thing to note: `break` only jumps out of a **loop** — it doesn't jump out of control structures like `if`. So in the code below, `break` exits the `for` loop, not the `if`:

```rust,editable
fn main() {
    for i in 0..10 {
        if i == 5 {
            println!("Found 5 — stopping here!");
            break;
        }
        println!("{}", i);
    }
}
```

Running this prints only 0~4; when it hits 5, `break` exits the loop.

## Recap

- `for i in 0..5` runs `i` from 0 to 4 (end excluded); `0..=5` includes 5.
- Compared to `while`, `for` doesn't need manual counter increments or condition checks — more concise and less error-prone.
- `break` works inside `loop`, `while`, and `for`.
