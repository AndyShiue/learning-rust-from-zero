# `RwLock<T>`

## Goal of This Episode

Learn the read-write-separated lock `RwLock<T>`, and how it compares to `Mutex`.

## Concept

### `Mutex`'s Limitation

`Mutex` locks whether you're reading or writing. But often many threads only want to read — reads don't conflict with reads, so locking everything is wasteful.

### `RwLock`: Separating Reads from Writes

`RwLock<T>` distinguishes read locks from write locks:

- **Read lock** (`read().expect(...)`): several threads may hold read locks **simultaneously**.
- **Write lock** (`write().expect(...)`): exclusive — while a write lock is held, no read locks nor other write locks may exist.

```rust,editable
use std::sync::RwLock;

fn main() {
    let lock = RwLock::new(42);

    // Several readers may read at once
    {
        let r1 = lock.read().expect("read lock failed");
        let r2 = lock.read().expect("read lock failed"); // OK: many readers
        println!("r1 = {}, r2 = {}", *r1, *r2);
    }

    // Writing is exclusive
    {
        let mut w = lock.write().expect("write lock failed");
        *w += 1;
    }
}
```

### The Guards' Behavior

The read lock returns an `RwLockReadGuard`; the write lock, an `RwLockWriteGuard`. Like `MutexGuard`, they're smart pointers — operate on the contents directly, unlocking automatically on `drop`.

The same caution applies: don't let guards live long.

### Compared with `RefCell`

|  | `RefCell` | `RwLock` |
|--|-----------|----------|
| Threads | Single-threaded | Multithreaded |
| Rule | Many `borrow()`s or one `borrow_mut()` | Many `read()`s or one `write()` |
| Enforcement | Runtime; violations panic | The OS's lock; violations block and wait |

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

- `RwLock<T>` separates read and write locks: many simultaneous readers, one exclusive writer.
- `read().expect(...)` takes the read lock; `write().expect(...)` the write lock.
- Guards operate on contents via `Deref`, unlocking automatically on `drop`.
- Against `RefCell`: `RefCell` is the single-threaded version; `RwLock` the multithreaded one.
- `Mutex` is simple and cheap — usually enough; `RwLock` suits read-heavy workloads, at higher cost and with writer-starvation risk.
