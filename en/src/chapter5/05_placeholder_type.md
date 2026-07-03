# The Placeholder Type `_`

## Goal of This Episode

Learn to use `_` in type annotations to let the compiler infer part of a type.

## Concept

Last episode's turbofish specifies all the type parameters by hand. But sometimes you only want to specify some of them and let Rust infer the rest. That's when `_` serves as a type-level wildcard.

### `_` as a Type Placeholder

Take this example:

```rust,editable
fn main() {
    let v: Vec<_> = vec![1, 2, 3];
}
```

We're telling Rust "this is a `Vec`," while the element type `_` says "you figure it out." Rust sees `1, 2, 3` are integers and infers `_` = `i32`.

`_` works inside a turbofish too:

```rust,ignore
# fn main() {
    let v = Vec::<_>::new();
# }
```

Though written this way it's really no different from `Vec::new()` with full inference. `_` shines when you need to specify the outer type but let Rust infer the inner one.

### When Is It Useful?

When a type has several parameters and you only want to annotate some. The power of `_` grows with the type's complexity — you'll feel it naturally once we meet more standard-library types.

## Example Code

```rust,editable
fn main() {
    // Let Rust infer the Vec's element type with _
    let v: Vec<_> = vec![1, 2, 3];
    println!("{:?}", v);

    // _ works in a turbofish too
    let v2 = Vec::<_>::new(); // Same as Vec::new(); _ lets Rust infer
    let v2: Vec<i32> = v2;    // The type gets pinned down by later usage
    println!("{:?}", v2);

    // Comparison: no annotation at all vs partial annotation with _
    let a = vec![true, false]; // Rust infers everything: Vec<bool>
    let b: Vec<_> = vec![true, false]; // Tell Rust it's a Vec; element type inferred
    println!("{:?}", a);
    println!("{:?}", b);
}
```

## Recap

- `_` can stand in as a placeholder in type annotations, letting Rust infer that position's type.
- Good for "I know the outer type; let Rust infer the inner one."
- Both turbofish and `let` annotations can use `_`.
