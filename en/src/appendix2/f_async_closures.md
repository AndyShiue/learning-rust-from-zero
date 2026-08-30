# `async` Closures

## Goal of This Episode

Learn the `async |...|` syntax, understand why an `async` closure can borrow the environment it captures, and see what `AsyncFnOnce`, `AsyncFnMut`, and `AsyncFn` are for.

> This episode supplements **Chapter 6's closures** and the **async chapter**.

## Concept

The async chapter already used `async fn` and `async` blocks. To hand a piece of asynchronous work to another function, the common approach used to be an ordinary closure returning an `async` block:

```rust,ignore
|name| async move {
    println!("Hello, {name}");
}
```

Modern Rust lets you write an `async` closure directly:

```rust,ignore
async |name| {
    println!("Hello, {name}");
}
```

Like an ordinary closure it can capture its environment, but calling it doesn't run the body immediately — it produces a `Future`. Only once that `Future` is `poll`ed does the body make progress.

The runnable examples below call `block_on`. It isn't a standard library API but the most bare-bones executor from Episode 6 of the async chapter; this episode merely borrows it to run immediately-completable `Future`s, so demonstrating language syntax doesn't tie us to a particular runtime.

### Why Do Ordinary Closures So Often Pair With `async move`?

When an ordinary closure is called, it runs the closure body first and then returns the `Future` the `async` block produced. That `Future` is `.await`ed later, so it may only really run after this call to the ordinary closure has finished.

Suppose the ordinary closure takes a `String` and lets the `async` block use it:

```rust,compile_fail
fn main() {
    let greet = |name: String| async {
        println!("Hello, {name}");
    };

    let _future = greet(String::from("Ming"));
}
```

There's no `move` here, so the `async` block tries to borrow the parameter `name`. But as soon as the ordinary closure returns the `Future`, this call's `name` parameter should go out of scope; if the `Future` were still borrowing it, the reference could later be invalid when it runs, so Rust rejects this code.

Adding `move` moves `name` into the `Future`:

```rust,editable
fn main() {
    let greet = |name: String| async move {
        println!("Hello, {name}");
    };

    let _future = greet(String::from("Ming"));
}
```

Now, when the ordinary closure returns, `name` isn't left behind in a call that has already finished — it's owned by the returned `Future` and lives alongside it until the `Future` completes or is dropped. That's why `|param| async move { ... }` is more common than `|param| async { ... }`.

That said, `async move` isn't mandatory in every situation. If the `async` block borrows no parameter or local variable from this closure call, `move` isn't necessarily needed. The point is: **a `Future` must not borrow data that expires when the ordinary closure's call ends.**

### Your First `async` Closure

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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
    let greet = async |name: &str| {
        std::future::ready(()).await;
        println!("Hello, {name}");
    };

    block_on(async {
        greet("Ming").await;
        greet("Mei").await;
    });
}
```

`greet("Ming")` produces a `Future`; only `.await` runs the `ready` and the `println!` inside. The same closure can be called twice, much like an ordinary `Fn` closure.

### So Why Not Always Use `|x| async move { ... }`?

An ordinary closure and the `async move` block it returns are two different things. The `async move` block below has to own `prefix`, so each time the outer ordinary closure is called it must move the `prefix` it captured into the newly produced `Future`:

```rust,compile_fail
fn main() {
    let prefix = String::from("message");

    let make_future = || async move {
        println!("{prefix}");
    };

    let _first = make_future();
    let _second = make_future();
}
```

`String` doesn't implement `Copy`. The first call to the outer closure moves `prefix` into the returned `Future`, which means moving the captured value out of its own environment, so this closure can only implement `FnOnce`. The first call consumes `make_future`, and there can be no second call.

An `async` closure lets the returned `Future` **borrow data held inside the closure**. To make this capability really visible — rather than just copying a shared reference — the closure below holds a mutable reference to a counter:

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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
    let mut count = 0;

    let mut increment = async || {
        std::future::ready(()).await;
        count += 1;
        println!("Call number {count}");
    };

    block_on(async {
        increment().await;
        increment().await;
    });
}
```

`increment` holds a mutable reference to `count` internally. The `Future` produced by each call to `increment()` obtains a shorter-lived mutable reference through that one and holds it until the `Future` completes or is dropped. Once the first `.await` finishes, that short-lived mutable reference is gone, so `increment()` can be called again. This closure implements `AsyncFnMut`, which is why the variable itself must be declared `mut` too.

An ordinary closure that returns an `async` block still holding such a mutable reference won't compile:

```rust,compile_fail
fn main() {
    let mut count = 0;

    let mut increment = || async {
        std::future::ready(()).await;
        count += 1;
    };

    let _future = increment();
}
```

This `Future` would have to go on holding a mutable reference obtained from inside the closure after the closure call ends, and that reference's lifetime comes from this particular `&mut self`. But an ordinary `FnMut`'s fixed `Self::Output` can't carry a lifetime produced anew on each call.

### The `AsyncFn` Trio

Chapter 6 taught that an ordinary closure implements `FnOnce`, `FnMut`, or `Fn` depending on how its body uses the captured values. `async` closures have a matching set of `trait`s:

| Ordinary closure | `async` closure | How it's called |
| --- | --- | --- |
| `FnOnce` | `AsyncFnOnce` | Callable once; may consume captured values |
| `FnMut` | `AsyncFnMut` | Callable repeatedly through a mutable reference |
| `Fn` | `AsyncFn` | Callable repeatedly through a shared reference |

### Roughly What Does the Compiler Implement?

Chapter 6 Episode 3 had us picture an ordinary closure as "an anonymous `struct` storing the captured values, with `FnOnce`, `FnMut`, or `Fn` implemented for it." The first half is the same for `async` closures; the difference is that the call method doesn't compute a result directly but returns a `Future` state machine.

With some implementation details omitted, the three `trait`s relate roughly as follows. This is a simplified version meant to explain the structure, not a definition from the standard library you can implement yourself:

```rust,noplayground
use std::future::Future;

trait AsyncFnOnce<Args> {
    type Output;
    type CallOnceFuture: Future<Output = Self::Output>;

    fn async_call_once(self, args: Args) -> Self::CallOnceFuture;
}

trait AsyncFnMut<Args>: AsyncFnOnce<Args> {
    type CallRefFuture<'a>: Future<Output = Self::Output>
    where
        Self: 'a;

    fn async_call_mut(&mut self, args: Args) -> Self::CallRefFuture<'_>;
}

trait AsyncFn<Args>: AsyncFnMut<Args> {
    fn async_call(&self, args: Args) -> Self::CallRefFuture<'_>;
}
```

The `self` and return type of the three calling conventions:

| `trait` | `self` | Type returned by the call |
| --- | --- | --- |
| `AsyncFnOnce` | `self` | `CallOnceFuture` |
| `AsyncFnMut` | `&mut self` | `CallRefFuture<'_>` |
| `AsyncFn` | `&self` | The same `CallRefFuture<'_>` |

`Output` is the final result obtained after awaiting the `Future`, not the `Future` itself. `CallOnceFuture` comes from a call that consumes the closure, so it can own the captured values moved out of it directly and needs no lifetime parameter.

An ordinary `FnMut`'s `call_mut` returns a fixed `Self::Output`; that associated type can't vary with the lifetime of each `&mut self` call. So an ordinary closure can't return a value that still holds "a mutable reference obtained from this `&mut self`." The crux is whether the return type can carry the reference lifetime of `&mut self`, not whether the work completes synchronously.

An `async` closure itself can be seen as an anonymous `struct` made of the captured values. The `Future`s returned by `AsyncFnMut` and `AsyncFn` may hold references into that anonymous `struct`'s data, so the `Future` type has to carry the lifetime of its borrow of the closure. `CallRefFuture<'a>` uses a GAT to write that lifetime into the associated type.

`AsyncFn` declares no associated type of its own and reuses `AsyncFnMut`'s `CallRefFuture<'a>`. Neither `async_call` nor `async_call_mut` consumes the closure, and the `Future`s they return may both go on borrowing the captured environment, so a single lifetime-carrying `Future` type suffices for both.

They can be used to write bounds for APIs that take an asynchronous handler:

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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

async fn run_twice<F>(job: F)
where
    F: AsyncFn(&str),
{
    job("first time").await;
    job("second time").await;
}

fn main() {
    let prefix = String::from("Running");

    block_on(run_twice(async |name| {
        std::future::ready(()).await;
        println!("{prefix}: {name}");
    }));
}
```

`AsyncFn(&str)` reads as: "callable through a shared reference, takes an `&str`, and the call yields asynchronous work that can be awaited."

Just as with `Fn(&str)`, the elided parameter lifetime here has the effect of an HRTB: each time `run_twice` calls `job`, it can pass in the `&str` borrowed on that occasion.

### `async move |...|`

`async` closures can take `move` as well:

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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
    let label = String::from("background job");

    let job = async move || {
        println!("{label}");
    };

    block_on(async {
        job().await;
        job().await;
    });
}
```

The `move` here controls how the closure captures `label` from the **enclosing environment**: the closure takes ownership of `label`. It doesn't mean every call has to move `label` back out of the closure; the body only reads it via sharing, so `job` still satisfies `AsyncFn`, which is what lets the code above call it twice in a row.

Keep the two layers distinct:

- `async move || { ... }`: moves outer values into the closure when the closure is created.
- Calling `job()`: produces a `Future` that may borrow that closure.

## Example Code

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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

async fn for_each_async<F>(items: &[String], action: F)
where
    F: AsyncFn(&str),
{
    for item in items {
        action(item).await;
    }
}

fn main() {
    let items = vec![
        String::from("alpha"),
        String::from("beta"),
        String::from("gamma"),
    ];
    let heading = String::from("Processing");

    block_on(for_each_async(&items, async |item| {
        std::future::ready(()).await;
        println!("{heading}: {item}");
    }));

    println!("{} items processed in total", items.len());
}
```

## Recap

- `async |params| { ... }` creates an `async` closure; calling it produces a `Future`.
- Compared with an ordinary closure returning an `async move` block, an `async` closure naturally expresses a `Future` borrowing the closure's captured environment.
- `AsyncFnOnce`, `AsyncFnMut`, and `AsyncFn` correspond to ordinary closures' `FnOnce`, `FnMut`, and `Fn`.
- `async move` controls how outer values are captured when the closure is created; it doesn't mean every call consumes those values.
