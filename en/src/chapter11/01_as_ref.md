# `AsRef<T>` / `AsMut<T>`

## Goal of This Episode

Learn to use `AsRef` and `AsMut` so a function can accept multiple types.

## Concept

### Motivation

Suppose you wrote a function that takes a `&str`:

```rust,noplayground
fn print_length(s: &str) {
    println!("length: {}", s.len());
}
#
# fn main() {}
```

If the caller holds a `String`, `&String` converts to `&str` automatically thanks to `Deref`, so that's fine. But what if you want a function that accepts `String`, `&str`, and maybe other types all at once?

### `AsRef`

The `AsRef<T>` `trait` means "I can be cheaply borrowed as a `&T`":

```rust,editable
fn print_length(s: impl AsRef<str>) {
    println!("length: {}", s.as_ref().len());
}

fn main() {
    print_length("hello");            // &str
    print_length(String::from("hi")); // String
}
```

The standard library already implements `AsRef` for many types:

- `String: AsRef<str>`
- `String: AsRef<[u8]>`
- `Vec<T>: AsRef<[T]>`

### `AsMut`

`AsMut<T>` is the mutable version — borrow as `&mut T`:

```rust,editable
fn fill_zeros(buf: &mut impl AsMut<[u8]>) {
    for byte in buf.as_mut() {
        *byte = 0;
    }
}

fn main() {
    let mut v = vec![1, 2, 3];
    fill_zeros(&mut v);
    println!("{:?}", v); // [0, 0, 0]
}
```

### Why `impl AsRef<T>` for `AsRef` but `&mut impl AsMut<T>` for `AsMut`?

`AsRef`'s `as_ref` only needs `&self`, so passing the value in is perfectly fine — the function borrows it briefly inside, and the caller's value is unaffected (if it's `Copy`), or you intended to move the value in anyway.

`AsMut` is different. If you write `fn foo(buf: impl AsMut<[u8]>)`, the value gets moved in — gone from the caller once used. If you're bothering to pass something mutable, you presumably want to keep using it after the changes, so the parameter is written `&mut impl AsMut<[u8]>` — borrow it mutably, no move needed.

You might wonder: "`&mut Vec<u8>` isn't a `Vec<u8>`, so why can `&mut Vec<u8>` be used as `AsMut<[u8]>`?" The answer is this blanket implementation in the standard library:

```rust,ignore
impl<T, U> AsMut<U> for &mut T
where
    T: AsMut<U> + ?Sized,
    U: ?Sized,
{ ... }
```

Meaning: if `T` implements `AsMut<U>`, then `&mut T` automatically implements `AsMut<U>` too. So a `&mut Vec<u8>` can be used directly as an `AsMut<[u8]>`.

### How It Differs from `Deref`

`Deref` is used automatically in places like `deref` coercion and method calls: Rust borrows through the value for you. `AsRef` is a manual `.as_ref()` call.

The more important difference: each type can have only one `Deref` target (`String`'s target is `str`), but it can implement multiple `AsRef`s (`String` is both `AsRef<str>` and `AsRef<[u8]>`). Same for `AsMut`.

### When to Use It

When you want a function parameter generalized to accept several types, use `impl AsRef<T>` and `&mut impl AsMut<T>`. The standard library uses this everywhere.

## Example Code

```rust,editable
fn describe(s: impl AsRef<str>) {
    let s = s.as_ref();
    println!("\"{}\" has {} characters", s, s.chars().count());
}

fn count_bytes(data: impl AsRef<[u8]>) {
    println!("{} bytes total", data.as_ref().len());
}

fn main() {
    // AsRef<str>: accepts &str and String
    describe("hello");
    describe(String::from("hi there"));

    // AsRef<[u8]>: accepts Vec<u8>, String, etc.
    count_bytes(vec![1, 2, 3]);
    count_bytes(String::from("hi"));
}
```

## Recap

- `AsRef<T>`: cheaply borrow as `&T`, invoked with `.as_ref()`.
- `AsMut<T>`: cheaply borrow as `&mut T`, invoked with `.as_mut()`.
- Write `AsRef` parameters as `impl AsRef<T>` (by value) and `AsMut` parameters as `&mut impl AsMut<T>` (borrowed, so the caller can keep using it afterwards).
- `&mut T` can be used as `impl AsMut<U>` thanks to a standard-library blanket implementation.
- One type can implement multiple `AsRef`s / `AsMut`s (`Deref` / `DerefMut` allow only one target).
- The standard library uses these heavily.
