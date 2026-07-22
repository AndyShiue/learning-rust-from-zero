# `spawn` and `JoinHandle`

## Goal of This Episode

Let `spawn`ed `Task`s hand their results back, by adding a `JoinHandle` — an `.await`able waiting end.

## Main Text

### Only Three Things Different from Last Episode

Last episode's `spawn` had a regret: it only accepted `Future<Output = ()>` — once the work finished, that was that; no way to return the result. This episode fills that in.

The good news: the core scheduling logic **doesn't change at all**. We add just three things on top:

1. A new shared state `Shared<T>`, plus a `JoinHandle<T>` (which is itself a `Future`).
2. `Executor::spawn` upgrades from accepting only `Future<Output = ()>` to accepting `Future<Output = T>` and returning `JoinHandle<T>`.
3. `Executor::block_on` upgrades from returning `()` to returning the passed-in `Future`'s value, `T`.

### How the Finishing Side Notifies the Waiting Side

The core question: when the background `Task` finishes, how does it deliver the result to "whoever is `.await`ing it"?

The answer: **through a piece of shared state, `Shared<T>`** — not one `Future` notifying another directly. `Shared<T>` holds two things: the computed result, and "the waiter's `Waker`."

The flow underneath goes like this:

- The `JoinHandle<T>` is not wrapped into an independent `Task` and never enters the ready queue by itself. It's just one of the `Future`s inside the waiter's `Task`, `poll`ed along the way during `.await`.
- When the waiter `poll`s the `JoinHandle` and the result isn't ready, the `JoinHandle` stores `cx.waker()` (that is, **the waiter's own** `Waker`, since a `JoinHandle` has no independent `Waker`) into `Shared<T>` and returns `Pending`.
- When the background `Task` finishes, it puts the result into `Shared<T>`, then takes out that stored `Waker` and `wake()`s it — so the waiter's `Task` is requeued onto the ready queue and the executor gets `unpark`ed. Next time the waiter is `poll`ed, it finds the result in `Shared<T>`.

```rust,editable
use std::collections::VecDeque;
use std::future::Future;
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
use std::time::{Duration, Instant};

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

type Queue = Arc<Mutex<VecDeque<Arc<Task>>>>;

struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    queue: Queue,
    executor_thread: Thread,
    queued: AtomicBool,
    done: AtomicBool,
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        if !self.queued.swap(true, Ordering::SeqCst) {
            self.queue.lock().expect("lock failed").push_back(self.clone());
            self.executor_thread.unpark();
        }
    }
}

// state shared between a background Task and its JoinHandle
struct Shared<T> {
    state: Mutex<(Option<T>, Option<Waker>)>, // (result, waiter's Waker)
}

struct JoinHandle<T> {
    shared: Arc<Shared<T>>,
}

impl<T> Future for JoinHandle<T> {
    type Output = T;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<T> {
        let mut state = self.shared.state.lock().expect("lock failed");
        if let Some(value) = state.0.take() {
            Poll::Ready(value) // the result is ready
        } else {
            state.1 = Some(cx.waker().clone()); // not yet — store the waiter's own Waker
            Poll::Pending
        }
    }
}

struct Executor {
    queue: Queue,
    executor_thread: Thread,
    remaining: usize,
}

impl Executor {
    fn new() -> Executor {
        Executor {
            queue: Arc::new(Mutex::new(VecDeque::new())),
            executor_thread: thread::current(),
            remaining: 0,
        }
    }

    // spawn<T>: accept a Future<Output = T>, return a JoinHandle<T>
    fn spawn<T, F>(&mut self, future: F) -> JoinHandle<T>
    where
        F: Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        let shared = Arc::new(Shared { state: Mutex::new((None, None)) });
        let shared_for_task = shared.clone();

        // wrap the Future<Output = T> into a Future<Output = ()> the executor understands
        let task_future = async move {
            let value = future.await; // actually run the job
            let mut state = shared_for_task.state.lock().expect("lock failed");
            state.0 = Some(value); // deposit the result
            if let Some(waker) = state.1.take() {
                waker.wake(); // wake whoever is waiting
            }
        };

        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(task_future)),
            queue: self.queue.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
            done: AtomicBool::new(false),
        });

        self.remaining += 1;
        task.wake();

        JoinHandle { shared }
    }

    fn block_on<T, F>(&mut self, future: F) -> T
    where
        F: Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        let handle = self.spawn(future); // spawn it as a Task; keep its JoinHandle

        // run until every Task completes (the loop is identical to last episode)
        while self.remaining > 0 {
            loop {
                let task = self.queue.lock().expect("lock failed").pop_front();
                let Some(task) = task else { break };

                if task.done.load(Ordering::SeqCst) {
                    continue;
                }

                task.queued.store(false, Ordering::SeqCst);
                let waker = Waker::from(task.clone());
                let mut cx = Context::from_waker(&waker);
                let mut future = task.future.lock().expect("lock failed");

                if future.as_mut().poll(&mut cx).is_ready() {
                    task.done.store(true, Ordering::SeqCst);
                    self.remaining -= 1;
                }
            }

            if self.remaining > 0 {
                thread::park();
            }
        }

        // pull the result out of the Shared and return it
        handle.shared.state.lock().expect("lock failed").0.take().expect("result not ready")
    }
}

fn main() {
    let mut executor = Executor::new();

    // spawn a background Task that returns an i32
    let handle = executor.spawn(async {
        Delay::new(Duration::from_secs(1)).await;
        println!("background task: computed");
        21 * 2
    });

    let result = executor.block_on(async move {
        // .await the background Task's JoinHandle here to get the result
        let value = handle.await;
        println!("main task: got the background result {}", value);

        value + 100 // return a value of our own
    });
    println!("block_on returned: {}", result);
}
```

### Walking Through It Step by Step

Say A is the background `Task` above: it waits one second, then computes `42`. B is the `Task` passed to `block_on`: it `.await`s A's `JoinHandle` and, once it has the result, returns `142`.

1. `executor.spawn(A)`: `spawn` first builds a wrapper `task_future`, responsible for awaiting A, writing the result into `Shared<T>`, and waking the waiter. What actually enters the ready queue is this wrapped `Task`; `spawn` then immediately returns a `JoinHandle<i32>`.
2. `executor.block_on(B)`: B is also `spawn`ed as a `Task` and queued; `block_on` keeps B's `JoinHandle` for itself, to extract B's return value at the end.
3. The executor `poll`s `Task` A first. What's actually `poll`ed is the outer `task_future`; it reaches `let value = future.await` and only then starts `poll`ing the real inner A. Inner A reaches `Delay::new(...).await` and `poll`s the `Delay`; the `Delay` isn't done, so it returns `Pending`. That `Pending` propagates back out through the `task_future`, and A's `poll` is over for now.
4. After A's `Pending`, the executor doesn't sleep — the ready queue still holds B. It immediately `poll`s `Task` B. Likewise, B's outer `task_future` is `poll`ed first; it reaches `let value = future.await` and starts `poll`ing the `async` block that was passed to `block_on`.
5. B's inner `async` block reaches `handle.await`, so it `poll`s A's `JoinHandle`. A's result isn't ready yet, so the `JoinHandle` stores B's `Waker` into `Shared<T>` and returns `Pending`. That `Pending` propagates back out through B's `task_future`, and B pauses too.
6. The ready queue is empty; the executor falls asleep via `thread::park()`.
7. About a second later, A's timing `Thread` calls A's `Waker`; A is requeued and the executor is `unpark`ed awake.
8. The executor `poll`s A again. As before, A's outer `task_future` is `poll`ed first and continues polling inner A; the `Delay` has completed, so A resumes past the `.await`, first printing `background task: computed`, then computing `42`.
9. A's outer `task_future` receives the `42`, deposits it into `Shared<T>`, then takes out B's stored `Waker` and `wake()`s it. This doesn't directly resume B — it requeues B onto the ready queue.
10. The executor next `poll`s B. B's outer `task_future` continues `poll`ing the inner `async` block; this time `handle.await` retrieves `42` from `Shared<T>`, prints `main task: got the background result 42`, and B returns `142`.
11. B's own outer `task_future` writes `142` into B's own `Shared<T>`. All `Task`s are done; `block_on` extracts `142` from B's `JoinHandle` and returns it, finally printing `block_on returned: 142`.

### Whose `Waker` Is `cx.waker()`, Exactly

Having walked that through, we can add a point you may not have noticed but which matters. When the executor `poll`s a `Task`, it first builds a `Waker` from that `Task` and puts it in the `Context`; that `Context` is then passed down through the outer `task_future`, the inner `async` block, and on to the `Future` before each `.await`. In other words, every `Future` `poll`ed along the way within a `Task` shares that same `Task`'s `Waker`.

This is close to the meaning of `Task` as the unit of scheduling: what gets requeued and re-`poll`ed by the executor is the `Task`, not any individual `Future` inside. So when an inner `Future` registers how it wants to be woken, there's no more sensible `Waker` to use than the current `Task`'s.

Mapping back onto the walkthrough, you can see the two different `Waker`s at play: when A is `poll`ed (step 3), the `Delay` gets **A's** `Waker` from `cx.waker()` and hands it to the timing `Thread`, which on expiry wakes "A, the doer" (step 7); when B is `poll`ed (step 5), the `JoinHandle` gets **B's** `Waker` from `cx.waker()` and stores it into `Shared<T>`, which A uses on completion to wake "B, the result-waiter" (step 9). Different origins, but both end down the same road: requeue the corresponding `Task`, then `unpark` the executor.

### Not `Future`-to-`Future` Notification

Please note: there is no direct line between the `JoinHandle` and the background `Task`; they only share a `Shared<T>`. The waiting side leaves its `Waker` in the shared state; the finishing side, when done, takes that `Waker` out of the shared state and `wake`s it. All waking ultimately returns to the same old road: "requeue onto the ready queue + `unpark` the executor."

At this point, our hand-written executor is looking respectable: it can `spawn`, sleep, and be woken. But one big puzzle piece is missing — "waiting" still relies on opening a `Thread` per `Delay`. Starting next episode, we bring in `mio` and the reactor, watching real I/O with just a few `Thread`s.

## Recap

- `JoinHandle<T>` is a `Future`; `.await` it to get the background `Task`'s return value.
- The scheduling core is unchanged; only three additions: `Shared<T>` + `JoinHandle<T>`, an `Executor::spawn` returning `JoinHandle<T>`, and an `Executor::block_on` returning `T`.
- When the executor `poll`s a `Task`, the `Context` flows down to the inner `Future`s; so the `cx.waker()` an inner `Future` sees is the current `Task`'s `Waker`.
- A `JoinHandle` has no independent `Waker`; at `.await` time it stores **the waiter's own** `Waker` into `Shared<T>`.
- On completion, the background `Task` deposits the result into `Shared<T>`, then takes out that `Waker` and `wake()`s it, rousing the waiter.
- Waking is not `Future` notifying `Future` directly — the finisher wakes the waiter through shared state.
