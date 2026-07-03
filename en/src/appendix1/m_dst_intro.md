# A Brief Introduction to DSTs

## Goal of This Episode

Understand what dynamically sized types (DSTs) are, and what `Sized` and `?Sized` mean in generics.

> This episode supplements **Chapter 5**.

## Concept

(The pointer sizes mentioned in this episode assume a 64-bit system — as nearly all computers now are.)

In Rust's type system, most types have compile-time-known sizes — `i32` is 4 bytes, `bool` 1 byte, `(i32, i32)` 8 bytes. But some types' sizes are **unknown at compile time** — these are **DSTs (Dynamically Sized Types)**.

### The Common DSTs

You've actually met them already:

- **`str`**: the "content" type of string slices. `"hello"` is 5 bytes, `"哈囉"` is 6 — no fixed length.
- **`[T]`**: the "content" type of array slices. A `[i32]` might have 3 elements or 100.

Because their sizes aren't fixed, you **can't** use them directly as values:

```rust,compile_fail
fn main() {
    let s: str = "hello";       // Compile error!
    let arr: [i32] = [1, 2, 3]; // Compile error!
}
```

### How to Use Them? Through Pointers!

A DST must hide behind some kind of pointer:

- `&str`, `&[T]` — references
- `Box<str>`, `Box<[T]>` — pointers to the heap

These pointers are the so-called **fat pointers** — storing not just an address but an extra length:

```ignore
Ordinary pointer: [address]         (8 bytes)
Fat pointer:      [address][length] (16 bytes)
```

So an `&str` actually occupies 16 bytes: 8 pointing at the string data, 8 recording the length.

### The `Sized` `trait`

Rust has a special trait called `Sized`, meaning "this type's size is known at compile time." **The vast majority of types implement `Sized` automatically.**

Furthermore — and many don't know this — **generic parameters carry a default `Sized` bound**:

```rust,ignore
fn print_it<T>(val: T) { ... }
// Is actually equivalent to
fn print_it<T: Sized>(val: T) { ... }
```

Sensible, since if `T`'s size were unknown, the function couldn't know how much stack space to allocate.

### `?Sized`: Loosening the Restriction

Sometimes you want a generic parameter to accept DSTs. That's when `?Sized` loosens the bound:

```rust,ignore
fn print_it<T: ?Sized>(val: &T) { ... }
//                     ^^^^^^^ Note: must go through a reference
```

`?Sized` means "`T` may be `Sized`, or may not." Since the size may be unknown, `T` is usually usable only through references or smart pointers.

### `Self` in a `trait` Defaults to `?Sized`

We said generic parameters `T` default to a `Sized` bound. But a `trait`'s `Self` is the exception — it defaults to `?Sized`; that is, `Self` needn't be `Sized`.

Remember `Clone` from Chapter 4 Episode 8? Its method is `fn clone(&self) -> Self` — returning `Self` outright. Since `Self` might not be `Sized` by default, while a returned type must have a known size, `Clone`'s actual definition is:

```rust,noplayground
trait Clone: Sized {
    fn clone(&self) -> Self;
}
#
# fn main() {}
```

### Looking Back at Chapter 5's `Cow`

When Chapter 5's last episode taught `Cow`, we used a simplified definition too:

```rust,noplayground
// The simplified version from Chapter 5
pub enum Cow<'a, B>
where
    B: 'a + ToOwned,
{
    Borrowed(&'a B),
    Owned(B::Owned),
}
#
# fn main() {}
```

If you'd tried putting `str` or `[T]` into that `Cow` — writing `Cow<'_, str>`, say — it wouldn't compile. The generic parameter `B` demands `Sized` by default, and `str` isn't `Sized`.

Adding `?Sized` fixes it:

```rust,noplayground
pub enum Cow<'a, B>
where
    B: 'a + ToOwned + ?Sized,
{
    Borrowed(&'a B),
    Owned(B::Owned),
}
#
# fn main() {}
```

The `B` in `Borrowed(&'a B)` already sits behind a reference, so `B` being a DST is fine — the fat pointer takes care of it.

### `&mut [T]` and `&mut str`

DSTs can take mutable references too. `&mut [T]` is quite useful — you can modify the slice's elements:

```rust,noplayground
# fn main() {
    let mut arr = [1, 2, 3, 4, 5];
    let slice: &mut [i32] = &mut arr[1..4];
    slice[0] = 99;  // arr becomes [1, 99, 3, 4, 5]
# }
```

But `&mut str` is nearly useless. Syntactically legal, yet there's almost nothing you can do with it. The reasons:

**First, `&mut str`, like `&mut [T]`, can't change the length.** `str` is a DST; `&mut str` is a fat pointer (address + length), the length being part of the reference. An `&mut str` is only a borrow — you don't own that memory's allocation, so you can't grow or shrink it. Consider `&'static mut str`: it points into the program file's read-only section; you certainly can't make that memory grow. Changing length requires the memory-owning `String`.

**Second, even changing the contents is restricted.** In UTF-8, one character may take 1~4 bytes:

- `'a'` → 1 byte
- `'é'` → 2 bytes
- `'哈'` → 3 bytes

Suppose you have `"哈囉"` (6 bytes) and want to change `'哈'` into `'a'` — `'a'` is 1 byte while `'哈'` occupies 3; in-place replacement is impossible with mismatched lengths. Forcing the first byte changed without handling the rest breaks the UTF-8 multi-byte sequence. And Rust's `str` guarantees its content is always valid UTF-8 — violating that guarantee causes undefined behavior.

Hence the standard library's methods on `&mut str` are pitifully few — basically just `make_ascii_uppercase()` and `make_ascii_lowercase()`, operations that "never change byte length" (ASCII case conversion happens to be 1 byte for 1 byte). For string modification, stick with `String`.

### DSTs and `Deref`

Chapter 5 also introduced the `Deref` `trait`. `String` and `Vec<T>` implement `Deref` too, and dereferencing them yields exactly DSTs:

- `String` implements `Deref`; `Deref::deref(&String)` returns `&str`.
- `Vec<T>` implements `Deref`; `Deref::deref(&Vec<T>)` returns `&[T]`.

That is, dereferencing a `String` yields `str`, and dereferencing a `Vec<T>` yields `[T]`. DSTs can't live in variables directly, but `deref` coercion happens at the **reference level**: `&String` becomes `&str`, `&Vec<T>` becomes `&[T]`. The result of the conversion is a fat pointer carrying address and length — no need to know the DST's actual size.

That's why a function accepting `&str` takes an `&String` directly, and one accepting `&[T]` takes an `&Vec<T>` — the mechanism underneath is exactly DSTs + `Deref` combined.

### Pointers Still Fuzzy?

If concepts like "pointer," "fat pointer," and "address" remain hazy, don't worry — the next chapter's first episode formally introduces what pointers really are.

## Example Code

```rust,editable
use std::fmt::Display;

// The default: T must be Sized
fn print_sized<T: Display>(val: T) {
    println!("A Sized value: {}", val);
}

// Loosened: T may be a DST, but must come through a reference
fn print_unsized<T: Display + ?Sized>(val: &T) {
    println!("Possibly a DST: {}", val);
}

// Showing fat pointer sizes on a 64-bit machine
fn show_pointer_sizes() {
    use std::mem::size_of;

    println!("--- Pointer size comparison ---");
    println!("&i32     = {} bytes", size_of::<&i32>());     // 8
    println!("&[i32]   = {} bytes", size_of::<&[i32]>());   // 16 (fat pointer)
    println!("&str     = {} bytes", size_of::<&str>());     // 16 (fat pointer)
    println!("Box<i32> = {} bytes", size_of::<Box<i32>>()); // 8
    println!("Box<str> = {} bytes", size_of::<Box<str>>()); // 16 (fat pointer)
}

fn main() {
    // Sized values: ordinary types
    print_sized(42);
    print_sized(String::from("hello"));

    // ?Sized: accepts &str (str being a DST)
    print_unsized("hello");                // T = str (a DST)
    print_unsized(&42);                    // T = i32 (Sized works too)
    print_unsized(&String::from("world")); // T = String (Sized)

    // &str and &[T] are fat pointers
    show_pointer_sizes();

    // str and [T] can't be used directly as values
    // let s: str = *"hello";    // Compile error!
    // let a: [i32] = *&[1,2,3]; // Compile error!

    // But through references, no problem
    let s: &str = "hello";
    let a: &[i32] = &[1, 2, 3];
    println!("\n&str = {}", s);
    println!("&[i32] length = {}", a.len());

    // Box<str> works as well
    let boxed: Box<str> = String::from("boxed string").into_boxed_str();
    println!("Box<str> = {}", boxed);
}
```

## Recap

- **DSTs (Dynamically Sized Types)**: types with compile-time-unknown sizes, like `str` and `[T]`.
- DSTs can't be used directly as values; they need pointers: `&str`, `&[T]`, `Box<str>`, etc.
- Pointers to DSTs are **fat pointers**: address + length, 16 bytes on 64-bit machines.
- **`Sized`**: the type's size is compile-time known; generic parameters default to the `T: Sized` bound.
- **`?Sized`**: loosens the bound so generics can accept DSTs (used through references).
- A `trait`'s `Self` defaults to `?Sized`; methods returning `Self` require `: Sized` on the `trait` (as in `Clone: Sized`).
- The `B: ?Sized` in `Cow<'a, B>` exists precisely so `B` can be a DST like `str` or `[T]`.
- `String`'s and `Vec<T>`'s `Deref` yield the DSTs `str` and `[T]`; `deref` coercion makes `&String` → `&str` and `&Vec<T>` → `&[T]` possible.
