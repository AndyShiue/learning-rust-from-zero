# `let mut`

## Goal of This Episode

Understand that Rust variables are immutable by default, and that you need `mut` to change their values.

## Main Text

Today let's talk about one of Rust's most distinctive design decisions — **variables are immutable by default**.

### First, See What Happens

```rust,compile_fail
fn main() {
    let x = 5;
    x = 10;
    println!("{}", x);
}
```

Do you think it prints 10? It doesn't. You get a compile error. Rust is telling you: "`x` is immutable — you can't give it a new value."

### Wait, Why Not?

In many programming languages, variables can be changed freely. But Rust's attitude is: **if you don't intend to change it, don't let it be changeable**.

Why? Because if you know a value never changes, you don't have to worry about it being modified behind your back while reading the code. This matters a lot in large programs.

### To Change It, Add `mut`

If you really do need to change the value, add `mut` (short for "mutable"):

```rust,editable
fn main() {
    let mut x = 5;
    println!("x was originally {}", x);
    x = 10;
    println!("x is now {}", x);
}
```

This time it works! By writing `let mut`, you've told Rust: "I'm going to change this variable later."

### Quick Summary

```rust,noplayground
# fn main() {
    let x = 5;     // Immutable; can't be changed later
    let mut x = 5; // Mutable; can be changed later
# }
```

Rust isn't forbidding you from changing variables — it just wants you to **say so explicitly**. This is part of Rust's design philosophy: **make choices consciously**.

## Recap

- Rust variables are **immutable** by default; they can't be reassigned.
- To make a variable changeable, add `mut` when declaring it: `let mut x = 5;`.
- To modify a mutable variable's value, just write `x = new_value;` (no `let` needed again).
- This is Rust's design philosophy: make you choose explicitly, rather than silently allowing modification.
