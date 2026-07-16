# `select!`

## Goal of This Episode

Learn to use `select!` to wait for "the first of several branches to finish with an output that matches its pattern," and understand its close ties to cancellation.

## Main Text

### Waiting for "Whoever Arrives First"

`join!` waits for "**all** done." `select!` is in a sense its opposite: it waits on several branches at once, and when one completes with an output that matches the pattern on the left, the handler for that branch runs and the whole `select!` ends — **the other unfinished branches get `drop`ped**.

### Basic Syntax

Each `select!` branch looks roughly like:

```rust,ignore
tokio::select! {
    pattern = future => {
        // when future completes, its output is caught by pattern
    }
    _ = other_future => {
        // we don't care about other_future's output
    }
}
```

The `pattern` before the equals sign catches the output of the `Future` after it; variables bound in the pattern are available inside the braces on the right. What goes after the equals sign is just the `Future` to wait on — do **not** add `.await` yourself. `select!` takes care of `poll`ing these `Future`s simultaneously, waiting for one to finish with an output that matches its pattern.

If you don't need some `Future`'s output, ignore it with `_`, just like an ordinary `match` pattern:

```rust,ignore
tokio::select! {
    value = compute() => {
        println!("computed: {}", value);
    }
    _ = shutdown.recv() => {
        println!("got the shutdown signal");
    }
}
```

If the output is itself an `Option<T>` or `Result<T, E>`, the most intuitive style is to catch the whole value, then `match` it inside the handler:

```rust,ignore
tokio::select! {
    message = receiver.recv() => {
        match message {
            Some(message) => println!("got a message: {}", message),
            None => println!("the channel closed"),
        }
    }
    _ = shutdown.recv() => {
        println!("preparing to shut down");
    }
}
```

`select!` can itself have a return value — the last expression in the winning branch's braces. Much like `match`: every branch must return the same type.

```rust,ignore
let status = tokio::select! {
    value = compute() => {
        println!("computed: {}", value);
        "done"
    }
    _ = shutdown.recv() => {
        println!("got the shutdown signal");
        "shutdown"
    }
};

println!("status: {}", status);
```

The most classic use of `select!` is **timeout**: `select!` on "the real work" and "a timer" together and see which arrives first.

```rust,editable
extern crate tokio;

use tokio::time::{sleep, Duration};

async fn do_work() {
    sleep(Duration::from_secs(5)).await; // pretend the work takes five seconds
    println!("work finished");
}

#[tokio::main]
async fn main() {
    tokio::select! {
        _ = do_work() => {
            println!("the work completed fine");
        }
        _ = sleep(Duration::from_secs(1)) => {
            println!("timeout! the work took too long — not waiting");
        }
    }
}
```

The timer fires at one second, beating the five-second job, so `select!` takes the timer branch, prints "timeout," and **`drop`s the `do_work()` `Future`** — the work is thereby cancelled.

`select!` shines in these situations:

- **timeout** (the example above).
- **Receiving on multiple channels at once**: whichever channel has a message first gets handled.
- **Waiting for a shutdown signal**: doing normal work while also listening for "time to wrap up," responding to whichever comes first.

### Watch Out for cancellation safety with `select!` in Loops

We just mentioned `drop` — this is exactly last episode's **cancellation**: `drop`ping a `Future` cancels it. And `select!`, by design, `drop`s all the other branches when one wins. Grasping this keeps later `select!` usage out of the minefield.

`select!` is often placed inside a `loop` and run repeatedly (e.g. a server loop: each round `select!`s on "new work" or "the shutdown signal"). Such code demands special care about last episode's **cancellation safety**.

Recall: operations like `read_exact` that "span multiple advances and accumulate state" are **not cancellation safe** — cancelled midway, some data may already be consumed with the "fill the buffer" operation unfinished. And every round of `select!` may `drop` (cancel) this branch's `Future` because **another** branch finished first. Put a `read_exact` in a `select!` branch inside a `loop`, and it may well be cancelled mid-read, leaving a half-done state that's hard to resume.

Losing branches never run their braces — that's `select!`'s normal behavior and not the problem. The real thing to watch: before being discarded, the losing `Future` may already have produced external effects — bytes read off a socket, part of the data written out.

So the risk isn't "the handler didn't run"; it's "the `Future` got cancelled with half-done work never properly wrapped up." If the operation needs to accumulate progress across steps, keep the progress outside the `select!`, and let the branch wait only on a single safely cancellable small step. Later in this chapter we demonstrate designs following this principle.

### A Few Practical Extras

`select!` has some further commonly used features:

**Branch preconditions**: append `, if condition` to a branch. The condition can use variables that already exist before entering the `select!`, such as `accepting_jobs` below, but it cannot use variables that will be bound by the pattern on the left. `job` becomes available inside the handler only after `jobs.recv()` completes and `Some(job)` matches successfully.

```rust,ignore
tokio::select! {
    Some(job) = jobs.recv(), if accepting_jobs => {
        handle(job).await;
    }
    _ = shutdown.recv() => {
        accepting_jobs = false;
    }
}
```

The relevant steps in one call to `select!` occur in this order:

1. Evaluate every branch's `if` precondition. A branch whose condition is false is disabled for this call to `select!`.
2. Evaluate every `async` expression on the right of an equals sign, including expressions in disabled branches. When a condition is false, the expression is still evaluated to create a `Future`, but that `Future` is not `poll`ed. Here, "evaluated" means creating the `Future`, not running the `async` work inside it; ordinary expressions such as argument calculations performed before creating the `Future` still run.
3. `poll` the `Future`s of the remaining branches.
4. When a `Future` completes, try to match its output against the pattern on the left. If it matches, run the handler and finish the `select!`; if it does not, disable that branch and continue waiting for the others. The first branch to complete is therefore not necessarily the winner; the winner is a branch that completes and whose pattern matches.
5. When all branches are disabled, run `else`; if there is no `else`, `select!` panics.

**The `else` branch**: for example, if `Some(job) = jobs.recv()` encounters a closed channel, `.recv()` returns `None`, so `Some(job)` fails to match and that branch is disabled. If every other branch is also disabled, the `else` branch runs.

```rust,ignore
tokio::select! {
    Some(job) = jobs.recv(), if accepting_jobs => {
        handle(job).await;
    }
    Some(msg) = messages.recv(), if accepting_messages => {
        handle_message(msg).await;
    }
    else => {
        break; // no branch could run this round
    }
}
```

**Fairness and `biased;`**: by default `select!` picks **randomly** among simultaneously ready branches (so no branch always wins and starves the rest). If you'd rather have "check top to bottom in order," add `biased;` at the top.

```rust,ignore
tokio::select! {
    biased; // check top to bottom in order instead of randomly
    _ = high_priority() => { /* ... */ }
    _ = low_priority()  => { /* ... */ }
}
```

## Recap

- `select!` waits on several branches at once; the first branch to complete with an output matching its pattern runs its handler, and the rest get `drop`ped (cancelled).
- Basic syntax is `pattern = future => { ... }`; don't write `.await` on the left side of `=>`; use `_ = future` when the output isn't needed; `select!` can return the winning branch's value.
- `select!` is thus the place in a program that **manufactures the most cancellations**; great for timeouts, multi-channel receives, and shutdown signals.
- Using `select!` in a `loop` demands cancellation-safety care: keep non-cancellation-safe `Future`s like `read_exact` out of branches that may be `drop`ped.
- Extras: branch `if` (preconditions), branches disabled on pattern mismatch, `else` (when all branches are disabled), and `biased;` to turn default randomness into top-down order.
