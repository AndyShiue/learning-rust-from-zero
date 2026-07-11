# Runtimes Other Than Tokio

## Goal of This Episode

Get to know `async` runtimes besides Tokio, and learn to tell which parts of your code are tied to a specific runtime and which aren't.

## Main Text

### The Standard Library Only Defines the Language-level Abstractions

This chapter took great pains to hand-write a runtime from scratch. By now it should be clear: the standard library defines only the **language-level abstractions** — the `Future` `trait`, `Poll`, `Context`, `Waker`, `Pin`. But "how a `Future` actually gets run" — how the executor schedules, how the reactor watches I/O, how timers are implemented — the standard library stays entirely out of, leaving it to third-party runtimes to do as they please. The things we hand-wrote earlier (the executor, reactor, timer, the design of `Task`) are exactly the parts a runtime should contain.

### Not Just Tokio

Tokio is currently the most mainstream runtime, but not the only choice. Since the standard library doesn't dictate how a runtime is written, the community has grown several runtimes, each with its own character:

- **Tokio**: the general-purpose runtime with the most complete features and the largest ecosystem — multithreaded, has everything. It's what the second half of this chapter used.
- **smol**: a runtime on the lightweight, minimal path — small core, easy to understand.
- **monoio / glommio**: specialized runtimes on the **thread-per-core** path, often paired with Linux's io_uring, built for extreme I/O performance.
- **Embassy**: a runtime for **embedded** devices, able to run `async` on microcontrollers with no operating system and no standard library.

These runtimes can differ in every dimension: how many `Thread`s, how scheduling works, how I/O is done, how timers are implemented, the details and restrictions of `spawn`. Which to pick depends on your situation — for ordinary network services Tokio is the least hassle; for embedded you'd use Embassy.

### runtime-agnostic vs runtime-specific

With this many runtimes around, it's worth keeping one question in mind as you write code: is this piece of code **tied** to a specific runtime or not?

- **The runtime-agnostic parts (not tied)**: pure `Future` composition logic. For example your own `impl Future`s, chains of `async` / `.await`, combinations via `join!` / `select!`, `FuturesUnordered` — these depend only on the standard library's `Future` abstraction and usually work unchanged on another runtime.
- **The runtime-specific parts (tied)**: the things that actually touch the outside world or the scheduler. For example `tokio::net::TcpStream` (I/O), `tokio::time::sleep` (timers), `tokio::spawn` (scheduling) — these come from Tokio, and switching runtimes means swapping in that runtime's equivalents.

In practice there's no need to hamstring yourself for "runtime neutrality" — most projects pick Tokio and use it all the way. But knowing where the line sits helps when you "want to switch runtimes" or "want to write a library for others without locking them into a runtime": you'll know exactly which code can stay untouched and which must be swapped.

## Recap

- Rust's standard library defines only the **language-level abstractions** like `Future`; there's no built-in runtime — executor, reactor, timers, I/O, and `Task` design all come from the runtime (exactly the parts we hand-wrote).
- Tokio is the mainstream general-purpose runtime; there's also lightweight smol, thread-per-core monoio / glommio, embedded Embassy, and more — designs can differ in every dimension.
- As you write code, note: pure `Future` composition logic (custom `Future`s, `join!`, `select!`, `FuturesUnordered`) is mostly **runtime-agnostic**; I/O, timers, and `spawn` are **runtime-specific** and must be swapped when switching runtimes.

Congratulations on finishing the async chapter! 🎉 This chapter started from the first `async fn` and took everything apart — `Future`, `poll`, `Waker`, executor, reactor, `Pin` — then returned to Tokio's `spawn`, I/O, channels, `select!`, graceful shutdown, and testing. Having come this far, you've seen the complete skeleton of "how lazy `Future`s get driven forward by a runtime" behind `async`. From now on, when using Tokio or any other runtime, you won't just be looking at async APIs — you'll also know roughly what those APIs are arranging on your behalf.
