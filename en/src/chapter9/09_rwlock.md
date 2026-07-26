# `RwLock<T>`

## Goal of This Episode

Learn the read-write-separated lock `RwLock<T>`, and how it compares to `Mutex`.

## Concept

### `Mutex`'s Limitation

`Mutex` locks whether you're reading or writing. But often many `Thread`s only want to read — reads don't conflict with reads, so locking everything is wasteful.

### `RwLock`: Separating Reads from Writes

`RwLock<T>` distinguishes read locks from write locks:

- **Read lock** (`.read().expect(...)`): several `Thread`s may hold read locks **simultaneously**.
- **Write lock** (`.write().expect(...)`): exclusive — while a write lock is held, no read locks nor other write locks may exist.

"Several readers at once" is not something a single `Thread` can demonstrate; this episode's example code at the end will show it with three `Thread`s. For now, just how the two locks are taken:

```rust,editable
use std::sync::RwLock;

fn main() {
    let lock = RwLock::new(42);

    // Read lock: look, don't touch
    {
        let r = lock.read().expect("read lock failed");
        println!("read {}", *r);
    } // r drops here, releasing the read lock

    // Write lock: exclusive, and you may modify
    {
        let mut w = lock.write().expect("write lock failed");
        *w += 1;
    } // w drops here, releasing the write lock

    println!("now {}", *lock.read().expect("read lock failed"));
}
```

### The Guards' Behavior

The read lock returns an `RwLockReadGuard`; the write lock, an `RwLockWriteGuard`. Like `MutexGuard`, they're smart pointers — operate on the contents directly, unlocking automatically on `drop`.

The same caution applies: don't let guards live long.

### Compared with `RefCell`

|  | `RefCell` | `RwLock` |
|--|-----------|----------|
| `Thread`s | Single-threaded | Multithreaded |
| Rule | Many `borrow()`s or one `borrow_mut()` | `read()`s from many `Thread`s, or one `write()` |
| Enforcement | Runtime; violations panic | The OS's lock; violations block and wait |

There is one trap `RefCell` doesn't have, though: `RefCell` lets you `borrow()` several times on the same `Thread`, but `RwLock`'s "many readers" means **many `Thread`s**. Taking a second read lock on the same `RwLock` from the same `Thread` **may panic** — the standard library says so outright — and on some platforms it can hang outright.

### `Mutex` vs `RwLock`

Which when?

- **`Mutex`**: simple, low overhead. Suits frequent reads-and-writes, or very short lock holds. `Mutex` suffices most of the time.
- **`RwLock`**: advantageous when reads far outnumber writes, since readers proceed simultaneously. But the lock itself costs more than a `Mutex`, and there's the risk of **writer starvation** — with readers streaming in endlessly, a writer may never get the lock.

## Example Code

```rust,editable
use std::sync::{Arc, RwLock};
use std::thread;

fn main() {
    let data = Arc::new(RwLock::new(vec![1, 2, 3]));

    let mut handles = vec![];

    // Launch 3 readers
    for i in 0..3 {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            let read_guard = data.read().expect("read lock failed");
            println!("Reader {}: {:?}", i, *read_guard);
            // Several readers may hold read locks at once
        });
        handles.push(handle);
    }

    // Launch 1 writer
    {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            let mut write_guard = data.write().expect("write lock failed");
            write_guard.push(4);
            println!("Writer: write complete; it's now {:?}", *write_guard);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("thread panicked");
    }

    println!("Final result: {:?}", *data.read().expect("read lock failed"));
}
```

## Recap

- `RwLock<T>` separates read and write locks: many `Thread`s may read simultaneously, one exclusive writer.
- `.read().expect(...)` takes the read lock; `.write().expect(...)` the write lock.
- Guards operate on contents via `Deref`, unlocking automatically on `drop`.
- Against `RefCell`: `RefCell` is the single-threaded version; `RwLock` the multithreaded one.
- Don't take a second read lock on the same `RwLock` from the same `Thread` — it isn't `RefCell`'s `borrow()`; it may panic or hang.
- `Mutex` is simple and cheap — usually enough; `RwLock` suits read-heavy workloads, at higher cost and with writer-starvation risk.
