# `mio`

## Goal of This Episode

Meet `mio` — the tool that makes "one `Thread` watching a big pile of I/O sources" possible, and the foundation of next episode's reactor.

## Main Text

### The reactor's Role in the runtime

Let's restate the full picture of our hand-written runtime. A runtime really has two roles, each with its own duty:

- **executor**: takes `Task`s off the ready queue and `poll`s them — "running `Task`s." It knows nothing about the outside world — not whether a network packet has arrived, nor whether a file read is done.
- **reactor**: watches all the I/O sources, and `wake`s the corresponding `Task` when one becomes ready — "waiting for events." It does **not** `poll` `Future`s and is not a `Task`; it only watches external event sources.

In recent episodes our "waiting" relied on one `Thread` per `Delay` — far too wasteful. The reactor's mission is to watch **many** I/O sources with **one** `Thread`. The way to do that is this episode's star: `mio`.

### `mio`'s Two Protagonists

`mio` is the low-level `crate` in the Rust ecosystem for cross-platform I/O event notification (Tokio uses it internally too). Add the dependency before use:

```toml
[dependencies]
mio = { version = "1", features = ["os-poll", "net"] }
```

Note one thing first: `mio` itself is **not** `async`. It doesn't know about `async fn`, won't build `Future`s for you, and won't `.await` on your behalf. What it provides is lower-level: for instance, setting a socket to non-blocking, registering it with a `Poll`, and letting "the `Thread` that calls `poll.poll(...)`" sleep while waiting on "is the socket ready."

This episode we only need to meet two of its pieces:

- **`mio::Poll`**: a place where you can "sleep waiting for I/O events." After one `Thread` registers many I/O sources with it, a single `poll.poll(...)` watches them all at once, waking whenever any shows activity.
- **`Token`**: an event source's "name tag." When registering an I/O source, you give it a `Token`; later, when `Poll` notifies you "there's an event," it hands that `Token` back, so you know which source is calling.

### Watching a `TcpListener` with `mio`

The example below registers a `TcpListener` (the thing that accepts connections) with a `Poll`, then opens another `Thread` that connects to it after one second. The main `Thread` sleeps on `poll.poll()` and wakes when the listener reports readiness:

```rust,editable
extern crate mio;

use mio::net::TcpListener;
use mio::{Events, Interest, Poll, Token};
use std::time::Duration;

// the listener's name tag
const SERVER: Token = Token(0);

fn main() {
    let mut poll = Poll::new().expect("Poll creation failed");
    let mut events = Events::with_capacity(128); // receive at most 128 events at a time

    let addr = "127.0.0.1:8080".parse().expect("failed to parse the address");
    let mut listener = TcpListener::bind(addr).expect("bind failed");

    // register the listener with the Poll: name tag SERVER, interested in "readable" events
    // (someone connecting counts as readable)
    poll.registry()
        .register(&mut listener, SERVER, Interest::READABLE)
        .expect("register failed");

    // another thread connects after one second
    std::thread::spawn(|| {
        std::thread::sleep(Duration::from_secs(1));
        let _ = std::net::TcpStream::connect("127.0.0.1:8080");
    });

    println!("sleeping on poll, waiting for I/O events…");
    loop {
        // poll sleeps here until a registered source has an event
        poll.poll(&mut events, None).expect("poll failed");

        for event in events.iter() {
            match event.token() {
                SERVER => {
                    // token matches: the listener reported readable, so try accepting
                    match listener.accept() {
                        Ok((_stream, addr)) => {
                            println!("someone connected: {}", addr);
                            return; // it's an example, so call it a day
                        }
                        // readiness events may be spurious; just wait for the next one
                        Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {}
                        Err(e) => panic!("accept failed: {}", e),
                    }
                }
                _ => {}
            }
        }
    }
}
```

### Walking the Flow

1. `Poll::new()` makes a `Poll`.
2. `registry().register(&mut listener, SERVER, Interest::READABLE)` registers the `listener`, gives it the name tag `SERVER`, and states our interest — "readable" (`Interest::READABLE`). To wait on "writable," use `Interest::WRITABLE`.
3. `poll.poll(&mut events, None)` puts this `Thread` **to sleep** until a registered source has an event (`None` means no timeout — sleep until something happens).
4. On waking, check the `events` one by one. `event.token()` hands back the name tag from registration; matching `SERVER` tells us the `listener` reported readiness, so we try `accept()`:
   - Success means we really got a connection.
   - `WouldBlock` means it still can't accept one right now, so we go back to waiting for the next event. Readiness notifications may be **spurious**, so this is normal rather than a failure.
   - Other errors mean something actually went wrong; this simplified example panics.

`mio`'s sockets are **non-blocking**: calling `accept` or `read` does not make the `Thread` wait for a connection or data. If the operation can't proceed yet, it returns immediately with `WouldBlock`. In this episode that means going back to `poll.poll()`; next episode, after we wrap I/O in a `Future`, the same situation maps to `Poll::Pending`.

The crux: even if you register **a hundred** I/O sources, only **one** `Thread` sleeps on that same `poll.poll()`. Whichever source acts up, `Poll` hands you its name tag. This is exactly the secret weapon a reactor uses to watch masses of I/O with just a few `Thread`s.

Next episode, we hook `mio` up to the runtime we hand-wrote earlier, building a real reactor — the first time our runtime can handle real network I/O.

## Recap

- A runtime has two roles: the **executor** runs `Task`s (`poll`), the **reactor** waits for events (watching I/O and `wake`ing the right `Task`); the reactor isn't a `Task` and doesn't `poll` `Future`s.
- `mio` itself is not an `async` runtime: it only does event notification for non-blocking I/O — no `Future`s, no `.await`, no `Task` scheduling.
- `mio::Poll` is the "sleep waiting for I/O events" place; one `Thread` can watch many I/O sources at once.
- A `Token` is a source's name tag: you give it at registration, and `Poll` returns it when the event fires so you can identify the source.
- Register with `registry().register(&mut source, token, Interest::READABLE)`, sleep on `poll.poll()`, identify by `event.token()`, then try the I/O operation. If it returns `WouldBlock`, wait for another event; inside a `Future`, that maps to `Poll::Pending`.
