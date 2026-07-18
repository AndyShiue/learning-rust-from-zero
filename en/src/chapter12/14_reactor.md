# Hand-writing a reactor

## Goal of This Episode

Hook the waking machinery from recent episodes up to **real I/O** — build a reactor, so our runtime can handle network connections for the first time.

## Main Text

### Not One Line of the executor Changes

Here's something reassuring about this episode: **the executor carries over from Episode 12 unchanged**. `Task`, `Executor::spawn<T>`, `JoinHandle<T>`, `Shared<T>`, `Executor::block_on` — not a line needs touching.

The only thing we swap out is "who does the `wake`ing." Before, each `Delay` opened its own timing `Thread` to `wake`; now we switch to a single **reactor `Thread`**, sleeping on a `mio::Poll` waiting for real I/O, and on waking it finds the matching `Waker` and `wake()`s it.

What we add is a `Reactor`, plus two I/O `Future`s (`Accept` and `Read`).

### The `Reactor` and the I/O `Future`s

The `Reactor` runs on its own `Thread`, asleep on a `mio::Poll`. So how do the `Future`s running on the executor `Thread` talk to it? The answer: **through shared state, not messages**. Three things are shared via `Arc`:

- **`Registry`** (from `mio`): `Future`s use it directly to register / deregister sockets.
- **`AtomicUsize`**: the reactor uses it to self-allocate a unique `Token` per source.
- **`Mutex<HashMap<Token, Waker>>`**: `Future`s write their `Waker` in as they run (keyed by `Token`); when the reactor receives an event it fetches by `Token` and `wake`s.

```rust,no_run
# extern crate mio;
#
use std::collections::{HashMap, VecDeque};
use std::future::Future;
use std::io::Read as _;
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};
use mio::event::Source;
use mio::net::{TcpListener, TcpStream};
use mio::{Events, Interest, Poll as MioPoll, Registry, Token};

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

struct Shared<T> {
    state: Mutex<(Option<T>, Option<Waker>)>,
}

struct JoinHandle<T> {
    shared: Arc<Shared<T>>,
}

impl<T> Future for JoinHandle<T> {
    type Output = T;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<T> {
        let mut state = self.shared.state.lock().expect("lock failed");
        if let Some(value) = state.0.take() {
            Poll::Ready(value)
        } else {
            state.1 = Some(cx.waker().clone());
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

    fn spawn<T, F>(&mut self, future: F) -> JoinHandle<T>
    where
        F: Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        let shared = Arc::new(Shared { state: Mutex::new((None, None)) });
        let shared_for_task = shared.clone();

        let task_future = async move {
            let value = future.await;
            let mut state = shared_for_task.state.lock().expect("lock failed");
            state.0 = Some(value);
            if let Some(waker) = state.1.take() {
                waker.wake();
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
        let handle = self.spawn(future);

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

        handle.shared.state.lock().expect("lock failed").0.take().expect("result not ready")
    }
}

struct Reactor {
    registry: Registry, // Futures use it to register / deregister sockets
    next_token: AtomicUsize, // self-allocated Tokens
    wakers: Mutex<HashMap<Token, Waker>>, // Token -> waiting Waker
}

impl Reactor {
    fn unique_token(&self) -> Token {
        Token(self.next_token.fetch_add(1, Ordering::Relaxed))
    }

    fn register(&self, source: &mut impl Source, token: Token, interest: Interest) {
        self.registry.register(source, token, interest).expect("register failed");
    }

    fn deregister(&self, source: &mut impl Source) {
        self.registry.deregister(source).expect("deregister failed");
    }

    fn set_waker(&self, token: Token, waker: Waker) {
        self.wakers.lock().expect("lock failed").insert(token, waker);
    }

    fn clear_waker(&self, token: Token) {
        self.wakers.lock().expect("lock failed").remove(&token);
    }

    // runs on its own Thread: sleeps on poll, wakes and looks up Wakers by Token
    fn run(&self, mut poll: MioPoll) {
        let mut events = Events::with_capacity(128);
        loop {
            poll.poll(&mut events, None).expect("poll failed");
            for event in events.iter() {
                let waker = self
                    .wakers
                    .lock()
                    .expect("lock failed")
                    .remove(&event.token());

                if let Some(waker) = waker {
                    waker.wake();
                }
            }
        }
    }
}

fn start_reactor() -> Arc<Reactor> {
    let poll = MioPoll::new().expect("Poll creation failed");
    let registry = poll.registry().try_clone().expect("failed to clone the Registry");
    let reactor = Arc::new(Reactor {
        registry,
        next_token: AtomicUsize::new(0),
        wakers: Mutex::new(HashMap::new()),
    });
    // the reactor runs on its own Thread
    let reactor_for_thread = reactor.clone();
    std::thread::spawn(move || reactor_for_thread.run(poll));
    reactor
}

// now for the new Futures

struct Accept {
    reactor: Arc<Reactor>,
    listener: TcpListener,
    listener_token: Token,
}

impl Accept {
    fn new(reactor: Arc<Reactor>, mut listener: TcpListener) -> Accept {
        let listener_token = reactor.unique_token();
        reactor.register(&mut listener, listener_token, Interest::READABLE);
        Accept { reactor, listener, listener_token }
    }
}

impl Future for Accept {
    type Output = TcpStream;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<TcpStream> {
        let this = self.get_mut();
        // the order is deliberately "register the Waker first, then try accept".
        // if we tried accept first, got WouldBlock, and only then went to register the Waker,
        // a connection might arrive in between; the reactor would find no Waker to wake,
        // and the executor could oversleep.
        this.reactor.set_waker(this.listener_token, cx.waker().clone());
        match this.listener.accept() {
            Ok((stream, _addr)) => {
                // this poll may have "registered first, then immediately succeeded".
                // after success there is no I/O event to wait for; clear the stored Waker.
                this.reactor.clear_waker(this.listener_token);
                this.reactor.deregister(&mut this.listener);
                Poll::Ready(stream)
            }
            Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => panic!("accept failed: {}", e),
        }
    }
}

struct Read<'a> {
    reactor: Arc<Reactor>,
    stream: &'a mut TcpStream,
    buf: &'a mut [u8],
    stream_token: Token,
}

impl<'a> Future for Read<'a> {
    type Output = usize;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<usize> {
        let this = self.get_mut();
        this.reactor.set_waker(this.stream_token, cx.waker().clone()); // register first
        match this.stream.read(this.buf) { // then try
            Ok(n) => {
                // clear the Waker
                this.reactor.clear_waker(this.stream_token);
                Poll::Ready(n)
            }
            Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => Poll::Pending,
            Err(e) => panic!("read failed: {}", e),
        }
    }
}

// accept one connection; read/print requests (simplified, no timeout)
async fn serve(reactor: Arc<Reactor>, listener: TcpListener) {
    let mut stream = Accept::new(reactor.clone(), listener).await;

    let stream_token = reactor.unique_token();
    reactor.register(&mut stream, stream_token, Interest::READABLE);

    for i in 1..=3 {
        let mut buf = vec![0u8; 1024];
        let n = Read {
            reactor: reactor.clone(),
            stream: &mut stream,
            buf: &mut buf,
            stream_token,
        }
        .await;
        if n == 0 {
            println!("the connection closed");
            break;
        }
        println!("request {}: {}", i, String::from_utf8_lossy(&buf[..n]).trim());
    }

    reactor.clear_waker(stream_token);
    reactor.deregister(&mut stream);
}

fn main() {
    let reactor = start_reactor();
    let addr = "127.0.0.1:8080".parse().expect("failed to parse the address");
    let listener = TcpListener::bind(addr).expect("bind failed");

    let mut executor = Executor::new();
    executor.block_on(serve(reactor, listener));
}
```

> Note: this program listens on `127.0.0.1:8080` locally; you need a tool like `nc` to connect to it (e.g. `nc 127.0.0.1 8080`) to see the effect. The web sandbox isn't suited to this kind of interactive network program; to experience the full result, run the code on your own machine.

### `Token`s Are Bound to I/O Sources

`Accept` and `Read` don't share one `Token`. The `listener_token` inside `Accept` belongs to the `TcpListener`; after a connection is accepted, `serve` creates a separate `stream_token` and registers it for that `TcpStream`.

The three later `Read`s share the same `stream_token`, deliberately: a `Token` is the name tag of an I/O source — you don't swap tags for every `.await`. This simplified example only ever waits on one `read` on this stream at a time, so one stream `Token` mapping to one waiting `Waker` suffices.

After the I/O succeeds, `Accept` / `Read` call `clear_waker`, removing this wait's `Waker` from the `HashMap`. That way the reactor holds no waiters who "no longer need waking."

### Why "Register First, Then Try" Matters

Notice that both `Accept`'s and `Read`'s `poll` do `set_waker` **first**, and **then** try `accept` / `read` once. The order is deliberate.

That "try once" doesn't mean this round will succeed. If it's still `WouldBlock`, this `poll` returns `Pending`; later, when the reactor receives the event and calls the `Waker` we just stored, the executor `poll`s this `Future` again next round, and only then does it retry the I/O.

Imagine the reverse: try `read` first, get `WouldBlock` (no data), and just as you're about to register the `Waker` — in that gap, the data arrives. The reactor wakes wanting to `wake`, but finds no `Waker` for this `Token` in the `HashMap`; the wakeup is **missed**, and this `Future` is never `poll`ed again.

Flipping the order — put the `Waker` in place first, then try the I/O once — plugs that gap: if the data already arrived, this `accept` / `read` simply succeeds and returns `Ready`; if it truly hasn't, the `Waker` is already in position, and the reactor's notification triggers the next round. Success → `Ready`; `WouldBlock` → `Pending`. And precisely because we "register first, then try," if this `accept` / `read` does succeed immediately, the `Waker` just placed in the `HashMap` is no longer needed. That's when `Accept` / `Read` call `clear_waker` before returning `Ready` to remove it. In other words, `set_waker` prevents "missing a wakeup by registering too late," and `clear_waker` prevents "finishing but leaving behind an unneeded waiter."

### The Wake Path Is Completely Unchanged

Compare this episode with Episode 12 and you'll find the wake path ends at exactly the same place. The reactor may run on its own `Thread`, but the `waker.wake()` it calls is still some `Task`'s `Waker` — and `wake` still requeues that `Task` and `unpark`s the executor. We merely replaced "the party responsible for waking the `Thread`" — timing `Thread` out, reactor `Thread` in; everything downstream is untouched.

And with that, our from-scratch, hand-written runtime is complete! It can `spawn`, sleep, and be woken by timers or real I/O. In the coming episodes, we turn back to finally open up that "state machine" behind `async fn` we've kept mentioning but never dissected.

## Recap

- The reactor connects waking to real I/O: **the executor carries over from Episode 12 unchanged**; only "who `wake`s" switches from timing `Thread`s to the reactor `Thread`.
- The reactor runs on its own `Thread`, sleeps on `mio::Poll`, and on waking fetches `Waker`s from the `HashMap` by `Token` to `wake`.
- `Future`s and the reactor communicate through `Arc`-shared `Registry`, `AtomicUsize`, and `Mutex<HashMap<Token, Waker>>` — shared state, not messages.
- A `Token` is an I/O source's name tag: the listener has its `listener_token`, the stream its `stream_token`; in our code, multiple `Read`s on one stream can share the same stream `Token`.
- `WouldBlock` is the normal state of non-blocking I/O — "can't `accept` / `read` yet, try later" — mapping to `Poll::Pending` in a `Future`.
- I/O `Future`s' `poll` always "**`set_waker` first, then try the I/O**" to avoid missed wakeups; on immediate success, `clear_waker` before returning `Ready`.
- Whether the wakeup comes from a timer or I/O, it takes the same road: "requeue onto the ready queue + `unpark` the executor."
