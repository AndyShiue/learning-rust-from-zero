# Writing a `Delay` `Future` by Hand

## Goal of This Episode

Hand-write your first `Future` that genuinely returns `Pending` — a timer called `Delay` — and run it with last episode's executor.

## Main Text

### Why Build a `Delay`

Last episode we promised a `Future` that "really needs to wait." But the real world's waitable events — network packets, disks, databases — all drag in a pile of operating system concepts, far too complex for a first encounter with `Pending`.

So we'll prop things up with the simplest possible thing: a **timer**. The rules are plain:

- Not yet expired → return `Pending` (not ready).
- Expired → return `Ready` (done).

This `Delay` will star in the next several episodes: whenever we need "an event that takes time to become ready," we'll use it as the stand-in for studying `.await`, join, and the `Waker`.

### Writing `Delay`

`Delay` remembers an "expiry moment" `when`, and each time it's `poll`ed, it checks whether the current time has passed it:

```rust,noplayground
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};
use std::time::{Duration, Instant};

struct Delay {
    when: Instant, // the moment it's scheduled to complete
}

impl Delay {
    fn new(duration: Duration) -> Delay {
        Delay {
            when: Instant::now() + duration, // expires duration from now
        }
    }
}

impl Future for Delay {
    type Output = ();

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            println!("Delay finished");
            Poll::Ready(()) // expired
        } else {
            Poll::Pending // not yet — ask again later
        }
    }
}
#
# fn main() {}
```

`poll`'s logic is that direct: time's up, return `Ready(())`; otherwise `Pending`. `Output` is `()` because this timer has no value to give when done — it's purely the event "the time has arrived."

### Running It on Our executor

Carry over last episode's dumbest `block_on`, and our own `Delay` runs:

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
            println!("Delay finished");
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

fn main() {
    println!("start");
    block_on(Delay::new(Duration::from_secs(1)));
    println!("one second has passed");
}
```

Run it and you'll see a one-second pause after "start" before "one second has passed" prints. Our first `Future` that genuinely returns `Pending` works! During that second, `block_on`'s loop frantically `poll`s and keeps getting `Pending`, until the time finally arrives and it gets `Ready`.

> **Note**: the web version's code sandbox doesn't always show time delays clearly. There are more timing and waiting examples later in this chapter; if you want to actually feel effects like "pause one second" or "wait on different jobs at once," copy the programs onto your own machine and run them there.

### Honestly: This `Delay` Is Oversimplified

This version runs, but it's actually **cutting corners** — `poll`'s `cx` parameter is written `_cx` and never used.

Inside `cx` lives something called a `Waker`. Before returning `Pending`, a proper `Future` should use it to tell the executor "call me when I'm ready." Our `Delay` does no such thing. Then why does it still work? Because the executor we paired it with is equally dumb — it never sleeps; on `Pending` it immediately `poll`s again, so nobody needs to notify it anyway.

In other words, this `Delay` only functions because it's **bound** to this dumb executor. Drop it onto a real executor — one that sleeps and continues only when woken by a `Waker` — and it would return `Pending` without ever notifying anyone. The executor would sleep forever; this `Delay` would effectively never complete.

We'll fix this corner-cutting later. But before that, we'll use this `Delay` to build up `.await` and some concurrency concepts. Next episode: what happens when you `.await` this `Delay` inside `async`.

## Recap

- Real I/O is too complex, so a bare-bones timer serves as the first encounter with `Pending`.
- `Delay` uses a timer to simulate "an event that takes time": `Pending` before expiry, `Ready` after — it stands in for the real thing over the next episodes.
- A custom `Future` — `impl Future` plus a `poll` implementation — runs fine with last episode's `block_on`.
- This `Delay` is oversimplified: `poll` ignores the `Waker` in `cx`, and it only happens to work because the paired executor never sleeps; on a sleeping executor it would break. We'll fix it later.
