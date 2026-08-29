# Simple Functions

## Goal of This Episode

Define your own function with `fn` and call it from `main`.

## Main Text

Up to now, almost all our code has lived inside `main`. But as programs grow, cramming everything together gets messy. That's when we can "package" a piece of code into a **function** and just call it whenever we need it.

### Defining a Function

```rust,editable
fn greet() {
    println!("Hello! Welcome to the world of Rust!");
}

fn main() {
    greet();
}
```

Breaking down the syntax:

- `fn` → tells Rust "I'm defining a function."
- `greet` → the function's name.
- `()` → the parameter list (empty for now; next episode covers this).
- `{ ... }` → what the function does.

Then writing `greet();` inside `main` calls it.

### Functions Can Be Called Many Times

```rust,editable
fn greet() {
    println!("Hi there!");
}

fn main() {
    greet();
    greet();
    greet();
}
```

That's the beauty of functions — write once, use many times.

### Functions Can Call Each Other

It's not just `main` that can call functions — functions can call one another. `main` is merely the program's **entry point** (where execution begins), but functions it calls can call other functions in turn:

```rust,editable
fn say_name() {
    println!("I'm Rust!");
}

fn greet() {
    say_name();
}

fn main() {
    greet(); // main calls greet, and greet calls say_name
}
```

### Where to Define Functions: Above or Below, Both Fine

In some languages, a function must be defined before it's used. Not in Rust!

```rust,editable
fn main() {
    greet(); // ✅ Called first
}

fn greet() { // Defined later
    println!("Hello!");
}
```

Totally fine. The Rust compiler scans the whole file first, so whether you put a function above or below `main`, it will be found.

### Function Naming Convention

Rust function names, like variables created with `let`, use **snake_case**: all lowercase, with words separated by underscores `_`.

```rust,noplayground
fn say_hello() { // ✅ snake_case
    println!("Hello!");
}

fn sayHello() {  // ⚠️ Runs, but the compiler warns
    println!("Hello!");
}
#
# fn main() {}
```

## Recap

- Define a function with `fn name() { ... }`.
- Call a function with `name();`.
- `main` is the program's entry point, but functions can call each other.
- Function definitions can go above or below `main`.
- The naming convention is snake_case (all lowercase with underscores).
