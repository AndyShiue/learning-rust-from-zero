# Your First `async` Program

## Goal of This Episode

Write a tiny server with Tokio that responds to a browser, to get a first impression of what `async` programs look like.

## Main Text

Welcome to the world of async! In this chapter we'll put in a lot of work slowly peeling open the workings of asynchrony (`async`), layer by layer. But this first episode skips the theory — we'll write a runnable program straight away so you get a feel for what `async` code looks like. Having read this far, you've learned a lot; just reading the code, you can probably guess what it does.

Let's start from the word itself. **Synchronous** means "everyone moves in lockstep": until one thing finishes, the next thing waits. **Asynchronous** means "no need to wait in lockstep": while one thing is waiting on a result, the program can push something else forward first. In a server, that means waiting for a browser to connect, or for a response to be sent, doesn't force every other connection to sit frozen.

### Rust's `async` Needs a runtime

Unlike many other languages, Rust's standard library has **no** built-in engine for executing async work (we'll call it a runtime from now on). The standard library only defines async's "specification"; how the async work actually gets run is left to third-party `crate`s. That sounds odd, but this design lets Rust's `async` serve everything from big servers to small embedded devices.

The most widely used runtime today is **Tokio**. In the second half of this chapter, we'll dig into Tokio's features. To use it, first add the dependency in `Cargo.toml`:

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

Or by command:

```bash
cargo add tokio --features full
```

The program below writes `.await` directly in `main`. Note this syntax rule now: **`.await` can only appear in an `async` context**. A plain `fn main()` can't `.await` directly, so we'll write it as `async fn main()`.

However, `async fn main()` can't serve as the program's entry point by itself the way a plain `fn main()` does. The `#[tokio::main]` attribute is the helper Tokio provides: it sets up the runtime for us so this `async fn main()` can actually be executed.

### A Server That Counts

The program below opens a little server on your machine; whenever someone connects, it replies "this is request number N." All connections share one counter, so as you refresh your browser, the number keeps climbing:

```rust,no_run
# extern crate tokio;
#
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};
use tokio::io::AsyncWriteExt;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    // the counter shared by all connections
    let counter = Arc::new(AtomicU64::new(0));

    // listen on local port 8080
    let listener = TcpListener::bind("127.0.0.1:8080").await.expect("bind failed");
    println!("server started — open http://127.0.0.1:8080 in your browser");

    loop {
        // wait for the next connection to come in
        let (mut socket, _) = listener.accept().await.expect("accept failed");

        // hand a share of the counter's ownership to the upcoming background job
        let counter = Arc::clone(&counter);

        // toss this connection to the background; the main loop goes right back to waiting
        tokio::spawn(async move {
            let n = counter.fetch_add(1, Ordering::SeqCst) + 1;
            let body = format!("this is request number {}\n", n);
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}",
                body.len(),
                body,
            );
            socket.write_all(response.as_bytes()).await.expect("failed to respond");
        });
    }
}
```

Once it's running on your machine, open your browser to `http://127.0.0.1:8080` and refresh a few times — you'll see the number keep going up.

### What `.await` Means

Several `.await`s appear in the program — this is the very heart of `async` code. For now, understand it like this:

> `.await` means "this may take a while to be ready; while we wait, please try to find something else to do."

Take `listener.accept().await`: accepting a new connection means waiting until someone actually connects, which could be a few milliseconds or several seconds. `.await` marks this "might have to wait" spot; while waiting, this `async` job can be paused, yielding its turn to run.

### It Really Does Handle Many Connections at Once

Notice we used `tokio::spawn` to toss "handling a single connection" into the background. The main loop only accepts new connections; for each one it spawns a background job to write the response, then immediately goes back to waiting for the next connection.

So even if some connection is in the middle of `socket.write_all(response.as_bytes()).await`, the main loop doesn't wait for the write to finish. Other connections keep being accepted and processed. This ability to split many things apart and advance them interleaved is exactly `async`'s selling point.

This episode showed you the look and effect of an `async` program. Next episode we spell out the motivation: what scenarios it suits, why not just open lots of `Thread`s, and what exactly separates "concurrency" from "parallelism."

## Recap

- Rust's standard library only defines `async`'s specification; actual execution relies on a third-party **runtime**, most commonly **Tokio**.
- `.await` can only be written in an `async` context; `#[tokio::main]` lets `main` be an `async fn`, sets up the runtime for you, and drives it.
- `.await` means "wait for this to be ready, and meanwhile go do other things" — not "sit and block."
- Paired with `tokio::spawn` to push work into the background, an `async` program can advance many connections at once.
