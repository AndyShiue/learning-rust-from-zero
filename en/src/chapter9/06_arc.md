# `Arc<T>`

## Goal of This Episode

Learn to share data safely among `Thread`s with `Arc<T>`.

## Concept

### The Problem, Recapped

We've said `Rc` can't cross `Thread`s — its reference count isn't atomic. Yet we genuinely need shared data across `Thread`s — what now?

### `Arc`: Atomic Reference Counting

`Arc<T>` is `Rc` with its reference count swapped for **atomic operations**. Atomic operations guarantee that even simultaneous counter updates from multiple `Thread`s never trample each other.

Usage is almost identical to `Rc`:

```rust,editable
use std::sync::Arc;

fn main() {
    let a = Arc::new(String::from("hello"));
    let b = Arc::clone(&a); // Like Rc: clone the pointer; data is shared
    println!("Count = {}", Arc::strong_count(&a)); // 2
}
```

### Sharing across `Thread`s

Move an `Arc::clone` into another `Thread`:

```rust,editable
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3]);

    let data_clone = Arc::clone(&data);
    let handle = thread::spawn(move || {
        println!("Child thread: {:?}", data_clone);
    });

    println!("Main thread: {:?}", data);
    handle.join().expect("thread panicked");
}
```

### `Arc<T>: Send` and `Arc<T>: Sync` Require `T: Send + Sync`

`Arc<T>` itself does not require `T: Send + Sync`. But to send and share an `Arc<T>` between `Thread`s as above, `T` must satisfy both traits. Why?

**`Sync`**: multiple `Thread`s access the same `T` simultaneously through their own `Arc`s. Chapter 5 taught `Deref` — `Arc` implements it, so `T`'s contents are reachable straight through the `Arc`. That amounts to multiple `Thread`s holding shared references to `T` at once, so `T` must be `Sync`.

**`Send`**: when the last `Arc` gets `drop`ped, `T` gets `drop`ped too. Which `Thread` holds the last `Arc` is indeterminate, so `T`'s `drop` may happen on any `Thread` — `T` is effectively "shipped" to that `Thread` for destruction, so `T` must be `Send`.

## Example Code

```rust,editable
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3, 4, 5]);

    let mut handles = vec![];

    for i in 0..3 {
        let data_clone = Arc::clone(&data);
        let handle = thread::spawn(move || {
            let sum: i32 = data_clone.iter().sum();
            println!("The sum thread {} computed: {}", i, sum);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("thread panicked");
    }

    println!("Final count = {}", Arc::strong_count(&data)); // 1
}
```

## Recap

- `Arc<T>` is `Rc<T>`'s multithreaded version, with atomic reference counting.
- Usage nearly matches `Rc`: `Arc::new()`, `Arc::clone()`.
- `Arc::clone` and move the `clone` into other `Thread`s to share data.
- `Arc<T>: Send` and `Arc<T>: Sync` both require `T: Send + Sync`: `Sync` for simultaneous multithreaded access, `Send` because the `drop` may happen on any `Thread`.
