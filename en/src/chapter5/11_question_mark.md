# The `?` Operator

## Goal of This Episode

Learn to streamline error propagation with the `?` operator, avoiding `match` after `match`.

## Concept

Last episode's `Result` was handled with `match` for success and failure. But what if one function has several fallible operations?

```rust,noplayground
fn do_stuff() -> Result<i32, String> {
    let a = match "42".parse::<i32>() {
        Ok(n) => n,
        Err(e) => return Err(format!("{:?}", e)),
    };
    let b = match "10".parse::<i32>() {
        Ok(n) => n,
        Err(e) => return Err(format!("{:?}", e)),
    };
    Ok(a + b)
}
#
# fn main() {}
```

A `match` for every `parse` — far too wordy. The `?` operator solves exactly this.

### The Essence of `?`

Placed after a `Result`, `?` does the following:

- If it's `Ok(v)`, extract `v` and keep going.
- If it's `Err(e)`, return the `Err`, leaving the function early.

So `?` is shorthand for `match` + early `return`.

### Note: Error Types Must Line Up

When using `Result`, the type inside the `Err` must match the function's declared `Err` type, or be related to it in a certain way (we'll cover exactly which way later). Without that relationship, `?` can't be used directly — you must first convert the error to the right type.

For instance, `.parse()`'s error type is `std::num::ParseIntError`, but your function returns `Result<_, String>`. You can convert it yourself with `match` and a manual `return`:

```rust,noplayground
# fn stringify_err() -> Result<i32, String> {
#     let input = "1";
    let n = match input.parse::<i32>() {
        Ok(v) => Ok(v),
        Err(e) => return Err(format!("{:?}", e)),
    };
#     n
# }
#
# fn main() {}
```

Or wrap a helper function that converts the error first; once that helper returns, `?` works directly — the example code below does exactly that.

Later we'll cover more convenient ways to handle this situation, without hand-converting error types every time.

### `?` Works on `Option` Too

`?` isn't just for `Result` — it works on `Option` as well: on `None`, it simply `return None`s.

### `main` Can Return a `Result` Too

If the `main` function returns `Result<(), String>`, you can use `?` inside `main`.

## Example Code

```rust,editable
// A helper function that converts the error type by hand
fn parse_i32(input: &str) -> Result<i32, String> {
    match input.parse::<i32>() {
        Ok(n) => Ok(n),
        Err(e) => Err(format!("Failed to parse '{}': {:?}", input, e)),
    }
}

// Streamlining error propagation with ?
fn add_two_strings(a: &str, b: &str) -> Result<i32, String> {
    let x = parse_i32(a)?; // Extract on Ok; return early on Err
    let y = parse_i32(b)?;
    Ok(x + y)
}

// ? on an Option: is the first element positive?
fn first_is_positive(numbers: &[i32]) -> Option<bool> {
    // If the slice is empty, .first() returns None, and ? returns None immediately
    let first = numbers.first()?;
    Some(*first > 0)
}

// main can return a Result too, enabling ?
fn main() -> Result<(), String> {
    let result = add_two_strings("42", "10")?;
    println!("42 + 10 = {}", result);

    // The error case
    let bad = add_two_strings("42", "abc");
    match bad {
        Ok(n) => println!("Result: {}", n),
        Err(e) => println!("Error: {}", e),
    }

    let nums = [3, 7, 2];
    match first_is_positive(&nums) {
        Some(true) => println!("The first element is positive"),
        Some(false) => println!("The first element isn't positive"),
        None => println!("An empty slice"),
    }

    let empty: &[i32] = &[];
    match first_is_positive(empty) {
        Some(b) => println!("Result: {}", b),
        None => println!("Empty slice; no first element"),
    }

    Ok(())
}
```

## Recap

- `?` is shorthand for `match` + early `return`.
- `?` on a `Result`: extract on `Ok`, return early on `Err`.
- `?` on an `Option`: extract on `Some`, return early on `None`.
- When using `?`, the error type must match the function's return type or be related to it; otherwise you convert it yourself.
- `fn main() -> Result<(), String>` lets `main` use `?` too.
