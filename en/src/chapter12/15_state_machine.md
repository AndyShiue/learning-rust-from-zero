# The State Machine behind `async fn`

## Goal of This Episode

Unmask `async fn`: the compiler rewrites it into a **state machine** that can pause and resume.

## Main Text

### `.await` Doesn't Open a New `Thread`

First, let's dispel a possible misconception. Seeing `.await`, you might imagine it "secretly opens a `Thread` in the background to wait." **Absolutely not.** From Episode 6 until now, the executor of our hand-written runtime has been one `Thread` `poll`ing over and over, start to finish — `.await` conjured no new `Thread`s.

So what does `.await` actually do? It **cuts your function into segments** — every `.await` is a cut point. The function can pause at a cut point, hand control back to the executor, and later resume from that same cut point.

The compiler achieves this by rewriting the whole `async fn` into a **state machine**: "which state am I in" records the progress, and the next `poll` picks up from that state and continues.

### What an `async fn` Gets Rewritten Into

Suppose we have this `async fn` that waits twice:

```rust,noplayground
# use std::future::Future;
# use std::pin::Pin;
# use std::task::{Context, Poll};
# use std::thread;
# use std::time::{Duration, Instant};
#
# struct Delay {
#     when: Instant,
#     started: bool,
# }
#
# impl Delay {
#     fn new(duration: Duration) -> Delay {
#         Delay {
#             when: Instant::now() + duration,
#             started: false,
#         }
#     }
# }
#
# impl Future for Delay {
#     type Output = ();
#
#     fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
#         let this = self.get_mut();
#         if Instant::now() >= this.when {
#             Poll::Ready(())
#         } else {
#             if !this.started {
#                 this.started = true;
#                 let waker = cx.waker().clone();
#                 let when = this.when;
#                 thread::spawn(move || {
#                     let now = Instant::now();
#                     if now < when {
#                         thread::sleep(when - now);
#                     }
#                     waker.wake();
#                 });
#             }
#             Poll::Pending
#         }
#     }
# }
#
async fn two_delays() {
    Delay::new(Duration::from_secs(1)).await;
    println!("one second is up");
    Delay::new(Duration::from_secs(1)).await;
    println!("two seconds are up");
}
#
# fn main() {}
```

On seeing it, the compiler rewrites it into an `enum` — each "state" standing for "which segment am I stuck in":

- `Start`: not yet begun.
- `FirstDelay`: waiting on the first `Delay` (the unfinished `Delay` itself must be stored in here too).
- `SecondDelay`: waiting on the second `Delay`.
- `Done`: finished.

It then implements `Future` for this `enum`, with `poll` using a `match` on the current state to decide what to do. Let's write this rewrite out **by hand**, and you'll see what an `async fn` looks like underneath:

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
    started: bool,
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
                let waker = cx.waker().clone();
                let when = this.when;
                thread::spawn(move || {
                    let now = Instant::now();
                    if now < when {
                        thread::sleep(when - now);
                    }
                    waker.wake();
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

// this is roughly what the two_delays async fn looks like underneath
enum TwoDelays {
    Start,
    FirstDelay(Delay), // waiting on the first Delay — keep it stored
    SecondDelay(Delay), // waiting on the second Delay
    Done,
}

impl Future for TwoDelays {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        loop {
            match this {
                TwoDelays::Start => {
                    // enter first segment: create first Delay and switch state
                    *this = TwoDelays::FirstDelay(Delay::new(Duration::from_secs(1)));
                }
                TwoDelays::FirstDelay(delay) => match Pin::new(delay).poll(cx) {
                    Poll::Ready(()) => {
                        println!("one second is up");
                        *this = TwoDelays::SecondDelay(Delay::new(Duration::from_secs(1)));
                    }
                    Poll::Pending => return Poll::Pending, // stuck in this segment — pause
                },
                TwoDelays::SecondDelay(delay) => match Pin::new(delay).poll(cx) {
                    Poll::Ready(()) => {
                        println!("two seconds are up");
                        *this = TwoDelays::Done;
                        return Poll::Ready(());
                    }
                    Poll::Pending => return Poll::Pending,
                },
                TwoDelays::Done => panic!("shouldn't be polled after Ready"),
            }
        }
    }
}

fn main() {
    println!("start");
    block_on(TwoDelays::Start); // equivalent to block_on(two_delays())
}
```

> The bare-bones `Delay` and `block_on` from earlier are included above only so this hand-written state machine actually runs. The star of this example isn't the executor but `TwoDelays`: it demonstrates the kind of state machine an `async fn` might be rewritten into.

### Side by Side

Compare this hand-written state machine with the original `async fn`:

- The **progress** through the original `async fn` becomes **a variant** of the `enum`.
- **Local variables** still needed across an `.await` (here, the unfinished `Delay`) get stored inside the variant and carried along.
- Each `.await` becomes "`poll` the child `Future`: on `Ready`, switch to the next state and continue; on `Pending`, `return Poll::Pending` and pause."
- On the next `poll`, the `match` jumps straight to the state where it last stopped and continues from there — that's "resuming in place."

This exactly explains the phenomena of the past few episodes: why a `Future` remembers where it got to on every `poll`, and why it resumes from the same place after pausing. Because it simply is a state machine that remembers "which state I'm in."

When you write `async fn` day to day, all of this is generated automatically by the compiler — you never hand-write such an `enum`. But knowing its true face is what makes the upcoming episodes on `Pin` meaningful — because this auto-generated state machine hides a danger related to "moving memory around." Next episode we look at that danger.

## Recap

- `.await` does **not** open a new `Thread`; it cuts the function into pausable, resumable segments.
- The compiler rewrites an `async fn` / `async` block into a **state machine** (conceptually an `enum`): progress becomes variants; locals crossing an `.await` are stored in the variant.
- `poll` uses `match` on the current state: child `Future` `Ready` → switch to the next state; `Pending` → return `Pending` and pause.
- The next `poll` jumps back to the last state and resumes in place — that's how a `Future` "remembers its progress."
- The rewrite is normally done by the compiler automatically, but understanding it is the prerequisite for understanding `Pin` later.
