# Operator Precedence

## Goal of This Episode

Understand Rust's order of operations — multiplication and division before addition and subtraction — and how to change the order with parentheses.

## Main Text

Last episode we learned addition, subtraction, multiplication, and division — but what if we mix them together? Which one does the computer compute first?

### Multiplication and Division First, Then Addition and Subtraction

```rust,editable
fn main() {
    println!("{}", 2 + 3 * 4);
}
```

What do you think the answer is?

If you thought 20 (first 2 + 3 = 5, then times 4), that's wrong!

The answer is **14**. Just like in math, Rust does **multiplication and division before addition and subtraction**. So it first computes `3 * 4 = 12`, then `2 + 12 = 14`.

### Changing the Order with Parentheses

What if you really do want the addition to happen first? Just add parentheses:

```rust,editable
fn main() {
    println!("{}", (2 + 3) * 4);
}
```

This time the answer is **20**. Whatever is inside the parentheses gets computed first: `2 + 3 = 5`, then `5 * 4 = 20`.

### A Little Tip

When you're not sure about the order, just add parentheses. Parentheses don't just change the order — sometimes they also make code easier to read. Even when the order is already correct, there's no harm in adding parentheses to make your intent clearer.

```rust,editable
fn main() {
    // These two lines give the same result, but the second is clearer
    println!("{}", 2 + 3 * 4);
    println!("{}", 2 + (3 * 4));
}
```

## Recap

- Rust's operator precedence works just like math: multiplication and division come before addition and subtraction.
- Parentheses `()` force a different order of operations.
- When in doubt, add parentheses — it's safe and makes the code easier to read.
