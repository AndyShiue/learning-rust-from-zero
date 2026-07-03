# Tuples

## Goal of This Episode

Use a tuple to bundle several values of different types into one, and learn how to get the values back out.

## Main Text

So far, one variable has held one value. But what if I want to tie together "an integer, a decimal, and a boolean"? That's what a **tuple** is for.

### Creating a Tuple

```rust,editable
fn main() {
    let t = (1, 3.14, true);
    println!("{}", t.0); // 1
    println!("{}", t.1); // 3.14
    println!("{}", t.2); // true
}
```

Wrap the values in parentheses `()`, separate them with commas, and you've got a tuple.

To get values out, use **a dot plus an index**: `t.0`, `t.1`, `t.2`. Note that indexing starts at 0!

### The Unit Type — the Empty Tuple

Rust has one special tuple with nothing inside:

```rust,editable
fn main() {
    let _u: () = ();
}
```

This `()` is called the **unit type**. It's "a type with only one value" — and that value is also written `()`.

### Annotating the Type

If you want to spell out a tuple's type explicitly:

```rust,editable
fn main() {
    let t: (i32, f64, bool) = (1, 3.14, true);
    println!("{} {} {}", t.0, t.1, t.2);
}
```

Each position's type must correspond.

### Single-element Tuples — Don't Forget the Comma!

If you want a tuple with just one element, remember the comma:

```rust,editable
fn main() {
    let not_a_tuple = (5);     // This is just the number 5, wrapped in parentheses
    let a_tuple = (5,);        // THIS is a tuple! Note the comma

    println!("{}", a_tuple.0); // 5
}
```

`(5)` is merely a number in parentheses, not a tuple. `(5,)` is. That comma matters!

The same goes for the type:

```rust,editable
fn main() {
    let t: (i32,) = (5,);
    println!("{}", t.0);
}
```

`(i32)` is just `i32` in parentheses; `(i32,)` is the type of a single-element tuple.

### Modifying Values inside a Tuple

If the tuple is declared with `let mut`, you can modify the values inside:

```rust,editable
fn main() {
    let mut t = (1, 2, 3, 4);
    println!("Before: {}", t.1); // 2
    t.1 = 99;
    println!("After: {}", t.1); // 99
}
```

Same as any other `mut` variable — no `mut`, no changes.

## Recap

- A tuple packs values of different types together with `()`.
- Get values with `t.0`, `t.1`, `t.2`... (indexing starts at 0).
- `()` is the unit type, representing "no meaningful value."
- Single-element tuples need the comma: `(5,)` is a tuple; `(5)` is just a number.
- A `let mut` tuple allows modifying inner values with `t.0 = new_value`.
