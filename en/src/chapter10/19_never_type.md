# The Never Type `!`

## Goal of This Episode

Meet the `!` type — the type of things that never produce a value.

## Concept

### Functions That Never Return

Most functions finish and return a value. But some functions **never return**:

```rust,noplayground
fn forever() -> ! {
    loop {
        // runs forever
    }
}
#
# fn main() {}
```

`-> !` means this function cannot possibly return.

### What Has Type !

- `panic!("...")` — panics the current `Thread` instead of returning normally.
- `std::process::exit(0)` — the program ends.
- `loop {}` (with no break) — runs forever.
- A `return` expression itself
- A `break` expression itself
- A `continue` expression itself

### `!` Coerces into Any Type

This is `!`'s most useful property. An expression that never produces a value can sit anywhere a value is expected without contradiction — it's never actually going to produce one anyway.

This is why code like the following compiles:

```rust,noplayground
# fn main() {
#     let option = Some(1);
    let x: i32 = match option {
        Some(v) => v,
        None => panic!("shouldn't be None"),
    };
# }
```

Every arm of a `match` must return the same type. `Some(v) => v` returns `i32`, and `None => panic!(...)` returns `!`. Since `!` can convert into any type, it's treated as `i32`, and the `match`'s types line up.

`return`, `break`, and `continue` work the same way:

```rust,ignore
# fn main() {
    let x: i32 = match option {
        Some(v) => v,
        None => return, // return has type !
    };
# }
```

```rust,ignore
# fn main() {
    for item in list {
        let value: i32 = match item.parse::<i32>() {
            Ok(n) => n,
            Err(_) => continue, // continue has type !
        };
        println!("{}", value);
    }
# }
```

### Using `!` in Other Type Positions

Like any other type, `!` can be written anywhere a type is expected. The simplest example is a variable's type:

```rust,should_panic
fn main() {
    let _never: ! = panic!("this variable never gets a value");
}
```

The right-hand side of `=` must be an expression of type `!`, such as `panic!(...)`. So this variable never actually gets a value — the program panics on this very line.

`!` can also go inside other types. For example, `Result<i32, !>` is a `Result` that always succeeds and can never be `Err`:

```rust,editable
fn always_ok() -> Result<i32, !> {
    Ok(42)
}

fn main() {
    let Ok(value) = always_ok();
    println!("{}", value);
}
```

In Chapter 3 we learned that `let` only accepts patterns that can't fail to match. `Ok(value)` can't fail here: to be an `Err`, it would have to hold a value of type `!`, and no such value exists.

Types like this usually show up when a `trait` requires returning a `Result`, but a particular implementation can never fail.

### `Result<i32, !>` Doesn't Automatically Become `Result<i32, ()>`

`!` coerces into any type, but that doesn't mean `Result<i32, !>` can be converted into `Result<i32, ()>`:

```rust,compile_fail
fn always_ok() -> Result<i32, !> {
    Ok(42)
}

fn main() {
    let result: Result<i32, ()> = always_ok(); // Compile error!
}
```

The coercion we saw earlier applies to expressions whose type is `!` itself: they never produce a value, so they can sit anywhere without contradiction. `Result<i32, !>` is different — `always_ok()` really does produce a value, `Ok(42)`; it's just that its type mentions `!`. `Result<i32, !>` and `Result<i32, ()>` are two different types, and there's no automatic conversion between them.

When you need a `Result<i32, ()>`, first take the value out with `let Ok(value)`, then wrap it back up yourself as `Ok(value)`.

## Example Code

```rust,editable
trait Source {
    type Error;
    fn read(&self) -> Result<String, Self::Error>;
}

// the user might not have typed anything, so reading can fail
struct Input {
    text: String,
}

impl Source for Input {
    type Error = String;

    fn read(&self) -> Result<String, String> {
        if self.text.is_empty() {
            Err(String::from("no input"))
        } else {
            Ok(self.text.clone())
        }
    }
}

// the data is already in memory, so reading can't fail — the error type is !
struct Memory {
    text: String,
}

impl Source for Memory {
    type Error = !;

    fn read(&self) -> Result<String, !> {
        Ok(self.text.clone())
    }
}

fn exit_with_error(msg: &str) -> ! {
    println!("error: {}", msg);
    std::process::exit(1);
}

fn read_or_exit(input: &Input) -> String {
    match input.read() {
        Ok(text) => text,
        Err(e) => exit_with_error(&e), // ! treated as String
    }
}

fn print_result(result: Result<String, String>) {
    match result {
        Ok(text) => println!("read: {}", text),
        Err(e) => println!("read failed: {}", e),
    }
}

fn main() {
    let input = Input { text: String::from("hello") };
    println!("input: {}", read_or_exit(&input));

    let memory = Memory { text: String::from("hi") };

    // the error type is !, so it can't be Err — take the value out with let
    let Ok(saved) = memory.read();

    print_result(input.read());

    // compile error: Result<String, !> is not Result<String, String>
    // print_result(memory.read());
    print_result(Ok(saved)); // after taking the value out, wrap it in Ok again

    // let empty = Input { text: String::new() };
    // read_or_exit(&empty); // this would call exit_with_error and end the program
}
```

## Recap

- `!` is the never type — it never produces a value.
- A `-> !` function never returns.
- `panic!`, `process::exit`, `return`, `break`, and `continue` all have type `!`.
- `!` coerces into any type — that's how a `match` can have one arm return a value and another panic.
- `!` can be written anywhere a type is expected, such as a variable's type or `Result<i32, !>`.
- `Result<i32, !>` can never be `Err`, so you can take the value out directly with `let Ok(value) = ...`.
- `Result<i32, !>` doesn't automatically convert into `Result<i32, ()>`.

Congratulations on finishing the advanced language features chapter! 🎉 This chapter covered Rust's advanced language features — from `dyn Trait`, compile-time computation, type conversion, attributes, and the macro system, to `unsafe`, `static`, FFI, `union`, and the never type. Most of these won't come up every day, but knowing they exist means you can reach for them when the need arises. In the next chapter we'll look at more practical tools in the standard library.
