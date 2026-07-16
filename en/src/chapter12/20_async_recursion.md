# `async` Recursion

## Goal of This Episode

Understand why an `async fn` can't call itself directly, and how to fix it with `Box::pin`.

## Main Text

### Direct Recursion Fails to Compile

Let's try an `async` factorial — an `async fn` that `.await`s itself:

```rust,compile_fail
async fn factorial(n: u64) -> u64 {
    if n == 0 {
        1
    } else {
        n * factorial(n - 1).await // compile error
    }
}

fn main() {}
```

The compiler refuses outright:

```text
error[E0733]: recursion in an async fn requires boxing
```

### Why? Because the `Future` Type's Size Can't Be Determined

Recall Episode 15: an `async fn` is rewritten into a state machine, and anything used across an `.await` gets stored inside it.

The key here isn't whether the recursion terminates at runtime. `n == 0` is of course the base case, and execution would stop; but before the program ever runs, the compiler must first determine how big the `Future` returned by `factorial` is.

Roughly picture what it would need to look like:

```rust,compile_fail
enum FactorialFuture {
    Start { n: u64 },
    Waiting {
        n: u64,
        child: FactorialFuture,
    },
    Done,
}
#
# fn main() {}
```

The `Waiting` state must store the `factorial(n - 1)` being `.await`ed — and `factorial(n - 1)` returns the very same `FactorialFuture`. The type directly contains itself, and when the compiler tries to compute how much space the `child` field takes, no fixed answer ever comes out.

You've seen this situation before. Chapter 5's discussion of recursive types hit exactly the same problem: a `struct` directly containing itself has infinite size. The fix back then was `Box`, putting the recursive part on the heap — no matter how big `T` is, a `Box<T>` itself is always just pointer-sized.

### The Fix: Wrap the Recursive Call in `Box::pin`

The fix for `async` recursion is the same: wrap the `Future` produced by the recursive call in `Box::pin`. Now the state machine stores only a fixed-size pointer instead of directly embedding another state machine of the same type:

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

async fn factorial(n: u64) -> u64 {
    if n == 0 {
        1
    } else {
        n * Box::pin(factorial(n - 1)).await
    }
}

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let mut cx = Context::from_waker(Waker::noop());
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(v) => return v,
            Poll::Pending => {}
        }
    }
}

fn main() {
    let result = block_on(factorial(5));
    println!("5! = {}", result);
}
```

> The most bare-bones `block_on` from earlier is attached above (this `factorial` has no `.await` that genuinely waits, so that version suffices).

`Box` and `Pin` each handle a different job here: `Box` lets the state machine store only a fixed-size pointer, while `Pin` makes the `Future` inside safely `poll`able. Writing only `Box::new(factorial(n - 1)).await` isn't enough, because the `Future` returned by an `async fn` isn't guaranteed to implement `Unpin`, and `Box<F>` implements `Future` only when `F: Unpin`. So we use `Box::pin` to get a `Pin<Box<F>>`; as long as `F: Future`, `Pin<Box<F>>` itself also implements `Future` and can be `.await`ed directly.

At this point, we've walked the whole of `async`'s underlying machinery — `Future`, executor, reactor, state machines, `Pin` — from start to finish. From next episode on, we return to Tokio to see what conveniences a truly mature runtime offers for writing `async` code.

## Recap

- An `async fn` calling itself directly fails to compile, because the compiler can't determine the state machine type's size.
- A base case only settles whether execution stops at runtime, not the type's size at compile time; it's the same problem as Chapter 5's recursive types — self containing self, infinite size.
- The fix is wrapping the recursive call in `Box::pin`, so the state machine stores only a fixed-size pointer.
