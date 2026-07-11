# `mpsc`

## Goal of This Episode
Learn to make `Thread`s communicate by passing messages through channels, and how this compares to shared memory.

## Concept

### A Different Line of Thought

The earlier `Mutex` and `RwLock` follow the "shared memory" approach — several `Thread`s access one piece of data, with locks preventing conflicts.

Channels take a completely different approach: **`Thread`s communicate by passing messages**. Data gets sent straight over — no sharing.

### Creating a Channel

`std::sync::mpsc::channel()` creates a sender (`tx`) and receiver (`rx`) pair:

```rust,noplayground
use std::sync::mpsc;

fn main() {
    let (tx, rx) = mpsc::channel::<i32>();
}
```

`mpsc` stands for **multiple producer, single consumer** — many senders allowed, but only one receiver.

### Sending and Receiving

`tx.send(value)` sends the value out (moving it); `rx.recv()` receives on the other end (blocking until something arrives):

```rust,editable
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        tx.send(String::from("hello")).expect("send failed");
    });

    let received = rx.recv().expect("receive failed");
    println!("Received: {}", received);
}
```

### Multiple Senders

`tx.clone()` produces additional senders:

```rust,editable
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    for i in 0..3 {
        let tx = tx.clone();
        thread::spawn(move || {
            tx.send(format!("From thread {}", i)).expect("send failed");
        });
    }

    drop(tx); // The original tx must be dropped too, or rx never finishes

    for received in rx {
        println!("Received: {}", received);
    }
}
```

### When Does It End

Once every `tx` is `drop`ped, `rx.recv()` first drains all unreceived messages; only calls to `recv()` after that return `Err`. The `for msg in rx` loop behaves likewise — it runs through the remaining messages, then ends. That's how "nobody will send again, and every message has been handled" gets determined.

Note the `drop(tx)` in the example above — if you `clone`d `tx` but never `drop`ped the original, the receiver believes a sender still lives and never finishes.

### Channels vs Shared Memory

Which when?

- **Several `Thread`s repeatedly reading and writing one piece of data** (a shared counter, a shared cache) → `Mutex` / `RwLock` is more direct.
- **A produce-on-one-side, consume-on-the-other** pipeline → channels are more natural. Ownership of the data transfers outright: no locks, and no forgetting to release one.

## Example Code

```rust,editable
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    // Launch 3 workers, each computing and sending its result back
    for i in 0..3 {
        let tx = tx.clone();
        thread::spawn(move || {
            let result = i * i;
            println!("Thread {} finished computing: {}", i, result);
            tx.send((i, result)).expect("send failed");
        });
    }

    // Drop the original tx so the rx loop ends once all clones finish
    drop(tx);

    // Receive every result
    let mut total = 0;
    for (id, result) in rx {
        println!("Main thread received: thread {}'s result is {}", id, result);
        total += result;
    }

    println!("The sum of all results: {}", total);
}
```

## Recap

- Channels let `Thread`s communicate by message passing; data is sent over, not shared.
- `mpsc::channel()` creates the sender `tx` and receiver `rx`.
- `tx.send(value)` moves `value`; `rx.recv()` blocks until something arrives.
- `tx.clone()` makes multiple senders, but there's only one receiver (`mpsc`).
- Once every `tx` is `drop`ped, the `rx` loop ends automatically.
- Pipelines take channels; repeated access to one piece of data takes `Mutex` / `RwLock`.
