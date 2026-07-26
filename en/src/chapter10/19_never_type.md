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

## Example Code

```rust,editable
fn exit_with_error(msg: &str) -> ! {
    println!("error: {}", msg);
    std::process::exit(1);
}

fn parse_or_exit(input: &str) -> i32 {
    match input.parse::<i32>() {
        Ok(n) => n,
        Err(_) => exit_with_error("please enter a valid number"), // ! treated as i32
    }
}

fn main() {
    let value = parse_or_exit("42");
    println!("parsed successfully: {}", value);

    // let bad = parse_or_exit("abc"); // this would call exit_with_error and end the program
}
```

## Recap

- `!` is the never type — it never produces a value.
- A `-> !` function never returns.
- `panic!`, `process::exit`, `return`, `break`, and `continue` all have type `!`.
- `!` coerces into any type — that's how a `match` can have one arm return a value and another panic.

Congratulations on finishing the advanced language features chapter! 🎉 This chapter covered Rust's advanced language features — from `dyn Trait`, compile-time computation, type conversion, attributes, and the macro system, to `unsafe`, `static`, FFI, `union`, and the never type. Most of these won't come up every day, but knowing they exist means you can reach for them when the need arises. In the next chapter we'll look at more practical tools in the standard library.
