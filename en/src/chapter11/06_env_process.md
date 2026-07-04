# `std::env` / `std::process`

## Goal of This Episode

Learn to read command-line arguments and environment variables, and to control how the program exits.

## Concept

### Command-line Arguments

A program can be given arguments when run, e.g. `cargo run -- hello world`. Get them with `std::env::args()`:

```rust,editable
use std::env;

fn main() {
    for arg in env::args() {
        println!("{}", arg);
    }
}
```

The first one is the path of the program itself; your arguments come after. Usually you `collect` them into a `Vec`:

```rust,editable
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("please provide an argument");
        return;
    }
    println!("you entered: {}", args[1]);
}
```

### Environment Variables

Environment variables are a set of key-value settings provided by the operating system; programs can read them to get information about the system. If you're not familiar with environment variables, look them up on your own.

```rust,editable
use std::env;

fn main() {
    match env::var("HOME") {
        Ok(val) => println!("HOME = {}", val),
        Err(_) => println!("HOME is not set"),
    }
}
```

`env::var` returns `Result<String, VarError>`. If the environment variable doesn't exist, it returns `Err`.

### `process::exit`

```rust,should_panic
use std::process;

fn main() {
    process::exit(1); // end the program immediately with error code 1
}
```

Returning 0 conventionally means success; nonzero means failure. As we learned in the advanced language features chapter, `process::exit`'s return type is `!` (the never type).

### `eprintln!`

```rust,editable
fn main() {
    eprintln!("this is an error message");
    println!("this is normal output");
}
```

`println!` writes to **`stdout`** (standard output); `eprintln!` writes to **`stderr`** (standard error). They look the same in a terminal, but they can be redirected to different places. Error messages should use `eprintln!`.

## Example Code

```rust,should_panic
use std::env;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("usage: {} <name>", args[0]);
        process::exit(1);
    }

    let name = &args[1];
    println!("hello, {}!", name);

    // print some environment variables
    if let Ok(home) = env::var("HOME") {
        println!("your HOME directory: {}", home);
    }

    if let Ok(path) = env::var("PATH") {
        println!("first 50 characters of PATH: {}", &path[..path.len().min(50)]);
    }
}
```

## Recap

- `env::args()` returns an iterator over the command-line arguments; the first is the program path.
- `env::var("NAME")` returns a `Result`.
- `process::exit(code)` ends the program immediately; its return type is `!`.
- `eprintln!` writes to `stderr` — use it for error messages.
