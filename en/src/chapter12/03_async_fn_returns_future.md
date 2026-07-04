# An `async fn` Returns a `Future`

## Goal of This Episode

Build a key mental model: calling an `async fn` doesn't execute it — you merely get a `Future` that hasn't started running.

## Main Text

### Calling an `async fn` Doesn't Run It

This is the pit beginners fall into most often, so let's prove it by experiment. Start with an ordinary `async fn`:

```rust,no_run
# extern crate tokio;
#
async fn say_hello() {
    println!("hello");
}

#[tokio::main]
async fn main() {
    say_hello(); // note: this line does NOT print hello!
}
```

Intuitively you'd expect calling `say_hello()` to print `hello`, but in fact **nothing happens**. The `println!` in the function body never runs. Not only that, the compiler gives you a warning:

```text
warning: unused implementor of `Future` that must be used
note: futures do nothing unless you `.await` or poll them
```

This warning (courtesy of `#[must_use]`) already spills the truth: calling `say_hello()` gives you a **`Future`** — a "job that hasn't run yet." You've only described the job; nobody executed it, so it got thrown away.

To actually run it, add `.await`:

```rust,no_run
# extern crate tokio;
#
async fn say_hello() {
    println!("hello");
}

#[tokio::main]
async fn main() {
    say_hello().await; // this time hello gets printed
}
```

### Making the Compiler Confirm It's a `Future`

Still not convinced? We can force the compiler to tell the truth another way: deliberately annotate the wrong return type and see how it complains.

```rust,compile_fail
# extern crate tokio;
#
async fn say_hello() {
    println!("hello");
}

#[tokio::main]
async fn main() {
    let x: () = say_hello(); // compile error
}
```

`say_hello`'s body returns nothing, so it "should" return `()`, and we deliberately write `let x: () = ...`. But the compiler errors:

```text
expected `()`, found future
```

It tells you plainly: the type of `say_hello()` is **not** `()` but a future. Confirmed — calling an `async fn` gets you a `Future`, not the result of the body's execution.

### `Future`s Are Lazy

The two sections above showed two things: calling `say_hello()` doesn't execute the body immediately; and `say_hello()`'s return type isn't `()` but a `Future`. Put together, they give this episode's most important sentence:

> Calling an `async fn` just gets you a `Future`, and that `Future` is **lazy**.

"Lazy" should sound familiar. Recall Chapter 6's **iterators**: when you write `v.iter().map(...).filter(...)`, those methods haven't processed a single element — they only describe "what to do later"; the real running starts the moment you `.collect()` or walk it with `for`.

`Future` and `Iterator` share the same design philosophy at heart: **describe first, execute later**. An `Iterator` describes "how a sequence of values gets computed" and moves only when you ask; a `Future` describes "what an async job will do" and moves only when the runtime pushes it forward.

Next episode we switch angles and set `.await` beside the `?` you've long known — you'll find they're the same kind of thing.

## Recap

- Calling an `async fn` does **not** execute the body; you only get a `Future`.
- Without a `.await` in `async fn main`, the called `async` function won't run a single line, and you'll get a `#[must_use]` warning.
- Annotating the return value as `()` makes the compiler report `expected (), found future`, proving it really is a `Future`.
- `Future`s are **lazy** — like Chapter 6's `Iterator`, the design is "describe first, execute later."
