# `Cow<'a, B>`

## Goal of This Episode

Learn to use `Cow<'a, str>` for a flexible "borrow when possible, `clone` only when needed" strategy.

## Concept

Some functions can sometimes return borrowed data directly, yet other times must return owned data.

### An Example

Suppose you have a function that prepends a greeting to a string. If the string already starts with "Hello", just return the original (borrowed). If not, a new string must be built (owned).

Should the return type be `&str` or `String`? Neither is quite right.

### `Cow` to the Rescue

`Cow` stands for **`Clone` on write**. It lives in the `std::borrow` module. Here's a simplified definition to show the core structure; it omits pieces needed by the full standard-library type, so this sketch is not a drop-in working implementation:

```rust,noplayground
enum Cow<'a, B>
where
    B: 'a + ToOwned,
{
    Borrowed(&'a B),
    Owned(B::Owned), // ToOwned's associated type
}
#
# fn main() {}
```

Line by line:

- **`'a`**: the lifetime parameter — the lifespan of the borrowed data.
- **`B: 'a`**: a lifetime bound (from recent episodes); references inside `B` must outlive `'a`.
- **`B: ToOwned`**: a `trait` bound; `B` must implement `ToOwned`.
- **`Borrowed(&'a B)`**: the borrowed version, holding an `&'a B`.
- **`Owned(...)`**: the owning version, whose type is decided by `ToOwned`'s associated type `Owned`.

`ToOwned` is a `trait` with an associated type `Owned`, representing "the owning version of the type."

For `str`:
- `str` implements `ToOwned` with `type Owned = String`.
- So `Cow<'a, str>` = `Borrowed(&'a str)` or `Owned(String)`.

For `[T]`:
- `[T]` implements `ToOwned` with `type Owned = Vec<T>`.
- So `Cow<'a, [T]>` = `Borrowed(&'a [T])` or `Owned(Vec<T>)`.

### `Cow` Implements `Deref`

The most crucial point when using `Cow`: `Cow<'a, B>` implements `Deref<Target = B>`. Meaning: whether it holds `Borrowed(&str)` or `Owned(String)`, you can use `&Cow<'_, str>` directly as an `&str` — calling `&str`'s methods or passing it to functions accepting `&str`, without ever caring whether it's borrowed or owned.

```rust,editable
use std::borrow::Cow;

fn main() {
    let cow: Cow<'_, str> = Cow::Owned(String::from("hello"));
    // Used directly as &str; Deref handles it
    println!("Length: {}", cow.len());
    println!("Uppercase: {}", cow.to_uppercase());
}
```

Thanks to `Deref`, callers usually needn't care whether the inside is borrowed or owned — just use it as an `&str`.

### Common Methods

- **`.to_mut()`**: if it's `Borrowed`, first `clone`s into `Owned`, then returns a mutable reference. If already `Owned`, returns its mutable reference directly. This is the heart of "`clone` on write."
- **`.into_owned()`**: converts either variant into an owned value. `Borrowed` gets `clone`d; `Owned` is taken as-is.

## Example Code

```rust,editable
use std::borrow::Cow;

// If the string already starts with "Hello", return it borrowed
// Otherwise build a new String
fn ensure_greeting(s: &str) -> Cow<'_, str> {
    if s.starts_with("Hello") {
        // No modification needed; borrow directly
        Cow::Borrowed(s)
    } else {
        // Modification needed; build a new string
        let mut greeting = String::from("Hello, ");
        greeting.push_str(s);
        Cow::Owned(greeting)
    }
}

fn main() {
    // Already starts with "Hello" → borrowed, zero cost
    let s1 = "Hello world";
    let result1 = ensure_greeting(s1);
    println!("{}", result1);

    // Doesn't start with "Hello" → a new string is built
    let s2 = "Rust";
    let result2 = ensure_greeting(s2);
    println!("{}", result2);

    // You can check whether it's borrowed or owned
    match ensure_greeting(s1) {
        Cow::Borrowed(s) => println!("Borrowed: {}", s),
        Cow::Owned(s) => println!("Owned: {}", s),
    }

    match ensure_greeting(s2) {
        Cow::Borrowed(s) => println!("Borrowed: {}", s),
        Cow::Owned(s) => println!("Owned: {}", s),
    }

    // to_mut: clone on write
    let mut cow: Cow<'_, str> = Cow::Borrowed("hello");
    // It's Borrowed now; calling to_mut clones it into Owned first
    cow.to_mut().push_str(" world");
    println!("{}", cow); // "hello world"

    // into_owned: converting into an owned String
    let cow2: Cow<'_, str> = Cow::Borrowed("bye");
    let owned: String = cow2.into_owned();
    println!("{}", owned);
}
```

## Recap

- `Cow<'a, str>` can be borrowed (`&str`) or owned (`String`), as circumstances demand.
- `Cow` uses the `ToOwned` `trait`'s associated type to decide the owning version's type (`str` → `String`, `[T]` → `Vec<T>`).
- `Cow` implements `Deref`: whether `Borrowed` or `Owned`, a `&Cow<'_, str>` can be used directly as an `&str` — its greatest strength.
- `.to_mut()`: `clone` on write (`Borrowed` → `clone` into `Owned` → return a mutable reference).
- `.into_owned()`: converts either variant into an owned value.
- Suited to "mostly no modification, occasional modification" scenarios.

Congratulations on finishing Chapter 5! 🎉 This chapter was truly packed — from generics, `trait` bounds, and lifetimes, through smart pointers like `Box` and `Rc` and the `Deref` machinery, to the interior mutability of `Cell` and `RefCell`, plus `Display`, associated types, and `Cow`. These are the most powerful weapons in Rust's type system, and the foundation for reading the standard library's source. Next chapter, we enter closures and iterators — Rust's most elegant style of functional programming!
