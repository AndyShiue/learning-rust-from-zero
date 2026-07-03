# Destructuring Tuples with `let`

## Goal of This Episode

Learn to use `let` to break a tuple apart directly, assigning its values to separate variables.

## Concept

We've learned to destructure tuples inside `match`, like `(x, y) => ...`. But actually, **you don't need `match` — `let` can destructure directly**!

```rust,noplayground
# fn main() {
    let (x, y) = (1, 2);
# }
```

This one line does two things:

1. Creates the tuple `(1, 2)`.
2. Takes the first value out as `x` and the second as `y`.

Back in Chapter 2, we always used `t.0` and `t.1` to access tuples. Now, with destructuring, one line splits all the values apart, each with a readable name.

The `_` and `..` we learned earlier work in `let` destructuring too.

## `mut` on Bindings

In Chapter 1 we learned `let mut x = 5;`. In fact, `mut` isn't part of the type — it's a modifier on the **binding**.

Since `let` destructuring is doing bindings, you can naturally put `mut` on individual variables:

```rust,compile_fail
# #![allow(unused)]
#
# fn main() {
    let (mut a, b) = (1, 2);
    a += 10; // OK, a is mutable
    b += 10; // Error, b is immutable
# }
```

Within one pattern, some variables can take `mut` and others not — each independent.

This rule isn't limited to `let`: **anywhere a variable is bound, `mut` can be added**:

- match arms: `Some(mut x) => { x += 1; }`.
- for loops: `for mut x in [1, 2, 3] { ... }`.
- function parameters: `fn foo(mut x: i32) { x += 1; }`.

The same goes for every binding construct we'll learn later. It's all one thing — `mut` modifies the binding, not the type.

## Example Code

```rust,editable
fn main() {
    // Basic let destructuring
    let (x, y) = (10, 20);
    println!("x = {}, y = {}", x, y);

    // Three-value tuples work too
    let (name, score, grade) = ("Ming", 95, 'A');
    println!("{} scored {} points, grade {}", name, score, grade);

    // Combine with _ to ignore one value
    let (_, second, _) = (1, 2, 3);
    println!("Just the second: {}", second);

    // Combine with .. to ignore several values
    let (first, ..) = (100, 200, 300, 400);
    println!("Just the first: {}", first);

    // mut on individual bindings
    let (mut a, b) = (1, 2);
    a += 10;
    println!("a = {}, b = {}", a, b);

    // A function returning a tuple, destructured directly
    let (min, max) = min_max(7, 3);
    println!("Smallest {}, largest {}", min, max);
}

fn min_max(a: i32, b: i32) -> (i32, i32) {
    if a < b {
        (a, b)
    } else {
        (b, a)
    }
}
```

## Recap

- `let (x, y) = (1, 2);` breaks a tuple apart directly.
- Destructuring a tuple reads better than `.0` and `.1`.
- Combine with `_` to ignore single values, or `..` to ignore several.
- `mut` modifies the binding, not the type — any binding position can take `mut`.
- When a function returns a tuple, `let` destructuring extracts every value at once.
