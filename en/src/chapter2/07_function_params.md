# Function Parameters

## Goal of This Episode

Add parameters to a function so it can receive data passed in from outside.

## Main Text

Last episode's `greet` function could only ever print the same thing — a bit boring. If we want functions to be more flexible — say, "give me two numbers and I'll add them for you" — we need **parameters**.

### Adding Parameters

```rust,editable
fn add(a: i32, b: i32) {
    println!("{} + {} = {}", a, b, a + b);
}

fn main() {
    add(3, 4);
    add(10, 20);
}
```

Syntax breakdown:

- `a: i32` → the first parameter is named `a`, with type `i32`.
- `b: i32` → the second parameter is named `b`, also of type `i32`.
- Parameters are separated by commas.

When calling, `add(3, 4)` passes 3 to `a` and 4 to `b`.

### Parameters Must Have Type Annotations

In Rust, function parameters **must be annotated with types** — no slacking:

```rust,compile_fail
fn add_v1(a, b) {           // ❌ Compile error! No type annotations
    println!("{}", a + b);
}

fn add_v2(a: i32, b: i32) { // ✅ Required
    println!("{}", a + b);
}
#
# fn main() {}
```

"But doesn't `let x = 5;` get to skip the annotation?"

True — `let` lets the compiler infer. But function parameters don't, because a function is your "public interface." Rust wants interfaces to be crystal clear, not vague and fuzzy.

### Multiple Parameters, Different Types

Parameters can have different types:

```rust,editable
fn describe(x: i32, is_positive: bool) {
    println!("Is {} positive? {}", x, is_positive);
}

fn main() {
    describe(5, true);
    describe(-3, false);
}
```

### One Parameter Works Too

```rust,editable
fn double(x: i32) {
    println!("Twice {} is {}", x, x * 2);
}

fn main() {
    double(5);
    double(100);
}
```

## Recap

- Function parameters go inside the parentheses: `fn name(param: type)`.
- Multiple parameters are separated by commas.
- **Parameters must have type annotations** — a hard rule in Rust.
- When calling, just pass in the corresponding values.
