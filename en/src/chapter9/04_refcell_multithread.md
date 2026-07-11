# `RefCell` under Multithreading

## Goal of This Episode

Understand why interior mutability is dangerous under multithreading, and `RefCell`'s `Send` / `Sync` characteristics.

## Concept

### Interior Mutability Is a Major Multithreading Threat

Chapter 5 taught that `RefCell` can modify its inner value through `&T` (a shared reference). In the single-threaded world, `RefCell` checks the borrowing rules at runtime and stays out of trouble.

The multithreaded world is different. `&T` looks "read-only," and `Sync`'s very definition is that `&T` can safely be shared among `Thread`s. If a type can sneak modifications through `&T`, several `Thread`s doing so at once can go wrong.

### `RefCell`'s Borrow Count Isn't Atomic

`RefCell` tracks its current borrow state (how many immutable borrows; any mutable borrow) with an ordinary integer. Operations on that counter aren't **atomic**. An atomic operation is indivisible — no other `Thread` can ever see a halfway state. `RefCell`'s counter doesn't provide this guarantee, so two `Thread`s could both read the same old value before either updates it. If two `Thread`s call `borrow_mut()` through `&RefCell<T>` simultaneously, this can happen:

1. `Thread` A calls `borrow_mut()`, reads the counter, sees 0 (nobody borrowing).
2. `Thread` B calls `borrow_mut()` too, reads the counter, also sees 0.
3. `Thread` A concludes "nobody's borrowing; the mutable borrow is mine," setting the counter to "mutably borrowed."
4. `Thread` B also concludes "nobody's borrowing" — its step-2 read was the stale value — and takes a mutable borrow too.

Result: two `Thread`s holding mutable borrows at once. `RefCell`'s runtime check was bypassed entirely.

### `RefCell` Is Not `Sync`

For the reason above, `RefCell` isn't `Sync` — `&RefCell<T>` can't be shared among `Thread`s. Try, and the compiler blocks you.

### `RefCell<T>` Is `Send` When `T: Send`

`RefCell<T>` can be **moved** to another `Thread` as long as `T` itself is `Send`. After the move, that one `Thread` alone owns the `RefCell` — no multiple `Thread`s operating simultaneously.

```rust,editable
use std::cell::RefCell;
use std::thread;

fn main() {
    let data = RefCell::new(vec![1, 2, 3]);

    // OK: RefCell<Vec<i32>> is Send; it can move to another thread
    let handle = thread::spawn(move || {
        data.borrow_mut().push(4);
        println!("{:?}", data.borrow());
    });

    handle.join().expect("thread panicked");
}
```

## Example Code

```rust,editable
use std::cell::RefCell;
use std::thread;

fn main() {
    // RefCell<String> can move to another thread (Send)
    let data = RefCell::new(String::from("hello"));

    let handle = thread::spawn(move || {
        // Within this thread, the RefCell works normally
        data.borrow_mut().push_str(" world");
        println!("Child thread: {}", data.borrow());
    });

    handle.join().expect("thread panicked");

    // But &RefCell can't be shared among threads (not Sync)
    // Try to have two threads share one RefCell, and the compiler stops you.
}
```

## Recap

- Interior mutability lets `&T` modify contents — dangerous under multithreading.
- Atomic operation = an indivisible operation: no other `Thread` can see a halfway state.
- `RefCell`'s `borrow` count is an ordinary integer, not atomic; simultaneous multithreaded operations can bypass the check.
- `RefCell` is not `Sync` — `&RefCell<T>` can't be shared among `Thread`s.
- `RefCell<T>` is `Send` when `T: Send` — it can then move to another `Thread`, which owns it alone.
