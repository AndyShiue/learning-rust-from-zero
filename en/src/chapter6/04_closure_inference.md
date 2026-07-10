# How Closure Kinds Are Inferred

## Goal of This Episode

Understand how Rust automatically infers whether a closure is `FnOnce`, `FnMut`, or `Fn` from the closure body's contents.

## Main Text

Last episode we hand-simulated the three closure kinds with `struct`s, corresponding to `self`, `&mut self`, and `&self`. Yet when writing closures you never tell Rust "this is `FnOnce`" or "this is `FnMut`" — Rust decides automatically.

### The Inference Rules

Rust looks at **what the closure body does with the captured variables**:

1. **If the body moves a captured variable** (e.g. `let s = captured_string;`) → the closure is **`FnOnce`** — once moved, it's gone; one call only.
2. **If the body needs mutable access to its captured state** (e.g. `count += 1;`) → the closure is **`FnMut`** — repeatable calls, but needing `&mut`.
3. **If the body only needs shared access to its captured state** (e.g. `println!("{}", name);`) → the closure is **`Fn`** — only `&self` needed.

Rust picks **the kind permitting the most usage patterns** — shared access gets `Fn` (an `Fn` closure also works as `FnMut` and `FnOnce`). Needing mutable access makes it `FnMut`. A move makes it `FnOnce`.

### Examples Side by Side

```rust,noplayground
# fn main() {
    let name = String::from("Alice");

    // Only reads name → Fn
    let greet = || println!("Hi, {}!", name);

    // Modifies count → FnMut
    let mut count = 0;
    let mut increment = || { count += 1; };

    // Moves name → FnOnce
    let consume = || { let s = name; };
# }
```

No markers needed — Rust reads the closure body and knows.

### What about Capturing Several Variables?

A closure may capture several variables at once, using each differently:

```rust,noplayground
# fn main() {
    let name = String::from("Alice");
    let mut count = 0;
    let closure = || {
        count += 1;           // Modifies count → needs &mut
        println!("{}", name); // Only reads name → needs just &
    };
# }
```

Pictured as a `struct`, this closure's anonymous `struct` has two fields: `count` (needing `&mut`) and `name` (needing only `&`). But a closure call has just one `self` — and `&mut self` can perform `&` operations, though not vice versa — so the whole closure is `FnMut` (`&mut self`). Just like a method taking `&mut self` that doesn't necessarily modify every field:

```rust,noplayground
struct Data<'a> {
    count: &'a mut i32,
    name: &'a String,
}

impl<'a> Data<'a> {
    fn increment_and_greet(&mut self) {
        *self.count += 1;                  // Modifies count
        println!("Hello, {}!", self.name); // Only reads name
    }
}
#
# fn main() {}
```

Closures work the same way.

Likewise, `FnOnce`'s `self` can of course take `&` or `&mut` of the values inside — owning a value includes being able to borrow it.

### What If Nothing Is Captured?

A capture-free closure is automatically `Fn`, since it needs no outside state:

```rust,noplayground
# fn main() {
    let add_one = |x: i32| x + 1; // Fn
# }
```

Episode 2's note that "capture-free closures convert to function pointers" follows from this too — such a closure doesn't even need the anonymous `struct`.

## Recap

- Rust infers a closure's kind from its body: move → `FnOnce`, mutable access → `FnMut`, shared access → `Fn`.
- No manual markers; the compiler picks the kind permitting the most usage patterns.
- Capture-free closures are `Fn`, convertible to function pointers.
- An `Fn` closure can go where `FnMut` or `FnOnce` is wanted; `FnMut` can go where `FnOnce` is wanted; never the reverse.
