# `LazyLock`

## Goal of This Episode

Learn to lazily initialize global variables with `LazyLock`.

## Concept

Strictly speaking, `LazyLock` is a standard-library utility, not a language feature. But since we just learned `static`, and it's the thing most often paired with `static`, we cover it here.

### The Problem: A `static`'s Value Must Be Known at Compile Time

A `static`'s value must be computable at compile time. An empty `Vec::new()` is fine (it's a `const fn` and allocates no memory), but what if you want a `Vec` that **already has contents**?

```rust,compile_fail
// the vec! macro and String::from both need to allocate memory at runtime
static NAMES: Vec<String> = vec![String::from("Alice"), String::from("Bob")];
#
# fn main() {}
```

So what now? If we can't provide the value at compile time, then **don't provide it yet** — initialize it the first time it's used at runtime. That's lazy initialization.

### `LazyLock`

`std::sync::LazyLock` does exactly this — you give it a closure, it runs the closure to produce the value only on first access, and every access after that uses the cached result. `LazyLock` implements `Deref`, so you can treat it directly as the value inside, just like `Box`, `Rc`, and the other smart pointers:

```rust,editable
use std::sync::LazyLock;

static NAMES: LazyLock<Vec<String>> = LazyLock::new(|| {
    vec![String::from("Alice"), String::from("Bob")]
});

fn main() {
    println!("{:?}", *NAMES); // first time: runs the closure
    println!("{}", NAMES[0]); // afterwards: uses the cache
}
```

### Why It's Called `LazyLock`

- **`Lazy`**: doesn't initialize until it's needed.
- **`Lock`**: there's a lock inside, so concurrent access from multiple `Thread`s initializes only once (thread-safe).

## Example Code

```rust,editable
use std::sync::LazyLock;

static NAMES: LazyLock<Vec<String>> = LazyLock::new(|| {
    println!("initializing NAMES!");
    vec![String::from("Alice"), String::from("Bob"), String::from("Charlie")]
});

fn print_first() {
    println!("first name: {}", NAMES[0]);
}

fn main() {
    println!("program start");
    print_first(); // first access — initialization happens now
    print_first(); // second access — straight from the cache
    println!("{} names total", NAMES.len());
}
```

## Recap

- A `static` initializer must be computable at compile time; operations such as building a populated `Vec` or calling `String::from` require runtime initialization.
- `LazyLock` postpones initialization to the first access and caches afterwards.
- `LazyLock` is thread-safe and can be used safely in a `static`.
