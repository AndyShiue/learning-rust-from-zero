# HRTB

## Goal of This Episode

Understand the `for<'a>` in a higher-ranked `trait` bound (HRTB), learn to tell "handles one particular lifetime" apart from "handles any lifetime," and read how the `Fn` trio elides the lifetimes of its inputs and return values.

> This episode supplements **Chapter 5's lifetimes** and **Chapter 6's closures**.

## Concept

Suppose we have two sets of product data and want to pick one featured product from each using the same rule:

```rust,noplayground
fn select_from_both<'first, 'second, T, F>(
    first: &'first [T],
    second: &'second [T],
    choose: F,
) -> (Option<&'first T>, Option<&'second T>)
where
    F: Fn(&[T]) -> Option<&T>,
{
    let from_first = choose(first);
    let from_second = choose(second);
    (from_first, from_second)
}
#
# fn main() {}
```

`first` and `second` are two different parameters, with lifetimes `'first` and `'second` respectively. Inside the function the same `choose` is called twice:

- The first call receives an `&'first [T]` and returns an `Option<&'first T>`.
- The second receives an `&'second [T]` and returns an `Option<&'second T>`.

The return type keeps both lifetimes: the first result follows `first`, the second follows `second`. So we can't simply shrink both inputs down to one shared lifetime.

The lifetimes in the bound are elided, but the full idea is this: whatever lifetime the slice `choose` receives has, it returns an element borrowed from that slice. Spelled out in full, that's an HRTB:

```rust,ignore
F: for<'a> Fn(&'a [T]) -> Option<&'a T>
```

On the first call `'a` can be `'first`; on the second it can switch to `'second`.

### The `Fn` Trio Has Lifetime Elision Too

Chapter 5 showed that functions can elide common lifetimes:

```rust,ignore
fn first<T>(values: &[T]) -> Option<&T>
```

Because there's only one input lifetime, the compiler knows the `&T` inside the `Option` must be borrowed from that `&[T]`. Written out in full:

```rust,ignore
fn first<'a, T>(values: &'a [T]) -> Option<&'a T>
```

The same lifetime elision applies to the parameters and return values of `Fn`, `FnMut`, and `FnOnce`. So all three bounds below have elided lifetimes:

```rust,ignore
F: Fn(&[T]) -> Option<&T>
F: FnMut(&[T]) -> Option<&T>
F: FnOnce(&[T]) -> Option<&T>
```

Their full forms are, respectively:

```rust,ignore
F: for<'a> Fn(&'a [T]) -> Option<&'a T>
F: for<'a> FnMut(&'a [T]) -> Option<&'a T>
F: for<'a> FnOnce(&'a [T]) -> Option<&'a T>
```

The difference between the three `trait`s is still how the closure may be called, and whether calling it modifies or consumes the captured values; the lifetime elision rules they use are the same.

### What `for<'a>` Means

`for<'a>` says "**this holds for every possible `'a`**." So:

```rust,ignore
for<'a> F: Fn(&'a [T]) -> Option<&'a T>
```

Or equivalently:

```rust,ignore
F: for<'a> Fn(&'a [T]) -> Option<&'a T>
```

Both say that `F` accepts an `&[T]` of any lifetime, and that the `&T` it returns uses the same lifetime as that call's input.

HRTB is short for **higher-ranked `trait` bound**. The name sounds forbidding, but for now there's only one reading that matters: "this `trait` bound must hold for all `'a`."

### Who Gets to Pick `'a`?

Back to the three lifetimes in `select_from_both`:

```rust,ignore
fn select_from_both<'first, 'second, T, F>(
    first: &'first [T],
    second: &'second [T],
    choose: F,
) -> (Option<&'first T>, Option<&'second T>)
where
    F: for<'a> Fn(&'a [T]) -> Option<&'a T>,
{
    /* ... */
}
```

`'first` and `'second` are the function's own generic parameters, fixed by the caller when they pass in the two sets of data.

`for<'a>`, on the other hand, sits inside `F`'s bound. `select_from_both` picks `'a = 'first` for the first call to `choose`, then `'a = 'second` for the second. So it's **the side using `choose`** that picks `'a` for each call, and `F` has to accept them all.

### Why Isn't an Ordinary Lifetime Parameter Enough?

If we tie `choose` to `'first` alone, the first call is fine and the second fails:

```rust,compile_fail
fn select_from_both<'first, 'second, T, F>(
    first: &'first [T],
    second: &'second [T],
    choose: F,
) -> (Option<&'first T>, Option<&'second T>)
where
    F: Fn(&'first [T]) -> Option<&'first T>,
{
    let from_first = choose(first);
    let from_second = choose(second);
    (from_first, from_second)
}
#
# fn main() {}
```

This bound only guarantees that `choose` can take an `&'first [T]` and return an `Option<&'first T>`. The second call needs it to take an `&'second [T]` and return an `Option<&'second T>`. Unless `'first` and `'second` happen to be identical, the guarantee falls short.

Switch to an HRTB and the same `choose` can use different lifetimes across the two calls:

```rust,noplayground
fn select_from_both<'first, 'second, T, F>(
    first: &'first [T],
    second: &'second [T],
    choose: F,
) -> (Option<&'first T>, Option<&'second T>)
where
    F: for<'a> Fn(&'a [T]) -> Option<&'a T>,
{
    let from_first = choose(first);
    let from_second = choose(second);
    (from_first, from_second)
}
#
# fn main() {}
```

In practice you can usually lean on lifetime elision and write the bound as:

```rust,ignore
F: Fn(&[T]) -> Option<&T>
```

You still need to recognize the full form with `for<'a>`, because more complicated APIs spell it out.

### The Key Test for HRTB

HRTB isn't needed only when the same closure gets called two or more times with different lifetimes. Even a single call may need it. First consider building and calling a closure directly in the same scope:

```rust,editable
fn main() {
    let values = [10, 20, 30];
    let length = |items: &[i32]| items.len();

    println!("Length: {}", length(&values));
}
```

There's no generic API taking an `F` here, so there's no bound for you to write `for<'a>` in. In fact, because the parameter is annotated `&[i32]`, the signature the compiler infers for `length` is higher-ranked all along: `for<'a> Fn(&'a [i32]) -> usize`. It's just that the compiler handles this `for<'a>` for you throughout, so you never see it.

The real difference appears when you have to write the bound yourself. A generic API takes a function or closure, then hands it a reference created only inside the API:

```rust,editable
struct Report {
    entries: usize,
}

fn inspect_report<F>(inspect: F)
where
    F: for<'a> Fn(&'a Report),
{
    let report = Report { entries: 3 };
    inspect(&report);
}

fn main() {
    inspect_report(|report| {
        println!("{} entries in total", report.entries);
    });
}
```

The `&Report` in the bound needs a lifetime, and it could come from two places: `inspect_report`'s own generic parameter, or `for<'a>`. The former is fixed by the caller when they call `inspect_report`, and `report` is only created after entering the function body — it can't outlive any `'a` the caller could possibly pick:

```rust,compile_fail
# struct Report {
#     entries: usize,
# }
#
fn inspect_report<'a, F>(inspect: F)
where
    F: Fn(&'a Report),
{
    let report = Report { entries: 3 };
    inspect(&report);
}
#
# fn main() {}
```

That leaves only `for<'a>`: letting `inspect_report` pick `'a` itself on each call to `inspect`. You could also lean on lifetime elision here and write `F: Fn(&Report)`, but that only elides the HRTB — it doesn't make the requirement go away.

A closure **capturing** references to outer local variables is a separate matter. Capturing constrains how long the closure itself can live, which is a different question from whether `F` has to accept multiple lifetimes.

When reading this sort of API, start by asking:

**Is the lifetime of the reference passed to `F` decided in advance by the caller, or by the API each time it calls `F`?**

If it's the latter, `F` usually needs higher-ranked capability.

## Example Code

```rust,editable
#[derive(Debug)]
struct Product {
    name: String,
    price: u32,
}

fn select_from_both<'first, 'second, F>(
    first: &'first [Product],
    second: &'second [Product],
    choose: F,
) -> (Option<&'first Product>, Option<&'second Product>)
where
    F: for<'a> Fn(&'a [Product]) -> Option<&'a Product>,
{
    let from_first = choose(first);
    let from_second = choose(second);
    (from_first, from_second)
}

fn main() {
    let first_catalog = vec![
        Product {
            name: String::from("Keyboard"),
            price: 2_500,
        },
        Product {
            name: String::from("Mouse"),
            price: 1_200,
        },
    ];
    let second_catalog = vec![
        Product {
            name: String::from("Monitor"),
            price: 8_000,
        },
        Product {
            name: String::from("Speakers"),
            price: 3_000,
        },
    ];

    let (first_featured, second_featured) = select_from_both(
        &first_catalog,
        &second_catalog,
        |products: &[Product]| {
            products.iter().max_by_key(|product| product.price)
        },
    );

    if let (Some(first), Some(second)) = (first_featured, second_featured) {
        println!("Featured in the first: {}, price: {}", first.name, first.price);
        println!("Featured in the second: {}, price: {}", second.name, second.price);
    }
}
```

## Recap

- Lifetime elision applies to the parameters and return values of `Fn`, `FnMut`, and `FnOnce` too.
- With only one input lifetime, `Fn(&[T]) -> Option<&T>` amounts to `for<'a> Fn(&'a [T]) -> Option<&'a T>`.
- `for<'a>` says the `trait` bound that follows holds for every `'a`.
- An outer `fn foo<'a>` usually lets the caller pick `'a`; the `for<'a>` in an HRTB lets the side using `F` pick `'a` on each call.
- When the same function or closure must be called once per reference of differing lifetimes while keeping each output's lifetime separate, an HRTB expresses that requirement directly.
- A generic API that hands `F` a reference created inside the function body also needs `F` to be higher-ranked; when you build and call a closure directly, the compiler infers this and you never write `for<'a>`.
- In practice lifetime elision usually hides this sort of HRTB, but you'll still meet `for<'a>` head-on when reading advanced signatures.
