# `Stream`

## Goal of This Episode

Meet `Stream` — the `async` version of `Iterator` — and learn how to walk through one.

## Main Text

### `Stream` Is the `async` Version of `Iterator`

Chapter 6's `Iterator` is "a sequence of values, taken one at a time." Its `.next()` is a **synchronous** call that returns the next value (or `None`) when it completes. If fetching the value requires expensive computation or blocking I/O, the call must wait for that work to finish.

`Stream` is its `async` counterpart: still a sequence of values taken one at a time, but you can **wait asynchronously for the next value**, such as the next piece of data arriving over the network. Its `.next()` returns a `Future`, and `.next().await` obtains the next value; while the data isn't ready, it can yield control so the runtime can work on other `Task`s.

The side-by-side makes it easy to remember:

- `iterator.next()` → a synchronous call that returns `Option<Item>` when it completes.
- `stream.next().await` → waits asynchronously through `.await`, producing `Option<Item>` when it completes.

Both use "`None` means the end."

These examples use the `tokio-stream` `crate` (it's not part of Tokio proper), so add the dependency first:

```toml
[dependencies]
tokio-stream = "0.1"
```

One small thing to watch: the `crate` name is written `tokio-stream` (hyphen) in `Cargo.toml`, but `tokio_stream` (underscore) in code — a `-` in a `crate` name always becomes `_` in code.

### Walking Through a `Stream`

An `Iterator` can be walked with `for`, but a `Stream` can't (`for` has no way to `.await`). The standard way to walk a `Stream` is **`while let Some(x) = stream.next().await`** — take values one by one, stopping at `None`:

```rust,editable
extern crate tokio;
extern crate tokio_stream;

use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    // build the simplest stream from a Vec
    let mut stream = tokio_stream::iter(vec![1, 2, 3]);

    // take values one at a time, until None
    while let Some(value) = stream.next().await {
        println!("got {}", value);
    }
}
```

### `Stream` Isn't in the Standard Library

One thing deserves special mention: unlike `Future`, `Stream` is **currently not in the standard library**. The `Stream` `trait` is defined in the `futures-core` `crate`; `tokio-stream` re-exports it and provides its own `StreamExt`. To use this episode's `next`, `map`, and `filter` methods, import `tokio_stream::StreamExt`:

```rust,editable
extern crate tokio;
extern crate tokio_stream;

use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    // just like Iterator, you can chain tools like map / filter
    let mut stream = tokio_stream::iter(1..=5)
        .map(|x| x * 2)
        .filter(|x| x % 3 == 0);

    while let Some(value) = stream.next().await {
        println!("{}", value);
    }
}
```

You'll notice `map`, `filter`, and friends are nearly identical to Chapter 6's `Iterator` — because `Stream` really is `Iterator`'s `async` twin. If you've learned `Iterator`, `Stream` is just that plus `.await`.

In practice, `Stream` is a great fit for "data that keeps arriving over time" — network connections coming in one by one, database query results row by row, or events fired on a schedule. `tokio_stream` provides a whole toolkit for working with them.

## Recap

- `Stream` is the `async` version of `Iterator`: a sequence of values taken one at a time, using `.next().await` to wait asynchronously for the next value.
- Side by side: `iterator.next()` returns an `Option` synchronously; `stream.next().await` needs `.await` to return an `Option`; both end with `None`.
- Walk it with **`while let Some(x) = stream.next().await`** (`for` doesn't work on a `Stream`).
- `Stream` isn't in the standard library; it's defined in `futures`, and `tokio_stream::StreamExt` provides `next`, `map`, `filter`, etc. (used almost exactly like `Iterator`).
