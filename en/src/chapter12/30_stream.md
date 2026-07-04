# `Stream`

## Goal of This Episode

Meet `Stream` — the `async` version of `Iterator` — and learn how to walk through one.

## Main Text

### `Stream` Is the `async` Version of `Iterator`

Chapter 6's `Iterator` is "a sequence of values, taken one at a time." But its `.next()` is **synchronous** — call it and you immediately get the next value (or `None`).

`Stream` is its `async` counterpart: still a sequence of values taken one at a time, but the next value **may require waiting** (say, for the network to deliver the next piece of data, for a timer, or for user input). So `Stream`'s `.next()` returns a `Future`, and you have to `.next().await` to get the next value.

The side-by-side makes it easy to remember:

- `iterator.next()` → returns `Option<Item>` (synchronous, immediate).
- `stream.next().await` → returns `Option<Item>` (requires `.await`, may wait a bit).

Both use "`None` means the end."

These examples use the `tokio_stream` crate (it's not part of Tokio proper), so add the dependency first:

```toml
[dependencies]
tokio-stream = "0.1"
```

One small thing to watch: the crate name is written `tokio-stream` (hyphen) in `Cargo.toml`, but `tokio_stream` (underscore) in code — a `-` in a crate name always becomes `_` in code.

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

One thing deserves special mention: unlike `Future`, `Stream` is **currently not in the standard library**. It's defined in a community project (`futures`), and the Tokio ecosystem provides `tokio_stream`. To use methods like `next`, `map`, and `filter`, you import the corresponding extension `trait`, `StreamExt`:

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

- `Stream` is the `async` version of `Iterator`: a sequence of values taken one at a time, where the next value may require waiting — hence `.next().await`.
- Side by side: `iterator.next()` returns an `Option` synchronously; `stream.next().await` needs `.await` to return an `Option`; both end with `None`.
- Walk it with **`while let Some(x) = stream.next().await`** (`for` doesn't work on a `Stream`).
- `Stream` isn't in the standard library; it's defined in `futures`, and `tokio_stream::StreamExt` provides `next`, `map`, `filter`, etc. (used almost exactly like `Iterator`).
