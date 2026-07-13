# `move` Closures

## Goal of This Episode

Learn to force a closure to capture outer variables by value with the `move` keyword, and understand when that fixes lifetime problems.

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

`move` tells Rust to capture every used outer variable **by value**. Here, the closure captures the `String` itself, so `name` now belongs to the closure; however the original scope ends, the closure keeps its `name`.

### The Anonymous `struct` of a move Closure

Recall recent episodes — a closure is an anonymous `struct`. Without `move`, the `struct`'s fields may be references to outer variables (`&T` or `&mut T`); with `move`, the closure captures those variables **by value**:

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

In this example, the captured variable is a `String`, so the closure owns the string and no longer borrows the local variable `name`. That is why it can be returned from the function safely.

But capturing by value does not turn a reference into an owned version of the data it points to. If the captured variable is itself a reference, the closure stores that reference unchanged:

```rust,editable
fn make_printer<'a>(text: &'a str) -> impl Fn() + 'a {
    // text itself is an &'a str; move captures that reference by value
    move || println!("{}", text)
}

fn main() {
    let message = String::from("hello");
    let print = make_printer(&message);
    print();
}
```

Here `text` is an `&'a str`. Since shared references are `Copy`, `move` copies that reference value into the closure; it does not give the closure ownership of the string data. In the `struct` analogy, the closure's field is still `text: &'a str`. The `+ 'a` on the return type makes this lifetime relationship explicit: when `text` refers to a local string, the returned closure cannot be used after that string is dropped. In other words, `move` does not automatically make a closure `'static`.

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

Until now, we've mostly treated closures as things you call. There wasn't a good place to ask a different ownership question: can the closure value itself be moved, copied, or `clone`d?

This episode is finally about ownership around closures, so this is the right place to answer that. Moving a closure value is allowed like moving other values, but whether it can be copied or `clone`d depends on what it captures — much like a tuple: if everything inside is copyable, the whole is:

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

- `move` forces the closure to capture every used outer variable by value. If a captured variable is itself a reference, it remains a reference and keeps its lifetime.
- Returning a closure often requires `move` so it captures local variables by value, but any references captured by value must still live long enough.
- `move` **does not affect** whether the closure is `FnOnce` / `FnMut` / `Fn` — that depends on **how it uses** the captured values.
- Whether a closure can `clone` / copy depends on whether all its captures are `Clone` / `Copy`.
