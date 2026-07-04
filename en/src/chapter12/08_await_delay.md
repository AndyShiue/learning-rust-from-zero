# Waiting on `Delay` with `.await`

## Goal of This Episode

Wait on last episode's `Delay` with `.await`, and watch with your own eyes — via `println!` — how a `Future` "pauses and resumes."

## Main Text

### Printing Around the `.await`s

We have `Delay`, and we have `block_on`. Now put `Delay` inside an `async` block, wait on it with `.await`, and add `println!` before and after every `.await` to observe the order of execution:

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

fn main() {
    block_on(async {
        println!("start");

        println!("waiting for the first delay…");
        Delay::new(Duration::from_secs(1)).await;
        println!("first delay done, moving on");

        println!("waiting for the second delay…");
        Delay::new(Duration::from_secs(1)).await;
        println!("second delay done, moving on");
    });
}
```

Run it, and the output appears step by step, like this:

```text
start
waiting for the first delay…
(one-second pause)
first delay done, moving on
waiting for the second delay…
(one-second pause)
second delay done, moving on
```

### How It "Pauses and Resumes"

This output order reveals how a `Future` operates. Remember, the whole `async` block is itself a `Future`, and `block_on` keeps `poll`ing it:

1. First `poll`: it runs from the top, prints "start" and "waiting for the first delay…", then hits the first `.await`. The `Delay` hasn't expired, so it returns `Pending` — and the whole `async` block returns `Pending` along with it, **pausing right here**.
2. The executor `poll`s again and again, but the `Delay` still isn't due; each time it gets stuck at that first `.await` returning `Pending`, unable to move on.
3. A second later, the `Delay` duly returns `Ready(())`. This `poll` gets past the first `.await`, prints "first delay done" and "waiting for the second delay…", hits the second `.await`, and returns `Pending` again — **paused at a new spot**.
4. One more second, the second `Delay` duly returns `Ready(())`; it clears the second `.await`, prints the final line, the whole `async` block returns `Ready`, and `block_on` finishes.

The crux: **each time it's `poll`ed, the `Future` picks up from where it last paused**, running until the next not-yet-ready `.await` where it may stop. This ability to "remember progress, pause, and resume from the same spot" is delivered by the "state machine" mentioned earlier — but this episode, just watch the phenomenon.

### `.await` Doesn't Give You Concurrency for Free

Note something important: the two `Delay`s above were waited on **one after the other**, taking two seconds in total. The second `Delay` started its countdown only after the first finished.

This trips up beginners a lot. `.await` means "wait for this to be ready" — it does **not** automatically make your program concurrent. Two `.await`s in a row wait dutifully in sequence; there's no cleverness that "waits on both together."

So what if I do want both `Delay`s timing simultaneously, one second total? That's next episode's topic — we'll build, by hand, a tool that advances multiple `Future`s concurrently.

## Recap

- Waiting on `Delay` with `.await` inside `async`, plus `println!`, lets you watch execution step forward.
- Each `poll` resumes the `Future` from where it last paused, until the next unfinished `.await` returns `Pending`.
- A `Future` remembers its progress and resumes in place — the state machine behind it deserves the credit.
- `.await` does **not** auto-parallelize: two consecutive `.await`s wait in sequence; concurrency needs other tools (one comes next episode).
