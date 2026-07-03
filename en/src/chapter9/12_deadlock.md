# Deadlocks

## Goal of This Episode

Understand what a deadlock is, why Rust's compiler can't stop it, and how to avoid it.

## Concept

### What's a Deadlock

A deadlock is two or more threads waiting for each other to release locks — nobody can move, and the program hangs forever.

The classic case: thread A holds lock 1 while waiting for lock 2; thread B holds lock 2 while waiting for lock 1. Both wait forever.

### A Code Demonstration

```rust,ignore,mdbook-runnable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let lock1 = Arc::new(Mutex::new(0));
    let lock2 = Arc::new(Mutex::new(0));

    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);

    let a = thread::spawn(move || {
        let _g1 = l1.lock().expect("Failed to acquire the lock"); // Takes lock 1
        // Imagine some delay here...
        let _g2 = l2.lock().expect("Failed to acquire the lock"); // Waits for lock 2
    });

    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);

    let b = thread::spawn(move || {
        let _g2 = l2.lock().expect("Failed to acquire the lock"); // Takes lock 2
        // Imagine some delay here...
        let _g1 = l1.lock().expect("Failed to acquire the lock"); // Waits for lock 1
    });

    // With unlucky timing, the program hangs here forever
    a.join().expect("The thread hit an error");
    b.join().expect("The thread hit an error");
}
```

Thread A takes lock 1 first, then wants lock 2. But lock 2 belongs to thread B, which is waiting for lock 1 — nobody can advance.

### The Compiler Doesn't Block Deadlocks

`Send` and `Sync` protect against **data races** — undefined behavior from simultaneous data access. A deadlock is a **logic problem**: nothing breaks and nothing is undefined; the program just hangs forever. Rust's compiler can't detect deadlocks.

### One Thread Can Deadlock Alone

Even with a single thread, calling `lock` twice on the same `Mutex` can deadlock — if the first `lock` hasn't been released, the second waits forever:

```rust,ignore,mdbook-runnable
use std::sync::Mutex;

fn main() {
    let m = Mutex::new(42);
    let _g1 = m.lock().expect("Failed to acquire the lock");
    let _g2 = m.lock().expect("Failed to acquire the lock"); // Possible deadlock! The first lock isn't released; the second waits forever
}
```

### How to Avoid It

- **All threads take locks in the same order**: if everyone takes lock 1 before lock 2, nobody jams anybody.
- **Hold fewer locks at once**: if one lock suffices, don't use two.
- **Don't let guards live long**: `drop` promptly when done, shortening lock-hold time.

## Example Code

```rust,editable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let lock1 = Arc::new(Mutex::new(String::from("resource A")));
    let lock2 = Arc::new(Mutex::new(String::from("resource B")));

    // The correct way: both threads take the locks in the same order

    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);
    let a = thread::spawn(move || {
        let g1 = l1.lock().expect("Failed to acquire the lock"); // Lock 1 first
        let g2 = l2.lock().expect("Failed to acquire the lock"); // Then lock 2
        println!("Thread A: {} and {}", *g1, *g2);
    });

    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);
    let b = thread::spawn(move || {
        let g1 = l1.lock().expect("Failed to acquire the lock"); // Also lock 1 first
        let g2 = l2.lock().expect("Failed to acquire the lock"); // Then lock 2
        println!("Thread B: {} and {}", *g1, *g2);
    });

    a.join().expect("The thread hit an error");
    b.join().expect("The thread hit an error");
    println!("No deadlock!");
}
```

## Recap

- Deadlock: threads waiting on each other's locks; the program hangs forever.
- Rust's compiler doesn't block deadlocks — `Send` / `Sync` guard against data races; deadlocks are logic problems.
- One thread `lock`ing the same `Mutex` twice can deadlock too, the first lock never having been released.
- Avoidance: a uniform lock order, fewer simultaneous locks, prompt guard `drop`s.
