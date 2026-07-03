# Function Pointers

## Goal of This Episode

Meet the function pointer type, and learn to pass and store function names as values.

## Concept

In Rust, functions can be more than called — they can be passed around like values, stored in variables, and put into `Vec`s. To do that, we need to meet the **function pointer** type.

### How Function Pointers Are Written

Suppose you have a function:

```rust,noplayground
fn add_one(x: i32) -> i32 {
    x + 1
}
#
# fn main() {}
```

This function's pointer type is `fn(i32) -> i32`. Note the lowercase `fn` — it denotes the function pointer type, not the keyword for defining functions.

### Storing a Function in a Variable

You can assign a function's name directly to a variable:

```rust,noplayground
# fn add_one(x: i32) -> i32 {
#     x + 1
# }
#
# fn main() {
    let f: fn(i32) -> i32 = add_one;
# }
```

Afterward, calling `f(10)` works the same as calling `add_one(10)` directly.

### Passing Functions as Arguments

One of the most common uses of function pointers is "passing one function to another":

```rust,noplayground
fn apply(f: fn(i32) -> i32, value: i32) -> i32 {
    f(value)
}
#
# fn main() {}
```

Now `apply` accepts any function with the signature `fn(i32) -> i32` — very flexible.

### Multiple Parameters and Different Return Types

A function pointer's type is determined by its parameters and return value:

- No parameters, no return value: `fn()`.
- Two parameters: `fn(i32, i32) -> i32`.
- Returning a `String`: `fn(&str) -> String`.

### Function Pointers vs Next Episode's Closures

The function pointer `fn(...) -> ...` is a concrete type with a fixed size. But it has one limitation — the function body can't use local variables from the call site. Next episode introduces closures, which can.

## Example Code

```rust,editable
fn add_one(x: i32) -> i32 {
    x + 1
}

fn double(x: i32) -> i32 {
    x * 2
}

fn apply(f: fn(i32) -> i32, value: i32) -> i32 {
    f(value)
}

fn pick_function(use_double: bool) -> fn(i32) -> i32 {
    if use_double {
        double
    } else {
        add_one
    }
}

fn main() {
    // Storing a function in a variable
    let f: fn(i32) -> i32 = add_one;
    println!("f(5) = {}", f(5));

    // Passing functions as arguments
    println!("apply(add_one, 10) = {}", apply(add_one, 10));
    println!("apply(double, 10) = {}", apply(double, 10));

    // Functions can be return values too
    let chosen = pick_function(true);
    println!("chosen(7) = {}", chosen(7));

    let chosen2 = pick_function(false);
    println!("chosen2(7) = {}", chosen2(7));

    // Putting functions in a Vec
    let operations: Vec<fn(i32) -> i32> = vec![add_one, double];
    for op in &operations {
        println!("op(3) = {}", op(3));
    }
}
```

## Recap

- The function pointer type is written `fn(param_types) -> return_type` — note the lowercase `fn`.
- A function's name works directly as a value: assign it to variables, pass it to other functions, store it in containers like `Vec`.
- Function pointers' limitation: no access to the call site's local variables. Next episode's closures can do that.
