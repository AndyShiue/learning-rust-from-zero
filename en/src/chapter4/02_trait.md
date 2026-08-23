# A Brief Introduction to `trait`s

## Goal of This Episode

Learn to define a `trait` and implement it for a type, and meet `#[derive]`, the shortcut that auto-generates implementations.

## Concept

### What Is a `trait`?

Before we get into ownership proper, let's learn an important tool: the **`trait`**. It has no direct connection to last episode's keychain analogy, but we'll need it when discussing `Clone`, `Copy`, and friends — so let's pick it up first.

In Chapter 3 we learned to add methods to `struct`s and `enum`s with `impl`. But what if we want to require that "certain types must all have a certain capability"?

Say I want to require: "these types must all be able to say hello." That's what a **`trait`** is for — it defines a set of "capabilities" or "behaviors," and different types can each implement those behaviors in their own way.

A `trait` is like a "spec sheet" that says: "To meet this spec, you must provide these features."

### Defining a `trait`

Use the `trait` keyword:

```rust,noplayground
trait Greet {
    fn greet(self);
}
#
# fn main() {}
```

This code means: "Any type that implements the `Greet` `trait` must have a `greet` method."

### Implementing a `trait` for a Type

```rust,noplayground
# trait Greet {
#     fn greet(self);
# }
#
# struct Cat;
#
impl Greet for Cat {
    fn greet(self) {
        println!("Meow~");
    }
}
#
# fn main() {}
```

Earlier we wrote `impl Cat { ... }` to add methods to `Cat` directly. Now, `impl Greet for Cat { ... }` says "`Cat` meets the `Greet` spec," and inside we provide the methods `Greet` demands.

### `derive`: The Shortcut That Auto-generates Implementations

Some `trait`s have very formulaic implementations that the Rust compiler can generate for you. That's when you use `#[derive(...)]`:

```rust,noplayground
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}
#
# fn main() {}
```

Remember using `{:?}` to print tuples and arrays in Chapter 2? That `{:?}` is actually using the `Debug` `trait`. Tuples and arrays come with `Debug` built in, but the `struct`s and `enum`s we define ourselves don't — so we add `#[derive(Debug)]` to have Rust generate the `Debug` implementation automatically.

## Example Code

```rust,editable
// Define a trait: every implementer must be able to "say hello"
trait Greet {
    fn greet(self);
}

// Define two kinds of animals
struct Cat;
struct Dog;

// Implement Greet for Cat
impl Greet for Cat {
    fn greet(self) {
        println!("I'm a cat, meow~");
    }
}

// Implement Greet for Dog
impl Greet for Dog {
    fn greet(self) {
        println!("I'm a dog, woof!");
    }
}

// Use derive to have Rust auto-generate a Debug implementation
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let cat = Cat;
    let dog = Dog;

    // Calling the trait methods
    cat.greet();
    dog.greet();

    // Printing the struct with {:?} (thanks to #[derive(Debug)])
    let p = Point { x: 3, y: 7 };
    println!("{:?}", p);
}
```

## Recap

- A **`trait`** is a spec defining a set of behaviors — like a "capability checklist."
- Implement a `trait` for a type with `impl TraitName for TypeName` (e.g. `impl Greet for Cat`).
- `#[derive(Debug)]` has Rust automatically implement the `Debug` `trait` for your `struct` / `enum`.
- With `#[derive(Debug)]` added, `{:?}` can print your custom `struct` / `enum`.
