# `join!`

## Goal of This Episode

Learn to wait on multiple `Future`s at once within a single `Task` using `join!`, and understand why it's a macro.

## Main Text

### Concurrency Within One `Task`

In Episode 9 we hand-wrote `JoinAll`, advancing several `Future`s together. Tokio provides a ready-made `join!` that does the same thing:

```rust,editable
extern crate tokio;

use tokio::time::{sleep, Duration};

async fn fetch_a() -> i32 {
    sleep(Duration::from_secs(1)).await;
    1
}

async fn fetch_b() -> &'static str {
    sleep(Duration::from_secs(1)).await;
    "hello"
}

#[tokio::main]
async fn main() {
    // both Futures wait simultaneously — about one second total — returning a tuple
    let (a, b) = tokio::join!(fetch_a(), fetch_b());
    println!("a = {}, b = {}", a, b);
}
```

`join!` waits for **all** branches to complete before moving on, handing back each branch's result packed into a tuple. The two `fetch`es above each wait one second, but because they're concurrent, the total is about one second, not two.

### The Difference Between `spawn` and `join!`

Both `spawn` and `join!` give you concurrency, but by different means:

- `tokio::spawn` turns each job into an **independent `Task`** handed to the runtime, possibly run on different `Thread`s — hence `Send + 'static`.
- `join!` `poll`s its branches in turn **within the same `Task`**; they do **not** become independent `Task`s.

Because the branches stay inside the current `Task` and `join!` waits for all of them to complete, they never become independent `Task`s that can outlive the current scope. That makes `join!` a good fit for a **fixed number** of concurrent I/O operations that should all complete within the current scope — calling three APIs at once, reading two files at once.

### `join!`'s Concurrency Is Not CPU Parallelism

An important limitation to clear up. `join!`'s branches are **`poll`ed in turn** on **the same `Task`**, which means its concurrency is the "interleaved switching" kind — it **cannot** be CPU parallelism.

The consequence is practical: if one branch goes a long time without `.await`ing (doing lengthy computation, or calling a synchronous blocking function), it hogs the `Thread` — and since everyone takes turns on the same `Task`, **even the other branches within the same `join!` go un`poll`ed**. The illusion of concurrency shatters on the spot.

This is exactly last episode's "don't block the `Thread`" iron rule playing out in `join!`. If some branch really has heavy lifting to do, use `spawn_blocking` — don't let it wedge inside the `join!`.

### Why `join!` Is a Macro

You've probably noticed `join!` is also a macro, not a function. Why must it be, this time?

Because it has to swallow any number of `Future`s of mutually different types, then return a tuple shaped to match. `join!(a, b)` and `join!(a, b, c, d)` both work, each branch's `Future` type entirely its own; the return type changes accordingly to `(A::Output, B::Output)` or `(A::Output, B::Output, C::Output, D::Output)`.

Rust functions can't do that: a function can't take an arbitrary number of parameters, much less have its returned tuple type shift to match. Only a macro can generate, at **compile time**, code tailored to the `Future`s you actually threw in.

The contrast with Episode 9's `JoinAll` sharpens the picture: `JoinAll` handles "**same type, dynamic count**" — a `Vec<F>` all of one `Future` kind, the count settled at runtime. `join!` is the reverse: "**mixed types, fixed count**" — count and types locked in as you write the code, so a macro can unroll them at compile time into a tuple that matches exactly.

## Recap

- `join!` waits on multiple `Future`s at once **within one `Task`**, returning the results as a tuple once all complete.
- Unlike `spawn`: `join!`'s branches don't become independent `Task`s — suited to a fixed number of concurrent I/O operations that should all complete within the current scope.
- `join!`'s concurrency isn't CPU parallelism: branches take turns being `poll`ed on one `Task`, and one stuck branch starves the rest.
- `join!` is a macro because it takes "any number + mutually different types" of `Future`s and returns a correspondingly typed tuple — impossible for a function.
- Against our own `JoinAll` (same type, dynamic count), `join!` is mixed types, fixed count.
