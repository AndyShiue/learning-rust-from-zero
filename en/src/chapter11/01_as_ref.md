# `AsRef<T>` / `AsMut<T>`

## Goal of This Episode

Learn to use `AsRef` and `AsMut` so a function can accept multiple types.

## Main Text

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

    print_length("hi");                    // &str
    print_length(&text);
    print_length(String::from("welcome")); // String

    println!("{text}"); // still usable
}
```

The standard library already implements `AsRef` for many types:

- `String: AsRef<str>`
- `String: AsRef<[u8]>`
- `Vec<T>: AsRef<[T]>`

### `AsMut`

`AsMut<T>` is the mutable version — borrow as `&mut T`:

In most cases, we use `AsMut` to modify a value the caller already owns, not to take ownership of it. Therefore, the parameter is usually written as `&mut impl AsMut<T>` rather than `impl AsMut<T>`.

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

### Ownership and When to Use It

`AsRef` and `AsMut` only describe which kind of reference a type can provide. They do not determine whether a function takes ownership of its argument; that depends on the parameter type and what the caller passes in.

Although `s: impl AsRef<str>` is a by-value parameter, the concrete type passed in can itself be a reference. `print_length(&text)` only borrows `text`, so it remains usable afterward; passing `text` directly would move it. This lets the caller choose between an owned value and a reference.

In `fill_zeros`, the outer `&mut` means that the function only borrows the buffer, while `AsMut<[u8]>` means that the buffer can provide a `&mut [u8]`.

### How It Differs from `Deref`

`Deref` is used automatically in places like `deref` coercion and method calls: Rust borrows through the value for you. `AsRef` is a manual `.as_ref()` call.

The more important difference: each type can have only one `Deref` target (`String`'s target is `str`), but it can implement multiple `AsRef`s (`String` is both `AsRef<str>` and `AsRef<[u8]>`). Same for `AsMut`.

Use `AsRef<T>` or `AsMut<T>` when a function needs a common way to borrow several possible input types.

## Recap

- `AsRef<T>` and `AsMut<T>` let a function borrow multiple input types as `&T` and `&mut T`, respectively.
- `AsRef` / `AsMut` do not decide ownership: `impl AsRef<T>` can receive an owned value or a reference, while `&mut impl AsMut<T>` borrows and modifies the original value.
- Conversions require an explicit `.as_ref()` or `.as_mut()` call; Rust can use `Deref` automatically.
- A type can implement multiple `AsRef`s / `AsMut`s, but it can have only one `Deref` target.
