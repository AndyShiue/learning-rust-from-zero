# `mpsc`

## Goal of This Episode

Learn to pass work between `Task`s with the `async` version of the `mpsc` channel, and understand the bounded channel's backpressure.

## Main Text

### A Work Queue Between `Task`s

In the multithreading chapter we used `std::sync::mpsc` to pass messages between `Thread`s. The `async` world's counterpart is `tokio::sync::mpsc`, the most common queue between `Task`s: one side (the producer) `send`s work in, the other (the consumer) `recv`s it out for processing. It's likewise **multi-producer single-consumer** — many senders allowed, but only one receiver.

```rust,editable
extern crate tokio;

use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    // create a bounded channel with capacity 32
    let (tx, mut rx) = mpsc::channel::<i32>(32);

    // producer: spawned off to send 5 jobs
    tokio::spawn(async move {
        for i in 0..5 {
            tx.send(i).await.expect("the receiver was closed");
            println!("sent {}", i);
        }
        // tx drops here; once the remaining messages are received, recv returns None
    });

    // consumer: keep receiving until the channel closes
    while let Some(value) = rx.recv().await {
        println!("received {}", value);
    }
    println!("the channel closed — done");
}
```

`rx.recv().await` returns an `Option`: a message is `Some(value)`; once every sender has been `drop`ped and the channel's leftover messages have all been received, it returns `None`, and the `while let` ends naturally.

### Bounded Channels and Backpressure

Notice we gave the channel a capacity of `32` — this is a **bounded** channel. That capacity ceiling is precisely last episode's backpressure: when the messages piling up in the channel **fill** all 32 slots (meaning the consumer can't keep up), the producer's `tx.send(value).await` **waits**, resuming only after the consumer clears some space.

That also explains why `send` needs `.await` — because it **may have to wait** (for a free slot). Contrast the synchronous `send` introduced in the multithreading chapter, which never waits (it's unbounded); the `.await` here is backpressure incarnate. Tokio also has `unbounded_channel`, whose `send` needs no `.await` — but then there's no backpressure, so use it with care.

## Recap

- `tokio::sync::mpsc` is the most common work queue between `async` `Task`s: many senders, one receiver.
- `rx.recv().await` returns an `Option`: `Some` while there are messages, `None` after all senders drop and the leftovers are drained.
- A **bounded channel** has a capacity ceiling; when full, `send().await` waits — that's backpressure, forcing producers to match the consumer's pace.
- `send` requires `.await` exactly because it may wait for a slot; `unbounded_channel` never waits but has no backpressure.
