# `JoinSet` and `FuturesUnordered`

## Goal of This Episode

Learn to handle "lots of dynamically generated concurrent work, processed in whatever order it finishes," and understand the trade-off between `JoinSet` and `FuturesUnordered`.

## Main Text

### Where `join!` Falls Short

`join!` is great, but it has two limitations: the number of branches is **fixed** (you must list them all when writing the program), and it waits for **all** of them to finish.

Yet often your work is "**a large amount, generated dynamically, and whoever finishes first gets processed first**" — crawling a thousand web pages, say. `join!` can't handle that; you need different tools. There are two routes, and the difference is whether each job becomes an independent `Task`.

### Route 1: `JoinSet` (the Dynamic Version of `spawn`)

Think of `tokio::task::JoinSet` as "**the dynamic version of `spawn`**." You `spawn` any number of jobs into it, each an **independent `Task`**, so they can be spread across `Thread`s and run **truly in parallel** (which also means, like `spawn`, they need `Send + 'static`). Then collect the finished results one by one with `join_next().await` — **whoever finishes first is received first**:

```rust,editable
# extern crate tokio;
#
use tokio::task::JoinSet;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let mut set = JoinSet::new();

    // dynamically spawn five jobs, deliberately with different delays
    for i in 0..5 {
        set.spawn(async move {
            sleep(Duration::from_millis(100 * (5 - i))).await;
            i
        });
    }

    // received in completion order (not spawn order)
    while let Some(result) = set.join_next().await {
        let value = result.expect("task panicked or was aborted");
        println!("done: {}", value);
    }
}
```

`join_next()` returns `Option<Result<T, JoinError>>`:

- `None`: no `Task`s left; you've collected them all.
- `Some(Ok(value))`: a `Task` finished successfully.
- `Some(Err(...))`: that `Task` panicked or was aborted (so handle this `Err`).

`JoinSet` also supports `.abort_all()` to call off all the work at once, and when a `JoinSet` is `drop`ped it **automatically aborts** every unfinished `Task` inside — very convenient for graceful shutdown (next episode uses this).

### Route 2: `FuturesUnordered` (the Dynamic Version of `join!`)

`futures::stream::FuturesUnordered` is "**the dynamic version of `join!`**." It advances a pile of `Future`s in turn **within a single `Task`** — it does **not** make them independent `Task`s and does **not** cross `Thread`s. Both the cost and the benefit flow from that:

- Since it doesn't cross `Thread`s, it **doesn't need `Send + 'static`** — it can hold `Future`s that borrow local variables (`JoinSet` can't, because it has to `spawn`).
- But since everyone takes turns on the same `Task`, **one stuck branch drags down the others** (that "don't block the thread" iron rule again).

`FuturesUnordered` is defined in the `futures` crate, so add the dependency first (last episode's `tokio-stream` is used here too):

```toml
[dependencies]
futures = "0.3"
tokio-stream = "0.1"
```

`FuturesUnordered` is itself really just a `Stream` — all it does is "`poll` its internal pile of `Future`s in turn"; it doesn't `spawn` or touch scheduling. So it **doesn't depend on a particular runtime**, a big advantage over `JoinSet` (whose `spawn` is tied to the Tokio runtime). Walk it the `Stream` way:

```rust,editable
extern crate futures;
extern crate tokio;
extern crate tokio_stream;

use futures::stream::FuturesUnordered;
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    let mut futures = FuturesUnordered::new();

    // dynamically push in a pile of Futures (they don't become independent Tasks)
    for i in 0..5 {
        futures.push(async move { i * 2 });
    }

    // it's a Stream — results pop out in completion order
    while let Some(value) = futures.next().await {
        println!("done: {}", value);
    }
}
```

### How to Choose

Both produce results in completion order, and both suit crawlers, batch requests, and the like. The differences:

- Want **true parallelism, jobs isolated from each other** (one stuck job doesn't drag down the rest) → use **`JoinSet`** (each is an independent `Task`, but needs `Send + 'static` and is tied to Tokio).
- Want to **borrow local variables in place, keep jobs lightweight, avoid depending on a particular runtime** → use **`FuturesUnordered`** (multiplexed within one `Task`, no `Send` needed, but one stuck branch drags down the others).

Next episode, we assemble the tools learned so far — `select!`, channels, `JoinSet` — into a complete graceful shutdown flow.

## Recap

- For "large, dynamic, first-done-first-served" work, `join!` isn't enough; use `JoinSet` or `FuturesUnordered`.
- **`JoinSet`** (dynamic `spawn`): each job is an independent `Task`, truly parallel, needs `Send + 'static`, tied to Tokio; `join_next()` returns `Option<Result<T, JoinError>>`, supports `.abort_all()` and auto-abort on `drop`.
- **`FuturesUnordered`** (dynamic `join!`): multiplexes within one `Task`, no `Thread` crossing, no `Send` needed (can borrow local variables), but one stuck branch drags down the rest; it's itself a runtime-agnostic `Stream`.
- True parallelism and isolation → `JoinSet`; in-place borrowing, lightweight work, runtime-agnostic → `FuturesUnordered`.
