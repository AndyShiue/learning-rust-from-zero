# Common `Option` Methods

## Goal of This Episode

Learn `Option`'s common methods — `unwrap`, `expect`, `unwrap_or`, `flatten` — plus extracting values with `if let`.

## Concept

Last episode we handled `Option` with `match`, the safest way. But writing `match` every time can be long-winded. Rust offers some convenient methods.

### `unwrap`: Brute-force Extraction

```rust,noplayground
# fn main() {
    let x: Option<i32> = Some(42);
    let value = x.unwrap(); // 42
# }
```

If it's `Some`, you get the value inside directly. But if it's `None`, the program panics (crashes)! So use `unwrap` with care — only when you're **certain** it can't be `None`.

### `expect`: `unwrap` with a Message

```rust,should_panic
# #![allow(unused_variables)]
#
# fn main() {
    let x: Option<i32> = None;
    let value = x.expect("This shouldn't be None"); // Panics, printing your message
# }
```

Same as `unwrap`, but the panic prints your custom message — handy for debugging.

### `unwrap_or`: Providing a Default

```rust,noplayground
# fn main() {
    let x: Option<i32> = None;
    let value = x.unwrap_or(0); // 0
# }
```

If it's `Some`, extract the value; if `None`, use the default you supplied. No panics — very safe.

### `flatten`: Squashing Nested `Option`s

Sometimes you run into the nested structure `Option<Option<T>>`:

```rust,noplayground
# fn main() {
    let nested: Option<Option<i32>> = Some(Some(42));
    let flat: Option<i32> = nested.flatten(); // Some(42)
# }
```

`flatten` squashes two layers of `Option` into one. If either the outer or inner layer is `None`, the result is `None`.

## Example Code

```rust,editable
fn find_even(numbers: &[i32]) -> Option<i32> {
    for n in numbers {
        if *n % 2 == 0 {
            return Some(*n);
        }
    }
    None
}

fn main() {
    let nums = [1, 3, 5, 7];
    let has_even = [2, 4, 6];

    // unwrap_or: safely provide a default
    let result = find_even(&nums).unwrap_or(0);
    println!("Even number (0 if not found): {}", result);

    // expect: for when you're sure there's a value
    let result2 = find_even(&has_even).expect("There should be an even number");
    println!("Found an even number: {}", result2);

    // if let: the syntax from Chapter 3
    if let Some(n) = find_even(&has_even) {
        println!("Extracted with if let: {}", n);
    }

    // flatten: squashing a nested Option
    let nested: Option<Option<i32>> = Some(Some(42));
    let flat = nested.flatten();
    println!("{:?}", flat);

    let nested_none: Option<Option<i32>> = Some(None);
    let flat_none = nested_none.flatten();
    println!("{:?}", flat_none);

    let outer_none: Option<Option<i32>> = None;
    let flat_outer = outer_none.flatten();
    println!("{:?}", flat_outer);
}
```

## Recap

- `unwrap()`: extracts the `Some` value; panics on `None` — handle with care.
- `expect("message")`: like `unwrap`, but the panic prints your custom message.
- `unwrap_or(default)`: returns the default on `None`; never panics.
- `flatten()`: squashes an `Option<Option<T>>` into an `Option<T>`.
- Pairing with `if let Some(x) = ...` (from Chapter 3) is convenient too.
