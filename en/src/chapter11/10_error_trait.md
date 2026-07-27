# The `Error` `trait`

## Goal of This Episode

Learn to define custom error types, and to handle errors of different kinds uniformly with `Box<dyn Error>`.

## Concept

### Recap: `Result` and `?`

Chapter 5 covered `Result<T, E>` and the `?` operator. But the error types back then were simple — one function produced one kind of error. Real programs often face several: reading a file can fail (`io::Error`), and parsing a number can fail too (`ParseIntError`). If both can happen inside one function, what do you put for the `E` in the returned `Result`?

### The `Error` `trait`

The standard library defines the `std::error::Error` `trait`, the common interface of all error types:

```rust,noplayground
pub trait Error: std::fmt::Display + std::fmt::Debug {
    fn source(&self) -> Option<&(dyn Error + 'static)> { None }
}
#
# fn main() {}
```

To implement `Error`, your type must first implement `Display` and `Debug`. `.source()` returns the underlying cause of this error, defaulting to `None`.

### Custom Error Types

Wrap all the possible errors together in an `enum`:

```rust,noplayground
use std::fmt;

#[derive(Debug)]
enum AppError {
    Io(std::io::Error),
    Parse(std::num::ParseIntError),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::Io(_) => write!(f, "I/O operation failed"),
            AppError::Parse(_) => write!(f, "failed to parse an integer"),
        }
    }
}

impl std::error::Error for AppError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            AppError::Io(e) => Some(e),
            AppError::Parse(e) => Some(e),
        }
    }
}
#
# fn main() {}
```

For example, `AppError::Parse` displays "failed to parse an integer," while `.source()` returns the original `ParseIntError` so callers can inspect the detailed parsing error when needed. This preserves both the outer message and the underlying cause without printing the same error text twice.

Chapter 5 said `?` returns early when it meets an `Err`. Actually `?` does one more thing: it calls `From::from(e)` to convert the error into the `E` of the function's return type. So as long as you implement `From` for the underlying errors, `?` converts automatically:

```rust,noplayground
# use std::fmt;
#
# #[derive(Debug)]
# enum AppError {
#     Io(std::io::Error),
#     Parse(std::num::ParseIntError),
# }
#
# impl fmt::Display for AppError {
#     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
#         match self {
#             AppError::Io(_) => write!(f, "I/O operation failed"),
#             AppError::Parse(_) => write!(f, "failed to parse an integer"),
#         }
#     }
# }
#
# impl std::error::Error for AppError {
#     fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
#         match self {
#             AppError::Io(e) => Some(e),
#             AppError::Parse(e) => Some(e),
#         }
#     }
# }
#
impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self {
        AppError::Io(e)
    }
}

impl From<std::num::ParseIntError> for AppError {
    fn from(e: std::num::ParseIntError) -> Self {
        AppError::Parse(e)
    }
}
#
# fn main() {}
```

Now one function can use `?` on both kinds of errors:

```rust,noplayground
# use std::fmt;
#
# #[derive(Debug)]
# enum AppError {
#     Io(std::io::Error),
#     Parse(std::num::ParseIntError),
# }
#
# impl fmt::Display for AppError {
#     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
#         match self {
#             AppError::Io(_) => write!(f, "I/O operation failed"),
#             AppError::Parse(_) => write!(f, "failed to parse an integer"),
#         }
#     }
# }
#
# impl std::error::Error for AppError {
#     fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
#         match self {
#             AppError::Io(e) => Some(e),
#             AppError::Parse(e) => Some(e),
#         }
#     }
# }
#
# impl From<std::io::Error> for AppError {
#     fn from(e: std::io::Error) -> Self {
#         AppError::Io(e)
#     }
# }
#
# impl From<std::num::ParseIntError> for AppError {
#     fn from(e: std::num::ParseIntError) -> Self {
#         AppError::Parse(e)
#     }
# }
#
fn read_number(path: &str) -> Result<i32, AppError> {
    let content = std::fs::read_to_string(path)?; // io::Error → AppError
    let num = content.trim().parse::<i32>()?;     // ParseIntError → AppError
    Ok(num)
}
```

### The Problem: All That Every Time?

A custom error type + `impl Display` + `impl Error` + a `From` for each kind... quite a mouthful. Is there a simpler way?

### `Box<dyn Error>`

If your return type doesn't need to expose a fixed set of error kinds that callers can match exhaustively, use `Box<dyn Error>` as a catch-all error type:

```rust,noplayground
use std::error::Error;

fn read_number(path: &str) -> Result<i32, Box<dyn Error>> {
    let content = std::fs::read_to_string(path)?;
    let num = content.trim().parse::<i32>()?;
    Ok(num)
}
#
# fn main() {}
```

Concrete error types implementing `Error + 'static` can be converted automatically into `Box<dyn Error>`, so these errors work directly with `?` without a hand-written `From` implementation.

`Box<dyn Error>` erases the concrete error's static type, so callers cannot exhaustively `match` it like a custom error `enum`. The error information is not completely lost, however: callers can inspect the underlying cause through `.source()` or check a known concrete type with `.downcast_ref::<T>()`.

For example, a caller can check whether a `Box<dyn Error>` contains a `std::io::Error`:

```rust,no_run
# use std::error::Error;
#
# fn read_number(path: &str) -> Result<i32, Box<dyn Error>> {
#     let content = std::fs::read_to_string(path)?;
#     let num = content.trim().parse::<i32>()?;
#     Ok(num)
# }
#
fn main() {
    if let Err(error) = read_number("missing.txt") {
        if let Some(io_error) = error.downcast_ref::<std::io::Error>() {
            println!("this is an I/O error of kind {:?}", io_error.kind());
        } else {
            println!("this is some other error: {}", error);
        }
    }
}
```

If the `Box` directly contains a `std::io::Error`, `.downcast_ref::<std::io::Error>()` returns `Some(&std::io::Error)`; for a different type it returns `None`. For example, if the `Box` contains an `AppError`, then `error.downcast_ref::<std::io::Error>()` still returns `None` even when the value is `AppError::Io` wrapping a `std::io::Error`, because the type stored directly in the `Box` is `AppError`. In that case, call `.source()` first to obtain the wrapped error, then call `.downcast_ref::<T>()` on it.

`Box<dyn Error>` by itself does not guarantee that the error can cross `Thread` boundaries. If an error must be sent to another `Thread`, or an API requires thread-safe errors, a common type is `Box<dyn Error + Send + Sync>`; the contained error must implement `Send + Sync` as well.

### Which One When

- **Quick prototypes, scripts, the `main` function**: `Box<dyn Error>` is the least effort.
- **Libraries, or when callers must handle errors precisely**: a custom error `enum` + `impl Error` + `impl From`.

Next episode we'll see how community `crate`s dramatically simplify writing custom error types.

## Example Code

```rust,editable
use std::error::Error;
use std::fs;

fn first_line_number(path: &str) -> Result<i32, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let first_line = content.lines().next().ok_or("the file is empty")?;
    let num = first_line.trim().parse::<i32>()?;
    Ok(num)
}

fn main() {
    match first_line_number("number.txt") {
        Ok(n) => println!("number read: {}", n),
        Err(e) => println!("error: {}", e),
    }
}
```

## Recap

- The `Error` `trait` requires `Display + Debug` and is the common interface of all error types.
- Custom errors: define an `enum` → `impl Display` → `impl Error` (preserving causes with `.source()`) → `impl From` for each underlying error.
- With `From` in place, `?` automatically converts underlying errors into your custom error.
- `Box<dyn Error>` erases the concrete error's static type, but errors remain inspectable through `.source()` or downcasting.
- To send errors across `Thread` boundaries, `Box<dyn Error + Send + Sync>` is commonly used.
- `Box<dyn Error>` suits rapid development; custom error `enum`s suit libraries.
