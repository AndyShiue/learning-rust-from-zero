# Variance

## Goal of This Episode

Understand covariance, invariance, and contravariance, and know how the original subtype relationship shifts once a type is wrapped in a reference, a `Cell`, or a function.

> This episode supplements **Chapter 5's lifetimes** and the first two episodes of this appendix.

## Concept

We already know that if `'long: 'short`, an `&'long T` can be shortened into an `&'short T`. That means lifetimes stand in a **subtype** relationship to one another: a reference with the longer guarantee can be used wherever only the shorter guarantee is required.

But once a type is placed inside another type, that relationship isn't necessarily preserved as-is. Studying "how the subtype relationship changes across a wrapper" is variance.

### Covariance: The Direction Stays the Same

Start with shared references:

```rust,editable
fn use_short<'short>(value: &'short str, _marker: &'short ()) {
    println!("{value}");
}

fn main() {
    let forever: &'static str = "I live until the program ends";

    {
        let marker = ();
        use_short(forever, &marker);
    }
}
```

An `&'static str` has a very long lifetime, but `use_short` only asks for one as short as `marker`'s. Rust can use the long reference as a short one.

We say `&'a T` is **covariant** in `'a`: if `'long` is a subtype of `'short`, then `&'long T` is likewise a subtype of `&'short T` — the direction is unchanged.

Common owning types such as `Box<T>`, `Vec<T>`, and `Option<T>` are usually covariant in `T` as well. If `'long: 'short`, for instance, a `Vec<&'long str>` can be used where a `Vec<&'short str>` is needed. Doing so hands over ownership of the whole `Vec`, so the original location can no longer reach that same `Vec` through the longer-lifetime type.

### Invariance: The Inner Type Can't Be Converted Along

Mutable references are a special case. An `&'a mut T` can still be shortened in the lifetime `'a`, but it is **invariant** in the `T` inside.

The reason is that `&mut T` doesn't just let you read the `T` — it lets you put a new `T` in.

Suppose we want to perform this assignment:

```rust,ignore
*slot = short;
```

`short`'s type is `&'short str`. For the assignment to work, the `*slot` on the left must also be an `&'short str`. And dereferencing `slot` gives `*slot`, so `slot`'s type must be:

```rust,ignore
&mut &'short str
```

So the function responsible for storing the short-lived reference would be written:

```rust,noplayground
fn replace_with_short<'short>(
    slot: &mut &'short str,
    short: &'short str,
) {
    *slot = short;
}
#
# fn main() {}
```

The assignment inside the function is fine, since `*slot` and `short` are both `&'short str`. The problem shows up at the call site:

```rust,compile_fail
fn replace_with_short<'short>(
    slot: &mut &'short str,
    short: &'short str,
) {
    *slot = short;
}

fn main() {
    let mut forever: &'static str = "the original long-lived data";

    {
        let temporary = String::from("short-lived data");
        replace_with_short(&mut forever, &temporary);
    }

    println!("{forever}");
}
```

`forever`'s type is `&'static str`, so `&mut forever` has type `&mut &'static str`. But `temporary` can only supply an `&'short str`, so `replace_with_short`'s first parameter needs an `&mut &'short str`.

Allowing the call would force the compiler to perform this conversion:

```rust,ignore
&mut &'static str → &mut &'short str
```

And then `*slot = short` inside the function would write the short-lived reference into `forever`. Once the mutable borrow ends, `forever`'s type still claims to be `&'static str` while in reality it may already dangle. So what Rust forbids is the conversion at the call site, not the assignment inside the function, where both sides have the same type.

Hence, even though an `&'static str` can serve as a shorter `&str`, an `&mut &'static str` cannot freely follow along into an `&mut &'short str`. Wrapped in `&mut`, the inner `T`'s subtype relationship is locked down.

Types offering interior mutability — `Cell<T>`, `RefCell<T>`, `Mutex<T>` — are invariant in `T` across the board. Even though what you hold may only be an `&Cell<T>`, they can still swap out the value inside.

### Contravariance: The Direction Reverses

A third case shows up in function parameters: **contravariance**.

To isolate variance alone, the outer function below fixes `'short` and `'long` up front:

```rust,noplayground
fn use_as_long_only<'short, 'long: 'short>(
    can_accept_short: fn(&'short str),
) -> fn(&'long str) {
    // fn(&'short str) is converted into fn(&'long str) here.
    can_accept_short
}
#
# fn main() {}
```

If `'long: 'short`, an `&'long str` can be used as an `&'short str`. But wrapped inside a function parameter, the direction of the permitted conversion reverses:

```text
&'long str      → &'short str
fn(&'short str) → fn(&'long str)
```

The function `use_as_long_only` returns will only ever receive `&'long str`. The original `can_accept_short` can handle anything whose reference lives at least as long as `'short`; an `&'long str`, living even longer, certainly meets that requirement, so the conversion is safe.

The relationship for a function's **input** type therefore runs opposite to intuition: a function that demands less and accepts a wider range of inputs can be placed where a narrower input is expected. Function parameters are contravariant in their type.

Function **return values**, by contrast, behave like ordinary reads and are covariant: a function that can return a reference with the longer guarantee also satisfies a caller who only asks for a shorter one.

### A Quick Reference Table

| Type position | Variance in the parameter | Intuition |
| --- | --- | --- |
| `&'a T` | Covariant in `'a` and `T` | Shared reads only, so the guarantee can be shortened |
| `&'a mut T` | Covariant in `'a`, invariant in `T` | Can swap the `T`, so the inner promise can't be rewritten |
| `*const T` | Covariant in `T` | The `T` can only be read through the pointer; direction unchanged |
| `*mut T` | Invariant in `T` | The `T` can be swapped through the pointer, so the inner promise can't be rewritten |
| `Box<T>`, `Vec<T>`, `Option<T>` | Usually covariant in `T` | They own the value; no arbitrary `T` gets swapped in through a shared entry point |
| `Cell<T>`, `RefCell<T>` | Invariant in `T` | The contents can still be swapped while shared |
| `fn(T) -> U` | Contravariant in `T`, covariant in `U` | Can accept wider input, and can return a value with a stronger guarantee |

This table is for looking things up, not memorizing. When the compiler rejects a lifetime shortening that looks perfectly reasonable, start by asking: "can a new value be written into this type?" If it can, invariance is usually the reason.

### Variance Doesn't Change Runtime Results

Variance is entirely a compile-time typing rule. It inserts no conversions at runtime and doesn't actually rebuild any reference. The compiler is merely deciding whether one type can safely be used where another is expected.

## Example Code

```rust,editable
fn choose_shorter<'short>(
    long: &'static str,
    short: &'short str,
    use_long: bool,
) -> &'short str {
    if use_long {
        long
    } else {
        short
    }
}

fn print_text(text: &str) {
    println!("The function received: {text}");
}

fn use_as_long_only<'short, 'long: 'short>(
    can_accept_short: fn(&'short str),
) -> fn(&'long str) {
    // fn(&'short str) is converted into fn(&'long str) here.
    can_accept_short
}

fn main() {
    let local = String::from("a local string");

    // Shared references are covariant: 'static can shorten to local's lifetime.
    let selected = choose_shorter("long-lived data", &local, true);
    println!("Selected: {selected}");

    // Function inputs are contravariant: the parameter type converts the other way.
    let print_long: fn(&'static str) = use_as_long_only(print_text);
    print_long("from a string literal");
}
```

## Recap

- Variance describes how the original subtype relationship changes once a type is placed inside another type.
- Covariant preserves the direction; shared references, function return values, and many owning types fall into this group.
- Invariant permits no conversion along the subtype relationship; `&mut T`, `Cell<T>`, and others that can write the inner value are the common cases.
- Contravariant reverses the direction; function parameters are the main example.
- Variance is a compile-time rule — it never extends a lifetime or produces a runtime conversion.
