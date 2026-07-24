# `Unpin`

## Goal of This Episode

Meet `Unpin`, the "doesn't break when moved" label, and see why, with it, a pinned `&mut` can turn back into a plain `&mut`.

## Main Text

### First, a Question: Who Does "No Moving" Actually Protect?

Last episode `Pin` went to great lengths to block post-pinning moves. But step back: who is this rule really guarding against?

The answer — apart from rare special cases like **self-referential `Future` state machines**, the types you use daily (`i32`, `String`, `Vec`, your own `struct`s…) don't break at all when moved; to them a move is just storing a few bytes somewhere else. Forcing "no moving" onto these types is pure meddling.

Rust separates the two camps with a label, and that label is **`Unpin`**: a type being `Unpin` means "**moving me doesn't break me; `Pin` needn't bother about me**."

### Almost Everything Is `Unpin`

Like the `Send` / `Sync` introduced in the multithreading chapter, `Unpin` is an **`auto trait`** — if everything a type stores is `Unpin`, the type itself is `Unpin` by default. Skipping to the punchline: **the overwhelming majority of types are `Unpin`**.

A small gadget verifies this. The `assert_unpin` below only accepts `Unpin` types, and all the common values pass:

```rust,editable
fn assert_unpin<T: Unpin>(_: T) {}

fn main() {
    assert_unpin(42);
    assert_unpin(String::from("hi"));
    assert_unpin(vec![1, 2, 3]);
    println!("these are all Unpin");
}
```

Even our hand-written `Delay`, `Counter`, `JoinAll`, and `JoinHandle` are all `Unpin` — their fields are ordinary movable things.

So who isn't `Unpin`? Point the same gadget at an `async fn` that "borrows a local across an `.await`" (i.e. Episode 16's self-referential state machine) and it gets blocked:

```rust,compile_fail
fn assert_unpin<T: Unpin>(_: T) {}

async fn other() {}

async fn demo() {
    let s = String::from("hi");
    let r = &s;
    other().await; // s and r both cross the .await
    println!("{}", r);
}

fn main() {
    assert_unpin(demo()); // compile error: demo()'s Future is not Unpin
}
```

The compiler says `... cannot be unpinned`. And rightly so: the `Future` of an `async fn` / `async` block **cannot be assumed `Unpin`**, because it might be exactly that move-breaks-it self-referential state machine.

### `Unpin` Types Can Ask for the Value Back

Knowing who's `Unpin`, we can now pay off last episode's foreshadowing: "turning a pinned value back into a plain `&mut T`" is open to `Unpin` types.

The logic is direct: since this type doesn't break when moved, `Pin`'s protection was superfluous for it anyway — so you may as well have the plain `&mut T` back. Concretely, only when `T: Unpin` does `Pin<&mut T>` offer `get_mut` to turn back into `&mut T`, and only then does `Pin<P<T>>` implement `DerefMut`:

```rust,editable
use std::pin::Pin;

fn main() {
    let mut n = 10;
    let mut pinned: Pin<&mut i32> = Pin::new(&mut n);

    // i32 is Unpin, so Pin<&mut i32> implements DerefMut
    *pinned = 100;
    println!("{}", pinned);

    // get_mut also recovers a plain &mut i32
    let back: &mut i32 = pinned.get_mut();
    *back += 5;
    println!("{}", back);
}
```

That's why every one of our custom `Future`s could open its `poll` with `let this = self.get_mut();` without trouble. Those types are all `Unpin`, so of course `get_mut` works. If some day your `Future` isn't `Unpin`, that line fails to compile, forcing you to handle things carefully through `Pin`'s methods instead.

### Two Actions, Both Demanding `Unpin`

Last episode said `Pin`'s guarantee rests on two things:

1. When the `Pin` is created, no alternative route may remain for later moving the value.
2. Once you hold a `Pin`, the safe API must never hand back an ordinary pointer that could move the value inside.

Now set `Pin::new` and `get_mut` side by side, and you'll see they each relax one of those restrictions — and both demand **the same condition**: `Unpin`:

```rust,ignore
// method one: create a Pin from an existing pointer
// not allowed if the pointed-to value isn't Unpin
impl<P: Deref> Pin<P> {
    pub fn new(pointer: P) -> Pin<P> where P::Target: Unpin { /* ... */ }
}

// method two: turn a pinned value back into a plain &mut
// also not allowed unless T is Unpin
impl<T: ?Sized> Pin<&mut T> {
    pub fn get_mut(self) -> &mut T where T: Unpin { /* ... */ }
}
```

`Pin::new` relaxes the first restriction. It lets you take an existing pointer — say a `&mut T` — and wrap it straight into a `Pin<&mut T>`. For move-breaks-it types this is dangerous, because `Pin<&mut T>` is only a temporary borrow; once the borrow ends, the original variable `T` outside can still be moved. So `Pin::new` is only permitted for `T: Unpin`.

`get_mut` relaxes the second restriction. It turns `Pin<&mut T>` back into a plain `&mut T`. That too is only safe for `T: Unpin`, since a plain `&mut T` can do things like `Option::take` that move values off their address. `DerefMut` likewise.

`Unpin` is the statement: "this type doesn't break when moved, so these actions are safe on it." Episode 16's `Counter` is `Unpin` — `Pin::new(&mut counter)`, `get_mut`, and `DerefMut` all sail through; the self-referential `async` state machine is not `Unpin`, and both actions are denied it.

So the practical judgment is simple: is the `Future` in your hand `Unpin`? If yes, `Pin::new`, `get_mut`, `DerefMut` are yours to use. If not (typically the `Future` born of an `async fn` / `async` block), you must pin it in a way that upholds `Pin`'s guarantee — `Box::pin` onto the heap, or the `pin!` macro debuting next episode, onto the stack.

## Recap

- Apart from rare cases like self-referential `async` state machines, most everyday types survive moves just fine.
- `Unpin` is the "doesn't break when moved" label — an `auto trait`, implemented automatically by the compiler; **the vast majority of types are `Unpin`**.
- The `Future` of an `async fn` / `async` block can't be assumed `Unpin` (it may be a self-referential state machine).
- Only when `T: Unpin` can `Pin<&mut T>` use `get_mut` to recover a plain `&mut T`, and only then does `Pin<P<T>>` implement `DerefMut` — which is why our hand-written `Future`s could call `self.get_mut()`.
- `Pin::new` and `get_mut` / `DerefMut` relax last episode's two restrictions respectively — creating a `Pin` from an existing pointer, and recovering a plain `&mut` — and both are open only to `Unpin`.
- When a `Future` isn't `Unpin`, pin it with `Box::pin` or next episode's `pin!`.
