# `move` Closures

## Goal of This Episode

Learn to force a closure to capture outer variables by move with the `move` keyword, and understand why that fixes lifetime problems.

## Concept

### The Default Capture Behavior

Rust's closures are clever, automatically picking the "lightest" way to capture:

- Only reading a variable → capture by `&T` (borrow).
- Needing to modify → by `&mut T` (mutable borrow).
- Needing to consume → by `T` (move).

Usually that's great. But sometimes borrowing creates lifetime problems.

### The Problem Scenario: Returning a Closure

Suppose you want a function that returns a closure:

```rust,compile_fail
fn make_greeter(name: String) -> impl Fn() {
    || println!("Hello, {}!", name) // Compile error!
}
#
# fn main() {}
```

This does not compile because the closure captures `name` by borrow (`&name`) by default, but `name` is a local variable of the function, discarded when the function ends. The borrow inside the closure becomes a dangling reference — our old friend from Chapter 4.

### The move Keyword

Adding `move` solves it:

```rust,editable
fn make_greeter(name: String) -> impl Fn() {
    move || println!("Hello, {}!", name)
}

fn main() {}
```

`move` tells Rust: "Don't borrow — **move** every captured variable into the closure." Now `name` belongs to the closure; however the original scope ends, the closure keeps its `name`.

### The Anonymous struct of a move Closure

Recall recent episodes — a closure is an anonymous `struct`. Without `move`, the `struct`'s fields may be references (`&T` or `&mut T`); with `move`, **every field becomes an owned value** (`T`):

```rust,noplayground
# fn main() {
    // Without move: the closure borrows name; the struct stores a reference
    let name = String::from("Alice");
    let greet = || println!("{}", name);
    // name stays usable, since the closure only borrows

    // With move: name is moved into the struct; the closure owns it
    let name = String::from("Alice");
    let greet = move || println!("{}", name);
    // name can't be used anymore; it's been moved into the closure
# }
```

With every field owned, the `struct` borrows nothing, so there's no lifetime issue — it can be returned from functions and stored in `struct`s safely.

### `move` Doesn't Affect Which `Fn` `trait` the Closure Gets

A common confusion: a `move` closure is not automatically `FnOnce`!

`move` affects only **how it captures**, not **how it uses**:

```rust,editable
fn main() {
    let name = String::from("Alice");
    let greet = move || println!("Hello, {}!", name);
    // name was moved into the closure, but the closure only "reads" name
    // So this closure is Fn, callable repeatedly
    greet();
    greet();
}
```

### The `trait`s Closures Implement Automatically

Whether a closure can `clone` or copy depends on its captured variables — much like a tuple: if everything inside is copyable, the whole is:

- All captured variables `Copy` → the closure is `Copy` too.
- All captured variables `Clone` → the closure is `Clone` too.
- The same holds for certain other `trait`s.

```rust,editable
fn main() {
    let x = 42;
    let f = move || x + 1; // x is i32 (Copy), so f is Copy too
    let g = f; // f was copied
    println!("{}", f()); // f is still usable
    println!("{}", g());
}
```

## Example Code

```rust,editable
// Returning a closure usually needs move
fn make_adder(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

fn make_counter(start: i32) -> impl FnMut() -> i32 {
    let mut count = start;
    move || {
        count += 1;
        count
    }
}

fn main() {
    // move gives the closure ownership of its captures, safe to return
    let add_five = make_adder(5);
    println!("10 + 5 = {}", add_five(10));
    println!("20 + 5 = {}", add_five(20));

    // move + FnMut: the closure owns count and modifies it each time
    let mut counter = make_counter(0);
    println!("Count: {}", counter());
    println!("Count: {}", counter());
    println!("Count: {}", counter());

    // move doesn't mean FnOnce
    let name = String::from("Bob");
    let greet = move || {
        println!("Hi, {}!", name); // Only reads name, so it's Fn
    };
    greet();
    greet(); // Repeatable calls — not FnOnce

    // A closure capturing Copy types can be Copied
    let factor = 3;
    let multiply = move |x: i32| x * factor;
    let multiply_copy = multiply; // Copied
    println!("multiply(4) = {}", multiply(4)); // The original still works
    println!("multiply_copy(4) = {}", multiply_copy(4));

    // A move closure capturing a String (non-Copy) can't be Copied
    let label = String::from("result");
    let show = move |x: i32| {
        println!("{}: {}", label, x);
    };
    // let show2 = show; // This would move show — not a Copy
    show(42);
}
```

## Recap

- `move` forces the closure to take ownership of every capture, independent of outside borrows — suited to long-lived scenarios.
- Returning a closure usually requires `move`, avoiding dangling references.
- `move` **does not affect** whether the closure is `Fn` / `FnMut` / `FnOnce` — that depends on **how it uses** the captured values.
- Whether a closure can `clone` / copy depends on whether all its captures are `Clone` / `Copy`.
