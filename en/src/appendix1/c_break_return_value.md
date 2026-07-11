# `break` with a Value

## Goal of This Episode

Learn to return a value from a `loop` with `break`, using the loop as an expression.

> This episode supplements **Chapter 1**.

## Concept

Remember how "almost everything in Rust is an expression"? The `loop` is no exception — `break` can carry a value out, turning the whole `loop` into an expression.

### Basic Syntax

```rust,noplayground
# fn main() {
    let result = loop {
        break 42;
    };
# }
```

Here `loop { break 42; }` has type `i32`, since `break` carried out `42`.

### Why Can Only `loop` Do This?

You might ask: why not `while` and `for`?

The reason: `while` and `for` can finish normally when their condition becomes false or their iterator runs out, without ever reaching a `break`. In that case, the loop produces `()` rather than a value carried by `break`.

`loop` differs because it has no condition that ends it normally. If a `loop` finishes, it must be through `break`; if no `break` is reached, it keeps running and produces no result. That's why the value carried by `break` can become the value of the entire `loop`.

### Practical Scenarios

The most common use is "searching for something inside a loop, carrying it out when found":

```rust,ignore
# fn main() {
    let found = loop {
        // Do some searching...
        if condition {
            break some_value;
        }
    };
# }
```

Much cleaner than declaring a variable first, assigning inside the loop, then `break`ing.

## Example Code

```rust,editable
fn main() {
    // Basic usage: a loop returning a value
    let lucky_number = loop {
        break 7;
    };
    println!("Lucky number: {}", lucky_number);

    // A practical example: the first square number exceeding 100
    let mut n = 1;
    let result = loop {
        let square = n * n;
        if square > 100 {
            break square;
        }
        n += 1;
    };
    println!("The first square exceeding 100: {}", result);
    println!("It's the square of {}", n);
}
```

## Recap

- `let x = loop { break value; };` makes the `loop` an expression, returning the value `break` carries.
- Only `loop` can do this — `while` and `for` can finish normally without reaching a `break`.
- The common use: search inside a loop and carry the result out with `break`.
