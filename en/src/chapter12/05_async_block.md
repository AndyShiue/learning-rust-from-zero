# `async` block

## Goal of This Episode

Learn to make a `Future` on the spot inside a function with `async { ... }`, and understand its relationship to `async fn`.

## Main Text

### Making a `Future` on the Spot

Besides `async fn`, Rust also lets you create a `Future` **on the spot**, mid-program, with `async { ... }`:

```rust,no_run
# extern crate tokio;
#
#[tokio::main]
async fn main() {
    // this async block is itself a Future
    let fut = async {
        println!("I'm inside an async block");
        42
    };

    // just like an async fn, it only runs when .awaited
    let value = fut.await;
    println!("got {}", value);
}
```

Note: exactly like an `async fn`, merely writing `async { ... }` doesn't execute its contents — you've only made a lazy `Future`, and it moves only when `.await`ed.

### How `async fn` and `async` blocks Relate

A rough first cut at telling them apart:

- An `async fn` is a **named `Future` factory** — define it once, call it repeatedly, each call producing a fresh `Future`.
- An `async` block is **an anonymous `Future` created on the spot** — right here, just this one, no name.

That is, looking only at "named and reusable" versus "anonymous and on the spot," they're a bit like the difference between ordinary functions and closures. But that's just a first-impression analogy — don't read too much into it: `async fn`s and `async` blocks both produce `Future`s, but an `async` block is not a closure; you don't call it with `()`. Once created, it's driven by `.await` or the runtime.

### In the `Result` World, This Needs No New Syntax

Here's an interesting contrast. In the `Result` world, if you want "a block right here where I can use `?`," you need **no new syntax at all** — an immediately invoked closure does it:

```rust,editable
fn main() {
    // define a closure, then call it immediately with ()
    let result: Result<i32, std::num::ParseIntError> = (|| {
        let x = "3".parse::<i32>()?;
        let y = "4".parse::<i32>()?;
        Ok(x + y)
    })();

    println!("{:?}", result);
}
```

The `(|| { ... })()` here means "define a closure and call it immediately." The closure's body can use `?` because the closure itself returns a `Result`; after the call, the outer `main` simply receives that `Result` value.

### Why the `Future` World Can't Copy That Trick

You might wonder: can the `Future` world just do the same? Stuff the `.await` into an immediately invoked closure?

```rust,compile_fail
# extern crate tokio;
#
async fn get_number() -> i32 {
    42
}

#[tokio::main]
async fn main() {
    let value = (|| {
        get_number().await // compile error: can't .await in an ordinary closure
    })();
}
```

No. The reason goes back to the previous episodes: `.await` requires the whole stretch of code to be **rewritten into a state machine** so it can "pause to allow concurrency." But an ordinary closure compiles into an ordinary function, which has **no** notion of "pause now, resume later" — it can't express that rewrite. So the `Result` world's trick doesn't carry over.

This is exactly why `async` blocks exist. Writing `async { ... }` explicitly tells the compiler: "rewrite this block into a `Future`." With that dedicated syntax in place, `.await` becomes legal inside:

```rust,editable
extern crate tokio;

async fn get_number() -> i32 {
    42
}

#[tokio::main]
async fn main() {
    let value = async {
        get_number().await // works this time, because this is an async block
    }.await;
    println!("{}", value);
}
```

With that, the first five episodes have laid down the basic syntax and mental models — `async fn`, `.await`, `async` blocks. Starting next episode, we roll up our sleeves and take the internals of `Future` apart with our own hands.

## Recap

- `async { ... }` creates an anonymous `Future` on the spot, mid-function; it likewise runs only when `.await`ed.
- An `async fn` is a named, reusable `Future` factory; an `async` block is one anonymous `Future` made in place.
- An immediately invoked closure that returns `Result` can use `?` inside; the outer code just receives the closure call's `Result` value.
- `.await` can't copy that trick — it may only appear inside `async` constructs, and an ordinary closure can't pause and resume — hence the dedicated `async` block syntax.
