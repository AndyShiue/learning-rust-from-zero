# `async` `Mutex`, `RwLock`, and `Notify`

## Goal of This Episode

Figure out why you sometimes need Tokio's locks, when the standard library's are fine, and meet the wakeup tool `Notify`.

## Main Text

### Starting from an Exception to `Send` / `Sync`

Back to the multithreading chapter's `Send` / `Sync`. Everyday types follow a pattern: if a type is `Sync` (borrowable by many `Thread`s at once), it's usually also `Send` (movable to another `Thread`).

But there are rare exceptions: the **guards** of `std::sync::Mutex` and `RwLock` (the `MutexGuard` / `RwLockReadGuard` / `RwLockWriteGuard` returned by `.lock()`) are **`Sync` but not `Send`**. Why? Because on some operating systems, a lock **must be unlocked by the same `Thread` that locked it**; moving the guard to another `Thread` before `drop`ping it (unlocking) would misbehave. So the standard library simply forbids these guards from being `Send`.

### These Exceptions Reach into `async`

This non-`Send` trait turns into a bewildering compile error in `async`. Recall Episode 21: a `Future` holding something non-`Send` across an `.await` is itself non-`Send`, hence un-`tokio::spawn`-able. And the standard library's guards are exactly non-`Send` — so **holding a std guard across an `.await`** gets you hit:

```rust,compile_fail
# extern crate tokio;
#
use std::sync::{Arc, Mutex};

async fn do_io() {}

#[tokio::main]
async fn main() {
    let data = Arc::new(Mutex::new(0));
    tokio::spawn(async move {
        let mut guard = data.lock().expect("failed to take the lock"); // std's MutexGuard — not Send
        do_io().await; // holding the guard across the .await
        *guard += 1;
    }); // compile error: the future isn't Send and can't be spawned
}
```

This error is really a **helpful warning** — it flags a violation of an important discipline: **a `Mutex` guards shared mutable state; keep lock scopes as short as possible, and try not to hold a lock while waiting on I/O.** Hold a lock while waiting on I/O, and everyone else stays shut out of the lock the whole time — concurrency can collapse.

So the best fix is usually not "find a way to hold the lock across the `.await`," but **shortening the lock scope**: finish the changes before the `.await` and let the guard leave scope:

```rust,noplayground
# extern crate tokio;
#
use std::sync::{Arc, Mutex};

async fn do_io() {}

#[tokio::main]
async fn main() {
    let data = Arc::new(Mutex::new(0));
    tokio::spawn(async move {
        {
            let mut guard = data.lock().expect("failed to take the lock");
            *guard += 1;
        } // the guard drops right here — it never crosses the .await
        do_io().await; // no lock in hand while waiting on I/O
    });
}
```

### Reach for Tokio's Locks Only When Necessary

But sometimes you truly **need** to hold a lock across an `.await` (say, performing an `async` operation while holding the lock, with logic that can't be split). Only then switch to `tokio::sync::Mutex` — its guard is `Send` and can safely cross `.await`s:

```rust,noplayground
# extern crate tokio;
#
use std::sync::Arc;
use tokio::sync::Mutex; // note: tokio's Mutex

#[tokio::main]
async fn main() {
    let data = Arc::new(Mutex::new(0));
    let d = data.clone();
    tokio::spawn(async move {
        let mut guard = d.lock().await; // note that lock() takes .await
        *guard += 1; // this guard is Send and may cross .awaits
    });
}
```

But remember: **the standard library's locks are faster than Tokio's** (Tokio's pay extra to be able to cross `.await`s). So default to `std`'s locks with short scopes; deploy Tokio's `Mutex` only when "holding the lock across an `.await`" is unavoidable.

Like the standard library, Tokio also has an `RwLock` separating reads from writes: `read().await` admits many readers at once, `write().await` is exclusive to a single writer. The usage principles match Tokio's `Mutex`.

### `Notify`: Wakeups Without Data

Finally, `tokio::sync::Notify`. It's a **wakeup tool without a payload (no data)** — it lets one `Task` sleep in wait (`notified().await`) and another give it a poke to wake up (`notify_one()`), but **transmits no value**.

```rust,no_run
# extern crate tokio;
#
use std::sync::Arc;
use tokio::sync::Notify;

#[tokio::main]
async fn main() {
    let notify = Arc::new(Notify::new());
    let n = notify.clone();

    tokio::spawn(async move {
        n.notified().await; // sleep awaiting notification
        println!("notified — waking up to work");
    });

    notify.notify_one(); // poke one waiter awake
}
```

`Notify` usually pairs with **shared state you manage yourself under a `Mutex`**: after changing the shared state, give a `notify`, and the awakened `Task` checks the state itself. It is **not a queue** — multiple `notify`s may merge into one (if no one is waiting yet, only a single notification may be recorded).

### `Notify` vs `watch`

`Notify` is easily confused with last episode's `watch`, but their roles differ:

- **`Notify`**: **no data, stateless**. It only handles "poking people awake"; what to look at upon waking is yours to manage with a `Mutex` or similar.
- **`watch`**: **carries the "latest value," stateful**. It stores the latest state itself, and receivers read it directly upon waking.

## Recap

- The standard library's `Mutex` / `RwLock` guards are `Sync` but not `Send` (some OSes require unlocking on the locking `Thread`); holding one across an `.await` makes the `Future` non-`Send` and unspawnable.
- That compile error is a useful warning: keep `Mutex` lock scopes short; don't hold a lock while waiting on I/O — usually just shorten the scope (`drop` the guard before the `.await`).
- Use `tokio::sync::Mutex` only when holding a lock across an `.await` is a must (its guard is `Send`; `.lock().await`), but prefer the faster std locks.
- Tokio's `RwLock` splits reads and writes: `.read().await` for many readers, `.write().await` for one writer.
- `Notify` is a data-free wakeup tool paired with self-managed shared state, not a queue (notifications may merge); versus `watch`: `Notify` is stateless (pokes you to look), `watch` is stateful (carries the latest value).
