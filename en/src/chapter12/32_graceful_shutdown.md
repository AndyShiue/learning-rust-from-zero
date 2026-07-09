# graceful shutdown

## Goal of This Episode

Assemble the tools from earlier episodes into a complete graceful shutdown flow.

## Main Text

### What Is graceful shutdown

When a server needs to stop, the crudest approach is to just kill it — but then work in progress is cut off mid-flight, possibly leaving corrupted data and unanswered requests. **graceful shutdown** is the politer way: on receiving a stop request, don't hard-cut — instead, "**tell everyone to wrap up → wait for work in hand to finish (or hit a deadline) → exit cleanly**."

Break it into three ingredients:

1. **Signal source**: how to know "it's time to stop."
2. **Broadcasting shutdown**: how to tell every worker "we're wrapping up."
3. **Waiting for the drain**: how to wait for all workers to finish up.

We'll match each one to a tool we've already learned.

### Assembling the Three Ingredients

- The **signal source** is `tokio::signal::ctrl_c()` — it's a `Future`; `.await`ing it waits until the user presses Ctrl-C (in practice you'd also listen for SIGTERM).
- **Broadcasting shutdown** uses Episode 28's `watch` as a shutdown flag: one-to-many, and workers who subscribe late can still read the current state.
- **Waiting for the drain** uses Episode 31's `JoinSet` — `join_next()` until it's empty.

Each worker internally uses `select!` to wait for "the next job" and "the shutdown signal" **at the same time**. If a job arrives first, leave the `select!` and process it; if shutdown arrives first, stop taking new jobs:

```rust,no_run
# extern crate tokio;
#
use std::time::Duration;
use tokio::sync::watch;
use tokio::task::JoinSet;
use tokio::time::{sleep, timeout};

async fn wait_next_job(id: u32, next_job: &mut u32) -> u32 {
    // here sleep stands in for "waiting for the next job to come in".
    // this wait may be cancelled by shutdown; actual processing happens outside the select!.
    sleep(Duration::from_millis(500)).await;
    let job = *next_job;
    *next_job += 1;
    println!("worker {} got job {}", id, job);
    job
}

async fn process_job(id: u32, job: u32) {
    // this stands in for "actually processing the job".
    // it's deliberately outside the select!, so shutdown can't cancel it midway.
    sleep(Duration::from_millis(300)).await;
    println!("worker {} finished job {}", id, job);
}

async fn worker(id: u32, mut shutdown: watch::Receiver<bool>) {
    let mut next_job = 0;

    loop {
        let job = tokio::select! {
            // waiting for the next job: this can be cancelled by shutdown
            job = wait_next_job(id, &mut next_job) => job,
            // the wrap-up signal
            _ = shutdown.changed() => {
                println!("worker {} got the shutdown signal, exiting", id);
                break;
            }
        };

        // process outside select!, so shutdown cannot drop it midway
        process_job(id, job).await;
    }
}

#[tokio::main]
async fn main() {
    // the watch flag used to broadcast shutdown
    let (shutdown_tx, shutdown_rx) = watch::channel(false);

    // manage all workers with a JoinSet
    let mut workers = JoinSet::new();
    for id in 0..3 {
        workers.spawn(worker(id, shutdown_rx.clone()));
    }

    // 1. wait for the signal
    tokio::signal::ctrl_c().await.expect("couldn't listen for Ctrl-C");
    println!("got Ctrl-C, starting graceful shutdown");

    // 2. broadcast the wrap-up
    shutdown_tx.send(true).expect("no worker is listening");

    // 3. wait for all workers to drain, with a 5-second deadline
    match timeout(Duration::from_secs(5), async {
        while workers.join_next().await.is_some() {}
    })
    .await
    {
        Ok(()) => println!("all workers exited cleanly"),
        Err(_) => {
            println!("timed out! force-aborting the remaining workers");
            workers.abort_all();
        }
    }
}
```

You can read `timeout(Duration::from_secs(5), future)` as: "wait at most five seconds for this `future`."

It is itself a `Future`. If the inner `future` finishes within five seconds, `.await` yields `Ok(the inner output)`; if five seconds pass without it finishing, `.await` yields `Err(_)`. In this example, the inner `future` is:

```rust,ignore
async {
    while workers.join_next().await.is_some() {}
}
```

That is, "keep waiting for workers to finish until the `JoinSet` is empty." So the whole `timeout` reads: **give all workers at most five seconds to wrap themselves up; if they all exit in time, print success — past five seconds, take the `Err(_)` branch and force-abort whoever's left**.

### The cancellation safety Design Point

Here's a key design choice echoing Episodes 24 and 25: **place the `select!` deliberately**. In the worker above, the `select!` waits on "the next job" and "shutdown"; once a job is actually in hand, we leave the `select!` and only then call `process_job`. So when shutdown wins, what gets `drop`ped (cancelled) is the resumable wait for the next job — not work that has already started.

If instead you put the real processing inside a branch that can lose to shutdown, operations that aren't safely cancellable — like `read_exact` — could be cut off midway, and the data lost with them. This is the concrete application to shutdown of the cancellation safety we emphasized earlier.

### Always Set a Deadline

Graceful doesn't mean waiting **indefinitely**. If some worker is stuck for good, you can't let the whole program keep it company forever. So the drain must have a **deadline**: above, we wrap the entire drain in `tokio::time::timeout`, and on timeout call `abort_all()` (or just `drop` the `JoinSet` — it auto-aborts the remaining `Task`s) to force things closed.

The principle in one sentence: **ask politely first; act if that fails**.

### A Better-fitting Tool: `CancellationToken`

Using `watch` as a shutdown flag works, but it feels a bit like "borrowing" a state-broadcast tool to serve as a switch. `tokio-util` provides a tool designed for "cancellation" from the ground up — `CancellationToken`, with semantics that fit better. `tokio-util` isn't part of Tokio proper, so add the dependency first:

```toml
[dependencies]
tokio-util = "0.7"
```

(As with `tokio-stream` in Episode 30, the `-` in the crate name becomes `_` in code: `use tokio_util::...`.)

Swapping it in for the `watch` above:

```rust,no_run
# extern crate tokio;
# extern crate tokio_util;
#
use std::time::Duration;
use tokio::task::JoinSet;
use tokio::time::{sleep, timeout};
use tokio_util::sync::CancellationToken;

async fn wait_next_job(id: u32, next_job: &mut u32) -> u32 {
    sleep(Duration::from_millis(500)).await;
    let job = *next_job;
    *next_job += 1;
    println!("worker {} got job {}", id, job);
    job
}

async fn process_job(id: u32, job: u32) {
    sleep(Duration::from_millis(300)).await;
    println!("worker {} finished job {}", id, job);
}

async fn worker(id: u32, token: CancellationToken) {
    let mut next_job = 0;

    loop {
        let job = tokio::select! {
            job = wait_next_job(id, &mut next_job) => job,
            _ = token.cancelled() => { // wait directly on "being cancelled"
                println!("worker {} got cancelled, exiting", id);
                break;
            }
        };

        process_job(id, job).await;
    }
}

#[tokio::main]
async fn main() {
    let token = CancellationToken::new();

    let mut workers = JoinSet::new();
    for id in 0..3 {
        workers.spawn(worker(id, token.clone())); // each worker gets a clone
    }

    tokio::signal::ctrl_c().await.expect("couldn't listen for Ctrl-C");
    token.cancel(); // one command, everyone cancelled

    match timeout(Duration::from_secs(5), async {
        while workers.join_next().await.is_some() {}
    })
    .await
    {
        Ok(()) => println!("all exited"),
        Err(_) => {
            println!("timed out! force-aborting the remaining workers");
            workers.abort_all();
        }
    }
}
```

`token.cancelled()` is a `Future` that waits for "being cancelled"; one call to `token.cancel()` wakes every worker holding a `clone`. It reads exactly like "cancellation," fitting the need better than borrowing `watch` as a switch.

## Recap

- graceful shutdown: no hard cut — "signal the wrap-up → wait for completion (or a deadline) → exit cleanly."
- Three ingredients: signal source (`tokio::signal::ctrl_c()`), broadcasting shutdown (a `watch` flag), waiting for the drain (`JoinSet`'s `join_next()` until empty).
- `select!` is a good fit for waiting on "the next job" and "shutdown" at once; if the real work can't be safely cancelled, use `select!` only to obtain the job, then leave the `select!` to process it, so shutdown can't `drop` in-flight work midway (cancellation safety).
- The drain must have a deadline: wrap it in `tokio::time::timeout`, and on timeout `abort_all()` or `drop` the `JoinSet` — ask politely first; act if that fails.
- The better-fitting tool is `tokio_util`'s `CancellationToken`: `token.cancel()` gives the order and every `token.cancelled()` wakes up — semantically a better match than borrowing `watch`.
