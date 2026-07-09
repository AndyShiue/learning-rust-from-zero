# `spawn` and the ready queue

## Goal of This Episode

Introduce the concept of a `Task`, letting the executor keep many `Future`s at once, managed through a ready queue (to-do queue).

## Main Text

### Why `Task`s Are Needed

The executors of the past few episodes always held exactly **one** `Future`, `poll`ing it repeatedly in a loop. But a real runtime keeps **many** `Future`s at once.

Here's the problem: when some `Future`'s `Waker` shouts "I'm ready!", if the executor holds a pile of bare `Future`s, how does it know **which one** is ready — which to `poll`? A `Future` by itself carries no such information.

Our solution is to give each `Future` a set of "carry-on data," wrapping it into a **`Task`**. A `Task` holds:

- Its own `Future`
- **Which** ready queue it should requeue onto
- **Which** executor `Thread` to wake
- A flag to avoid queuing itself twice
- A flag marking that it has already finished

From now on the executor manages `Task`s, not `Future`s directly. And `spawn` simply means "wrap a `Future` into a `Task` and hand it to the executor."

### The ready queue and "Waking"

The executor will keep a **ready queue**: the `Task`s that "should be `poll`ed now." The executor's job is to take `Task`s off the queue and `poll` their `Future`s; when the queue is empty, it sleeps.

When a `Task` gets `wake`d, it puts **itself** back onto the ready queue, then `unpark`s the sleeping executor. Note that this `unpark` is only an **alarm bell** — it says "there's work, get up!" without pointing at which `Task` is ready. The real information — "which `Task`s should be `poll`ed" — lives in the ready queue.

### Writing It Out

This episode's program is longer, but the skeleton is just the sentences above. See how a `Task` requeues itself (that's its `Wake` implementation), and how the `Executor` explicitly provides `spawn` and `block_on`:

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

// a Future + the carry-on data needed to reschedule it
struct Task {
    future: Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>,
    queue: Queue,
    executor_thread: Thread,
    queued: AtomicBool, // am I currently in the queue?
    done: AtomicBool,   // am I finished?
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        // grab the old queued value while leaving true in its place
        if !self.queued.swap(true, Ordering::SeqCst) {
            self.queue.lock().expect("failed to take the lock").push_back(self.clone());
            self.executor_thread.unpark(); // wake the executor
        }
    }
}

struct Executor {
    queue: Queue,
    executor_thread: Thread,
    remaining: usize, // number of unfinished Tasks
}

impl Executor {
    fn new() -> Executor {
        Executor {
            queue: Arc::new(Mutex::new(VecDeque::new())),
            executor_thread: thread::current(),
            remaining: 0,
        }
    }

    // spawn: wrap a Future into a Task and put it on the executor's queue
    fn spawn(&mut self, future: impl Future<Output = ()> + Send + 'static) {
        let task = Arc::new(Task {
            future: Mutex::new(Box::pin(future)),
            queue: self.queue.clone(),
            executor_thread: self.executor_thread.clone(),
            queued: AtomicBool::new(false),
            done: AtomicBool::new(false),
        });

        self.remaining += 1;
        task.wake(); // a new task needs its first trip into the ready queue
    }

    fn block_on(&mut self, future: impl Future<Output = ()> + Send + 'static) {
        // spawn the incoming Future as a Task too
        self.spawn(future);

        while self.remaining > 0 {
            // first, drain the ready queue
            loop {
                let task = self.queue.lock().expect("failed to take the lock").pop_front();
                let Some(task) = task else { break };

                if task.done.load(Ordering::SeqCst) {
                    continue; // a stale wakeup queued after completion — skip it
                }

                task.queued.store(false, Ordering::SeqCst); // release the flag before polling
                let waker = Waker::from(task.clone());
                let mut cx = Context::from_waker(&waker);
                let mut future = task.future.lock().expect("failed to take the lock");

                if future.as_mut().poll(&mut cx).is_ready() {
                    task.done.store(true, Ordering::SeqCst); // all later wakeups are ignored
                    self.remaining -= 1; // finished
                }
            }

            // the queue is empty. is every Task done?
            if self.remaining > 0 {
                // some remain — sleep until someone wakes us
                thread::park();
            }
        }
    }
}

fn main() {
    let mut executor = Executor::new();

    executor.spawn(async {
        println!("task A: starting");
        Delay::new(Duration::from_secs(1)).await;
        println!("task A: one second is up");
    });

    executor.block_on(async {
        println!("task B: starting");
        Delay::new(Duration::from_secs(2)).await;
        println!("task B: two seconds are up");
    });

    println!("executor finished");
}
```

Run it and the two `Task`s (A and B) advance concurrently: A comes due at second one, B at second two; when each expires, it requeues only **itself** to get `poll`ed once, without disturbing the other. `block_on` waits until every `Task` in the executor completes before returning, so "executor finished" prints last.

### Why the `queued` Flag Uses `swap`

The `queued.swap(true, ...)` in `wake` closely resembles Episode 9's `Option::take`: it's not simply "reading a value" — it **grabs the old value while leaving a new one in its place**.

Episode 9's `slot.take()` was "take the `Some(fut)` out, leave `None` in its place." Here, `queued.swap(true, ...)` is "take the old `queued` out, leave `true` in its place." So:

- Getting `false` means this `Task` was **not** in the queue — so we push it in.
- Getting `true` means it's already queued, and this `wake` needn't queue it again.

Why not `load` then `store`? Because `wake` can come from different `Thread`s. To be safe, `swap` binds "look at the old value" and "leave the new value" into a single atomic operation, so two `Thread`s can't both see `false` at once and push the same `Task` into the queue twice.

### The `done` Flag: Honoring Contract Two

Last episode's contract two said: once a `Future` returns `Ready`, it must never be `poll`ed again. Back then, `block_on` simply `return`ed the moment it got `Ready`, so it couldn't offend; but now that the executor keeps many `Task`s at once, things aren't so simple anymore.

The threat comes from the `Waker` copies scattered outside. After a `Task` completes, the executor itself certainly won't requeue it; but a copy like the one `Delay` handed to its timing `Thread` is beyond the executor's recall. If someone holding such a stale `Waker` calls `wake()` **after** the `Task` has completed, the finished `Task` gets requeued onto the ready queue and then `poll`ed again — contract two is broken, and `remaining -= 1` gets subtracted one extra time.

So a `Task` also needs a `done` flag, to invalidate stale wakeups. The defense sits on the executor's side: after popping a `Task`, check `done` first — if it's `true`, just `continue` past it. That way a stale wakeup at worst puts the `Task` into the queue one extra time; it can never get it `poll`ed again. And since only the executor thread ever `poll`s the `Future`s, and only it sets `done` to `true`, "never `poll` again once `done` is set" holds strictly.

Honestly, this episode's examples can't actually trigger the problem — every timer fires exactly once, and always before its `Task` completes. But the executor's correctness can't rest on that kind of luck.

### Why the `Future` Field Must Be `Send`

You may also notice the `Task`'s `future` field is typed `Mutex<Pin<Box<dyn Future<Output = ()> + Send>>>` — why `Send`?

Follow the chain and it makes sense: the `Future` goes inside the `Task`, and the `Task` also `impl Wake`, doubling as the `Waker` (in theory the `Task` needn't be its own `Waker`, but this is the most economical way to write it). The conversion `Waker::from(Arc<Task>)` requires `Task: Send + Sync + 'static`. For a type to be `Send + Sync`, **every field** must be `Send + Sync` — including that `Future`.

Hence the `dyn Future` gains `+ Send` (so it can be moved to another `Thread`), wrapped in a `Mutex` (a `Mutex<T>` is automatically `Sync` when `T: Send`). Last episode's `Waker` was simple enough in construction that we didn't have to fret over these bounds; this episode, with the `Task` serving as its own `Waker`, they must be taken seriously.

Next episode we build on this and let `spawn` return results — adding a `JoinHandle`.

## Recap

- Wrap each `Future` into a **`Task`** (`Future` + scheduling carry-on data); the executor manages `Task`s, not bare `Future`s.
- The **ready queue** holds the `Task`s due for polling; a `wake`d `Task` requeues itself, then `unpark`s the executor.
- `unpark` is only the "get up" alarm — it doesn't say which `Task` is ready; that information lives in the ready queue.
- `spawn` is an `Executor` method: wrap the `Future` into a `Task` and put it on its ready queue.
- `queued.swap(true, ...)` is like `Option::take`: grab the old value, leave the new — one atomic operation, preventing duplicate queue entries.
- After a `Task` completes, unretrievable `Waker` copies may still deliver **stale wakeups**; the `done` flag upholds contract two — the executor checks `done` right after popping a `Task`, sets it on `Ready`, and every wakeup thereafter is void.
- With `Task` as its own `Waker`, `Waker::from(Arc<Task>)` demands `Task: Send + Sync + 'static`, so the `Future` field needs `+ Send` and a `Mutex` around it.
