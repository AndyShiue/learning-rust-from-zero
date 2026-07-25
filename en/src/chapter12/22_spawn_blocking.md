# `spawn_blocking`

## Goal of This Episode

Learn the discipline of "don't block the `Thread`," and how to house must-block work properly with `spawn_blocking`.

## Main Text

### An Iron Rule: Don't Block the `Thread`

`async` can advance masses of work on a few `Thread`s because everyone **takes turns**. An `.await` is a **possible** yield point: if the `Future` being awaited isn't ready and returns `Pending`, the `Task` yields the `Thread`, letting someone else run. If the `Future` is already ready, execution continues immediately without yielding.

That leads to an iron rule: **a `Task` must not go long without `.await`ing**. If a `Task` hogs the `Thread` — maybe doing an expensive computation (seconds of math), maybe calling some **synchronous** blocking function (`std::thread::sleep`, synchronous file reads, a slow synchronous database call) — it monopolizes that `Thread`. Until the blocking work finishes, **that `Thread` cannot `poll` any other `Task`**.

A bad example:

```rust,no_run
# extern crate tokio;
#
#[tokio::main]
async fn main() {
    // heavy synchronous computation inside an async task — bad!
    let sum: u64 = (0..2_000_000_000u64).sum(); // no .await anywhere in this stretch
    println!("sum: {}", sum);
}
```

This computation contains no `.await` from start to finish, so the `Future` running it cannot yield until the computation is done. If code like this runs in a spawned `Task`, it occupies one worker `Thread` for the duration and prevents that `Thread` from advancing other `Task`s, though other worker `Thread`s can continue running.

### The Fix: `spawn_blocking`

For this kind of "must block" work, the fix is `tokio::task::spawn_blocking`. It tosses the work onto a **dedicated blocking `Thread` pool** (whose `Thread`s are designed to be tied up), returning an awaitable handle:

```rust,no_run
# extern crate tokio;
#
#[tokio::main]
async fn main() {
    let handle = tokio::task::spawn_blocking(|| {
        // heavy computation goes to the dedicated blocking pool
        (0..2_000_000_000u64).sum::<u64>()
    });

    // if the work isn't done yet, awaiting here yields the thread until it is
    let sum = handle.await.expect("the blocking task failed");
    println!("sum: {}", sum);
}
```

The crux: because you wait on the handle with `.await`, your own `Task` **yields while the handle is not ready**, and the runtime can use the `Thread` to advance other `Task`s; when the blocking pool finishes the computation, you're woken. The slow computation is quarantined in its dedicated pool, never dragging down the `Thread`s doing `async` work.

(Incidentally: to "sleep a bit" in `async`, don't use `std::thread::sleep` — that blocks the `Thread`. Use `tokio::time::sleep(...).await`, which is `async` and duly yields.)

### Why Not Just `std::thread::spawn`

You might ask: to push work onto another `Thread`, doesn't the multithreading chapter give us `std::thread::spawn`?

The problem is "how to get the result back." The `JoinHandle` from `std::thread::spawn` requires calling `.join()` for the result — and `.join()` is **blocking**; it isn't `async` and can't be `.await`ed. Call `.join()` inside `async` and you've jammed the `Thread` again, right back at the original problem.

`spawn_blocking`'s value is that it packages up "when the synchronous work finishes in the blocking pool, notify the `.await`ing `async` `Task` to continue." You don't `.join()` a `std::thread::JoinHandle` yourself, nor wire up a `Waker`; just `.await` the returned handle, and while the result isn't ready your `Task` yields the `Thread`, then gets woken when the result is ready.

### But Long-lived Background `Thread`s Still Belong to `thread::spawn`

One last point worth making: `spawn_blocking` suits one-off work that **will finish**. If what you want is a **long-lived, independent background `Thread`** (say, a listener spinning an infinite loop for the program's whole lifetime), then `std::thread::spawn` is still the right tool.

Why? Because the blocking pool has limited capacity. Toss an infinite loop into `spawn_blocking` and it **permanently occupies** a slot in the pool, never giving it back — a misuse. Over time the pool fills up, and the short jobs that truly need it can't get in.

## Recap

- The iron rule: `Thread`s are yielded only at `.await`, so a `Task` mustn't go long without one — otherwise it hogs the `Thread` and stalls every other `Task` on it.
- Expensive computation and synchronous blocking calls (`std::thread::sleep`, sync I/O, slow sync DB calls) all block the `Thread`.
- `tokio::task::spawn_blocking` sends such work to a dedicated blocking pool and returns an `.await`able handle, letting your `Task` yield the `Thread` while the result isn't ready.
- We avoid `std::thread::spawn` because its `.join()` blocks and can't be `.await`ed; `spawn_blocking` builds the "done → wake the `Task`" bridge for you.
- But long-lived independent background `Thread`s still belong to `std::thread::spawn`; an infinite loop in `spawn_blocking` permanently eats a pool slot — a misuse.
