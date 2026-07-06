# `Result<T, E>`

## Goal of This Episode

Learn to handle fallible operations with `Result<T, E>`, and understand its symmetry with `Option`.

## Concept

The last two episodes covered `Option<T>` — "maybe there's a value, maybe not." But sometimes "no value" isn't enough — you also need to know **why** there isn't one.

Take parsing a number: on failure, you want to know whether it was "bad format" or "number too large." That's what `Result<T, E>` is for.

### The Definition of `Result`

```rust,noplayground
enum Result<T, E> {
    Ok(T),
    Err(E),
}
#
# fn main() {}
```

- `Ok(T)` means success, wrapping the successful value.
- `Err(E)` means failure, wrapping the error information.

Like `Option`, `Result`, `Ok`, and `Err` are imported into every file by default.

### The Symmetry between `Option` and `Result`

| `Option` | `Result` |
|----------|----------|
| `Some(T)` | `Ok(T)` |
| `None` | `Err(E)` |

`Option` only knows "there is or there isn't"; `Result` also knows "why there isn't."

### Revisiting Chapter 1's Black Box

Remember Chapter 1's `.expect("Failed to read input")` and `.parse::<i32>().expect("Please enter a number")`?

What `.parse()` returns is a `Result`. And `expect` behaves exactly like `Option`'s `expect` — on success, extract the `Ok` value; on failure, panic and print your message.

Now we can finally understand Chapter 1's "black box" code in full.

### Common Methods

Like `Option`, `Result` has:

- `unwrap()`: extract the value on success; panic on failure.
- `expect("message")`: like `unwrap`, with a custom panic message.
- `unwrap_or(default)`: use the default on failure.

## Example Code

```rust,editable
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("The divisor can't be zero"))
    } else {
        Ok(a / b)
    }
}

fn main() {
    // Handling a Result with match
    let result = divide(10, 3);
    match result {
        Ok(value) => println!("10 / 3 = {}", value),
        Err(msg) => println!("Error: {}", msg),
    }

    // The division-by-zero case
    let bad = divide(10, 0);
    match bad {
        Ok(value) => println!("Result: {}", value),
        Err(msg) => println!("Error: {}", msg),
    }

    // unwrap_or: a default on failure
    let safe = divide(10, 0).unwrap_or(0);
    println!("The safe result: {}", safe);

    // Back to Chapter 1: parse returns a Result
    let input = "42";
    let num: Result<i32, _> = input.parse();
    match num {
        Ok(n) => println!("Parsed successfully: {}", n),
        Err(e) => println!("Parse failed: {:?}", e),
    }

    // expect: for when you're sure it won't fail
    let num2 = "100".parse::<i32>().expect("This shouldn't fail");
    println!("{}", num2);
}
```

## Recap

- `Result<T, E>` expresses "success (`Ok`) or failure (`Err`)" — `Option` plus error information.
- `Ok(T)` corresponds to success; `Err(E)` to failure.
- Like `Option`, `Result`, `Ok`, and `Err` come pre-imported in every file.
- `unwrap()`, `expect()`, and `unwrap_or()` work exactly as they do with `Option`.
- Chapter 1's `.parse().expect(...)` was using `Result` all along — now we understand.
