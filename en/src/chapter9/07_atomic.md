# Atomic Types

## Goal of This Episode

Learn to read and write simple values safely across threads with atomic types.

## Concept

### What's an Atomic Operation

Last episode's `Arc` counts references with atomic operations. What exactly is atomic?

Suppose two threads run `count += 1` on one variable simultaneously. It looks like one step, but it's really three: read the current value, add 1, write it back. With both threads doing those three steps at once, this can happen:

1. Thread A reads `count` = 0.
2. Thread B reads `count` = 0.
3. Thread A writes `count` = 1.
4. Thread B writes `count` = 1.

Each side added once, yet the result is 1, not 2.

An **atomic operation** fuses read, modify, and write into one indivisible act — no thread can ever see a halfway state. Do `count += 1` atomically, and two simultaneous threads always yield 2.

### `AtomicI32` and `AtomicBool`

The standard library provides several atomic types in `std::sync::atomic`, integers and booleans being the most used:

```rust,noplayground
use std::sync::atomic::{AtomicI32, AtomicBool, Ordering};

fn main() {
    let counter = AtomicI32::new(0);
    let flag = AtomicBool::new(false);
}
```

### Basic Operations

```rust,noplayground
use std::sync::atomic::{AtomicI32, Ordering};

fn main() {
    let counter = AtomicI32::new(0);

    counter.store(10, Ordering::Relaxed);              // Write
    let val = counter.load(Ordering::Relaxed);         // Read: 10
    let old = counter.fetch_add(5, Ordering::Relaxed); // Add 5, returning the old value 10
    // counter is now 15
}
```

Every operation takes an `Ordering` parameter. Why?

Modern processors, for performance, may **reorder instruction execution**. Single-threaded, that's harmless — the processor guarantees results identical to in-order execution. But multithreaded, one thread's reordering can show another thread an inconsistent state.

`Ordering` tells the processor "instructions around this operation may not be freely reordered" — generally, the stricter the restriction, the higher the performance cost.

An example: thread A writes data into a `Vec`, then sets an atomic flag `true`; thread B, seeing the flag `true`, reads the `Vec`:

```rust,ignore
// Thread A
data.push(42);                        // Step 1: write the data
ready.store(true, Ordering::Relaxed); // Step 2: set the flag

// Thread B
if ready.load(Ordering::Relaxed) {    // Sees true
    println!("{}", data[0]);          // But the data may not be written yet!
}
```

With `Relaxed`, the processor may reorder thread A's steps 1 and 2 — thread B sees the flag already `true` while the data isn't in yet. The processor dares to reorder because, from thread A's own perspective, flag-then-data and data-then-flag give identical results — it doesn't know another thread is watching. `SeqCst` avoids the problem, guaranteeing all threads see one consistent operation order.

The details run deep; as a beginner, remember two:

- `Ordering::Relaxed`: guarantees only this atomic operation itself; no restrictions on other instructions' order. Fine for plain counters.
- `Ordering::SeqCst`: the strictest — all threads see the same operation order.

When unsure, `SeqCst` is safest.

### Interior Mutability

Look at the code above — `store` and `fetch_add` clearly modify the value, yet need no `&mut self`; `&self` suffices. Like Chapter 5's `Cell`, this is interior mutability.

Why must it be designed so? If modification required `&mut self`, only one thread could hold the `&mut`, and no other thread could touch the value at all — what cross-thread anything would that be? Atomics exist precisely so multiple threads access one value simultaneously through `&`, so interior mutability is mandatory.

`Cell` has interior mutability too, but `Cell` isn't `Sync` (no cross-thread sharing). Atomics are `Sync` — the underlying hardware guarantees the operations' atomicity, so simultaneous modification through `&` from many threads stays sound.

### Pairing with `Arc`

Atomics most commonly pair with `Arc`, letting several threads update one counter together:

```rust,editable
use std::sync::Arc;
use std::sync::atomic::{AtomicI32, Ordering};
use std::thread;
fn main() {
    let counter = Arc::new(AtomicI32::new(0));

    let mut handles = vec![];

    for _ in 0..10 {
        let counter_clone = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                counter_clone.fetch_add(1, Ordering::Relaxed);
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("thread panicked");
    }

    println!("Final result: {}", counter.load(Ordering::Relaxed)); // Always 10000
}
```

Ten threads adding 1000 each — the result is always 10000, never undercounted.

### Atomic Types vs Locks

Atomic operations apply only to simple types — integers (`AtomicI32`, `AtomicU64`, `AtomicUsize`, etc.) and booleans (`AtomicBool`). To protect a `Vec`, `String`, or any complex structure, atomics can't; you need next episode's locks.

But for simple counters and flags, atomics beat locks — every thread operates directly, no queueing for someone else to finish.

## Example Code

```rust,editable
use std::sync::Arc;
use std::sync::atomic::{AtomicI32, Ordering};
use std::thread;

fn main() {
    let counter = Arc::new(AtomicI32::new(0));

    let mut handles = vec![];

    // Three threads, each counting to a different limit
    for limit in [100, 200, 300] {
        let counter_clone = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..limit {
                counter_clone.fetch_add(1, Ordering::Relaxed);
            }
            println!("Added {} times; now: {}", limit, counter_clone.load(Ordering::Relaxed));
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("thread panicked");
    }

    // 100 + 200 + 300 = 600, whatever the execution order
    println!("Final result: {}", counter.load(Ordering::Relaxed));
}
```

## Recap

- Atomic operations fuse read-modify-write into one indivisible act, safe under simultaneous threads.
- Common types: `AtomicI32`, `AtomicUsize`, `AtomicBool`.
- Common methods: `load` (read), `store` (write), `fetch_add` (add, returning the old value).
- `Ordering` controls memory ordering; when unsure, `SeqCst`.
- Atomic types have interior mutability — modifying through `&self` — and are `Sync` (shareable across threads).
- Simple types only; complex data needs locks.
