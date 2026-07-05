# `Arc<T>`

## Goal of This Episode

Learn to share data safely among threads with `Arc<T>`.

## Concept

### The Problem, Recapped

We've said `Rc` can't cross threads — its reference count isn't atomic. Yet we genuinely need shared data across threads — what now?

### `Arc`: Atomic Reference Counting

`Arc<T>` is `Rc` with its reference count swapped for **atomic operations**. Atomic operations guarantee that even simultaneous counter updates from multiple threads never trample each other.

Usage is almost identical to `Rc`:

```rust,editable
use std::sync::Arc;

fn main() {
    let a = Arc::new(String::from("hello"));
    let b = Arc::clone(&a); // Bumps the count; no inner data replicated
    println!("Count = {}", Arc::strong_count(&a)); // 2
}
```

### Sharing across Threads

Move an `Arc::clone` into another thread:

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
    handle.join().expect("The thread hit an error");
}
```

### `T` Must Be `Send + Sync`

`Arc` requires `T: Send + Sync`. Why?

**`Sync`**: multiple threads access the same `T` simultaneously through their own `Arc`s. Chapter 5 taught `Deref` — `Arc` implements it, so `T`'s contents are reachable straight through the `Arc`. That amounts to multiple threads holding immutable references to `T` at once, so `T` must be Sync.

**`Send`**: when the last `Arc` gets `drop`ped, `T` gets `drop`ped too. Which thread holds the last `Arc` is indeterminate, so `T`'s `drop` may happen on any thread — `T` is effectively "shipped" to that thread for destruction, so `T` must be `Send`.

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
        handle.join().expect("The thread hit an error");
    }

    println!("Final count = {}", Arc::strong_count(&data)); // 1
}
```

## Recap

- `Arc<T>` is `Rc<T>`'s multithreaded version, with atomic reference counting.
- Usage nearly matches `Rc`: `Arc::new()`, `Arc::clone()`.
- `Arc::clone` and move the clone into other threads to share data.
- `T` must be `Send + Sync`: `Sync` for simultaneous multithreaded access, `Send` because the `drop` may happen on any thread.
