# Supertraits

## Goal of This Episode

Learn to define dependencies between `trait`s with supertraits, and understand the design reasoning behind `Copy: Clone` and `DerefMut: Deref`.

## Concept

Sometimes one `trait` needs to build on top of another.

### Supertrait Syntax

```rust,noplayground
trait Summarize: std::fmt::Display {
    fn summary(&self) -> String;
}
#
# fn main() {}
```

`Summarize: Display` means: "To implement `Summarize`, you must first implement `Display`." `Display` is `Summarize`'s **supertrait**; conversely, `Summarize` is `Display`'s **subtrait**.

The benefit: inside `Summarize`'s default implementations, or in user code, you can rely on `self` implementing `Display`.

Note: **implementing `Summarize` does not implement `Display` for you automatically**. You must implement `Display` by hand before you can implement `Summarize`. A supertrait is a "prerequisite," not a "free bonus."

### `Copy: Clone`

Chapter 4 covered `Copy` and `Clone`. The relationship between them is exactly a supertrait:

```rust,noplayground
trait Copy: Clone { }
#
# fn main() {}
```

This says: **to implement `Copy`, you must first implement `Clone`.**

Why? Because `Copy` is an "automatic copying" ability, while `Clone` is "manual cloning." Logically, if you can copy automatically, you can surely clone manually. So `Copy` demands `Clone` as its prerequisite.

That's why `#[derive(Copy, Clone)]` lists both — writing only `derive(Copy)` errors, since `Copy` requires `Clone`.

### `DerefMut: Deref`

Episode 23's `DerefMut` follows the same reasoning — `DerefMut`'s supertrait is `Deref`. To dereference mutably, you must first be able to dereference immutably. So any type implementing `DerefMut` necessarily implements `Deref` too.

## Example Code

```rust,editable
use std::fmt::Display;
use std::fmt::Formatter;

// Defining a supertrait: Summarize requires Display
trait Summarize: Display {
    fn summary(&self) -> String {
        // Display is required by the supertrait bound,
        // so Rust also provides .to_string() through ToString
        let full = self.to_string();
        // Collect the chars into a Vec so we measure length in characters
        // (.len() on a string counts bytes)
        let mut chars = Vec::new();
        for c in full.chars() {
            chars.push(c);
        }
        if chars.len() > 10 {
            let mut s = String::new();
            // Take the first 10 characters
            for c in &chars[..10] {
                s.push(*c);
            }
            s.push_str("...");
            s
        } else {
            full
        }
    }
}

struct Article {
    title: String,
    content: String,
}

// Display (the supertrait) must be implemented first
impl Display for Article {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{}: {}", self.title, self.content)
    }
}

// Only then can Summarize be implemented
impl Summarize for Article {}

// Demonstrating Copy: Clone
#[derive(Debug, Clone, Copy)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let article = Article {
        title: String::from("Rust"),
        content: String::from("A wonderful programming language, well worth learning"),
    };

    // Using Display (the supertrait)
    println!("Full: {}", article);

    // Using Summarize's default implementation:
    // .to_string() comes from ToString, made available by Display
    println!("Summary: {}", article.summary());

    // Demonstrating that Copy requires Clone
    let p = Point { x: 1, y: 2 };
    let p2 = p; // copy (automatic)
    let p3 = p.clone(); // clone (manual) works too
    println!("{:?} {:?} {:?}", p, p2, p3);
}
```

## Recap

- `trait A: B` means "implementing `A` requires implementing `B` first" — `B` is `A`'s supertrait, `A` is `B`'s subtrait.
- `Copy: Clone` — `Copy` requires `Clone`, hence both must appear in the `derive`.
- `DerefMut: Deref` — mutable dereferencing presupposes immutable dereferencing.
- Implementing a subtrait doesn't auto-implement the supertrait — you must write `impl Supertrait` yourself first.
- A subtrait's default implementations may rely on capabilities guaranteed by the supertrait.
