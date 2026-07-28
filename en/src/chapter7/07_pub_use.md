# `pub use`

## Goal of This Episode

Learn to re-export internal items with `pub use`, so users never need to know your `mod` structure.

## Concept

Suppose you've written a library whose internals look like:

```ignore
src/
├── lib.rs
├── math.rs
└── math/
    ├── basic.rs
    └── advanced.rs
```

With no further arrangement, users of your library must write:

```rust,ignore
use your_crate::math::basic::add;
use your_crate::math::advanced::power;
```

Cumbersome — users couldn't care less how you divide folders internally; they just want `add` and `power`.

### The Magic of `pub use`

`pub use` "re-exports" internal things into the current `mod`, giving the outside a shorter path:

```rust,ignore
// lib.rs
mod math;

// Re-export, sparing users the math::basic:: path
pub use math::basic::add;
pub use math::advanced::power;
```

Now users of your library need only:

```rust,ignore
use your_crate::add;
use your_crate::power;
```

Much cleaner.

Note: `pub use` can only export **things that were already `pub`**. Attempting to `pub use` a private item makes the compiler complain — you can't publicize what someone else has hidden.

### Re-exporting from Other `crate`s

`pub use` isn't limited to your own `mod`s — it can export things from **other `crate`s** too:

```rust,ignore
// lib.rs
pub use rand::RngExt; // Users just write use your_crate::RngExt — no rand dependency of their own
#
# fn main() {}
```

Common in library design — your library depends on some `crate`, and you want users to reach those types through your `crate` without adding the dependency to their own `Cargo.toml`.

### Layered Re-exports

You can also re-export at intermediate `mod` levels, building a more layered public library:

```rust,ignore
// math.rs
pub mod basic;
pub mod advanced;

// Promote the common functions up to the math level
pub use basic::add;
pub use basic::subtract;
pub use advanced::power;
```

Now the outside can use `your_crate::math::add`, never needing to know about the `basic` layer.

### Real-world Cases

Many famous Rust libraries re-export heavily. When you write `use std::io::Read;`, `Read` may well be defined somewhere deeper — merely re-exported up to `std::io`.

## Example Code

```rust,editable
mod shapes {
    pub mod circle {
        pub struct Circle {
            pub radius: f64,
        }

        impl Circle {
            pub fn new(radius: f64) -> Circle {
                Circle { radius }
            }

            pub fn area(&self) -> f64 {
                std::f64::consts::PI * self.radius * self.radius
            }
        }
    }

    pub mod rectangle {
        pub struct Rectangle {
            pub width: f64,
            pub height: f64,
        }

        impl Rectangle {
            pub fn new(width: f64, height: f64) -> Rectangle {
                Rectangle { width, height }
            }

            pub fn area(&self) -> f64 {
                self.width * self.height
            }
        }
    }

    // Re-exports: users needn't know about the circle and rectangle sub-mods
    pub use circle::Circle;
    pub use rectangle::Rectangle;
}

// Taken straight from shapes; no shapes::circle::Circle needed
use shapes::{Circle, Rectangle};

fn main() {
    let c = Circle::new(5.0);
    println!("Circle area: {}", c.area());

    let r = Rectangle::new(4.0, 6.0);
    println!("Rectangle area: {}", r.area());
}
```

## Recap

- `pub use path::Item;` re-exports internal things, giving the outside a shorter path.
- It can export your own `mod`s' contents, or things from other `crate`s.
- A library's `lib.rs` commonly uses `pub use` to lift important types to the `crate`'s top level.
