# Multiple `trait` Bounds and `where`

## Goal of This Episode

Learn to combine multiple `trait` bounds with `+`, and make complex bounds more readable with `where` clauses.

## Concept

Episode 13 gave us `T: Clone`, requiring `T` to implement `Clone`. But what if you want `T` to implement several `trait`s at once?

### Multiple `trait` Bounds

Chain them with `+`:

```rust,noplayground
fn show_clone<T: Clone + std::fmt::Display>(x: &T) {
    let cloned = x.clone();
    println!("Original: {}", x);
    println!("Clone: {}", cloned);
}
#
# fn main() {}
```

`T: Clone + Display` means `T` must implement both `Clone` and `Display`.

### `where` Clauses

When `trait` bounds get long, cramming them into the `<>` gets crowded. Rust offers the `where` clause, placed after the function signature:

```rust,noplayground
fn show_clone<T>(x: &T)
where
    T: Clone + std::fmt::Display,
{
    let cloned = x.clone();
    println!("Original: {}", x);
    println!("Clone: {}", cloned);
}
#
# fn main() {}
```

The two forms are completely equivalent; `where` just reads better.

### `where` Is More Flexible Than Angle Brackets

What sits before the colon in a `where` clause isn't limited to `T` — it can be something more complex, such as a tuple type:

```rust,noplayground
fn clone_pair<T, U>(pair: &(T, U)) -> (T, U)
where
    (T, U): Clone,
{
    pair.clone()
}
#
# fn main() {}
```

`(T, U): Clone` requires the tuple `(T, U)` to be `clone`-able. This form can only appear in a `where` clause, not inside `<>` — that's where `where`'s extra flexibility lies.

## Example Code

```rust,editable
use std::fmt::Display;

// Multiple trait bounds: Clone + Display
// Make a replica with clone, print the original, then return the replica
fn clone_and_show<T: Clone + Display>(x: &T) -> T {
    println!("Cloned: {}", x);
    x.clone()
}

// With a where clause: sometimes more readable
fn show_pair<T, U>(a: &T, b: &U)
where
    T: Display,
    U: Display,
{
    println!("a = {}, b = {}", a, b);
}

fn main() {
    // Multiple trait bounds
    let cloned = clone_and_show(&42);
    println!("The replica received: {}", cloned);

    let cloned2 = clone_and_show(&String::from("hello"));
    println!("The replica received: {}", cloned2);

    // A where clause
    show_pair(&10, &"world");
}
```

## Where Else Can `where` Go

`where` isn't just for functions. It works in many other generic spots, such as `impl` blocks:

```rust,ignore
impl<T> Pair<T>
where
    T: Clone + Display,
{
    // Method definitions
}
```

Furthermore, `where` can appear on `struct`, `enum`, and `trait` definitions too. Just knowing this is enough for now — it'll come back to you when needed.

## Recap

- Combine multiple `trait` bounds with `+`: `T: Clone + Display`.
- The `where` clause is another way to write `trait` bounds — more readable.
- `where` is more flexible than angle brackets: complex types like tuples can precede the colon (e.g. `(T, U): Clone`).
- `where` works beyond functions — on `impl`, `struct`, `enum`, `trait`, anywhere generics go.
