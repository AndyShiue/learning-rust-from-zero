# Array Basics

## Goal of This Episode

Use an array to line up multiple values of the same type, and learn how to access and create them.

## Main Text

We've learned that tuples can package values of different types together. Today let's meet another good friend — the **array**. An array is "a bunch of values of the **same type**, lined up in a row."

### Creating an Array

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];
    println!("{:?}", arr);
}
```

We used `{:?}` (the `Debug` format) to print the array — remember Episode 5 of this chapter? Like tuples, arrays only have the `Debug` format; `{}` doesn't work.

Wrap the values in square brackets `[]`, separated by commas. Note: the values in an array **must all be the same type**.

```rust,compile_fail
# fn main() {
    let arr = [1, "hello", 3.14]; // ❌ No! Different types
# }
```

Want to mix types? Use the tuple from a few episodes back.

### Accessing by Index

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];
    println!("First: {}", arr[0]);
    println!("Third: {}", arr[2]);
    println!("Last: {}", arr[4]);
}
```

Key point: **indexing starts at 0**! So the indices of 5 elements are 0, 1, 2, 3, 4.

### Going Out of Bounds Panics

If you access an index that doesn't exist:

```rust,should_panic
# #![allow(unconditional_panic)]
#
fn main() {
    let arr = [1, 2, 3, 4, 5];
    println!("{}", arr[10]); // 💥 index out of bounds!
}
```

The program **crashes** (panics) and prints an error. Rust won't let you sneak a read of memory you shouldn't touch. Compared to silently handing you a garbage value, crashing outright is actually safer — at least you know immediately where things went wrong.

### The Type of an Array

An array's type is written `[element_type; length]`:

```rust,editable
fn main() {
    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    println!("{:?}", arr);
}
```

`[i32; 5]` means "an array holding 5 `i32`s." Note that **the length is part of the type** — `[i32; 3]` and `[i32; 5]` are different types!

Most of the time Rust infers this automatically, no annotation needed. But knowing how to write the type will be useful later.

### Quick Creation: the Repeat Syntax

If you want an array of "5 zeros":

```rust,editable
fn main() {
    let zeros = [0; 5];
    println!("{:?}", zeros);
}
```

`[0; 5]` means "the value 0, repeated 5 times." Before the semicolon is the value; after it, the count.

A few more examples:

```rust,editable
fn main() {
    let ones = [1; 10];    // ten 1s
    let flags = [true; 3]; // three trues
    println!("{:?}", ones);
    println!("{:?}", flags);
}
```

## Recap

- Create arrays with `[value1, value2, ...]`; all elements must share a type.
- Indexing starts at 0; access values with `arr[0]`.
- Accessing an out-of-range index panics (crashes the program).
- Array types are written `[type; length]`, e.g. `[i32; 5]` (the length is part of the type).
- `[value; count]` quickly creates a repeated array, e.g. `[0; 5]`.
- Print whole arrays with `{:?}`.
