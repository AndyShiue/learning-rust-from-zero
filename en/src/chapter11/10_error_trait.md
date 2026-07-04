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
            AppError::Io(e) => write!(f, "I/O error: {}", e),
            AppError::Parse(e) => write!(f, "parse error: {}", e),
        }
    }
}

impl std::error::Error for AppError {}
#
# fn main() {}
```

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
#             AppError::Io(e) => write!(f, "I/O error: {}", e),
#             AppError::Parse(e) => write!(f, "parse error: {}", e),
#         }
#     }
# }
#
# impl std::error::Error for AppError {}
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
#             AppError::Io(e) => write!(f, "I/O error: {}", e),
#             AppError::Parse(e) => write!(f, "parse error: {}", e),
#         }
#     }
# }
#
# impl std::error::Error for AppError {}
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

If you don't need to distinguish error kinds precisely, use `Box<dyn Error>` as a catch-all error type:

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

Any type implementing `Error` converts into `Box<dyn Error>` automatically, so `?` just works — no manual `From` needed.

The downside: callers can't `match` to handle different error kinds precisely — they only know "there was an error," not which one.

### Which One When

- **Quick prototypes, scripts, the `main` function**: `Box<dyn Error>` is the least effort.
- **Libraries, or when callers must handle errors precisely**: a custom error `enum` + `impl Error` + `impl From`.

Next episode we'll see how community crates dramatically simplify writing custom error types.

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
- Custom errors: define an `enum` → `impl Display` → `impl Error` → `impl From` for each underlying error.
- With `From` in place, `?` automatically converts underlying errors into your custom error.
- `Box<dyn Error>`: a catch-all error type; any `Error` converts automatically and `?` just works.
- `Box<dyn Error>` suits rapid development; custom error `enum`s suit libraries.
