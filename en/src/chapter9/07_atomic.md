# Atomic Types

## Goal of This Episode

Learn to read and write simple values safely across `Thread`s with atomic types.

## Concept

### What's an Atomic Operation

Last episode's `Arc` counts references with atomic operations. What exactly is atomic?

Suppose two `Thread`s run `count += 1` on one variable simultaneously. It looks like one step, but it's really three: read the current value, add 1, write it back. With both `Thread`s doing those three steps at once, this can happen:

1. `Thread` A reads `count` = 0.
2. `Thread` B reads `count` = 0.
3. `Thread` A writes `count` = 1.
4. `Thread` B writes `count` = 1.

Each side added once, yet the result is 1, not 2.

Some **atomic operations** fuse read, modify, and write into one indivisible act — no `Thread` can ever see a halfway state. Do `count += 1` atomically, and two simultaneous `Thread`s always yield 2.

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

Modern processors, for performance, may **reorder instruction execution**. Single-threaded, that's harmless — the processor guarantees results identical to in-order execution. But multithreaded, one `Thread`'s reordering can show another `Thread` an inconsistent state.

`Ordering` tells the processor "instructions around this operation may not be freely reordered" — generally, the stricter the restriction, the higher the performance cost.

An example: `Thread` A writes data into a `Vec`, then sets an atomic flag `true`; `Thread` B, seeing the flag `true`, reads the `Vec`:

```rust,ignore
// Thread A
data.push(42);                        // Step 1: write the data
ready.store(true, Ordering::Relaxed); // Step 2: set the flag

// Thread B
if ready.load(Ordering::Relaxed) {    // Sees true
    println!("{}", data[0]);          // But the data may not be written yet!
}
```

With `Relaxed`, the processor may reorder `Thread` A's steps 1 and 2 — `Thread` B sees the flag already `true` while the data isn't in yet. The processor dares to reorder because, from `Thread` A's own perspective, flag-then-data and data-then-flag give identical results — it doesn't know another `Thread` is watching. `SeqCst` prevents this problem by preserving the two orders written in the code: `Thread` A writes the data before setting the flag, and `Thread` B checks the flag before reading the data. Therefore, if `Thread` B sees `true`, it is guaranteed to also see the data that `Thread` A wrote first.

The details run deep; as a beginner, remember two:

- `Ordering::Relaxed`: guarantees only this atomic operation itself; no restrictions on other instructions' order. Fine for plain counters.
- `Ordering::SeqCst`: the strictest. In this example, it preserves "write data → set flag" and "check flag → read data," so when `Thread` B sees `ready == true`, it is guaranteed to also see the data that `Thread` A wrote first.

When unsure, `SeqCst` is safest.

### Interior Mutability

Look at the code above — `store` and `fetch_add` clearly modify the value, yet need no `&mut self`; `&self` suffices. Like Chapter 5's `Cell`, this is interior mutability.

Why must it be designed so? If modification required `&mut self`, only one `Thread` could hold the `&mut`, and no other `Thread` could touch the value at all — what cross-thread anything would that be? Atomics exist precisely so multiple `Thread`s access one value simultaneously through `&`, so interior mutability is mandatory.

`Cell` has interior mutability too, but `Cell` isn't `Sync` (no cross-thread sharing). Atomics are `Sync` — the underlying hardware guarantees the operations' atomicity, so simultaneous modification through `&` from many `Thread`s stays sound.

### Pairing with `Arc`

Atomics most commonly pair with `Arc`, letting several `Thread`s update one counter together:

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

Ten `Thread`s adding 1000 each — the result is always 10000, never undercounted.

### Atomic Types vs Locks

Atomic operations apply only to simple types — such as integers (`AtomicI32`, `AtomicU64`, `AtomicUsize`, etc.) and booleans (`AtomicBool`). To protect a `Vec`, `String`, or any complex structure, atomics can't; you need next episode's locks.

But for simple counters and flags, atomics beat locks — every `Thread` operates directly, no queueing for someone else to finish.

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

- Some atomic operations fuse read-modify-write into one indivisible act, safe under simultaneous `Thread`s.
- Common types: `AtomicI32`, `AtomicUsize`, `AtomicBool`.
- Common methods: `load` (read), `store` (write), `fetch_add` (add, returning the old value).
- `Ordering` controls memory ordering; when unsure, `SeqCst`.
- Atomic types have interior mutability — modifying through `&self` — and are `Sync` (shareable across `Thread`s).
- Simple types only; complex data needs locks.
