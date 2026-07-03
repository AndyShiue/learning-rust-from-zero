# Generic Functions

## Goal of This Episode

Learn to define generic functions with `<T>`, so one function can handle different types.

## Concept

In Chapter 4 we learned `Vec` and used it to store a bunch of `i32`s. But did you notice we always wrote `vec![1, 2, 3]` and let Rust infer the type?

In truth, `Vec` isn't a complete type. Its full form is `Vec<i32>`, `Vec<String>`, `Vec<bool>` — the angle brackets `<>` hold "what type of thing this `Vec` stores."

Chapter 4 deliberately kept quiet about the angle brackets, because we hadn't learned generics yet. Now it's time to lift the veil.

### What Are Generics?

Suppose you want a function that takes two values and returns the first:

```rust,noplayground
fn first_i32(a: i32, b: i32) -> i32 {
    a
}
#
# fn main() {}
```

What if you also need to handle `f64`? Surely not a whole separate `first_f64`?

Generics solve this. We use a "type parameter" `T` in place of a concrete type:

```rust,noplayground
fn first<T>(a: T, b: T) -> T {
    a
}
#
# fn main() {}
```

The `<T>` after the function name says "this function has a type parameter named T." The parameters `a` and `b` both have type `T`, and so does the return value.

When you call `first(10, 20)`, Rust sees `10` is an `i32` and knows `T = i32`. Calling `first(3.14, 2.71)` makes `T = f64`. One function definition, automatically fitting different types.

### Naming Convention

Type parameters usually use single capital letters: `T` (Type), `U`, `V`. Longer, meaningful names appear when there's semantic weight, but `T` is fine for now.

## Example Code

```rust,editable
// A generic function: return the first of two values
fn first<T>(a: T, _b: T) -> T {
    a
}

// Multiple type parameters are allowed
fn make_pair<T, U>(a: T, b: U) -> (T, U) {
    (a, b)
}

fn main() {
    // T is inferred as i32
    let x = first(10, 20);
    println!("{}", x);

    // T is inferred as &str
    let y = first("hello", "world");
    println!("{}", y);

    // But both arguments must share a type, since first's parameters are both T
    // let bad = first(1, "a"); // Compile error! 1 is i32 but "a" is &str

    // T = i32, U = &str
    let pair = make_pair(42, "hello");
    println!("{:?}", pair);
}
```

## Recap

- `Vec`'s full form is `Vec<T>`, with a type parameter in the angle brackets — Chapter 4 deliberately omitted this; now it's official.
- Generic functions declare type parameters with `<T>`, letting one function handle different types.
- Rust infers what `T` is from the values passed in.
- Multiple type parameters are allowed: `<T, U>`.
- Type parameters conventionally use capital letters: `T`, `U`, `V`.
