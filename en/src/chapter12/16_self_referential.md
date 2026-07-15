# Self-referential `Future`s

## Goal of This Episode

Understand why an `async` state machine can become a structure that "points at itself," and why moving such a structure spells trouble.

## Main Text

### Moving a Value Changes Its Address

Start with an ordinary program containing **no** `async` at all. Using `{:p}` (the address-printing format), we look at a value's address before and after a move:

```rust,editable
fn main() {
    let p1 = String::from("hello");
    println!("p1's address: {:p}", &p1);

    let p2 = p1; // move: relocate p1 into p2
    println!("p2's address: {:p}", &p2);
}
```

The two addresses differ. Which makes sense — `p1` and `p2` are two different local variables living at different spots on the stack, and a move relocates the value from one place to the other.

For ordinary values this is perfectly fine: after the move, the old variable `p1` can't be used anymore (Chapter 4's ownership rules), so "the old address is dead" bothers no one.

### But What If the Value Stores "an Address Pointing Into Itself"?

The trouble comes with a special kind of value: **one of its fields stores the address of another of its own fields**.

Imagine such a value being moved to a new location. The address stored inside **doesn't update itself** — it still points at the **old** spot. But what lived there has moved away, so the pointer becomes a **dangling pointer** (pointing into memory that's no longer valid). The moment anyone follows it, that's undefined behavior — the program might read garbage, or blow up outright.

Do such "pointing at itself" values actually come up? They do — **a self-referential `Future` state machine is exactly such a value**. Recall last episode: an `async fn` gets rewritten into a state machine, and locals needed across an `.await` get stored inside it. If one of those locals is "a reference to another local," then the state machine holds a field pointing at another of its own fields — a textbook self-referential structure.

```rust,noplayground
# async fn other() {}
#
async fn borrows() {
    let s = String::from("hello");
    let r = &s; // r borrows s
    other().await; // crossing an .await — both s and r must be preserved by the state machine
    println!("{}", r); // r is used after the .await
}
#
# fn main() {}
```

This `async fn`'s state machine, in the state at that `.await`, stores both `s` and `r`, with `r` pointing at `s`. That's self-reference. Move it while in that state, and `r` becomes a dangling pointer. Hence the conclusion: **once a `Future` has been `poll`ed into a possibly self-referential state, moving it is dangerous**.

### First, Prove "create → `poll` → move → `poll`" Is Achievable

Before discussing defenses, though, let's confirm one thing: a `Future` really can be "moved after being `poll`ed, then `poll`ed again." Here's a minimal `Future` — `Counter` — that bumps a count on every `poll` and prints `self`'s address with `{:p}`:

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};

struct Counter {
    count: u32,
}

impl Future for Counter {
    type Output = ();

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        this.count += 1;
        println!("poll number {}, self at address {:p}", this.count, this);
        Poll::Pending
    }
}

fn main() {
    let mut cx = Context::from_waker(Waker::noop());

    let mut counter = Counter { count: 0 };
    let _ = Pin::new(&mut counter).poll(&mut cx); // poll once

    let mut moved = counter; // move to a new location
    let _ = Pin::new(&mut moved).poll(&mut cx); // poll again
}
```

Run it and the two `poll`s print **different** addresses — proof that the "`poll` → move → `poll` again" sequence really can happen, with the `Future` at a new address by the second `poll`. `Counter` has no self-references, so moving it is harmless; but swap in the self-referential state machine above, and that move is a disaster.

### Rust's Line of Defense: If Moving Breaks It, You Don't Even Get in the Door

So how does Rust stop self-referential `Future`s from being moved about? Let's apply the same sequence to the "borrow across `.await`" `async fn` from before:

```rust,compile_fail
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Waker};

async fn other() {}

async fn borrows() {
    let s = String::from("hello");
    let r = &s;
    other().await;
    println!("{}", r);
}

fn main() {
    let mut cx = Context::from_waker(Waker::noop());
    let mut fut = borrows();

    // try to do what Counter did: poll once
    let _ = Pin::new(&mut fut).poll(&mut cx); // compile error!

    // then move to a new location
    let mut moved = fut;

    // and poll again
    let _ = Pin::new(&mut moved).poll(&mut cx); // this wouldn't be allowed either
}
```

The compiler blocks it flat:

```text
error[E0277]: `{async fn body of borrows()}` cannot be unpinned
```

The code spells out the whole "`poll` once, move, `poll` again" routine, but the compiler actually stops it at the very first `Pin::new(&mut fut)`.

`Pin::new` requires the type to be `Unpin` (meaning "safe to move" — details soon). `Counter` is `Unpin`, so it passes; but this self-referential `async fn` state machine is **not** `Unpin`, so `Pin::new` bars the way **before you've actually polled it or actually moved it**.

Comparing the two examples, Rust's line of defense is clear: things that survive moving (like `Counter`) get the convenience — move them at will; things that break when moved (self-referential state machines) don't even get through the `Pin::new` door. How `Pin` builds this defense out of the type system is the subject of what comes next.

## Recap

- Moving a value changes its address; for ordinary values that's fine, since the old variable can't be used anymore.
- If a value stores "an address pointing into itself," a move leaves that address un-updated — a dangling pointer. Dangerous.
- The state machines produced by `async fn` / `async` blocks can be such values: if a borrow crosses an `.await`, the machine may hold both the borrowed value and the reference — one field pointing at another.
- The `Counter` example proves "`poll` → move → `poll` again" is achievable (two different addresses).
- Rust's defense is `Unpin`: `Counter` is `Unpin` and passes `Pin::new`; a self-referential `async` state machine is not `Unpin`, and `Pin::new` fails to compile.
