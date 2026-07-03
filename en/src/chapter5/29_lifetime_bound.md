# Lifetime Bounds

## Goal of This Episode

Learn lifetime bounds like `T: 'a`, and understand why `&'a T` requires every reference inside `T` to outlive `'a`.

## Concept

### The Problem: `T` Might Contain References

So far, our generic functions have mostly handled types owning their own data — `i32`, `String`. But `T` could also be `&str`, or some other type containing references.

Take this `struct`:

```rust,noplayground
struct Ref<'a, T> {
    value: &'a T,
}
#
# fn main() {}
```

If `T` is `&'x str`, then `value` is `&'a &'x str` — a reference pointing at another reference. In that case, `'x` must live at least as long as `'a`, or the inner `&'x str` might expire while the outer `&'a` is still alive.

### What `T: 'a` Means

`T: 'a` is a **lifetime bound**, meaning "every reference inside `T` outlives `'a`."

If `T` is `i32` (no references), `T: 'a` is satisfied automatically.
If `T` is `&'x str`, then `T: 'a` requires `'x` to live at least as long as `'a`.

### When Do You Write It?

In many cases, the compiler sees `&'a T` and knows `T: 'a` is needed, adding it for you. But in certain `trait` definitions or more intricate generic structures, you may need to write it by hand:

```rust,noplayground
struct Ref<'a, T: 'a> {
    value: &'a T,
}
#
# fn main() {}
```

The `T: 'a` here is actually redundant (the compiler derives it from `&'a T`), but writing it out isn't wrong, and it makes the intent clearer.

### References to Lifetime-carrying Types

The same reasoning extends to any type carrying a lifetime. If you have `&'b A<'a>` — a reference living for `'b`, pointing at an `A<'a>` — then the whole `A<'a>` must remain valid throughout `'b`. That means the data `A` borrows must outlive `'b`; in other words, `'a` must be at least as long as `'b`.

The reason is intuitive: holding a `&'b` reference, you can reach all the data `A` borrows. If `A`'s borrowed data expired before your reference did, you could touch memory that's already been reclaimed. So Rust requires `'a` to live at least as long as `'b`.

## Example Code

```rust,editable
struct Excerpt<'a> {
    text: &'a str,
}

// T: 'a ensures the references inside T outlive 'a
struct Ref<'a, T: 'a> {
    value: &'a T,
}

impl<'a, T: 'a> Ref<'a, T> {
    fn new(value: &'a T) -> Ref<'a, T> {
        Ref { value }
    }

    fn get(&self) -> &T {
        self.value
    }
}

fn main() {
    // T = i32 (no references; T: 'a automatically satisfied)
    let num = 42;
    let r = Ref::new(&num);
    println!("Ref<i32>: {}", r.get());

    // T = &str (T is itself a reference)
    let text = String::from("hello");
    let slice: &str = &text;
    let r2 = Ref::new(&slice);
    println!("Ref<&str>: {}", r2.get());

    // An example of &'b A<'a>
    let novel = String::from("A very long story...");
    let excerpt = Excerpt { text: &novel };
    let r3 = &excerpt; // &'b Excerpt<'a>
    // Here 'a is novel's lifespan, and 'b is how long r3 borrows excerpt
    // novel lives at least as long as r3, so 'a outlives 'b — condition satisfied
    println!("Reading through the reference: {}", r3.text);

    // T = String (owns its data, no references; T: 'a automatically satisfied)
    let s = String::from("world");
    let r3 = Ref::new(&s);
    println!("Ref<String>: {}", r3.get());
}
```

## Recap

- `T: 'a` means every reference inside `T` outlives `'a`.
- If `T` holds no references (like `i32`, `String`), `T: 'a` is automatically satisfied.
- For `&'a T` to be legal, `T: 'a` is required — usually inferred by the compiler.
- Understanding lifetime bounds is key to reading the standard library's more intricate generics.
