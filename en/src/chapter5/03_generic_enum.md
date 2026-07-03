# Generic `enum`s

## Goal of This Episode

Learn to define `enum`s with type parameters.

## Concept

Last episode was generic `struct`s; this one is generic `enum`s. The idea is exactly the same — add `<T>` after the `enum` name, and the data variants carry can be of any type.

### Defining a Generic `enum`

Suppose we want a "maybe there's a value" type — it might hold something, or be empty:

```rust,noplayground
enum Maybe<T> {
    Something(T),
    Nothing,
}
#
# fn main() {}
```

`Something(T)` carries a value of type `T`; `Nothing` carries nothing.

Generic `enum`s can have multiple type parameters too. Say, an "either-or" type:

```rust,noplayground
enum Either<L, R> {
    Left(L),
    Right(R),
}
#
# fn main() {}
```

An `Either<L, R>` is either `Left(L)` or `Right(R)` — the two types fully independent.

## Example Code

```rust,editable
// Our own generic enum
#[derive(Debug)]
enum Maybe<T> {
    Something(T),
    Nothing,
}

// A generic enum with two type parameters
#[derive(Debug)]
enum Either<L, R> {
    Left(L),
    Right(R),
}

fn main() {
    let a: Maybe<i32> = Maybe::Something(42);
    let b: Maybe<i32> = Maybe::Nothing;

    println!("{:?}", a);
    println!("{:?}", b);

    // Extracting the value with match
    match a {
        Maybe::Something(val) => println!("There's something inside: {}", val),
        Maybe::Nothing => println!("Empty"),
    }

    // Two type parameters
    let x: Either<i32, &str> = Either::Left(100);
    let y: Either<i32, &str> = Either::Right("hello");

    println!("{:?}", x);
    println!("{:?}", y);
}
```

## Recap

- `enum`s can take type parameters too: `enum Maybe<T> { ... }`.
- The data a variant carries can be generalized with `T`.
- Multiple type parameters are allowed: `enum Either<L, R> { Left(L), Right(R) }`.
- The standard library has many important generic `enum`s — we'll meet them in due course.
