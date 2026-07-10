# `Send` / `Sync`

## Goal of This Episode

Understand how Rust guarantees at compile time that types are safe to use across threads.

## Concept

### Why Extra Protection Is Needed

Remember the keychain analogy that opened Chapter 4? By now you can see that the key is a pointer.

One reason Rust has ownership rules and borrowing rules — no two `&mut`s at once, for example — is to keep one address's value from being read and written simultaneously, causing the **data race** mentioned before. A concrete example: suppose an `i32` holds 0, and threads A and B each add 1 to it through pointers. You expect 2, but reality might go:

1. Thread A reads the value: 0.
2. Thread B reads it too: 0.
3. Thread A writes back 0 + 1 = 1.
4. Thread B also writes back 0 + 1 = 1.

The result is 1, not 2. Two increments, only one took effect.

Note the crux: two threads reading and writing the same data simultaneously — in fact, whenever data is shared and someone is writing, trouble looms. Even a party that's merely reading might read data whose write hasn't fully finished.

Rust's ownership and borrowing rules prevent many problems — no two `&mut`s at once, no `&` alongside `&mut`. But under multithreading, they alone don't suffice. Take the example above: merely passing an `i32`'s value to another thread is fine — `i32` is `Copy`, a duplicate goes over, and each side works on its own copy. But some types aren't so simple — after moving one over, the original thread might still hold shared data. Which types can cross threads safely? Which can't? Rust answers with two `trait`s — `Send` and `Sync`.

### What spawn Actually Does

Last episode, creating threads with `thread::spawn`, we passed a closure. Closures capture outside variables — and `spawn` in effect **ships those captured variables to another thread**. That's the real question: what can be shipped safely?

### `Send`

A type implementing `Send` means its values can safely move to another thread. Most types are `Send` — `i32`, `String`, `Vec<T>` (when `T` is `Send`), and so on.

### `Sync`

A type implementing `Sync` means its `&T` (shared reference) can safely be shared among threads. In other words:

> `T: Sync` is equivalent to `&T: Send`

If `&T` can be shipped safely to another thread, `T` is `Sync`.

### `Sync` Usually Implies `Send`

If something can be read by many threads at once without trouble (`Sync`), then moving it wholesale to another thread — eliminating even the possibility of simultaneous reads — can usually only be safer. So most `Sync` types are `Send` too, with a few exceptions.

### `auto trait`s: `trait`s the Compiler Implements for You

You never implement `Send` or `Sync` by hand. They're **`auto trait`s** — the compiler implements them for your types automatically. The rule is simple: if everything a type stores is `Send`, the type itself defaults to `Send`. Same for `Sync`.

```rust,noplayground
struct MyData {
    x: i32,    // Send + Sync
    s: String, // Send + Sync
}
// MyData is automatically Send + Sync
#
# fn main() {}
```

### No Memorizing Required

You needn't memorize which types are `Send` or `Sync`. Toss an unsafe type into `thread::spawn` and the compiler tells you outright:

```rust,compile_fail
use std::rc::Rc;
use std::thread;

fn main() {
    let data = Rc::new(42);
    thread::spawn(move || {
        println!("{}", data);
    });
    // Compile error! Rc<i32> is not Send
}
```

### Back to `spawn`'s Type Signature

Knowing `Send` and `Sync`, we can revisit `thread::spawn`'s signature:

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
where
    F: FnOnce() -> T + Send + 'static,
    T: Send + 'static,
```

The closure `F` must be `Send` — a closure's type includes whatever it captured, so a non-`Send` capture makes the closure non-`Send` and `spawn` fails to compile. The return value `T` must be `Send` too, since the result travels back from the child thread.

And that `'static` — why? Because we have no idea how long a `spawn`ed thread lives. You might `join` it; you might not, letting it run until `main` ends and it's forcibly terminated. Rust's type system can't guarantee you'll `join` at any particular moment, so it demands the most conservative guarantee: nothing in the closure or return value may hold a borrow that could expire. Chapter 5 Episode 29 taught lifetime bounds — `T: 'a` means every reference in `T` outlives `'a`. `F: 'static` is that concept's extreme: references inside the closure must live as long as the whole program. In practice, the usual answer is last episode's `move` — with values moved into the closure, it borrows nothing, satisfying `'static` naturally.

## Example Code

```rust,editable
use std::thread;

// All this struct's fields are Send + Sync,
// so it's automatically Send + Sync
struct Config {
    name: String,
    max_retries: u32,
}

fn main() {
    let config = Config {
        name: String::from("my_app"),
        max_retries: 3,
    };

    // Config is Send; it can safely move to another thread
    let handle = thread::spawn(move || {
        println!("Config name: {}", config.name);
        println!("Max retries: {}", config.max_retries);
    });

    handle.join().expect("thread panicked");
}
```

## Recap

- Data race: several threads accessing the same data at once with at least one writing — unpredictable results.
- `thread::spawn`'s closure ships its captures to another thread, so those variables must be `Send`.
- `Send` = the value can safely move to another thread.
- `Sync` = `&T` can safely be shared among threads (`T: Sync` equals `&T: Send`).
- `Sync` usually implies `Send` — what many threads may read at once is only safer moved.
- The compiler derives `Send` / `Sync` automatically; no manual marking.
