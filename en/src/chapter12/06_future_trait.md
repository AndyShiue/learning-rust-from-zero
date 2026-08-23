# The `Future` `trait` and the Most Bare-bones Executor

## Goal of This Episode

Read and understand the formal definition of the `Future` `trait`, and hand-write the dumbest executor that actually runs.

## Main Text

### What the `Future` `trait` Looks Like

We've been saying "`Future`" for several episodes; time to see its real definition. It's a `trait` in the standard library:

```rust,ignore
pub trait Future {
    type Output;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

Piece by piece:

- `type Output` is the type of the value this `Future` will yield once complete.
- `poll` is the core method. It asks the `Future`: "are you done yet?"
- The return value is `Poll`, an `enum` with just two states:

```rust,ignore
pub enum Poll<T> {
    Ready(T), // done — here's the result
    Pending,  // not yet — ask again later
}
```

So the way to advance a `Future` is to `poll` it repeatedly: `Pending` means not done yet, `Ready(value)` means finished and the result can be taken.

### Why `poll`'s `self` Is `Pin<&mut Self>`

You've probably noticed something odd: `poll`'s first parameter isn't the familiar `self` / `&self` / `&mut self`, but `self: Pin<&mut Self>`.

Don't panic — later in this chapter we'll spend several episodes on the details of `Pin`. For now, accept one thing: **`Pin` is a very special type**. Rust decrees that besides the `self` / `&self` / `&mut self` we already know, only a small handful of "smart pointers" may sit in the `self` position:

- `Box<Self>`, `Rc<Self>`, `Arc<Self>`.
- And `Pin<...>`.

Your own custom types generally **can't** be used in the `self` position like that. `poll` can be written `self: Pin<&mut Self>` precisely because `Pin` is special enough. For the moment, think of `Pin<&mut Self>` as "a restricted `&mut Self`" — it lets you modify the `Future`'s contents but forbids moving the whole thing away. Why that restriction exists comes later.

### The Most Bare-bones Executor

`poll` is the `Future`'s engine, but someone has to crank it — the role that "keeps `poll`ing until completion" is called the **executor**. Rust's standard library ships **no** executor, so let's write the dumbest possible one ourselves:

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

fn block_on<F: Future>(future: F) -> F::Output {
    // put the Future on the heap and "pin" it, getting a Pin<Box<F>>
    let mut future = Box::pin(future);

    // make a Context wrapping a do-nothing Waker — what it's for comes later
    let mut cx = Context::from_waker(Waker::noop());

    loop {
        // .as_mut() borrows the Pin<Box<F>> as Pin<&mut F>, exactly the type poll wants
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value, // done — return the result
            Poll::Pending => {
                // not ready; this dumbest executor just polls again (busy-spins)
            }
        }
    }
}

fn main() {
    let value = block_on(async {
        println!("the async block is running");
        1 + 2
    });
    println!("the result is {}", value);
}
```

### Two Little Value-shuffling Tools

This executor used two `Pin`-related tools; a quick introduction:

`Box::pin(x)` has type `fn pin(x: T) -> Pin<Box<T>>` — it puts the value on the heap and pins it with `Pin`. For now, just treat it as "a restricted pointer."

`as_mut` on `Pin<Ptr>` has type `fn as_mut(&mut self) -> Pin<&mut <Ptr as Deref>::Target>`, which for `Pin<Box<T>>` means `-> Pin<&mut T>` — exactly the `self: Pin<&mut Self>` that `poll` needs. The key point is that `as_mut` is only a mutable borrow; it doesn't give `future` away, which is why our `loop` can `poll` the same `future` over and over.

### Honestly: Nothing Has Actually Been Waiting So Far

Time for an honest confession. From Episode 3 through this one, the `async fn`s and `async` blocks we wrote haven't **really waited for anything** — none of them contain a `.await` that could stall. For such `Future`s, the very first `poll` returns `Ready`, and our `Pending` branch never runs at all.

In other words, the examples so far were purely demonstrations of the `Future` and executor machinery — not yet programs that "really use `async`." Next episode we hand-write a `Delay` — a `Future` that genuinely returns `Pending` and needs a stretch of time to finish. That will be our first more respectable piece of async work.

### Executors Come in Many Designs

One last idea to keep: Rust's standard library only defines the `Future` `trait`; **how to implement an executor is left entirely up to the runtime**. What we wrote this episode is the dumb version that "busy-spins re-polling on `Pending`" — a colossal waste of CPU. Real runtimes are much smarter: they sleep when there's nothing to do and get woken when there is.

Precisely because the standard library doesn't dictate how executors are written, we have Tokio, smol, and other runtimes each with their own character. Over the coming episodes, we'll evolve this dumbest version step by step toward something resembling a real runtime.

## Recap

- The heart of the `Future` `trait` is `poll`, returning `Poll::Ready(value)` (done) or `Poll::Pending` (not yet).
- `poll`'s `self` is `Pin<&mut Self>`; `Pin` is one of the few special types allowed directly in the `self` position — for now, "a restricted `&mut Self`."
- The **executor** keeps `poll`ing a `Future` until `Ready`; the standard library ships none, so you build one or use a runtime's.
- `Box::pin` heap-allocates and pins the value; `as_mut` lends out `Pin<&mut T>`; together they let the `loop` repeatedly `poll` the same `Future`.
- The earlier episodes' `async` never waited on anything — one `poll` and it's `Ready`; next episode's `Delay` will genuinely go `Pending`.
- The standard library defines only `Future`; executors are the runtime's business — which is why Tokio, smol, and friends exist.
