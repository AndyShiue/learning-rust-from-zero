# Hand-writing join

## Goal of This Episode

Write a `Future` of your own that wraps several `Future`s into one, advancing them **concurrently**.

## Main Text

### The Goal: Waiting on Several `Future`s Together

Last episode ended with a question: two consecutive `.await`s wait in sequence. If I want several jobs going **at the same time**, waiting until they all finish, what do I do?

The answer is to write a `Future` ourselves — call it `JoinAll`. It takes in a whole `Vec` of `Future`s, and each time it's `poll`ed, it runs a `for` loop `poll`ing **each** unfinished `Future` inside once, nudging it forward. Only when all of them are done does it return `Ready` itself.

### Writing `JoinAll`

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};
use std::time::{Duration, Instant};

struct Delay {
    when: Instant,
}

impl Delay {
    fn new(duration: Duration) -> Delay {
        Delay {
            when: Instant::now() + duration
        }
    }
}

impl Future for Delay {
    type Output = ();

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let mut cx = Context::from_waker(Waker::noop());
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => {}
        }
    }
}

type BoxFuture = Pin<Box<dyn Future<Output = ()>>>;

// wrap a Vec of Futures, each held in a Some (swapped to None once done)
struct JoinAll {
    futures: Vec<Option<BoxFuture>>,
}

fn boxed<F>(future: F) -> BoxFuture
where
    F: Future<Output = ()> + 'static,
{
    Box::pin(future)
}

fn join_all(futures: Vec<BoxFuture>) -> JoinAll {
    JoinAll {
        futures: futures.into_iter().map(Some).collect(),
    }
}

impl Future for JoinAll {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut(); // JoinAll is Unpin, so we can get a plain &mut back
        let mut all_done = true;

        for slot in &mut this.futures {
            // temporarily take the Future out (slot becomes None) and poll it once
            if let Some(mut fut) = slot.take() {
                match fut.as_mut().poll(cx) {
                    Poll::Ready(_) => {
                        // done — don't put it back; the slot stays None
                    }
                    Poll::Pending => {
                        *slot = Some(fut); // not ready — put it back to poll next round
                        all_done = false;
                    }
                }
            }
        }

        if all_done {
            Poll::Ready(()) // everything finished
        } else {
            Poll::Pending // some remain unfinished
        }
    }
}

// a job with "two .awaits", so it takes multiple polls to complete
async fn worker(id: u32) {
    println!("worker {} starting", id);
    Delay::new(Duration::from_secs(1)).await;
    println!("worker {} past the first second", id);
    Delay::new(Duration::from_secs(1)).await;
    println!("worker {} done", id);
}

fn main() {
    block_on(async {
        let workers = vec![
            boxed(worker(1)),
            boxed(worker(2)),
            boxed(worker(3)),
        ];
        join_all(workers).await;
        println!("all workers are done");
    });
}
```

Here `type BoxFuture = Pin<Box<dyn Future<Output = ()>>>` gives the type a short name; `BoxFuture` is only a type alias and adds no extra wrapper. `dyn Future<Output = ()>` means: "I don't care which concrete kind of `Future` this is, as long as it returns `()` when done." `boxed(...)` calls `Box::pin`, producing a `Pin<Box<F>>`; its declared return type then erases the concrete `F` behind `dyn Future<Output = ()>`. The results therefore all have the same `BoxFuture` type, so the `Vec` inside `JoinAll` can hold them all.

You may notice this line:

```rust,ignore
let this = self.get_mut(); // JoinAll is Unpin, so we can get a plain &mut back
```

The `self` that `poll` receives has type `Pin<&mut JoinAll>`, not a plain `&mut JoinAll`. But in some situations, Rust lets us strip that outer `Pin` and recover the original mutable reference inside. That's what `get_mut()` does: it turns `Pin<&mut JoinAll>` back into `&mut JoinAll`. The formal justification comes later; for now, know only this: with a plain `&mut JoinAll` in hand, we can modify the `Vec` inside in the familiar ways.

Also worth a look:

```rust,ignore
if let Some(mut fut) = slot.take() { ... }
```

`slot` has type `&mut Option<BoxFuture>`. `Option::take` **takes the value out** of the `Option` (gaining ownership) and leaves `None` in its place. So if `slot` was `Some(fut)`, after calling `take()` we hold that `Some(fut)` while `slot` temporarily becomes `None`.

That's exactly what we want: take the child `Future` out and `poll` it once. If it finished, don't put it back — the `slot` stays `None`; if it hasn't, put it back with `*slot = Some(fut)` and keep `poll`ing next round.

### Why This Is Concurrent

Run it and you'll find the three `worker`s start nearly together and finish nearly together, taking **two seconds** in total rather than six.

The reason: one round of `JoinAll`'s `poll` nudges all three `worker`s once each. The three `Delay`s are timing simultaneously, so two seconds later all three `worker`s come due. That's concurrency — over the same stretch of time, three "all waiting" jobs get pushed forward together. Compare last episode: writing `worker(1).await; worker(2).await; worker(3).await;` runs one to completion before the next, six seconds in total.

### Even `Future`s Needing Many `poll`s Get Pushed Along Fine

Note that we deliberately chose `worker` — a job with **two `.await`s** — to put inside. This kind of `Future` isn't done in one `poll`; it takes many, many `poll`s (each `Delay` waits a second, during which the executor polls furiously) to walk through.

And `JoinAll` needn't worry about any of that — its only job is "`poll` each unfinished `Future` once per round." Which `.await` a given `Future` is stuck at internally, and how many more `poll`s it needs, is remembered by that `Future` itself (remember? `Future`s remember their own progress). `JoinAll` just keeps `poll`ing round after round, and each `Future` naturally steps forward until they all return `Ready`. This is exactly the power of the `poll` design: whoever merely composes `Future`s need not understand the internals of what's being composed.

Still, our executor remains that furiously busy-spinning dumb version. Next episode we fix that — letting the executor sleep when idle and get woken when it's time.

## Recap

- The way to advance multiple `Future`s concurrently is to write a `Future` yourself (`JoinAll`) whose `poll` uses a `for` loop to `poll` each child `Future` once.
- Finished children get swapped to `None`; only when all are `None` (done) does `JoinAll` return `Ready`.
- `JoinAll` needn't handle "this `Future` takes many `poll`s" — each child remembers its own progress; just keep `poll`ing round after round.
