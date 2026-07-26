# Back to Tokio

## Goal of This Episode

Return from the hand-written runtime to Tokio: revisit `tokio::spawn` and `JoinHandle`, compare Tokio's `block_on` with our hand-written one, and learn the runtime's multithreaded / single-threaded flavors.

## Main Text

### You Already Understand the Underneath

Congratulations on surviving the hardest episodes! We hand-wrote an executor, reactor, `Task`, and `JoinHandle` from scratch, and dissected state machines and `Pin`. Tokio's real implementation is of course far more sophisticated, but looking back at its API now, most of the terms and design trade-offs should feel familiar.

### `tokio::spawn` and `JoinHandle`

`tokio::spawn` is the `spawn` we hand-wrote: wrap a `Future` into a `Task`, hand it to the runtime's scheduler, and get back a `JoinHandle`:

```rust,editable
# extern crate tokio;
#
#[tokio::main]
async fn main() {
    let handle = tokio::spawn(async {
        21 * 2
    });
    let result = handle.await.expect("the background task panicked");
    println!("result: {}", result);
}
```

(`.await`ing Tokio's `JoinHandle` returns a `Result`, since the background `Task` might panic — hence the `expect` here.)

### How Tokio's `block_on` Differs from Ours

Unlike our hand-written version, `tokio::runtime::Runtime::block_on` requires **neither** `Send` nor `'static`. It simply runs the `Future` you give it to completion on the current calling `Thread`, never moving it elsewhere, so `Send` isn't a concern.

There is also an important semantic difference: the `block_on` we hand-wrote from Episode 11 onward waits until **every** `Task` in the ready queue completes before returning. Tokio's `block_on` instead "**returns as soon as the `Future` you passed it completes**," without waiting for other background `Task`s opened via `tokio::spawn`. Unfinished background `Task`s stay on the runtime.

The one-line contrast: the hand-written version "finishes the whole batch before moving on"; Tokio "finishes the one I specified, then moves on." So in Tokio, `block_on` returning only means your `Future` finished; `Task`s you `spawn`ed may still be running. If the runtime then shuts down, those background `Task`s never get to finish.

### The Most Common Beginner Compile Error: Holding a Non-`Send` Value Across `.await`

`tokio::spawn` requires `Future: Send`, and whether a `Future` is `Send` depends on **what it stores across `.await`s**. Holding a non-`Send` value such as `Rc` across an `.await` makes the whole `Future` non-`Send`, so it can't be `spawn`ed:

```rust,compile_fail
# extern crate tokio;
#
use std::rc::Rc;

async fn some_async() {}

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let rc = Rc::new(5);
        some_async().await; // rc is held across the .await, and Rc isn't Send
        println!("{}", rc);
    });
}
```

The compiler says `future cannot be sent between threads safely` and points out that `Rc<i32>` is used across an `.await`.

Several fixes:

**Use a `Send` substitute.** Here, swap `Rc<i32>` for `Arc<i32>`, which is `Send`:

```rust,noplayground
# extern crate tokio;
#
use std::sync::Arc;

async fn some_async() {}

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let arc = Arc::new(5);
        some_async().await;
        println!("{}", arc);
    });
}
```

**Dispose of the non-`Send` value before the `.await`.** Shrink its scope with `{}` so it's `drop`ped before the `.await`, and the state machine never holds it across:

```rust,noplayground
# extern crate tokio;
#
use std::rc::Rc;

async fn some_async() {}

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let n = {
            let rc = Rc::new(5);
            *rc
        }; // rc is dropped at the end of this block — it never crosses the .await
        some_async().await;
        println!("{}", n);
    });
}
```

(Explicitly calling `drop(rc)` before the `.await` achieves the same.)

### `#[tokio::main]` flavors

Finally: `#[tokio::main]` defaults to the multithreaded runtime, but you can change it:

```rust,editable
extern crate tokio;

// single-threaded runtime
#[tokio::main(flavor = "current_thread")]
async fn main() {
    println!("I run on a single thread");
}
```

Or specify the number of worker `Thread`s:

```rust,editable
extern crate tokio;

// multithreaded, with 4 workers
#[tokio::main(flavor = "multi_thread", worker_threads = 4)]
async fn main() {
    println!("I have 4 worker threads");
}
```

The single-threaded runtime's upside is that it pays no cross-`Thread` cost; the downside is no true parallelism.

## Recap

- `tokio::spawn` hands a `Future` to the runtime and returns a `JoinHandle` (`.await` yields a `Result`, since the `Task` may panic).
- Unlike our hand-written `block_on`, Tokio's requires neither `Send` nor `'static` and returns as soon as **the specified `Future`** completes instead of waiting for **all** `Task`s.
- Holding a non-`Send` value such as `Rc` across an `.await` makes the `Future` non-`Send` and unspawnable; fix with `Arc`, or scope / `drop` it away before the `.await`.
- `#[tokio::main]` defaults to multithreaded, adjustable via `flavor = "current_thread"` or `worker_threads = N`; either way, `tokio::spawn` still requires its `Future` and output to be `Send + 'static`.
