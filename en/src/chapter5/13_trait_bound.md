# `trait` Bounds

## Goal of This Episode

Learn to constrain a generic parameter's capabilities with `trait` bounds, and add methods to qualifying types with conditional `impl`.

## Concept

Back in Episode 1's generic functions, we wrote `fn first<T>(a: T, b: T) -> T`. But what if you want to `clone` a value inside a generic function?

```rust,compile_fail
fn duplicate<T>(x: &T) -> (T, T) {
    (x.clone(), x.clone()) // Compile error!
}
#
# fn main() {}
```

The compiler complains: "Not every `T` has a `clone()` method."

Fair enough — `T` could be any type. What if some type doesn't implement `Clone`?

### `trait` Bounds: Constraining What `T` Can Do

The fix is a **`trait` bound**, telling Rust "`T` must implement `Clone`":

```rust,editable
fn duplicate<T: Clone>(x: &T) -> (T, T) {
    (x.clone(), x.clone())
}

fn main() {}
```

`T: Clone` means "`T` must implement the `Clone` `trait`." Now Rust knows `x.clone()` is always callable.

### `trait` Bounds Go Everywhere

`trait` bounds aren't just for functions. Nearly anywhere a generic parameter appears can take one — `struct`, `enum`, and `impl` definitions included:

```rust,noplayground
struct Wrapper<T: Clone> {
    value: T,
}
#
# fn main() {}
```

### Conditional `impl`

The most practical spot is on an `impl` block. This is a **conditional impl** — providing certain methods only when the type parameter meets certain conditions.

```rust,noplayground
# #[derive(Debug)]
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
impl<T: Clone> Pair<T> {
    fn to_tuple(&self) -> (T, T) {
        (self.first.clone(), self.second.clone())
    }
}
#
# fn main() {}
```

This says: only when `T` implements `Clone` does `Pair<T>` have the `to_tuple` method.

### The Effect in Practice

```rust,compile_fail
# #[derive(Debug)]
# struct Pair<T> {
#     first: T,
#     second: T,
# }
#
# impl<T: Clone> Pair<T> {
#     fn new(first: T, second: T) -> Pair<T> {
#         Pair { first, second }
#     }
#
#     fn to_tuple(&self) -> (T, T) {
#         (self.first.clone(), self.second.clone())
#     }
# }
# fn main() {
    let p1 = Pair::new(1, 2); // i32 has Clone
    let t = p1.to_tuple();    // Callable ✓

    let p2 = Pair::new(Pair::new(1, 2), Pair::new(3, 4)); // Pair doesn't derive Clone
    p2.to_tuple(); // Compile error! Pair<i32> doesn't implement Clone
# }
```

`Pair<Pair<i32>>` can't call `to_tuple()`, because `Pair<i32>` doesn't implement `Clone` (we never `derive`d `Clone` for it).

## Example Code

```rust,editable
#[derive(Debug)]
struct Pair<T> {
    first: T,
    second: T,
}

// Every Pair<T> has new
impl<T> Pair<T> {
    fn new(first: T, second: T) -> Pair<T> {
        Pair { first, second }
    }
}

// Only Pair<T> with T: Clone has to_tuple
impl<T: Clone> Pair<T> {
    fn to_tuple(&self) -> (T, T) {
        (self.first.clone(), self.second.clone())
    }
}

// Generic function + trait bound
fn duplicate<T: Clone>(x: &T) -> (T, T) {
    (x.clone(), x.clone())
}

fn main() {
    // i32 has Clone, so Pair<i32> has to_tuple
    let p = Pair::new(10, 20);
    let t = p.to_tuple();
    println!("{:?}", t);

    // The generic function works too
    let pair = duplicate(&42);
    println!("{:?}", pair);

    let pair2 = duplicate(&String::from("hello"));
    println!("{:?}", pair2);

    // Pair<Pair<i32>> can't call to_tuple
    // because Pair<i32> doesn't derive Clone
    let nested = Pair::new(Pair::new(1, 2), Pair::new(3, 4));
    println!("{:?}", nested);
    // nested.to_tuple(); // Compile error! Pair<i32> doesn't implement Clone
}
```

## Recap

- The `trait` bound `T: Clone` requires `T` to implement a specific `trait`.
- `trait` bounds can go on functions, `struct`s, `enum`s, `impl`s — any generic parameter.
- Without a `trait` bound, a generic function or method can't assume `T` has any capability.
- Conditional `impl`: `impl<T: Clone> Pair<T> { ... }` provides methods only when `T` qualifies.
