# `async` Is an effect

## Goal of This Episode

Look at `async` from another angle: set `.await` beside the `?` you already know, and discover they're the same kind of thing.

## Main Text

### Two Little Tails

Think back to Chapter 5's `?`. When an expression's type is `Option` / `Result`, sticking a `?` on the end pulls out the "success value" for you to use, while "what if it failed" gets handled automatically by the compiler:

```rust,ignore
let x = a.parse::<i32>()?; // ? pulls the value out of the Result
```

`.await` does something very similar. When an expression's type is `Future`, sticking a `.await` on the end pulls out the "value that will be computed later" for you to use, while "what if it's not ready yet" gets handled automatically by the runtime:

```rust,ignore
let x = some_async_thing().await; // .await pulls the value out of the Future
```

See it? `?` and `.await` are both **little tails stuck onto expressions** that pull "a value wrapped in some special world" into your hands.

### Two Worlds, Each with Its Own Rules

Think of it this way: some values don't live in the "ordinary world" but in a wrapped-up special world.

- **The `Option` / `Result` world**: the value might not be computable. This world's rule is "may fail."
- **The `Future` world**: the value might not be ready yet; you have to wait. This world's rule is "may not be ready."

When you pull values out with `?` or `.await`, your code reads just like ordinary code — line after line, using values in computations. But behind the scenes the compiler is doing something for you: **chaining** these "wrapped values" together according to each world's rules. Every `?` or `.await` is a seam where the rules get applied: the `?` seam auto-returns early on error; the `.await` seam auto-pauses when things aren't ready and yields the `Thread`.

### Why `.await` Needs Its Own `async` Syntax

`?`'s rule is fairly simple — the compiler only inserts an "on error, `return` early" check. But `.await`'s rule is far more involved: when "not ready," it must **pause** the whole function, remember where it got to, hand the `Thread` to someone else, and resume from that spot once ready.

To pull that off, the compiler must **heavily rewrite** your `async` function into something called a "state machine" (explained later in this chapter — just remember the term for now). It's precisely because the rewrite is so extensive that Rust needs the dedicated `async` keyword — it effectively tells the compiler: "please rewrite this part into a pausable, resumable form."

### `async` Is "Contagious"

`?`'s restriction is that you can only use it inside "functions that return `Option` / `Result`." Likewise, `.await` can only be used in an `async` context. `.await`ing directly in an ordinary function fails to compile:

```rust,compile_fail
# extern crate tokio;
#
async fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn normal_function() {
    let sum = add(3, 4).await; // compile error: can't .await in a regular function
}
#
# fn main() {}
```

In other words, you can only pull values out "from inside the world." To use `.await`, the function you're in must itself be `async` — and so `async` "infects" its way up the call chain. This is the same story as `?` requiring "the caller must itself be able to handle errors."

### Effects Must Eventually "Land"

Whichever world it is, at some point you must return to the ordinary world — unwrap the packaging and get a concrete value. First look at how error handling "lands"; it has two routes.

Route one: let `main` itself return a `Result`, handing things to the compiler at the program's boundary.

```rust,editable
fn parse_and_add(a: &str, b: &str) -> Result<i32, std::num::ParseIntError> {
    let x = a.parse::<i32>()?;
    let y = b.parse::<i32>()?;
    Ok(x + y)
}

fn main() -> Result<(), std::num::ParseIntError> {
    let sum = parse_and_add("3", "4")?;
    println!("the result is {}", sum);
    Ok(())
}
```

Route two: take the `Result` apart yourself with `match`, handling it in ordinary code.

```rust,editable
fn parse_and_add(a: &str, b: &str) -> Result<i32, std::num::ParseIntError> {
    let x = a.parse::<i32>()?;
    let y = b.parse::<i32>()?;
    Ok(x + y)
}

fn main() {
    match parse_and_add("3", "4") {
        Ok(sum) => println!("the result is {}", sum),
        Err(e) => println!("something went wrong: {}", e),
    }
}
```

### `async` Lands the Same Way, in Perfect Correspondence

The `Future` world lands by the same two routes, and they line up one to one:

**Route one: `#[tokio::main]`**, corresponding to "a `main` that returns `Result`." You just make `main` `async`, letting the Tokio framework handle things at the program's boundary:

```rust,editable
extern crate tokio;

async fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[tokio::main]
async fn main() {
    let sum = add(3, 4).await;
    println!("the result is {}", sum);
}
```

**Route two: `block_on`**, corresponding to "`match` it yourself." Inside an ordinary `main`, you ask the runtime on the spot to run a `Future` to completion, settling it into an ordinary value:

```rust,editable
extern crate tokio;

async fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let runtime = tokio::runtime::Runtime::new().expect("failed to create the runtime");
    let sum = runtime.block_on(add(3, 4)); // run the Future into a plain value now
    println!("the result is {}", sum);
}
```

Pair them up: a `Result`-returning `main` ↔ `#[tokio::main]` (let the framework settle things at the boundary), `match` ↔ `block_on` (settle it yourself on the spot in synchronous code). Keep this correspondence in mind, and `async` stops being something brand new — it's "the `?` you already know, with a more complicated set of rules."

## Recap

- `?` and `.await` are both little tails on expressions that pull out "values from a special world."
- The `Result` world's rule is "may fail"; the `Future` world's rule is "may not be ready yet"; the compiler chains the wrapped values together by each world's rules.
- `.await`'s rule is complex — it rewrites the function into a **state machine** — hence the dedicated `async` syntax.
- Like `?`, `async`'s `.await` is "contagious": to `.await`, the enclosing function must itself be `async`.
- Two landing routes in perfect correspondence: `Result`-returning `main` ↔ `#[tokio::main]`, `match` ↔ `block_on`.
