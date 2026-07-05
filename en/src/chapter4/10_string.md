# `String`

## Goal of This Episode

Meet Rust's `String` type — a string that owns its data and can be modified.

## Concept

### The Strings We Had Were All Borrowed

Since Chapter 1, we've been using the `&str` type:

```rust,noplayground
# fn main() {
    let greeting: &str = "Hello";
# }
```

The string `"Hello"` is written directly in the code; its data gets compiled into the program itself. `&str` is a reference — you're only looking at the text; you **don't own** it and **can't modify** it.

### `String`: a String You Own

`String` is a string type you can own and modify. Its data lives on the heap.

Create one with `String::from()`:

```rust,noplayground
# fn main() {
    let s = String::from("Hello");
# }
```

`String::from` is an associated function (called with `::`, as in Chapter 3). It copies the `&str`'s contents onto the heap, creating a `String` you own.

### `push_str`: Appending Text

A `String` can be modified! Use `push_str` to tack on more text:

```rust,editable
fn main() {
    let mut s = String::from("Hello");
    s.push_str(", world!");
    println!("{}", s); // Hello, world!
}
```

Note the variable must be declared `let mut`, since we're modifying it.

### `format!`: Combining Values into a String

`format!` works exactly like `println!`, except it doesn't print — it returns a `String`:

```rust,editable
fn main() {
    let name = "Ming";
    let age = 20;
    let msg = format!("My name is {} and I'm {} years old", name, age);
    println!("{}", msg);
}
```

### `String` Follows the Ownership Rules Too

Because a `String`'s data lives on the heap, it is **not `Copy`**. Assignment and passing into functions both move:

```rust,noplayground
# fn main() {
    let s1 = String::from("hello");
    let s2 = s1; // Move! s1 can't be used anymore
# }
```

Same as before — to keep `s1`, use `.clone()` or borrow with `&`.

## Example Code

```rust,editable
fn main() {
    // Creating a String
    let mut greeting = String::from("Hello");
    println!("{}", greeting);

    // push_str: appending more text
    greeting.push_str(", world");
    greeting.push_str("!");
    println!("{}", greeting);

    // format!: combining several values
    let name = "Hana";
    let score = 95;
    let report = format!("Student {} scored {} points", name, score);
    println!("{}", report);

    // String moves (it's not Copy)
    let s1 = String::from("Rust");
    // let s2 = s1; // Writing this would move s1 away, making it unusable
    let s2 = s1.clone(); // Make a replica with clone; s1 survives
    println!("s1 = {}", s1);
    println!("s2 = {}", s2);

    // Passing into a function: borrowing avoids the move
    let s3 = String::from("Hi there");
    print_string(&s3);
    println!("s3 is still here: {}", s3);

    // The Debug format works too
    let s4 = String::from("debug test");
    println!("{:?}", s4);
}

fn print_string(s: &String) {
    println!("The function received: {}", s);
}
```

## Recap

- `String` is a string type that owns its data, which lives on the heap.
- `String::from("...")` creates a new `String`.
- `push_str` appends more text to the string (requires `let mut`).
- `format!` shares `println!`'s syntax but returns a `String` instead of printing.
- String is **not `Copy`** — assignment and passing into functions move it.
- To keep the original `String`, use `.clone()` or borrow with `&`.
