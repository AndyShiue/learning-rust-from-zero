# `JoinSet` and `FuturesUnordered`

## Goal of This Episode

Learn to handle "lots of dynamically generated concurrent work, processed in whatever order it finishes," and understand the trade-off between `JoinSet` and `FuturesUnordered`.

## Main Text

### Where `join!` Falls Short

`join!` is great, but it has two limitations: the number of branches is **fixed** (you must list them all when writing the program), and it waits for **all** of them to finish.

Yet often your work is "**a large amount, generated dynamically, and whoever finishes first gets processed first**" — crawling a thousand web pages, say. `join!` can't handle that; you need different tools. There are two routes, and the difference is whether each job becomes an independent `Task`.

### Route 1: `JoinSet` (the Dynamic Version of `spawn`)

Think of `tokio::task::JoinSet` as "**the dynamic version of `spawn`**." You `spawn` any number of jobs into it, each an **independent `Task`**. On a multi-thread runtime, Tokio can schedule them on different worker `Thread`s, allowing them to run in parallel (and, like `spawn`, they need `Send + 'static`). Then collect the finished results one by one with `join_next().await` — **whoever finishes first is received first**:

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
        let value = result.expect("task panicked or was cancelled");
        println!("done: {}", value);
    }
}
```

`join_next()` returns `Option<Result<T, JoinError>>`:

- `None`: no `Task`s left; you've collected them all.
- `Some(Ok(value))`: a `Task` finished successfully.
- `Some(Err(...))`: that `Task` panicked or was cancelled (so handle this `Err`).

`JoinSet` also supports `.abort_all()` to cancel all the work at once, and when a `JoinSet` is `drop`ped it **automatically cancels** every unfinished `Task` inside — very convenient for graceful shutdown (next episode uses this).

### Route 2: `FuturesUnordered` (the Dynamic Version of `join!`)

`futures::stream::FuturesUnordered` is "**the dynamic version of `join!`**." It advances a pile of `Future`s in turn **within a single `Task`** — it does **not** make them independent `Task`s and does **not necessarily** cross `Thread`s. Both the cost and the benefit flow from that:

- Since it doesn't `spawn` them as independent `Task`s, `FuturesUnordered` itself **doesn't require those `Future`s to be `Send + 'static`** — it can hold `Future`s that borrow local variables (`JoinSet` can't, because it has to `spawn`).
- But since everyone takes turns on the same `Task`, if one `Future`'s `poll` blocks or runs for too long, `poll`ing the others is delayed (that "don't block the `Thread`" iron rule again).

`FuturesUnordered` is defined in the `futures` `crate`, so add the dependency first (last episode's `tokio-stream` is used here too):

```toml
[dependencies]
futures = "0.3"
tokio-stream = "0.1"
```

`FuturesUnordered` is itself really just a `Stream` — it tracks wake-ups and `poll`s only newly added or woken `Future`s; it doesn't `spawn` them as `Task`s. So it **doesn't depend on a particular runtime**, a big advantage over `JoinSet` (whose `spawn` is tied to the Tokio runtime). Walk it the `Stream` way:

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

- Want **independent `Task`s that can run in parallel, with greater scheduling isolation** → use **`JoinSet`** (but it needs `Send + 'static` and is tied to Tokio).
- Want to **borrow local variables in place, keep jobs lightweight, avoid depending on a particular runtime** → use **`FuturesUnordered`** (multiplexed within one `Task`, no `Send` needed, but one `Future`'s blocking or long-running `poll` delays `poll`ing the others).

Next episode, we assemble the tools learned so far — `select!`, channels, `JoinSet` — into a complete graceful shutdown flow.

## Recap

- For "large, dynamic, first-done-first-served" work, `join!` isn't enough; use `JoinSet` or `FuturesUnordered`.
- **`JoinSet`** (dynamic `spawn`): each job is an independent `Task`, can run in parallel on a multi-thread runtime, needs `Send + 'static`, tied to Tokio; `join_next()` returns `Option<Result<T, JoinError>>`, supports `.abort_all()`, and cancels whatever is left on `drop`.
- **`FuturesUnordered`** (dynamic `join!`): multiplexes within one `Task`, doesn't spawn independent `Task`s, and doesn't itself require its `Future`s to be `Send + 'static` (so they can borrow local variables when the surrounding context allows), but one `Future`'s blocking or long-running `poll` delays polling the others; it's itself a runtime-agnostic `Stream`.
- Independent `Task`s, possible parallel execution, and greater scheduling isolation → `JoinSet`; in-place borrowing, lightweight work, runtime-agnostic → `FuturesUnordered`.
