# Closures in Action

## Goal of This Episode

Learn basic closure syntax, see how closures capture outside variables, and look at real standard-library cases that use closures.

## Concept

### Closure Syntax

Last episode's function pointers are handy, but a function can't reach the local variables inside another function — anything it needs has to be passed in as a parameter. Closures are different: wherever one is written, it can use the local variables right there — which is exactly why they exist.

A closure's basic syntax wraps the parameters in `|`:

```rust,ignore
# fn main() {
    let add_one = |x| x + 1;
# }
```

You can add type annotations, explicit like a function:

```rust,noplayground
# fn main() {
    let add_one = |x: i32| -> i32 { x + 1 };
# }
```

Calling a closure works like calling an ordinary function — just `add_one(5)`, no special syntax needed.

### When Are Braces Required?

The rule is simple:

- With **a single expression**, the braces can be dropped: `|x| x + 1`.
- With **multiple lines** or **statements like `let`**, wrap them in braces:

```rust,noplayground
# fn main() {
    let process = |x: i32| {
        let doubled = x * 2;
        println!("Computing: {}", doubled);
        doubled + 1
    };
# }
```

As with functions, the last line inside the braces without a semicolon is the return value.

Also, with a return type annotation (`-> i32`), the braces become mandatory:

```rust,noplayground
# fn main() {
    let add_one = |x: i32| -> i32 { x + 1 }; // With -> the {} are required
    let add_one = |x: i32| x + 1;            // Without -> the {} can be dropped
# }
```

### Closures Capture Outside Variables

This is the biggest difference from function pointers:

```rust,editable
fn main() {
    let offset = 10;
    let add_offset = |x| x + offset; // Captures offset
    println!("{}", add_offset(5));   // 15
}
```

The closure `add_offset` "remembers" the outer `offset`, using it on every call. An ordinary function can't do that.

### Not All Closures Are Alike

Depending on **how** a closure uses its captured variables, Rust sorts closures into different kinds — some callable only once, others many times. This episode shows two examples to get a feel; the next few episodes dig deeper.

### `Result`'s `map` — a `FnOnce` Example

Many standard-library methods take closures. Remember `Result<T, E>` from Chapter 5? It has a `map` method that transforms the value inside an `Ok`. `map` only needs to call the closure once, so it accepts `FnOnce` — "callable at least once" suffices.

That means you can hand it a closure that **consumes a captured variable**:

```rust,editable
fn main() {
    let prefix = String::from("The result is: ");
    let result: Result<i32, String> = Ok(42);
    let message = result.map(|x| {
        // prefix gets moved in; this closure can only be called once
        let mut s = prefix; // Move!
        s.push_str(&x.to_string());
        s
    });
    println!("{:?}", message); // Ok("The result is: 42")
}
```

This closure moves `prefix` in; after one call, `prefix` is gone. That's fine — `map` was only ever going to call the received function once.

### `Vec`'s `retain` — a `FnMut` Example

`Vec<T>`'s `retain` method keeps elements meeting a condition and removes the rest. It takes a closure receiving `&T` (a reference to each element) and returning `bool` (`true` keeps, `false` removes). Since `retain` must call it once per element, it demands `FnMut` — "callable repeatedly."

You can pass a closure that **modifies a captured variable**:

```rust,editable
fn main() {
    let mut numbers = vec![1, 2, 3, 4, 5, 6];
    let mut removed_count = 0;
    numbers.retain(|x| {
        if x % 2 == 0 {
            true // Keep the evens
        } else {
            removed_count += 1; // Modifying an outer variable
            false
        }
    });
    println!("{:?}, removed {}", numbers, removed_count);
    // [2, 4, 6], removed 3
}
```

This closure modifies `removed_count` each time it's called — it's `FnMut`. Note it moves nothing (it only modifies the outer variable through `&mut`), so it can be called many times.

### What If a `FnOnce` Goes to `retain`?

Could the variable-moving closure we gave `Result`'s `map` be passed to `retain`?

```rust,compile_fail
# fn main() {
    let mut items = vec![1, 2, 3];
    let header = String::from("Removing: ");
    items.retain(|x| {
        if *x <= 1 {
            let mut log = header; // Moves header
            log.push_str(&x.to_string());
            log.push(' ');
        }
        *x > 1
    }); // Compile error!
# }
```

This closure moves `header` away the first time it removes an element; by the second removal, `header` no longer exists. It's callable only once (`FnOnce`), but `retain` needs repeated calls (`FnMut`). So the compiler objects.

### Capture-free Closures → Convertible to Function Pointers

If a closure captures no outer variables, it's not much different from an ordinary function. Rust allows it to convert automatically into a function pointer `fn`:

```rust,noplayground
# fn main() {
    let add_one: fn(i32) -> i32 = |x| x + 1; // No captures; convertible to fn
# }
```

But once it captures an outer variable, that conversion is off the table.

## Example Code

```rust,editable
fn apply_fn_pointer(f: fn(i32) -> i32, value: i32) -> i32 {
    f(value)
}

fn main() {
    // Basic closure syntax
    let square = |x: i32| -> i32 { x * x };
    println!("square(4) = {}", square(4));

    // Capturing an outer variable
    let base = 100;
    let add_base = |x| x + base;
    println!("add_base(7) = {}", add_base(7));

    // Result's map (FnOnce)
    let result: Result<i32, String> = Ok(21);
    let doubled = result.map(|x| x * 2);
    println!("doubled = {:?}", doubled);

    let err_result: Result<i32, String> = Err(String::from("oops"));
    let still_err = err_result.map(|x| x * 2);
    println!("still_err = {:?}", still_err);

    // Vec's retain (FnMut)
    let mut scores = vec![55, 72, 88, 43, 91, 60];
    scores.retain(|s| *s >= 60);
    println!("Passing scores: {:?}", scores);

    // A capture-free closure converts to a function pointer
    let triple: fn(i32) -> i32 = |x| x * 3;
    println!("apply_fn_pointer(triple, 5) = {}", apply_fn_pointer(triple, 5));

    // A capturing closure can't convert to a function pointer
    // let offset = 10;
    // let bad: fn(i32) -> i32 = |x| x + offset; // Compile error!
}
```

## Recap

- Closures use the `|params| expression` syntax; type annotations can be omitted for Rust to infer.
- A closure's defining feature is **capturing outer variables** — something function pointers can't do.
- `Result`'s `map` accepts `FnOnce` closures — one call needed.
- `Vec`'s `retain` accepts `FnMut` closures — repeated calls needed.
- A once-only closure (`FnOnce`) can't go to a method that needs repeated calls.
- Capture-free closures convert automatically into function pointers `fn`.
