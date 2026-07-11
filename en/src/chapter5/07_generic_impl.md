# Generic `impl`

## Goal of This Episode

Learn to implement methods for a generic `struct`, and understand what the two `T`s in the `impl<T>` syntax mean.

## Concept

In Episode 2 we defined the generic `struct` `Pair<T>`. This episode we give it an `impl`.

Recall from Chapter 3, `impl` on a `struct` looks like this:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn sum(&self) -> i32 {
        self.x + self.y
    }
}
#
# fn main() {}
```

What about a generic `struct`?

### The `impl<T>` Syntax

```rust,noplayground
# #[derive(Debug)]
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
impl<T> Pair<T> {
    fn new(first: T, second: T) -> Pair<T> {
        Pair { first, second }
    }
}
#
# fn main() {}
```

Note there are **two** `T`s in different positions, playing different roles:

1. The `<T>` in `impl<T>`: **declares** a type parameter `T`. It tells Rust "I'm about to use a type parameter named `T`."
2. The `<T>` in `Pair<T>`: **uses** the just-declared `T`. It tells Rust "the type I'm implementing for is `Pair<T>`."

In other words: `impl<T>` declares `T`, then hands `T` to `Pair<T>` — "for any type `T`, implement the following methods for `Pair<T>`."

If you wrote only `impl Pair<T>` without the `impl<T>`, Rust would assume `T` is a concrete type name (like `i32` or `String`), fail to find a type called `T`, and report an error.

Conversely, writing `impl Pair<i32>` (no `impl<T>` needed) adds methods only to `Pair<i32>` — `Pair<String>` and the rest get nothing.

### Using `T` inside Methods

Once `T` is declared, the whole `impl` block can use it:

```rust,noplayground
# #[derive(Debug)]
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
impl<T> Pair<T> {
    fn new(first: T, second: T) -> Pair<T> {
        Pair { first, second }
    }

    fn first(&self) -> &T {
        &self.first
    }
}
#
# fn main() {}
```

### Implementing `trait`s Works the Same Way

When Chapter 4 taught `trait`s, we implemented them for concrete types, like `impl Greet for Cat`. To implement a `trait` for a generic type, the syntax is the same — declare the type parameter after `impl`:

```rust,noplayground
# trait SomeTrait {}
#
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
impl<T> SomeTrait for Pair<T> {
    // ...
}
#
# fn main() {}
```

Again: "for any type `T`, implement this `trait` for `Pair<T>`."

## Example Code

```rust,editable
#[derive(Debug)]
struct Pair<T> {
    first: T,
    second: T,
}

impl<T> Pair<T> {
    // Associated function
    fn new(first: T, second: T) -> Pair<T> {
        Pair { first, second }
    }

    // Method: return a reference to first
    fn first(&self) -> &T {
        &self.first
    }

    // Method: return a reference to second
    fn second(&self) -> &T {
        &self.second
    }
}

fn main() {
    let p = Pair::new(10, 20);
    println!("first = {}", p.first());
    println!("second = {}", p.second());
    println!("{:?}", p);

    let q = Pair::new("hello", "world");
    println!("first = {}", q.first());
    println!("second = {}", q.second());
}
```

## Recap

- To implement methods for a generic `struct`, write `impl<T> Pair<T> { ... }`.
- The `<T>` in `impl<T>` **declares** `T`; the `<T>` in `Pair<T>` **uses** `T`.
- Bottom line: `impl<T>` declares `T`, then hands it to `Pair<T>`.
- Once declared, every method in the `impl` block can use `T`.
- Implementing a `trait` for a generic type is similar: `impl<T> SomeTrait for Pair<T> { ... }`.
