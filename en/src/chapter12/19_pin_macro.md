# `pin!`

## Goal of This Episode

Learn to pin a `Future` on the stack with `pin!`, and understand why it absolutely has to be a macro.

## Main Text

### stack pinning

So far, to pin a `Future` we've always used `Box::pin` — putting it on the heap. But sometimes you'd rather not pay for a heap allocation just to pin a `Future` (there is a cost to it), especially when the `Future` is only used within the current scope and never passed out.

For that, use `std::pin::pin!`. It pins a value within the current scope and gives you a `Pin<&mut T>`:

```rust,editable
use std::future::Future;
use std::pin::pin;
use std::task::{Context, Poll, Waker};

async fn hello() -> i32 {
    42
}

fn main() {
    // pin this future on the stack, getting a Pin<&mut _>
    let mut future = pin!(hello());

    let mut cx = Context::from_waker(Waker::noop());
    match future.as_mut().poll(&mut cx) {
        Poll::Ready(value) => println!("done: {}", value),
        Poll::Pending => println!("not ready yet"),
    }
}
```

Here's an easy point of confusion: the compiler currently takes the conservative stance that `Future`s produced by `async fn`s like `hello()` — and `async` blocks — are all treated as **not** `Unpin`, even this `hello`, which has no `.await` and couldn't possibly be self-referential (the compiler doesn't want to judge case by case, so it simply implements `Unpin` for none of them). So last episode's `Pin::new` won't work on it — but `pin!` will: `pin!` performs **stack pinning**, and its way of pinning doesn't require `Unpin`.

### Why `pin!` Must Be a Macro

This is a delightful question. Why is `pin!` a macro rather than an ordinary function?

Grab the key fact first: the `Pin<&mut T>` that `pin!` hands you is a **reference**, and a reference must point at a value that's still alive. As long as you hold that `Pin<&mut T>`, the value it borrows must not disappear.

So the problem isn't merely "how to produce a `Pin<&mut T>`"; it's that the value this `Pin<&mut T>` borrows has to live long enough.

Written as an ordinary function, it would look like:

```rust,ignore
fn pin<T>(value: T) -> Pin<&mut T> { /* ??? */ }
```

That can't work. `value` is a local variable of the `pin` function itself. The moment the function returns, its locals are cleaned up and `value` vanishes — the returned `Pin<&mut T>` instantly becomes a dangling reference into invalidated memory. In fact the compiler flat-out won't let you return a reference to "a function's own local variable."

`pin!` isn't an ordinary function, so it doesn't have the "returning a reference to my own stack variable" problem. The `Pin<&mut T>` that `pin!` produces borrows a value in the scope where `pin!` is used, not some ordinary function's own temporary. Hence the borrow doesn't dangle the moment a function returns, and you can use it with confidence.

### Contrast with `Box::pin`

Then why can `Box::pin` be an ordinary function? Because it takes an entirely different road: `Box::pin` puts the value on the **heap** and hands you ownership of that heap memory wrapped in a `Pin<Box<T>>`. Something owned on the heap outlives "this function call" — returning doesn't discard it — so returning an owning `Pin<Box<T>>` is perfectly fine.

In short, here's how they differ:

- `pin!`: **stack borrowing** — obtain a `Pin<&mut T>` from a value in the current block without heap allocation; since ordinary functions can't return references to their own stack variables, this must be done by a macro at the call site.
- `Box::pin`: **heap owning** — the value goes on the heap, ownership is handed over, it can be passed around freely, so an ordinary function works. The cost is one heap allocation.

## Recap

- `pin!` does **stack pinning**: a `Pin<&mut T>` valid only within the current block, no heap allocation — good when the pinned value needn't leave the scope.
- `pin!` must be a **macro**, not a function: an ordinary function can't return a `Pin<&mut T>` into its own stack; the reference would dangle on return (and the compiler forbids it anyway).
- `Box::pin` hands over ownership with the value on the heap (outliving the call), so it can be an ordinary function; the difference is "stack borrowing vs heap owning."
