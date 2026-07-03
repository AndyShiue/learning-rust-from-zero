# The Orphan Rule

## Goal of This Episode

Understand Rust's orphan rule, and what to do when you want to implement an external `trait` for an external type.

## Concept

In Chapter 5 we learned `trait`s — you can implement any `trait` for your own types. But have you ever tried this:

```rust,compile_fail
use std::fmt;

impl fmt::Display for Vec<i32> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "my vec")
    }
}
#
# fn main() {}
```

The compiler refuses flat out. Why?

### The Orphan Rule

Rust has a rule:

> **To `impl` a `trait`, at least one of the `trait` or the type must be defined in your own crate.**

Put differently: **the `trait` is yours, or the type is yours** — at least one must hold.

In the example above, `Display` is defined by the standard library, and so is `Vec<i32>` — neither is yours, so no.

### Why This Restriction Exists

Imagine there were no orphan rule:

- Crate `A` implements `Display` for `Vec<i32>`, printing `[1, 2, 3]`.
- Crate `B` also implements `Display` for `Vec<i32>`, printing `1 | 2 | 3`.
- Your program uses both `A` and `B`... which should the compiler pick?

That's a conflict. The orphan rule prevents the problem at its root.

### The Legal Cases

All of these are legal:

```rust,noplayground
// Case 1: your type + an external trait
struct MyPoint {
    x: f64,
    y: f64,
}

impl std::fmt::Display for MyPoint {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

// Case 2: an external type + your trait
trait Describable {
    fn describe(&self) -> String;
}

impl Describable for Vec<i32> {
    fn describe(&self) -> String {
        format!("A Vec with {} elements", self.len())
    }
}
#
# fn main() {}
```

### The Newtype Pattern (the Workaround)

If you truly need to implement an external `trait` for an external type, use the **newtype pattern** — a tuple `struct` wrapping the external type:

```rust,noplayground
use std::fmt;

struct MyVec(Vec<i32>);

impl fmt::Display for MyVec {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let items: Vec<String> = self.0.iter()
            .map(|x| x.to_string())
            .collect();
        write!(f, "[{}]", items.join(", "))
    }
}
#
# fn main() {}
```

`MyVec` is a type you defined, so implementing `Display` for it is allowed. `self.0` reaches the inner `Vec<i32>`.

## Example Code

```rust,editable
use std::fmt;

// The newtype pattern: wrapping an external type in your own struct
struct Scores(Vec<i32>);

impl Scores {
    fn new() -> Scores {
        Scores(Vec::new())
    }

    fn add(&mut self, score: i32) {
        self.0.push(score);
    }

    fn total(&self) -> i32 {
        self.0.iter().sum()
    }
}

// Now Display can be implemented for "your type"
impl fmt::Display for Scores {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let items: Vec<String> = self.0.iter()
            .map(|x| x.to_string())
            .collect();
        write!(f, "Scores: [{}], total: {}", items.join(", "), self.total())
    }
}

fn main() {
    let mut scores = Scores::new();
    scores.add(85);
    scores.add(92);
    scores.add(78);
    scores.add(95);

    // With Display implemented, println works directly
    println!("{}", scores);
}
```

## The Multi-parameter `trait` Case

The rule above is the simplest version. For multi-parameter `trait`s (like Chapter 5's `From<T>`), the rules are actually more intricate. In brief:

```rust,ignore
// OK: your type appears among the parameters
impl From<MyType> for String { ... }

// Not allowed: both sides are external
impl From<String> for Vec<i32> { ... }
```

The complete rules involve concepts like "covered type parameters," beyond this tutorial's scope. The curious can consult [the official documentation](https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules).

## Recap

- **The orphan rule**: to `impl` a `trait`, at least one of the `trait` or the type must be defined in your crate.
- "Your type + an external `trait`" ✅ legal.
- "An external type + your `trait`" ✅ legal.
- "An external type + an external `trait`" ❌ illegal.
- The rule exists to prevent `impl` conflicts between crates.
- **The newtype pattern**: wrap the external type in `struct MyWrapper(OriginalType)`, and it becomes your type.
- The orphan rule for multi-parameter `trait`s is far subtler — see the official documentation.
