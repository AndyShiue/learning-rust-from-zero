# Variables and Output

## Goal of This Episode

Learn to create variables with `let`, then print them out with `println!`.

## Main Text

Last episode we successfully printed "Hello, Rust!", but that text was hard-coded into the program. What if we want to be a bit more flexible? That's where **variables** come in.

### What Is a Variable?

A variable is like a container: you can put something into it and take it out to use later.

Let's see how to use one:

```rust,editable
fn main() {
    let x = 5;
    println!("{}", x);
}
```

Here, `let x = 5;` says: "I want to create a variable called `x`, and put `5` into it."

Then, in `println!("{}", x);`, the `{}` is a placeholder — it means "at this spot, please fill in the value of `x`."

### Text Variables

Variables can hold more than just numbers — they can hold text too:

```rust,editable
fn main() {
    let name = "Rust";
    println!("Hello, {}!", name);
}
```

See that? The `{}` was replaced by the value of `name`, which is `"Rust"`.

Try changing `"Rust"` to your own name and see what gets printed!

### `let` Doesn't Have to Assign Right Away

When you declare a variable with `let`, you don't have to give it a value immediately. You can declare first and assign later:

```rust,editable
fn main() {
    let x;
    x = 5;
    println!("{}", x);
}
```

This is perfectly legal, but you must assign to it exactly once before using it — using it without assigning causes a compile error.

## Recap

- `let` creates a variable.
- Text is wrapped in `"double quotes"`.
- `println!("{}", variable)` prints out the value of a variable.
- `{}` is a placeholder that gets replaced by the value that follows.
- A `let` declaration doesn't have to assign right away, but it must assign exactly once.
