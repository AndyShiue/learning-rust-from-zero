# Why `poll` Needs `Pin`

## Goal of This Episode

Figure out why `poll` writes its `self` as `Pin<&mut Self>`, and by what means `Pin` actually turns "no moving allowed" into reality.

## Main Text

### What `poll` Wants

Recap: once a `Future` in a self-referential state gets moved, its internal self-pointing pointer dangles.

Remember the sequence we ran on `Counter` last episode?

```rust,ignore
let _ = Pin::new(&mut counter).poll(&mut cx); // poll once
let mut moved = counter; // move the whole thing to a new spot with let
let _ = Pin::new(&mut moved).poll(&mut cx); // poll again
```

The two `poll`s printed different addresses — proving a `Future` really can be "polled, moved away, polled again." `Counter` has no self-references, so the move doesn't matter; but run the same routine on a self-referential `Future`, and by the second `poll` it lies at a new address with its self-pointing pointer dangling.

So whoever advances the `Future` (the executor) must keep one rule: **between successive `poll`s, this `Future` must not be moved**. The question is: what kind of `self` should `poll` take to help enforce that rule? From `poll`'s point of view, it wants two properties at once:

1. **Hands-on access**: every `poll` must modify the `Future`'s internals (advancing the state machine, carrying progress forward), so it needs some kind of "mutable" access.
2. **But no relocation**: it must not let anyone seize the chance to move the whole `Future` off its address, or the self-references are ruined.

The ready-made tool — a plain `&mut Self` — satisfies only the first. If `poll` took `&mut Self`, then to the executor this `Future` would be just another ordinary value in hand; between two `poll`s the executor could `let moved = ...` it away exactly as above, with nothing to stop it.

So Rust needs a "hands-on but no-moving" flavor of `&mut`. That's `Pin<&mut T>` — you can read it as "**a `&mut T` tied down in place, not allowed to be moved away**."

Note, though, that "not allowed to move" doesn't mean the value could never move from the moment of its creation. Before being pinned, a value may be moved around under ordinary Rust rules just fine; what `Pin` guarantees is that once you've pinned a value needing pinning, the compiler can no longer let it be moved. After all, before `poll`ing starts, an `async` state machine holds no self-references yet; the real danger is the state machine establishing self-references after a `poll`, then getting relocated.

### The Key: Leave No Route for Moving the Value Out

`Pin<&mut T>` claims "no moving" — but **on what grounds** can it deliver?

The two real keys:

1. When the `Pin` is created, no alternative route may remain by which you could later move the value.
2. Once you hold a `Pin`, the safe API must never hand you back an ordinary pointer capable of moving the value inside.

The first point first.

For `Pin` to keep its "no move" promise, it isn't enough for `Pin` itself to be leak-free; you must also ask whether, after the `Pin` is created, the outside still holds another road to move the value away.

That's what makes `Pin::new(&mut value)` suspicious. A `Pin<&mut T>` is only a temporary borrow: once the borrow ends, the original variable outside still exists and can still be moved. If `Pin::new(&mut value)` were allowed for any `T`, then the `Counter`-style "`poll`, move, `poll` again" routine could be applied verbatim to a self-referential `Future`.

So for types that "break when moved," `Pin::new(&mut value)` ought not be freely available. Right — that's the principle; it's just that some types "don't break when moved," and Rust is happy to let those take this road. Next episode explains that part.

Now the second point.

To a `Pin<&mut T>`, the dangerous thing is a plain `&mut T`. Because with a `&mut T` you can do things like `Option::take`:

```rust,ignore
let old = option.take();
```

It doesn't just turn `Some(value)` into `None` — it moves the `value` out and returns it as `Some(value)`. So if you have a pinned `Option<Future>` and someone can obtain a plain `&mut Option<Future>` from it, they can `.take()` it, moving that `Future` off its original address.

Hence, for an unknown, arbitrary `T`, a `Pin<&mut T>` won't give you a plain `&mut T`. More generally, `Pin<P>` carefully guards the pointer layer `P`. `P` might be `&mut T`, `Box<T>`, or another smart pointer. If a `Pin<Box<T>>` casually handed back the `Box<T>` inside, you'd again hold an ordinary owner of `T`, and could proceed to move `T` out. So for arbitrary `T`, `Pin`'s safe API doesn't return pointers to `T` directly; it offers only a few operations that can't break the pin guarantee.

### `Pin` Has Only a Few Moves

Precisely because its job is "blocking moves," `Pin` doesn't let you do much. The usual repertoire:

**Read-only** — a `Pin<P<T>>` can always be dereferenced to `T` (reading can't move the value out; no risk), courtesy of `Deref`:

```rust,ignore
impl<Ptr: Deref> Deref for Pin<Ptr> {
    type Target = Ptr::Target;
    fn deref(&self) -> &Ptr::Target { /* ... */ }
}
```

**Re-lending a pinned reference** — `as_mut` borrows something like a `&mut Pin<Box<T>>` into a `Pin<&mut T>`. `as_mut` can be called again and again, because it only borrows — and what it lends out is still a `Pin<&mut T>`, not a plain `&mut T`.

And of course, holding a `Pin<&mut F>`, you can do the one thing that matters most — call its `poll`. For a `Future` produced by an `async fn` or `async` block, you never implement `poll` yourself; the compiler generates the implementation for you. Episode 6's executor running `future.as_mut().poll(...)` over and over is exactly this: `as_mut` re-lends a `Pin<&mut F>` and feeds it to `F`'s own `poll` — and when that `F` comes from an `async fn` / `async` block, what runs is precisely the compiler-generated `poll`.

### `Pin` Pins the "Value," Not the "Pointer"

Next, a point that's very easy to get wrong:

> What `Pin<P>` pins is **the value `P` points to** — not "the `Pin<P>` pointer variable itself."

So a `Pin<Box<T>>` can **itself** be moved around freely. Shift it from one variable to another, stuff it into a `Vec`, take it back out — all fine, because what you're moving is only the pointer; the value it points to stays put at its original spot on the heap. Below we print the pointed-to value's address with `{:p}` (`&*` obtains a `&T` from `Pin<P<T>>`) and let the facts speak:

```rust,editable
use std::pin::Pin;

struct Data {
    value: i32,
}

fn main() {
    let mut queue: Vec<Pin<Box<Data>>> = Vec::new();

    let boxed = Box::pin(Data { value: 7 });
    println!("before entering the queue, the value is at {:p}", &*boxed);

    queue.push(boxed); // the Pin<Box<Data>> pointer moves into the Vec
    let popped = queue.pop().unwrap(); // and moves back out

    println!("after leaving the queue, the value is at {:p}", &*popped); // identical address
}
```

The two printed addresses are exactly the same: the pointer went in and out of the `Vec`, but the `Data` on the heap was never moved. The only thing `Pin` forbids is the single act of "**using it to move the pointed-to value off its address**."

### `Pin` Usually Stays Behind the Scenes

Finally, a reassurance: when you write everyday `async fn` + `.await` code on a ready-made runtime, `Pin` usually stays behind the scenes. The compiler generates the `Future` state machine, and the runtime pins and `poll`s it. We meet `Pin` directly in this chapter because we are exploring that machinery ourselves. So don't fret if the details of these episodes feel hazy — they are here to show you what happens underneath, not because you will routinely handle it all by hand.

Should the day come when you hand-roll a low-level `Future` and need to extract a field's `Pin<P<Inner>>` from an outer `Pin<P<Outer>>` (an operation called projection), the community's `pin-project` `crate` does it safely for you, no hand-written `unsafe` required. Knowing the tool exists is enough; we won't go deeper here.

And if you want to "get the value in a `Pin` back as a plain `&mut T`," next episode covers the trick that's often available when "moving wouldn't break it anyway."

## Recap

- `poll` wants both "can modify the innards" and "can't be moved away"; a plain `&mut Self` can't block moves (the executor could still `let moved = ...` between `poll`s), so it won't do.
- `Pin<&mut T>` is "a `&mut` tied down in place"; hence `poll` takes `Pin<&mut Self>`.
- Before being pinned, a value moves freely under normal Rust rules; `Pin` governs what happens "after pinning" — the value can't be moved thereafter.
- Blocking moves requires two things: creation must leave no external route to later move the value; and the safe API must never hand out inner pointers that could move the value.
- `Pin`'s repertoire is small: read via `Deref`, re-lend via `as_mut`, and of course feed it to `poll`.
- `Pin<P>` pins the pointed-to value, not the pointer itself — so a `Pin<Box<T>>` moves freely (even in and out of a `Vec`), which is why the executor can shuffle `Pin<Box<Fut>>`s around.
- For everyday `async fn` + `.await` on a ready-made runtime, `Pin` usually stays behind the scenes: the compiler generates the `Future` state machine, and the runtime pins and `poll`s it. In this chapter, we meet `Pin` directly because we are exploring that machinery ourselves.
