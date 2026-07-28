# Poisoning

## Goal of This Episode

Understand what lock poisoning is, and how to handle it.

## Concept

### Why `.lock()` Returns a `Result`

Learning `Mutex` and `RwLock` in recent episodes, we always wrote `.lock().expect("lock failed")`. But when can acquiring the lock "fail"? The answer: **poisoning**.

### What Is Poisoning

If a `Thread` panics while holding a `Mutex` lock or an `RwLock` write lock, the lock gets marked "poisoned." Every later attempt to take the lock — `Mutex::lock`, or the `RwLock`'s `read` or `write` — receives `Err(PoisonError)`.

```rust,editable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let data = Arc::new(Mutex::new(vec![1, 2, 3]));
    let data2 = Arc::clone(&data);

    let handle = thread::spawn(move || {
        let mut guard = data2.lock().expect("lock failed");
        guard.push(4);
        panic!("Oops!"); // The guard is alive at the panic → the lock is poisoned
    });

    let _ = handle.join(); // Collect the panic; don't let it propagate

    // A later lock → Err
    match data.lock() {
        Ok(guard) => println!("Normal: {:?}", *guard),
        Err(poisoned) => println!("The lock is poisoned!"),
    }
}
```

### Why Poisoning Exists

A panic usually means an unexpected error. If a `Thread` panics halfway through modifying data, that data may be a half-finished product — a `Vec` mid-`push`, or two fields with only one updated. Poisoning is a safety mechanism: it tells you something went wrong, and lets you decide whether to keep using the data.

### Three Ways to Handle It

**1. Panic outright (the most common)**

```rust,noplayground
use std::sync::Mutex;

fn main() {
    let data = Mutex::new(Vec::<i32>::new());
    let guard = data.lock().expect("lock failed");
}
```

If the lock is poisoned, your `Thread` panics too. Usually that's fine — the previous `Thread` panicking generally means the whole program should end.

**2. Ignore the poison and carry on**

```rust,noplayground
use std::sync::{Mutex, PoisonError};

fn main() {
    let data = Mutex::new(Vec::<i32>::new());
    let guard = data.lock().unwrap_or_else(PoisonError::into_inner);
}
```

`PoisonError::into_inner` hands back the guard, skipping the poison warning. If you're sure the data's state is fine, or don't care, this works.

Note that this is a "**write it this way at every lock site**" approach: the lock itself stays poisoned throughout; you simply ignore it every time. If one place in the program forgets and reaches for a plain `lock().expect(...)`, that place panics.

**3. Repair the data, then continue**

```rust,noplayground
use std::sync::{Mutex, PoisonError};

fn main() {
    let data = Mutex::new(Vec::<i32>::new());
    let guard = match data.lock() {
        Ok(g) => g,
        Err(poisoned) => {
            let mut g = poisoned.into_inner();
            *g = vec![];         // Reset to a known-safe state
            data.clear_poison(); // Clear the poison so later locks work again
            g
        }
    };
}
```

Take the guard, restore the data to a sensible value, then proceed.

Option 2 can ignore the poison indefinitely because every lock site is written the same way. Option 3 means something different: repair the data, then go back to running normally. Repairing the data isn't enough for that — every plain `lock()` elsewhere in the program still comes back `Err` — so the repair is followed by `clear_poison()`, which is what actually clears it (`RwLock` has a method of the same name).

### Why `.into_inner()` Is Safe

You might wonder: the data in a poisoned lock may be half-finished — is touching it really okay?

From memory's standpoint, yes. Poisoned or not, the data inside is valid memory — no touching memory that's no longer usable, no type confusion, no data races. Poisoning protects **logical consistency**, not **memory safety**. The data may be logically wrong, yet perfectly legal from memory's perspective. Hence `.into_inner()` can be called safely.

### `RwLock`'s Poisoning

`RwLock` poisons only when a **write lock** panics. A panicking read lock doesn't poison — reading modifies nothing and leaves no inconsistent state behind. But once poisoned, both `read` and `write` return `Err`.

## Example Code

```rust,editable
use std::sync::{Arc, Mutex, PoisonError};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));

    // Launch a thread that panics
    let counter2 = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut guard = counter2.lock().expect("lock failed");
        *guard += 1;
        panic!("Uh-oh, something broke!");
    });

    // Wait for that thread (it panics, but let _ ignores it)
    let _ = handle.join();

    // Try to take the lock — a PoisonError arrives
    match counter.lock() {
        Ok(guard) => {
            println!("Lock acquired normally, value = {}", *guard);
        }
        Err(poisoned) => {
            println!("The lock is poisoned!");

            // Take a look at the data
            let guard = poisoned.into_inner();
            println!("The value inside = {}", *guard);
        }
    }

    // Or ignore the poison in one line
    let guard = counter.lock().unwrap_or_else(PoisonError::into_inner);
    println!("Ignoring the poison, value = {}", *guard);
}
```

## Recap

- A `Thread` panics while holding a `Mutex` lock or an `RwLock` write lock → the lock is poisoned.
- Afterward `lock` / `read` / `write` all return `Err(PoisonError)`.
- `RwLock` poisons only on a write-lock panic; read-lock panics don't.
- `PoisonError::into_inner` recovers the guard — memory safety is intact; only logical consistency is in question.
- Three handling options:
  - Panic (`.unwrap()` or `.expect()`).
  - Ignore (`.unwrap_or_else(PoisonError::into_inner)`).
  - Repair the data and continue (`into_inner` doesn't clear the poison; you also need `clear_poison()` for a real recovery).
