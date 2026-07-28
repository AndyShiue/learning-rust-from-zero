# `oneshot`, `watch`, and `broadcast`

## Goal of This Episode

Meet three more kinds of channels and learn to judge which to use.

## Main Text

Last episode's `mpsc` was "many senders, one receiver." Tokio has three more channels, each suiting different situations. The most basic distinction is how many **senders** and **receivers** each has.

### `oneshot`: One Value, Once

`oneshot` is "**one sender, one receiver, one value only**." Perfect for one-time returns of the "compute a result in the background, send it back when done" kind.

```rust,editable
extern crate tokio;

use tokio::sync::oneshot;

#[tokio::main]
async fn main() {
    let (tx, rx) = oneshot::channel::<i32>();

    tokio::spawn(async move {
        // compute a result and send it back (send is single-use and needs no .await)
        tx.send(42).expect("the receiver disappeared");
    });

    // rx is itself a Future — .await it to get the value
    let result = rx.await.expect("the sender disappeared");
    println!("got the result: {}", result);
}
```

Note that `oneshot`'s receiving end `rx` is itself a `Future`; just `rx.await`.

### `watch`: Only the "Latest State" Matters

`watch` is "**many senders, many receivers, with only the latest value retained**." Its `Sender` can be cloned, so multiple tasks can update the same channel. It's not a queue delivering every message — it's more like a "bulletin board": senders can update what's on it at any time, and receivers only care about "what does the board say now." Old values missed in between are not made up to you.

It's best for broadcasting state like "what's the current configuration."

```rust,editable
extern crate tokio;

use tokio::sync::watch;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = watch::channel("starting up");

    tokio::spawn(async move {
        tx.send("running").expect("no receivers");
        tx.send("finished").expect("no receivers");
    });

    // changed().await waits for an update; borrow() reads the current latest value
    while rx.changed().await.is_ok() {
        println!("latest state: {}", *rx.borrow());
    }
}
```

### `broadcast`: Deliver Events to Every Subscriber

`broadcast` is "**many senders, many receivers, each receiver with its own progress**." Unlike `watch`, it doesn't give only the latest value — it delivers every message to all currently subscribed receivers. Suits "one event must notify every subscriber."

```rust,editable
extern crate tokio;

use tokio::sync::broadcast;

#[tokio::main]
async fn main() {
    let (tx, mut rx1) = broadcast::channel::<i32>(16);
    let mut rx2 = tx.subscribe(); // open another receiver

    tx.send(1).expect("no receivers");
    tx.send(2).expect("no receivers");

    // rx1 and rx2 both receive 1 and 2
    println!("rx1 got: {}", rx1.recv().await.expect("receive failed"));
    println!("rx1 got: {}", rx1.recv().await.expect("receive failed"));
    println!("rx2 got: {}", rx2.recv().await.expect("receive failed"));
    println!("rx2 got: {}", rx2.recv().await.expect("receive failed"));
}
```

That said, `broadcast` isn't an unlimited historical record. The `16` given at creation is the capacity; if some receiver goes too long without receiving and falls behind by more than the capacity, old messages get discarded. Its `recv().await` then returns `Lagged(n)`, telling you how many you missed:

```rust,ignore
match rx.recv().await {
    Ok(value) => println!("got: {}", value),
    Err(broadcast::error::RecvError::Lagged(n)) => {
        println!("too slow — missed {} messages", n);
    }
    Err(broadcast::error::RecvError::Closed) => {
        println!("all senders closed");
    }
}
```

So, more precisely: `broadcast` broadcasts messages to all receivers, but each receiver must keep up on its own; fall behind and you get `Lagged`, not a guarantee of every old message forever.

## Recap

- Channels differ in their "number of senders / receivers."
- `oneshot`: one-to-one, a single value once; the receiver is itself a `Future` (`rx.await`) — good for returning results.
- `watch`: many-to-many, latest value only — good for broadcasting current state; use `.changed().await` + `.borrow()`.
- `broadcast`: many-to-many, notifying every subscriber of each event; each receiver keeps its own progress, but falling behind the capacity yields `Lagged`.
- Contrast with last episode's `mpsc` (many-to-one, every message, a queue).
