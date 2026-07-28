# A Brief Introduction to `thread::scope`

## Goal of This Episode

Learn to create bounded-lifetime `Thread`s with `thread::scope`, borrowing outside data without `move` or `Arc`.

## Concept

### `thread::spawn`'s Limitation

Using `thread::spawn` earlier, outside variables had to be `move`d into the closure or wrapped in `Arc`. That's because a `spawn`ed `Thread` may outlive the function that called it — Rust can't guarantee the data survives until the `Thread` finishes.

### Why `spawn` Can't Borrow

Episode 3 examined `thread::spawn`'s type signature: the closure and return value both demand `'static` — living as long as the whole program. That's why local variables can't be borrowed: references to locals aren't `'static`.

### `thread::scope`

`thread::scope` solves this. It guarantees every `Thread` `spawn`ed inside gets `join`ed before the `scope` ends:

```rust,editable
use std::thread;

fn main() {
    let data = vec![1, 2, 3, 4, 5];

    thread::scope(|s| {
        s.spawn(|| {
            println!("Child thread: {:?}", data); // Borrowed directly — no move needed
        });
    }); // Every scoped thread is guaranteed finished by here

    // data remains usable
    println!("Main thread: {:?}", data);
}
```

Since `scope` guarantees all `Thread`s finish before the `}`, `data` can't be discarded early — the closure borrows it safely, needing neither `move` nor `Arc`.

### Compared with the `spawn` + `Arc` Style

The same job with `thread::spawn` reads:

```rust,editable
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3, 4, 5]);
    let data_clone = Arc::clone(&data);

    let handle = thread::spawn(move || {
        println!("{:?}", data_clone);
    });

    handle.join().expect("thread panicked");
}
```

With `thread::scope`, far cleaner:

```rust,editable
use std::thread;

fn main() {
    let data = vec![1, 2, 3, 4, 5];

    thread::scope(|s| {
        s.spawn(|| {
            println!("{:?}", data);
        });
    });
}
```

No `Arc`, no `clone`, no `move`, no manual `join`.

## Example Code

```rust,editable
use std::thread;

fn main() {
    let mut results = vec![];
    let input = vec![1, 2, 3, 4, 5];

    thread::scope(|s| {
        // Several threads borrowing input simultaneously (immutable borrows)
        let h1 = s.spawn(|| {
            let sum: i32 = input.iter().sum();
            sum
        });

        let h2 = s.spawn(|| {
            let max = input.iter().max().expect("empty input");
            *max
        });

        let h3 = s.spawn(|| {
            let min = input.iter().min().expect("empty input");
            *min
        });

        // Inside the scope, join retrieves return values too
        results.push(h1.join().expect("thread panicked"));
        results.push(h2.join().expect("thread panicked"));
        results.push(h3.join().expect("thread panicked"));
    });

    println!("input is still usable: {:?}", input);
    println!("Sum = {}, max = {}, min = {}", results[0], results[1], results[2]);
}
```

## Recap

- `thread::spawn` demands `'static`, so its closure can't borrow locals.
- `thread::scope` guarantees every scoped `Thread` `join`s before the `scope` ends, so outside data can be borrowed safely.
- No `move`, no `Arc`, no manual `join` — far cleaner code.
- When multithreading is needed only within one region, `thread::scope` beats `thread::spawn` for convenience.

Congratulations on finishing the multithreading chapter! 🎉 Starting from the low-level notion of pointers, this chapter worked through `Thread`s, `Send` / `Sync`, `Arc`, `Mutex`, `RwLock`, poisoning, channels, and `thread::scope`. In many languages, multithreaded programming is headache territory, but Rust's type system blocks data races at compile time — no relying on experience and intuition to dodge bugs; the compiler is your best teammate. Next chapter: advanced language features!
