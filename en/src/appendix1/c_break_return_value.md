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

The reason: `while` and `for` might **never execute even once**. If the loop body never ran, the value `break` would carry out simply doesn't exist — the compiler can't guarantee a return value.

`loop` differs — it's an unconditional loop that **always enters its body**, so the compiler knows a `break` must eventually be reached (otherwise it's an infinite loop). That's why only `loop` can serve as a value-returning expression.

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
- Only `loop` can do this — not `while` or `for`, which might never run at all.
- The common use: search inside a loop and carry the result out with `break`.
