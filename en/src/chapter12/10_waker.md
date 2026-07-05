# Waking the executor with `Thread`s and `Waker`

## Goal of This Episode

Teach the executor to sleep: `park` when there's nothing to do, and get woken by a `Waker` when an event completes. Along the way, nail down `poll`'s two important contracts.

## Main Text

### No More Busy-spinning

So far our executor has a nasty habit: on `Pending`, it immediately `poll`s again, burning an entire thread on a job that's still just waiting. A real runtime doesn't do this — it goes to **sleep** when idle and gets woken when there's actual progress.

The waking tool is the `Waker` we've been neglecting for several episodes. `cx.waker()` yields a `Waker`; before returning `Pending`, a `Future` should hand that `Waker` to "whoever is responsible for announcing it's ready." When the event completes, that party calls `waker.wake()`, rousing the sleeping executor.

This episode we make **another `Thread`** responsible for timing: on `Delay`'s first `poll`, `spawn` a `Thread` that `sleep`s, and once well rested, `wake()`s the executor.

### Making a `Waker` of Our Own

First, how a `Waker` is born. The standard library provides a `Wake` `trait`: implement its `wake` method to describe "what should happen on wakeup," then convert with `Waker::from` into a `Waker`.

We want "waking" to mean rousing the executor's `Thread`, so make a small type that remembers it:

```rust,noplayground
use std::sync::Arc;
use std::task::Wake;
use std::thread::{self, Thread};

struct ThreadWaker {
    thread: Thread, // the executor's Thread
}

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.thread.unpark(); // waking = unparking that Thread
    }
}
#
# fn main() {}
```

Note that `wake`'s `self` is `Arc<Self>` (another of those special types allowed in the `self` position, as mentioned last episode). `Waker::from(Arc::new(...))` turns it into a `Waker`.

### An executor That Sleeps

With `ThreadWaker`, the executor can switch to "`park` and sleep on `Pending`":

```rust,noplayground
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
#
# struct ThreadWaker {
#     thread: Thread,
# }
#
# impl Wake for ThreadWaker {
#     fn wake(self: Arc<Self>) {
#         self.thread.unpark();
#     }
# }

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);

    // make a Waker that unparks this executor Thread
    let waker = Waker::from(Arc::new(ThreadWaker {
        thread: thread::current(),
    }));
    let mut cx = Context::from_waker(&waker);

    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(), // nothing to do — sleep until unparked
        }
    }
}
```

### A `Delay` That Wakes Others Itself

Finally, rewrite `Delay`: before returning `Pending`, `spawn` a `Thread` to sleep, waking on schedule:

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
use std::time::{Duration, Instant};

struct ThreadWaker {
    thread: Thread,
}

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.thread.unpark();
    }
}

struct Delay {
    when: Instant,
    started: bool, // has the timing Thread been started
}

impl Delay {
    fn new(duration: Duration) -> Delay {
        Delay {
            when: Instant::now() + duration,
            started: false,
        }
    }
}

impl Future for Delay {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        if Instant::now() >= this.when {
            Poll::Ready(())
        } else {
            if !this.started {
                this.started = true;
                let waker = cx.waker().clone(); // give a Waker replica to the timing Thread
                let when = this.when;
                thread::spawn(move || {
                    let now = Instant::now();
                    if now < when {
                        thread::sleep(when - now);
                    }
                    waker.wake(); // time's up — wake the executor
                });
            }
            Poll::Pending
        }
    }
}

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let waker = Waker::from(Arc::new(ThreadWaker {
        thread: thread::current(),
    }));
    let mut cx = Context::from_waker(&waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(),
        }
    }
}

fn main() {
    block_on(async {
        println!("start");
        Delay::new(Duration::from_secs(1)).await;
        println!("one second later");
        Delay::new(Duration::from_secs(1)).await;
        println!("two seconds later");
    });
}
```

This time the executor no longer burns CPU spinning — one `poll` yields `Pending`, it `park`s and sleeps a full second, and only after the timing `Thread`'s `wake()` rouses it does it `poll` again.

### If `wake` Happens Before `park`, Do We Sleep Forever?

There's a timing concern worth raising. Between the executor's `poll` returning `Pending` and it actually executing `thread::park()`, there's a small gap. What if the timing `Thread` happens to `wake` → `unpark` inside that gap? Wouldn't the executor be "woken first, then go to sleep," the `unpark` land on nothing, and the executor never wake?

No. `unpark` is designed so that if the `Thread` isn't parked yet, it **leaves a permit**. The next time that `Thread` calls `park()`, it sees the permit and **returns immediately** — no sleeping at all. So whether `wake()` (i.e. `unpark`) lands before or after `park()`, nothing is missed. It's precisely because `park` / `unpark` carry this guarantee that we dare use them directly as our "sleep / wake" tools.

### `poll`'s Two Contracts

With this `poll` / `wake` logic freshly assembled, let's spell out the standard library's two important contracts on `Future::poll`:

**Contract one: only the `Waker` from the most recent poll counts.** On each `poll`, the `Waker` from `cx.waker()` **may differ** (e.g. the `Task` got moved to another thread). So a correct `Future` should re-store the latest `Waker` on every `poll` and wake with the newest one.

Our `Delay` cheats — thanks to the `started` flag, it grabs the `Waker` once on the first `poll` and never again. That causes no harm here purely because our executor uses **the same** `Waker` throughout, so the stale one happens to still work. Swap in an executor that hands out a different `Waker` each time, and this `Delay` would fail to wake it. In practice you must honestly re-store it each time; the serious versions later in this chapter all do.

**Contract two: after `Ready`, never `poll` again.** Once a `Future` returns `Ready`, it must **not** be polled again; otherwise behavior is unguaranteed (it might panic, might wedge). So the executor must remember: once a `Future` finishes, remove it and don't touch it. Our current `block_on` `return`s the moment it gets `Ready`, so it can't offend; but when we're managing many `Future`s at once, this needs real care (we'll do that next episode).

### One `Thread` per `Future`? Not Acceptable

Finally, some cold water: right now, "every waiting `Delay` `spawn`s a `Thread`." That's clearly no good — remember Episode 2? `Thread`s are memory-hungry. Ten thousand waiting connections would mean ten thousand `Thread`s — **exactly the problem `async` set out to avoid**, and we've circled right back into it.

The next several episodes solve this for good. First we'll wrap each woken `Future` into something called a **`Task`** that can queue itself back onto the executor's "ready queue" (to-do queue); after that we can introduce the **reactor**, using one or a few `Thread`s to watch large amounts of I/O — escaping "one job, one `Thread`" once and for all.

## Recap

- Before returning `Pending`, a `Future` should hand `cx.waker()` to "whoever will notify it"; on completion, `waker.wake()` rouses the executor.
- DIY `Waker`: implement the `Wake` `trait`'s `wake` method, then convert via `Waker::from(Arc::new(...))`.
- The executor sleeps with `thread::park()` and the `Waker` wakes it with `unpark()`; `unpark` leaves a permit, so `wake` before or after `park` is never missed.
- **Contract one**: the `Waker` may differ per `poll`; a correct `Future` re-stores the latest one each time (`Delay` storing it once is an oversimplification).
- **Contract two**: no `poll`ing after `Ready`; the executor must remove finished `Future`s.
- "One `Thread` per `Future`" is too costly; starting next episode we switch to `Task` + ready queue, and later a reactor, to fix it.
