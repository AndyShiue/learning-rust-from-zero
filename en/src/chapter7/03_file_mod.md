# File `mod`s

## Goal of This Episode

Learn to split `mod`s into separate files, and understand Rust's file-to-`mod` correspondence rules.

## Concept

Last episode we wrote `mod`s inside one file, but real projects can't stuff everything together. Rust provides rules for splitting `mod`s into standalone files.

### The Basic Split: `mod` + a Standalone File

Suppose you have a `math` `mod` and want to move it into its own file. The recipe is simple:

1. In `main.rs` (or `lib.rs`) write `mod math;` (note the trailing semicolon, not braces).
2. Create `math.rs` and put the `mod`'s contents in it.

```ignore
src/
├── main.rs
└── math.rs
```

**main.rs:**

```rust,ignore
mod math;

fn main() {
    let result = math::add(3, 5);
    println!("3 + 5 = {}", result);
}
```

**math.rs:**

```rust,ignore
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

pub fn subtract(a: i32, b: i32) -> i32 {
    a - b
}
```

Note that inside `math.rs` you **don't write `mod math { ... }` again** — the file itself is that `mod`.

### Folder Structures for Sub-`mod`s

If the `math` `mod` has sub-`mod`s of its own, there are two ways to organize:

**Way 1: with `mod.rs` (the traditional style)**

```ignore
src/
├── main.rs
└── math/
    ├── mod.rs
    ├── basic.rs
    └── advanced.rs
```

`math/mod.rs` is the `math` `mod`'s entry point, declaring the sub-`mod`s:

```rust,ignore
// math/mod.rs
pub mod basic;
pub mod advanced;
```

**Way 2: a same-named file + folder (recommended)**

```ignore
src/
├── main.rs
├── math.rs          ← The math mod's entry point
└── math/
    ├── basic.rs
    └── advanced.rs
```

```rust,ignore
// math.rs
pub mod basic;
pub mod advanced;
```

Both ways work identically — pick whichever you like. Newer projects lean toward Way 2, avoiding a pile of files all named `mod.rs` that are hard to tell apart in an editor.

### `lib.rs` vs `main.rs`

A Rust project can contain one or more `crate`s. A `crate` comes in two types:

- **binary `crate`**: has `src/main.rs`, compiling to an executable.
- **library `crate`**: has `src/lib.rs`, a library for others to use.

One project can contain **both** `main.rs` and `lib.rs`. `main.rs` is the binary `crate`'s root; `lib.rs` is the library `crate`'s root.

```ignore
src/
├── main.rs    ← binary crate root
├── lib.rs     ← library crate root
├── math.rs
└── math/
    ├── basic.rs
    └── advanced.rs
```

Inside `main.rs`, refer to things in `lib.rs` via the `crate`'s name:

```rust,ignore
// main.rs
// Assuming Cargo.toml's [package] name = "my_project"
use my_project::math;

fn main() {
    let result = math::basic::add(1, 2);
    println!("{}", result);
}
```

## Example Code

Since file `mod`s span multiple files, a single-file demo isn't possible. Below is a complete multi-file example — create the corresponding file structure and run it with `cargo run`:

```ignore
src/
├── main.rs
├── math.rs
└── math/
    ├── basic.rs
    └── advanced.rs
```

**main.rs:**

```rust,ignore
mod math;

fn main() {
    let sum = math::basic::add(10, 20);
    println!("10 + 20 = {}", sum);

    let p = math::advanced::power(2, 8);
    println!("2 ^ 8 = {}", p);
}
```

**math.rs:**

```rust,ignore
pub mod basic;
pub mod advanced;
```

**math/basic.rs:**

```rust,ignore
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

**math/advanced.rs:**

```rust,ignore
pub fn power(base: i32, exp: u32) -> i32 {
    let mut result = 1;
    for _ in 0..exp {
        result *= base;
    }
    result
}
```

## Recap

- `mod math;` (semicolon-terminated) tells Rust to go find the sub-`mod`.
- The split-out file **doesn't** contain another `mod math { ... }` — the file itself is the `mod`.
- Sub-`mod`s can use `math/mod.rs` (traditional) or `math.rs` + a `math/` folder (recommended).
- `main.rs` is the binary `crate`'s root; `lib.rs` is the library `crate`'s root.
- One project can contain a binary `crate` and a library `crate` at the same time.
