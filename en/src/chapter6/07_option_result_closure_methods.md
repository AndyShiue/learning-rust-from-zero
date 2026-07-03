# Closure Methods on `Option` / `Result`

## Goal of This Episode

Meet the common closure-taking methods on `Option` and `Result`, and feel how closures make code cleaner and more fluent.

## Concept

In Chapter 5 we handled `Option` and `Result` with `match`, spelling out two arms every time. With closures learned, many operations shrink to one line.

### `Option`'s Closure Methods

The following methods are defined on `Option<T>`; the `T` in the signatures is `Option<T>`'s type parameter.

**`map` — Transforming the Value inside `Some`**

```rust,noplayground
# fn main() {
    // A method on Option<T>:
    // fn map<U>(self, f: impl FnOnce(T) -> U) -> Option<U>
    let x: Option<i32> = Some(5);
    let y = x.map(|v| v * 2); // Some(10)
# }
```

On `None`, `map` does nothing and returns `None` as-is. No `match` needed.

**`and_then` — Chaining (Possibly Failing) Operations**

`map`'s closure returns a plain value — but what if your transformation can itself return `None`? Use `and_then`:

```rust,noplayground
# fn main() {
    // A method on Option<T>:
    // fn and_then<U>(self, f: impl FnOnce(T) -> Option<U>) -> Option<U>
    let x: Option<i32> = Some(5);
    let y = x.and_then(|v| if v > 3 { Some(v * 2) } else { None });
# }
```

`and_then`'s closure returns an `Option`, avoiding the nested `Option<Option<T>>` problem. In fact, `and_then` equals `map` followed by `flatten` — `map` would produce `Option<Option<U>>`, and `flatten` squashes it into `Option<U>`. `and_then` does it in one step.

**`unwrap_or_else` — a Closure Computing the Default**

```rust,editable
fn main() {
    // A method on Option<T>:
    // fn unwrap_or_else(self, f: impl FnOnce() -> T) -> T
    let x: Option<i32> = None;
    let y = x.unwrap_or_else(|| {
        println!("No value; computing a default...");
        42
    });
}
```

Unlike `unwrap_or`, `unwrap_or_else` computes its default **lazily** — the closure runs only when it's actually `None`.

**`filter` — Conditional Filtering**

```rust,noplayground
# fn main() {
    // A method on Option<T>:
    // fn filter(self, predicate: impl FnOnce(&T) -> bool) -> Option<T>
    let x: Option<i32> = Some(4);
    let y = x.filter(|v| v % 2 == 0); // Some(4), since 4 is even
    let z = x.filter(|v| v % 2 != 0); // None, since 4 isn't odd
# }
```

### `Result`'s Closure Methods

`Result` has a similar set. The following are defined on `Result<T, E>`, where `T` is the `Ok` type and `E` the `Err` type.

**`map` — Transforming the `Ok` Value**

```rust,noplayground
# fn main() {
    // A method on Result<T, E>:
    // fn map<U>(self, f: impl FnOnce(T) -> U) -> Result<U, E>
    let r: Result<i32, String> = Ok(10);
    let doubled = r.map(|v| v * 2); // Ok(20)
# }
```

**`map_err` — Transforming the `Err` Value**

The mirror of `map` — `map` acts on `Ok` and leaves `Err` alone; `map_err` acts on `Err` and leaves `Ok` alone.

```rust,noplayground
# fn main() {
    // A method on Result<T, E>:
    // fn map_err<F>(self, f: impl FnOnce(E) -> F) -> Result<T, F>
    let r: Result<i32, String> = Err(String::from("not found"));
    let r2 = r.map_err(|e| format!("Error: {}", e));
# }
```

**`and_then` — Chaining**

```rust,noplayground
# fn main() {
    // A method on Result<T, E>:
    // fn and_then<U>(self, f: impl FnOnce(T) -> Result<U, E>) -> Result<U, E>
    let r: Result<i32, String> = Ok(5);
    let r2 = r.and_then(|v| {
        if v > 0 {
            Ok(v * 10)
        } else {
            Err(String::from("Must be positive"))
        }
    });
# }
```

As with `Option`, `and_then` equals `map` then `flatten`.

**`unwrap_or_else` — Computing a Default from the `Err`**

```rust,editable
fn main() {
    // A method on Result<T, E>:
    // fn unwrap_or_else(self, f: impl FnOnce(E) -> T) -> T
    let r: Result<i32, String> = Err(String::from("oops"));
    let value = r.unwrap_or_else(|e| {
        println!("An error occurred: {}; using the default", e);
        0
    });
}
```

### Comparison with `match`

With `match`:
```rust,noplayground
# fn main() {
#     let opt = Some(1);
    let result = match opt {
        Some(v) => Some(v * 2),
        None => None,
    };
# }
```

With the closure method:
```rust,noplayground
# fn main() {
#     let opt = Some(1);
    let result = opt.map(|v| v * 2);
# }
```

One line, and the intent is clearer — "transform the value inside the `Some`."

## Example Code

```rust,editable
fn parse_and_double(input: &str) -> Result<i32, String> {
    input
        .parse::<i32>()
        .map_err(|e| format!("Parse failed: {}", e))
        .and_then(|n| {
            if n >= 0 {
                Ok(n * 2)
            } else {
                Err(String::from("Negative numbers not accepted"))
            }
        })
}

fn find_even(numbers: &[i32]) -> Option<i32> {
    for n in numbers {
        if n % 2 == 0 {
            return Some(*n);
        }
    }
    None
}

fn main() {
    // Option's map
    let maybe_num: Option<i32> = Some(21);
    let doubled = maybe_num.map(|n| n * 2);
    println!("map: {:?}", doubled);

    // Option's and_then
    let result = maybe_num.and_then(|n| {
        if n > 10 { Some(n - 10) } else { None }
    });
    println!("and_then: {:?}", result);

    // Option's filter
    let even = maybe_num.filter(|n| n % 2 == 0);
    println!("filter(even): {:?}", even);

    // Option's unwrap_or_else
    let none_value: Option<i32> = None;
    let default = none_value.unwrap_or_else(|| {
        println!("Computing a default...");
        99
    });
    println!("unwrap_or_else: {}", default);

    // Chained Result operations
    println!("\n--- Chained Result operations ---");
    let good = parse_and_double("21");
    println!("parse_and_double(\"21\") = {:?}", good);

    let bad_parse = parse_and_double("abc");
    println!("parse_and_double(\"abc\") = {:?}", bad_parse);

    let negative = parse_and_double("-5");
    println!("parse_and_double(\"-5\") = {:?}", negative);

    // Result's unwrap_or_else
    let safe_value = parse_and_double("oops").unwrap_or_else(|e| {
        println!("Handling the error: {}", e);
        0
    });
    println!("Safely obtained value: {}", safe_value);

    // Combining Option methods
    println!("\n--- Chained Option operations ---");
    let numbers = vec![1, 3, 5, 8, 11];
    let result = find_even(&numbers)
        .filter(|n| *n > 5)
        .map(|n| n * 10);
    println!("First even number, times 10 only if > 5: {:?}", result);
}
```

## Recap

- `Option`'s and `Result`'s `map` transform the inner value; nothing runs on `None` / `Err`.
- `and_then` is for closures that themselves return `Option` / `Result`, avoiding nesting.
- `unwrap_or_else` computes the default lazily — the closure runs only on `None` / `Err`.
- `Option`'s `filter` keeps the `Some` or turns it into `None` based on a condition.
- `Result`'s `map_err` converts the error type — handy in error-handling chains.
- These methods chain, reading far cleaner than stacked `match`es.
- You may have noticed: the type signature alone tells you what a method does (`Option<T>`'s `map` takes `FnOnce(T) -> U`, returns `Option<U>`). A hallmark of functional programming — the types are the documentation.
