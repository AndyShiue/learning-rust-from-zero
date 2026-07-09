# `Mutex<T>`

## Goal of This Episode

Learn to let multiple threads safely modify shared data with `Mutex<T>`.

## Concept

### What about Modifying Complex Shared Data?

Last episode's atomics apply only to simple types like integers and booleans. What if several threads should modify a `Vec`, a `String`, or any complex structure?

### `Mutex`: Multithreaded Interior Mutability

`Mutex<T>` somewhat resembles `RefCell` — both provide interior mutability, modifying values without `&mut`. The difference:

- **`RefCell`**: single-threaded, borrow-checking with an ordinary integer.
- **`Mutex`**: multithreaded, guarding the data with an operating-system lock.

### `lock` and `MutexGuard`

Acquire the lock with `mutex.lock().expect("lock failed")`. It returns a `MutexGuard`:

```rust,editable
use std::sync::Mutex;

fn main() {
    let m = Mutex::new(42);
    {
        let mut guard = m.lock().expect("lock failed");
        *guard += 1; // Modify the value through the guard
        println!("{}", *guard); // 43
    } // The guard is dropped; automatic unlock
}
```

`MutexGuard` implements `Deref` and `DerefMut` (from Chapter 5), making it a smart pointer too — usable directly as `&T` or `&mut T`.

Only one thread can `lock` successfully at a time. Other threads calling `.lock()` **block** (wait) until the lock-holding thread `drop`s its guard.

### `Arc` + `Mutex`

In practice they usually pair up — `Arc` lets several threads share the `Mutex`; the `Mutex` guards the data inside:

```rust,editable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().expect("lock failed");
            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("thread panicked");
    }

    println!("Result: {}", *counter.lock().expect("lock failed")); // 10
}
```

### Don't Let the `MutexGuard` Live Long

While the guard lives, the lock stays held, and every other thread waits. So keep the guard's lifespan short:

```rust,ignore
// Bad: the guard lives to scope's end; the lock is held too long
let mut guard = mutex.lock().expect("lock failed");
*guard += 1;
// ... lots of work that doesn't need the lock ...
// The guard only drops way down here

// Good: release when done
{
    let mut guard = mutex.lock().expect("lock failed");
    *guard += 1;
} // The guard drops immediately; the lock releases immediately
// ... other work ...
```

### `Mutex` Turns `Send` into `Sync`

Episode 3 taught `Send` and `Sync`. Some types are `Send` but not `Sync` — Episode 4's `RefCell<T>`, say: safely movable to another thread (`Send`), but not accessible by several threads at once through `&RefCell<T>` (not `Sync`).

`Mutex` solves this. `Mutex<T>` guarantees that only one thread accesses `T` at a time — even with many threads sharing one `&Mutex<T>`, only the lock-holder touches the inner `T`. So `Mutex<T>` requires only `T: Send` for `Mutex<T>` itself to be `Sync`.

Put differently: `T` not being `Sync` is fine — the `Mutex`'s locking already rules out simultaneous access. `T` needs `Send` because: thread A takes the lock, works on `T`, releases; the next lock-taker might be thread B. From `T`'s perspective, it was A's exclusively, now it's B's exclusively — effectively `T` was "shipped" from A to B. Hence `T` must be `Send`.

## Example Code

```rust,editable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            // Shrinking the guard's scope
            {
                let mut num = counter.lock().expect("lock failed");
                *num += 1;
                println!("Thread {} set the counter to {}", i, *num);
            } // The guard drops right here

            // The lock is no longer held here
            println!("Thread {} is done", i);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("thread panicked");
    }

    println!("Final result: {}", *counter.lock().expect("lock failed"));
}
```

## Recap

- `Mutex<T>` is multithreaded interior mutability, guarding data with a lock.
- `lock().expect(...)` returns a `MutexGuard`, usable directly as `&mut T` via `DerefMut`.
- Only one thread holds the lock at a time; the rest wait.
- Dropping the guard unlocks automatically.
- The common pairing: `Arc<Mutex<T>>` — `Arc` for sharing, `Mutex` for safe modification.
- Don't let the `MutexGuard` live long; while locked, every other thread waits.
- `Mutex<T>` needs only `T: Send` to be `Sync` — its locking lets non-`Sync` types be safely shared among threads.
