# `String` vs `&str`

## Goal of This Episode

Get the difference between `String` and `&str` straight, and figure out which one function parameters should use.

## Concept

### Two Kinds of Strings — What Exactly Differs?

| | `String` | `&str` |
|---|---|---|
| Owns the data? | ✅ Yes | ❌ Just borrowing |
| Where's the data? | On the heap | Possibly in the code itself, or borrowing a `String`'s data |
| Modifiable? | ✅ Yes (`push_str`, etc.) | ❌ No |
| Moves? | ✅ Yes | ❌ No (it's just a reference) |

### `&String` Converts to `&str` Automatically

When you have a `String` and want to pass its reference to a function that accepts `&str`, Rust converts for you:

```rust,editable
fn greet(name: &str) {
    println!("Hello, {}!", name);
}

fn main() {
    let s = String::from("Ming");
    greet(&s); // &String converts to &str automatically — totally fine!
}
```

Why does this work? We'll learn later. For now, just know: **where you pass an `&String` and the parameter type is `&str`, Rust handles it automatically**.

### Function Parameters Prefer `&str`

If your function only needs to "read" a piece of text without owning it, make the parameter `&str`:

```rust,noplayground
fn count_chars(s: &str) -> i32 {
    let mut count = 0;
    for _c in s.chars() {
        count += 1;
    }
    count
}
#
# fn main() {}
```

The `.chars()` used here is a method — implemented on both `String` and `&str`. It splits the string into individual characters for you to iterate over.

The benefits of this approach:

1. Passing an `&str` (string literal) works.
2. Passing an `&String` works too (automatic conversion).
3. Nothing gets moved.

That's why the Rust community broadly recommends: **use `&str` for function parameters, not `&String`**.

### When to Use `String`?

- You need to **own** the text (storing it in a `struct`, returning it to the caller).
- You need to **modify** the text (`push_str`, etc.).

## Example Code

```rust,editable
// Parameter as &str: accepts both &str and &String
fn greet(name: &str) {
    println!("Hello, {}!", name);
}

fn char_count(s: &str) -> i32 {
    let mut count = 0;
    for _c in s.chars() {
        count += 1;
    }
    count
}

fn main() {
    // &str: a string literal
    let literal = "world";
    greet(literal);

    // String: an owned string
    let owned = String::from("Hana");
    greet(&owned); // &String auto-converts to &str

    // Both can be passed to a function accepting &str
    println!("\"{}\" has {} characters", literal, char_count(literal));
    println!("\"{}\" has {} characters", owned, char_count(&owned));

    // String can be modified; &str can't
    let mut s = String::from("Rust");
    s.push_str(" is fun");
    println!("{}", s);

    // String moves
    let s1 = String::from("hello");
    let s2 = s1; // move
    // println!("{}", s1); // Compile error!
    println!("{}", s2);

    // &str doesn't move (it's a reference by nature)
    let greeting: &str = "Hi";
    let greeting2 = greeting;  // This is a Copy! (&str is Copy)
    println!("{}", greeting);  // OK
    println!("{}", greeting2); // OK
}
```

## Recap

- **`String`** owns its data (on the heap), can be modified, and moves.
- **`&str`** is a reference — owns nothing, can't be modified, doesn't move.
- `&String` converts to `&str` automatically.
- Prefer `&str` for function parameters — it accepts more (both `&str` and `&String` can be passed).
- Use `String` only when you need to own or modify the text.
