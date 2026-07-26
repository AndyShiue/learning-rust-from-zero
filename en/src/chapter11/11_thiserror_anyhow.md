# A Brief Introduction to `thiserror` / `anyhow`

## Goal of This Episode

Meet the community's two most popular error-handling `crate`s.

## Concept

This episode covers not the standard library, but two community `crate`s. They're practically standard equipment in the Rust ecosystem and extremely useful, so we introduce them here.

Install them before use:

```bash
cargo add thiserror
cargo add anyhow
```

### Background

Last episode we saw how much boilerplate a custom error takes (`enum` + `Display` + `Error` + a `From` for each kind). `thiserror` and `anyhow` solve exactly that.

### `thiserror`: For Libraries

`thiserror` auto-generates `Display`, `Error`, and `From` with a `derive` macro:

```rust,noplayground
# extern crate thiserror;
#
use thiserror::Error;

#[derive(Debug, Error)]
enum AppError {
    #[error("I/O operation failed")]
    Io(#[from] std::io::Error),

    #[error("failed to parse an integer")]
    Parse(#[from] std::num::ParseIntError),

    #[error("custom error: {0}")]
    Custom(String),
}
#
# fn main() {}
```

- `#[error("...")]` auto-generates the `Display` implementation.
- `#[from]` auto-generates the `From` implementation and treats the same field as the underlying cause returned by `.source()`.
- What took dozens of hand-written lines last episode is now a few lines.

Usage is the same as last episode — `?` converts automatically:

```rust,noplayground
# extern crate thiserror;
#
# use thiserror::Error;
#
# #[derive(Debug, Error)]
# enum AppError {
#     #[error("I/O operation failed")]
#     Io(#[from] std::io::Error),
#
#     #[error("failed to parse an integer")]
#     Parse(#[from] std::num::ParseIntError),
#
#     #[error("custom error: {0}")]
#     Custom(String),
# }
#
fn read_number(path: &str) -> Result<i32, AppError> {
    let content = std::fs::read_to_string(path)?;
    let num = content.trim().parse::<i32>()?;
    Ok(num)
}
#
# fn main() {}
```

Callers can still `match` and handle each error kind precisely.

### `anyhow`: For Applications

If callers don't need to distinguish error kinds (say, in the `main` function or a CLI tool), `anyhow` is even simpler:

```rust,noplayground
# extern crate anyhow;
#
use anyhow::{Context, Result};

fn read_number(path: &str) -> Result<i32> {
    let content = std::fs::read_to_string(path)
        .context("failed to read the file")?;
    let num = content.trim().parse::<i32>()
        .context("failed to parse the number")?;
    Ok(num)
}
#
# fn main() {}
```

- `anyhow::Result<T>` is just `Result<T, anyhow::Error>`.
- `anyhow::Error` is similar to `Box<dyn Error + Send + Sync>`, but more convenient to use.
- `.context("...")` adds extra explanation to an error, handy for debugging.
- No new error type to define; errors implementing `Error + Send + Sync + 'static` convert automatically.

### How the Two Relate

- **`thiserror`**: helps you define precise error types without the repetitive hand-written code. For libraries — users can `match` on your errors.
- **`anyhow`**: no separate error type to define; errors meeting the bounds above are handled uniformly through one type. For applications — you just need to report errors, not let others handle them programmatically.

They combine well: libraries define errors with `thiserror`, applications receive them all through `anyhow`.

## Example Code

```rust,no_run
// this example shows anyhow in action
extern crate anyhow;

use anyhow::{Context, Result};
use std::fs;

fn read_config(path: &str) -> Result<(String, i32)> {
    let content = fs::read_to_string(path)
        .context("couldn't read the config file")?;

    let mut lines = content.lines();

    let name = lines.next()
        .context("the config file is empty")?
        .to_string();

    let value = lines.next()
        .context("missing second line")?
        .trim()
        .parse::<i32>()
        .context("the second line isn't a valid number")?;

    Ok((name, value))
}

fn main() -> Result<()> {
    let (name, value) = read_config("config.txt")?;
    println!("name: {}, value: {}", name, value);
    Ok(())
}
```

## Recap

- `thiserror`: auto-generates `Display`, `Error`, and `From` via `derive`; suits libraries.
- `#[error("...")]` generates `Display`; `#[from]` generates `From` and marks the field as the underlying `source`.
- `anyhow`: handles errors implementing `Error + Send + Sync + 'static` uniformly without an error `enum`; suits applications.
- `.context("...")` adds extra explanation to errors.
- Libraries use `thiserror`, applications use `anyhow`, and the two combine well.
