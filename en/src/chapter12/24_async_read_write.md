# `AsyncRead` and `AsyncWrite`

## Goal of This Episode

Meet the `async` versions of the I/O operations, and make first contact with an `async`-specific concept: **cancellation**.

## Main Text

### Reading and Writing, the `async` Way

Chapter 11 used the synchronous `Read` / `Write` `trait`s. The `async` world has corresponding `AsyncRead` / `AsyncWrite` — same idea, except the reads and writes become `.await`able.

One important property up front: the true core methods underlying the `AsyncRead` / `AsyncWrite` `trait`s are `poll_read` / `poll_write`. They only promise to "**try to make progress once**"; `poll_read` fills what it read into the buffer, and `poll_write` reports how many bytes this attempt actually wrote. Neither **guarantees** filling your whole buffer in one go, nor writing all the data at once. Say you want 100 bytes: some `poll_read` might fill in only 30 — the rest must be read later.

### The Convenience helpers in `AsyncReadExt` / `AsyncWriteExt`

Handling "didn't read enough, didn't finish writing" yourself every time is tedious. So Tokio's extension `trait`s `AsyncReadExt` / `AsyncWriteExt` provide many helpers that wrap the loop for you. Internally they too repeatedly drive the underlying `poll_read` / `poll_write`. Two of them:

- `.read_exact(&mut buf)`: keeps reading until `buf` is **completely filled**.
- `.write_all(buf)`: keeps writing until `buf` is **entirely written out**.

```rust,no_run
# extern crate tokio;
#
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

#[tokio::main]
async fn main() {
    let mut stream = TcpStream::connect("127.0.0.1:8080").await.expect("failed to connect");

    // write_all: writes the whole buffer (may call poll_write more than once)
    stream.write_all(b"GET / HTTP/1.0\r\n\r\n").await.expect("failed to write");

    // read_exact: reads 16 bytes (may call poll_read more than once)
    let mut buf = [0u8; 16];
    stream.read_exact(&mut buf).await.expect("failed to read");
    println!("read 16 bytes: {:?}", buf);
}
```

### First Contact with "Cancellation"

Helpers like `read_exact` happen to bring us to a concept that's vital in `async` yet easy to overlook: **cancellation**.

Remember that `Future`s are lazy? They only move when `poll`ed. Flip that around — if you **stop `poll`ing** one and just `drop` it, that `async` job has effectively been **called off**; the code after that point will never run. That's `async` cancellation: **`drop`ping a `Future` is cancelling it**.

This is an ability unique to `async`. Ordinary `Thread`s can't be stopped this cleanly — there's no safe way to halt a running `Thread` midway from the outside. But an `async` job is just an unfinished `Future`; ignore it, discard it, and it stops.

### `read_exact` Is Not cancellation safe

Convenient as cancellation is, there's a trap. Operations like `read_exact` — "**spanning several advances, accumulating state along the way**" — call for care.

Imagine preparing a 100-byte buffer and handing it to `read_exact(&mut buf)`. Its goal is to return only after filling the whole `buf`. But the underlying `poll_read` might read just 30 bytes the first time, so `read_exact` remembers "30 read so far, 70 to go" and continues `.await`ing.

Here's the problem: if this `read_exact` gets cancelled midway (`drop`ped), the progress it remembered vanishes with it. Continuing the "30 bytes on the first read" scenario: those 30 bytes have already been taken off the socket and written into the front of `buf`; but `read_exact` never returned successfully, so it never handed back the fact that "30 bytes have been read so far." In other words, the "fill 100 bytes" operation stopped mid-road, and the remaining 70 bytes won't complete themselves.

Cancellation can strike at other moments too: earlier, and perhaps 0 bytes had been read; later, and maybe 80; land exactly on 100 and `read_exact` may complete normally. The nuisance is: whenever it's discarded before completing normally, you lose the "where exactly did I get to" progress. For I/O that must be parsed in order, bytes already consumed can't be un-read and retried; without separately saving the progress yourself, safely continuing the read becomes very hard.

We say `read_exact` and `write_all` are **not cancellation safe**: cancelled midway, they leave a mess (some data may already be consumed, yet the whole "fill the buffer" operation never finished). So you should **not** place operations like `read_exact` or `write_all` anywhere they "might get discarded midway."

And where might that be? The classic case is next episode's `select!` — by its very nature, when one branch completes, it `drop`s (i.e. cancels) the other unfinished branches. So next episode returns to cancellation safety and how to avoid this pit inside `select!`.

## Recap

- `AsyncRead` / `AsyncWrite` are the `async` versions of `Read` / `Write`; the core is `poll_read` / `poll_write`, each attempting one advance: `poll_read` fills the buffer, `poll_write` reports bytes written — neither guarantees a full read or complete write.
- `AsyncReadExt` / `AsyncWriteExt` provide helpers like `read_exact` and `write_all` that wrap the "fill / finish" loop for you.
- **Cancellation**: `Future`s are lazy; `drop`ping one (never `poll`ing again) cancels the `async` job — unique to `async`, impossible with `Thread`s.
- Operations like `read_exact` that "span multiple advances and accumulate state" are **not cancellation safe**: cancelled midway, data may be partially consumed with the "fill the buffer" operation unfinished — keep them out of places that may get `drop`ped midway.
