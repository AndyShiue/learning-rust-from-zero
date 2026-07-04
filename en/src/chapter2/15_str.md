# String Slices: `&str`

## Goal of This Episode

Meet the `&str` type — it turns out the strings we've been using all along are slices!

## Main Text

In recent episodes we learned array slices, `&[i32]`. Today let's meet another kind of slice — the **string slice**. As it happens, the `"hello"` we've been writing all along is a string slice.

### The True Face of Strings

```rust,editable
fn main() {
    let s = "hello";
    println!("{}", s);
}
```

You've seen this kind of code countless times. But what is the type of `s`?

The answer: **`&str`** (a string slice).

```rust,editable
fn main() {
    let s: &str = "hello"; // Type spelled out explicitly
    println!("{}", s);
}
```

`&str` is read "string slice." Just like the array slice `&[i32]`, it's a "window pointing at a stretch of data."

### Comparison with Array Slices

| Array slice | String slice |
|---|---|
| `&[i32]` | `&str` |
| Points at a stretch of `i32` data | Points at a stretch of text data |
| `let s = &arr[1..4];` | `let s = "hello";` |

Exactly the same concept! One is a slice of numbers, the other a slice of text.

### String Slices Can Take Substrings Too

```rust,editable
fn main() {
    let s = "hello world";
    let hello = &s[0..5];
    let world = &s[6..11];
    println!("{}", hello); // hello
    println!("{}", world); // world
}
```

`&s[0..5]` takes the first 5 bytes of `s` (note: bytes, not characters).

As with array slices, `..=` includes the end:

```rust,editable
fn main() {
    let s = "hello world";
    let hello = &s[0..=4]; // Includes index 4; same as &s[0..5]
    println!("{}", hello); // hello
}
```

### ⚠️ Careful When Slicing Chinese Strings!

An English letter takes 1 byte, but a Chinese character usually takes **3 bytes**. If your cut lands right in the "middle" of a Chinese character, the program crashes outright:

```rust,editable
fn main() {
    let s = "你好";
    let first = &s[0..3]; // ✅ "你" (exactly 3 bytes)
    println!("{}", first);
}
```

But try slicing `&s[0..1]`:

```rust,should_panic
fn main() {
    let s = "你好";
    let oops = &s[0..1];  // ❌ Program crashes!
    println!("{}", oops);
}
```

Because "你" occupies 3 bytes (indices 0, 1, 2), cutting at index 1 lands in the middle of the character, and Rust won't allow it.

**In short**: slicing English strings is safe, but when slicing strings with Chinese (or other multi-byte) characters, make sure the cut lands exactly on a character boundary. When unsure, hold off on using `&s[start..end]` with such strings.

### `&str` as a Function Parameter

Now that you know strings are `&str`, you can use it as a function parameter:

```rust,editable
fn greet(name: &str) {
    println!("Hi, {}!", name);
}

fn main() {
    greet("Andy");
    greet("Ming");
}
```

`"Andy"` is itself of type `&str`, so it can be passed straight in.

## Recap

- The type of `"hello"` is `&str` — a string slice.
- `&str` shares the concept of the array slice `&[i32]` — both are "windows onto a stretch of data."
- Write `&str` for parameters to accept strings.
- You can take substrings with `&s[start..end]`, but beware: indices are byte positions, not character positions — cutting through the middle of a multi-byte character (like Chinese) panics.

Congratulations on finishing Chapter 2! 🎉 In this chapter we learned more ways to organize programs — functions, arrays, slices, and assorted techniques for clearer code. In the next chapter we'll start defining custom types, describing your own data with `struct` and `enum`!
