# Function Return Values

## Goal of This Episode

Make a function return a value, and learn Rust's distinctive "no semicolon means return value" style.

## Main Text

Last episode's functions just printed their results. But often what we want is: "Once you've computed it, **hand the answer back** — I'll decide what to do with it."

### Basic Syntax

```rust,editable
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let result = add(3, 4);
    println!("3 + 4 = {}", result);
}
```

The key points:

1. `-> i32` after the parameters tells Rust "this function returns an `i32`."
2. The function's last line, `a + b`, has **no semicolon** → that's the return value.

### No Semicolon = Return Value

This is one of Rust's most distinctive designs. If the last line of a function has **no semicolon**, its value automatically becomes the return value:

```rust,noplayground
fn double(x: i32) -> i32 {
    x * 2 // ✅ No semicolon — this is the return value
}
#
# fn main() {}
```

### What If You Add a Semicolon?

If you accidentally add one:

```rust,compile_fail
fn double(x: i32) -> i32 {
    x * 2; // ❌ Semicolon added
}
#
# fn main() {}
```

The compiler reports an error. Why? With the semicolon, the result of `x * 2` gets thrown away, and the function ends without leaving any meaningful value. In that case, what's actually returned is `()` (the unit type — remember Episode 4?). But you promised to return an `i32`; the types don't match, so the compiler complains.

### Functions with No Declared Return Value

Look back at the `greet` function from Episode 6 of this chapter — it has no `->` return type:

```rust,noplayground
fn greet() {
    println!("Hello!");
}
#
# fn main() {}
```

In Rust, every function has a return value. Omitting `->` is the same as writing `-> ()`:

```rust,noplayground
fn greet() -> () {
    println!("Hello!");
}
#
# fn main() {}
```

It's just that `-> ()` is usually left out. `println!("Hello!");` ends with a semicolon, its result is discarded, and the function returns `()` — exactly matching the declaration.

### Catching the Return Value

```rust,editable
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let result = add(3, 4);
    println!("Result: {}", result);

    // You can also use it directly inside an expression
    println!("Plus 10 more: {}", add(3, 4) + 10);
}
```

### Returning Multiple Values with a Tuple

A function can only return "one" value — so what if you want to return several? Just pack them in a tuple:

```rust,editable
fn swap(a: i32, b: i32) -> (i32, i32) {
    (b, a)
}

fn main() {
    let result = swap(1, 2);
    println!("First: {}, second: {}", result.0, result.1);
}
```

`-> (i32, i32)` means returning a tuple containing two `i32`s. After the call, use `.0` and `.1` to pull the values out.

Here's a more practical example:

```rust,editable
fn min_max(a: i32, b: i32) -> (i32, i32) {
    if a < b {
        (a, b)
    } else {
        (b, a)
    }
}

fn main() {
    let result = min_max(7, 3);
    println!("Smallest: {}, largest: {}", result.0, result.1);
}
```

## Recap

- Declare a function's return type with `-> type`.
- The last line **without a semicolon** is the return value (the idiomatic Rust style).
- With a semicolon, it becomes an ordinary statement, and `()` gets returned instead.
- A function without a declared return type actually returns `()`.
- Want to return multiple values? Wrap them in a tuple: `-> (i32, i32)`, retrieved with `.0` and `.1`.
