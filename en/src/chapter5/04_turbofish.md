# The Turbofish Syntax

## Goal of This Episode

Learn to specify type parameters manually with the `::<>` turbofish syntax, and understand its relationship to generic definitions.

## Concept

Over the past few episodes we've learned generics — functions, `struct`s, and `enum`s can all take type parameters `<T>`. Most of the time Rust infers what `T` is, but sometimes the compiler can't work it out, and we must tell it ourselves.

### What's a Turbofish?

Remember writing this back in Chapter 1 when learning `parse`?

```rust,editable
fn main() {
    let input = "1";
    let num = input.trim().parse::<i32>().expect("Please enter a number");
}
```

Back then we copied `::<i32>` as a black box. Now, with generics learned, we can finally understand it!

`.parse()` is a generic method with a type parameter `T`, meaning "what type you want to turn the string into." But from `input.trim().parse()` alone, the compiler can't tell whether you want an `i32`, an `f64`, or something else.

So we manually specify `T = i32` with `::<i32>`. This `::<>` syntax is called the **turbofish** (because `::<>` looks like a fish 🐟).

### The Essence of the Turbofish

The turbofish is "manually filling in the type parameters declared in the generic definition's angle brackets":

- Generic definition: `fn parse<T>(...)` — the `<T>` here is the declaration.
- Turbofish: `.parse::<i32>()` — the `::<i32>` here fills it in.

Functions, methods, and types can all take a turbofish:

```rust,ignore
// Turbofish on a function
func::<i32>(arg);

// Turbofish on a type
Vec::<i32>::new();
```

### What Does `.parse()` Do?

While we're at it, the full story on `parse`: it converts a string into the type you specify. The conversion can fail (e.g. `"abc"` can't become a number), so it pairs with `.expect()` to handle failure — as we did back in Chapter 1.

## Example Code

```rust,editable
fn first<T>(a: T, _b: T) -> T {
    a
}

fn main() {
    // Usually Rust infers on its own; no turbofish needed
    let x = first(10, 20);
    println!("{}", x);

    // Manually specifying the type with a turbofish
    let y = first::<f64>(3.14, 2.71);
    println!("{}", y);

    // Turbofish on Vec
    let v = Vec::<i32>::new();
    println!("{:?}", v);

    // Turbofish on parse — echoing Chapter 1's black box
    let input = "42";
    let num = input.parse::<i32>().expect("Not a number");
    println!("{}", num);

    let pi = "3.14".parse::<f64>().expect("Not a number");
    println!("{}", pi);
}
```

## Recap

- The **turbofish** `::<>` is the syntax for specifying generic type parameters manually.
- Most of the time Rust infers automatically and no turbofish is needed.
- When the compiler can't infer the type (e.g. `.parse()`), use the turbofish.
- Chapter 1's `.parse::<i32>()` was a turbofish all along — now we understand why it's written that way.
- `.parse()` converts a string into the given type; conversion can fail, hence the `.expect()`.
