# Generic `struct`s

## Goal of This Episode

Learn to define `struct`s with type parameters, so one structure can hold data of different types.

## Concept

Last episode we learned generic functions. Well, `struct`s can have type parameters too!

Recall that `Vec<i32>` and `Vec<String>` are the same `struct` definition, just holding different types. We can define generic `struct`s of our own the same way.

### Defining a Generic `struct`

```rust,noplayground
struct Pair<T> {
    first: T,
    second: T,
}
#
# fn main() {}
```

The `<T>` after the `struct` name says "`Pair` has one type parameter `T`." Both `first` and `second` have type `T`, so they must be the same type.

In use:

```rust,noplayground
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
# fn main() {   
    let p = Pair { first: 1, second: 2 };       // T = i32
    let q = Pair { first: "hi", second: "yo" }; // T = &str
# }
```

### Multiple Type Parameters

If you want `first` and `second` to be different types, use two type parameters:

```rust,noplayground
struct MixedPair<T, U> {
    first: T,
    second: U,
}
#
# fn main() {}
```

Exactly the same idea as last episode's `make_pair<T, U>`.

## Example Code

```rust,editable
// The two fields must share a type
#[derive(Debug)]
struct Pair<T> {
    first: T,
    second: T,
}

// The two fields may differ in type
#[derive(Debug)]
struct MixedPair<T, U> {
    first: T,
    second: U,
}

fn main() {
    let int_pair = Pair { first: 10, second: 20 };
    println!("{:?}", int_pair);

    let str_pair = Pair { first: "hello", second: "world" };
    println!("{:?}", str_pair);

    // Pair<T>'s two fields must share a type; this would be a compile error:
    // let bad = Pair { first: 42, second: "oops" };

    let mixed = MixedPair { first: 42, second: "answer" };
    println!("{:?}", mixed);
}
```

## Recap

- A `struct` can declare type parameters with `<T>`, making one definition fit many types.
- `Pair<T>`'s two fields are both `T`, so they must share a type.
- When different types are needed, use multiple type parameters: `MixedPair<T, U>`.
- As with generic functions, Rust infers type parameters from usage.
