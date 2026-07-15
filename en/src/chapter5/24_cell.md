# `Cell<T>`

## Goal of This Episode

Learn to modify values through shared references with `Cell<T>`, and understand its limitations.

## Concept

Chapter 4 taught the borrowing rules: either one `&mut` or many `&`s, never both at once. Safe — but sometimes, holding only a `&` (shared reference), you still want to modify a value.

### The Idea of `Cell`

`Cell<T>` provides interior mutability — it copies values out with `.get()` and replaces them with `.set(v)`, **no mutable reference required**. It never hands out a reference to the inner value, so it doesn't violate the borrowing rules.

```rust,editable
use std::cell::Cell;

fn main() {
    let x = Cell::new(42);
    x.set(100);              // No mut needed!
    println!("{}", x.get()); // 100
}
```

But `.get()` comes with one important restriction:

### `T` Must Be `Copy` to Use `.get()`

`Cell<T>`'s `.get()` **copies** the value out (rather than borrowing). So `T` must implement `Copy` to use `.get()`.

You can't call `.get()` on a `Cell<String>`, since `String` isn't `Copy`. Only `Copy` types work with `.get()` (`i32`, `f64`, `bool`, etc.).

### Why Not Just Use `mut`?

Sometimes getting a `&mut` isn't convenient. Say a `struct` is shared by reference in several places (`&self`), but you want to bump a counter inside it. `Cell` fits that scenario nicely.

### `Rc` Is Built on `Cell`

Last episode's `Rc<T>` needs a reference counter — +1 on every `clone`, -1 on every `drop`. But look at `Clone`'s signature: `fn clone(&self) -> Self`. It only gets `&self` (a shared reference), yet it must bump the count. How? With `Cell`! The counter inside `Rc` is a `Cell<usize>`, so the count can update even through `&self`.

## Example Code

```rust,editable
use std::cell::Cell;

struct Counter {
    count: Cell<i32>,
    name: String,
}

impl Counter {
    fn new(name: String) -> Counter {
        Counter {
            count: Cell::new(0),
            name,
        }
    }

    // Note: only &self needed, not &mut self
    fn increment(&self) {
        let current = self.count.get();
        self.count.set(current + 1);
    }

    fn get_count(&self) -> i32 {
        self.count.get()
    }
}

fn main() {
    // Basic usage
    let x = Cell::new(42);
    println!("Original value: {}", x.get());

    x.set(100);
    println!("After modifying: {}", x.get());

    // Using Cell inside a struct
    let counter = Counter::new(String::from("visit count"));

    // Only &counter (a shared reference), yet count can be modified
    counter.increment();
    counter.increment();
    counter.increment();

    println!("Count for {}: {}", counter.name, counter.get_count());
}
```

## Recap

- `Cell<T>` lets you modify a value without needing `&mut`.
- `.get()` copies the value out; `.set(v)` writes a new one.
- **`T` must be `Copy` to use `.get()`** — because `get` copies rather than borrows.
- Great for "I only have `&self` but want to modify a field" scenarios.
