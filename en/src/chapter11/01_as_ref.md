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
    let text = String::from("hello");
    print_length(&text);
    println!("{text}"); // still usable
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

### Who Owns the Argument?

`AsRef` and `AsMut` only describe which kind of reference a type can provide. They do not determine whether a function takes ownership of its argument; that depends on the parameter type and what the caller passes in.

Although `s: impl AsRef<str>` is a by-value parameter, the concrete type represented by `impl AsRef<str>` can itself be a reference. In `print_length(&text)`, that type is `&String`, so the function receives only a reference and `text` remains usable. If the caller has a value it wants to keep, it will therefore usually pass `&value`.

We could instead declare the parameter as `s: &impl AsRef<str>` to require a borrow. However, `s: impl AsRef<str>` is more flexible: callers can pass a reference to keep an existing value, or pass an owned value when they no longer need it.

A function with an `AsMut` parameter usually wants to modify a value the caller already owns, so it normally does not want to take ownership of that value. `fill_zeros` therefore uses an outer `&mut` to require a mutable borrow. The outer `&mut` says how the function receives the buffer, while `AsMut<[u8]>` says the buffer can provide a `&mut [u8]`. In `fill_zeros(&mut v)`, `impl AsMut<[u8]>` represents `Vec<u8>`, and `buf.as_mut()` produces the mutable slice used by the loop.

### How It Differs from `Deref`

`Deref` is used automatically in places like `deref` coercion and method calls: Rust borrows through the value for you. `AsRef` is a manual `.as_ref()` call.

The more important difference: each type can have only one `Deref` target (`String`'s target is `str`), but it can implement multiple `AsRef`s (`String` is both `AsRef<str>` and `AsRef<[u8]>`). Same for `AsMut`.

### When to Use It

Use `AsRef<T>` or `AsMut<T>` when a function needs a common way to borrow several possible input types. Usually, an `AsRef` parameter is written as `impl AsRef<T>`, while an `AsMut` parameter is written as `&mut impl AsMut<T>`. The former lets callers pass either an owned value or a reference; the latter modifies the caller's existing value without taking ownership. Use another form only when the function deliberately needs a different ownership relationship.

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
    let message = String::from("hello");
    describe(&message);
    println!("original: {message}");

    let numbers = vec![1, 2, 3];
    count_bytes(&numbers);
    println!("original: {numbers:?}");
}
```

## Recap

- `AsRef<T>`: cheaply borrow as `&T`, invoked with `.as_ref()`.
- `AsMut<T>`: cheaply borrow as `&mut T`, invoked with `.as_mut()`.
- `AsRef` and `AsMut` do not decide ownership; the parameter type and the argument passed by the caller do.
- A by-value `impl AsRef<T>` parameter can still receive a reference, allowing the caller to keep its value.
- An `AsMut` parameter usually uses an outer `&mut` to modify the caller's existing value without taking ownership.
- One type can implement multiple `AsRef`s / `AsMut`s (`Deref` / `DerefMut` allow only one target).
- The standard library uses these heavily.
