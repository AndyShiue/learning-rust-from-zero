# `use`

## Goal of This Episode

Learn to simplify paths with `use`, and understand Rust's path-resolution rules and the various import styles.

## Concept

We've had a first taste of `use` before; here we lay out all its usages and the path rules in full.

### Why `use` Is Needed

Writing the full path at every call site gets tiring:

```rust,ignore
# fn main() {
    let sum = crate::math::basic::add(1, 2);
    let diff = crate::math::basic::subtract(5, 3);
# }
```

Bring the path in with `use`, and short names work from then on:

```rust,ignore
use crate::math::basic::add;
use crate::math::basic::subtract;

fn main() {
    let sum = add(1, 2);
    let diff = subtract(5, 3);
}
```

### Absolute vs Relative Paths

Rust paths have two starting points:

**Absolute paths** — starting from the `crate` root:

```rust,ignore
use crate::math::add; // The math mod within this very crate
```

**Relative paths** — starting from the current `mod`'s position:

```rust,ignore
use math::add; // The math sub-mod under the current mod
```

### Paths for External `crate`s

After adding an external `crate` in `Cargo.toml`, use the `crate`'s name as the path's head:

```rust,ignore
use std::collections::HashMap;
use rand::Rng;
#
# fn main() {}
```

`std` is Rust's **standard library** — a built-in toolkit including the `Vec`, `String`, `Option`, `Result`, `println!` we've already used, plus much more: file operations, networking, collections, and so on. No Cargo.toml dependency is needed, since every Rust program links `std` automatically. Its paths read like an external `crate`'s — `std::collections::HashMap`, `std::fmt::Display`, etc. And not only is `std` linked automatically — `std`'s **prelude** is imported automatically too, meaning the most common types and `trait`s (`Vec`, `String`, `Option`, `Result`, `Clone`, `Copy`...) work with no `use` at all. That's why the early chapters never needed `use`.

To emphasize "this is an external `crate`" explicitly, start with `::`:

```rust,ignore,mdbook-runnable
use ::rand::Rng;  // Explicitly: rand is an external crate, not a local mod
#
# fn main() {}
```

Especially useful when your own `crate` also has a `mod` named `rand` — it removes the ambiguity.

### super:: and self::

- `super::`: one level up, to the **parent `mod`**.
- `self::`: the **current `mod`** (usually omitted, but occasionally useful within `use`).

```rust,noplayground
mod outer {
    pub fn greet() -> String {
        String::from("Hello from outer")
    }

    pub mod inner {
        pub fn call_parent() -> String {
            super::greet() // Calling the parent mod's greet
        }
    }
}
#
# fn main() {}
```

### `use`-ing Several Things at Once

Importing several items under one path can be merged with braces:

```rust,noplayground
use std::io::{self, Read, Write};
// Equivalent to:
// use std::io;
// use std::io::Read;
// use std::io::Write;
#
# fn main() {}
```

`self` here stands for `std::io` itself — so you've imported the `io` `mod` along with the `Read` and `Write` inside it.

### `use` ... `as` (Aliases)

When two different places have same-named things, alias with `as`:

```rust,noplayground
use std::fmt::Result as FmtResult;
use std::io::Result as IoResult;

fn format_something() -> FmtResult {
    Ok(())
}

fn read_something() -> IoResult<()> {
    Ok(())
}
#
# fn main() {}
```

### Name Collisions with `use`

`use`-ing two same-named things into one scope makes Rust error outright:

```rust,compile_fail
mod a {
    pub fn hello() -> &'static str { "from a" }
}

mod b {
    pub fn hello() -> &'static str { "from b" }
}

use a::hello;
use b::hello; // Compile error! hello is already defined
```

That's when `as` aliases save the day.

But across **different scopes**, an inner `use` shadows the outer — just like `let` shadowing:

```rust,editable
mod a {
    pub fn hello() -> &'static str { "from a" }
}

mod b {
    pub fn hello() -> &'static str { "from b" }
}

use a::hello;

fn main() {
    println!("{}", hello());     // "from a"

    {
        use b::hello;            // Shadows the outer hello within this scope
        println!("{}", hello()); // "from b"
    }

    println!("{}", hello());     // "from a" (back to the outer)
}
```

### Glob Imports (the Asterisk)

`*` brings in everything `pub` under a `mod`:

```rust,noplayground
use std::collections::*; // HashMap, HashSet, BTreeMap... all available
#
# fn main() {}
```

**Generally not recommended** in production code — it's unclear what came in, inviting collisions. But it's very common in **tests** — `use super::*;` brings everything from the parent `mod` into the test `mod`. Next episode covers `cargo test`, where you'll see this in action.

### `use`-ing `enum` Variants

`use` isn't just for things under a `mod` — `enum` variants can be imported too:

```rust,noplayground
use std::cmp::Ordering::{Less, Equal, Greater};

fn compare(a: i32, b: i32) {
    match a.cmp(&b) {
        Less => println!("Less than"),
        Equal => println!("Equal"),
        Greater => println!("Greater than"),
    }
}
#
# fn main() {}
```

No writing `Ordering::Less` every time — plain `Less` suffices. Especially handy when a `match` has many variants.

## Example Code

```rust,editable
mod math {
    pub mod basic {
        pub fn add(a: i32, b: i32) -> i32 {
            a + b
        }

        pub fn subtract(a: i32, b: i32) -> i32 {
            a - b
        }
    }

    pub mod advanced {
        pub fn power(base: i32, exp: u32) -> i32 {
            let mut result = 1;
            for _ in 0..exp {
                result *= base;
            }
            result
        }

        pub fn factorial(n: u64) -> u64 {
            let mut result: u64 = 1;
            for i in 1..=n {
                result *= i;
            }
            result
        }
    }
}

// The various flavors of use
use math::basic::add;
use math::basic::subtract;
use math::advanced::{power, factorial};

fn main() {
    println!("3 + 5 = {}", add(3, 5));
    println!("10 - 4 = {}", subtract(10, 4));
    println!("2 ^ 10 = {}", power(2, 10));
    println!("10! = {}", factorial(10));
}
```

## Recap

- `use` brings a path into scope, sparing you the full path each time.
- Absolute paths start with `crate::`; relative paths start from the current `mod`.
- External `crate`s start with their name; a `::` prefix marks one explicitly as external.
- `std` is the standard library — usable without a dependency; the prelude lives there too.
- `super::` points to the parent `mod`; `self::` to the current one.
- `use a::b::{self, X, Y};` imports several things at once.
- `use X as Alias;` aliases, resolving name collisions.
- Same-scope same-name `use`s error; different scopes shadow (inner over outer).
- `use something::*;` — the glob import: common in tests, rare in production code.
- `enum` variants can be `use`d too.
