# `if` as an Expression

## Goal of This Episode

Learn to treat `if` as an "expression" and use it directly to assign a value to a variable.

## Main Text

This is the last episode of Chapter 1! Today I'll introduce one of Rust's cool features — `if` isn't just for making decisions; it can also **return a value**.

### First, the Usual Way

Suppose you want to give a variable different values based on a condition. You might write:

```rust,editable
fn main() {
    let condition = true;
    let x;

    if condition {
        x = 1;
    } else {
        x = 2;
    }

    println!("{}", x);
}
```

Nothing wrong with that — but Rust has a more concise way.

### `if` as an Expression

```rust,editable
fn main() {
    let condition = true;
    let x = if condition { 1 } else { 2 };

    println!("{}", x);
}
```

Running it prints `1`.

See that? The whole `if condition { 1 } else { 2 }` sits on the right side of `let x =`, assigning its result directly to `x`.

If `condition` is `true`, `x` is 1; if it's `false`, `x` is 2.

### Note: No Semicolons Inside the Braces

```rust,editable
fn main() {
    let condition = true;
    let x = if condition { 1 } else { 2 };
    //                      ^          ^
    //                no semicolon  no semicolon
}
```

Those values (1 and 2) have **no semicolon** after them. In Rust, a value without a semicolon is the "return value." This is Rust's expression syntax — we'll go into more detail when we learn about functions.

### Both Sides Must Have the Same Type!

```rust,compile_fail
fn main() {
    let condition = true;
    let x = if condition { 1 } else { "hello" }; // ❌ Error!
}
```

This fails, because `1` is an integer and `"hello"` is a string. Rust won't allow `x` to be sometimes a number and sometimes a string — it needs one definite type.

The values inside the two sets of braces **must have the same type**:

```rust,compile_fail
# fn main() {
#     let condition = true;
#
    // ✅ Both sides are integers
    let x = if condition { 1 } else { 2 };

    // ✅ Both sides are strings
    let msg = if condition { "good" } else { "bad" };

    // ❌ One side an integer, the other a string
    let bad = if condition { 1 } else { "hello" };
# }
```

### What's the Benefit?

1. `x` doesn't need to be `mut`.
2. The code is more concise.
3. It reflects Rust's design philosophy: many things are "expressions" that can return values.

## Recap

- In Rust, `if` is an **expression** and can return a value directly: `let x = if condition { 1 } else { 2 };`.
- The part inside the braces that serves as the return value takes **no semicolon**.
- The `if` and `else` sides must have matching types.

Congratulations on finishing Chapter 1! 🎉 You've learned Rust's basic syntax: variables, arithmetic, conditionals, loops, types, and more. In the next chapter, we'll start learning more of Rust's distinctive features!
