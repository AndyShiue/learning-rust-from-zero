# Cargo and crates.io

## Goal of This Episode

Get to know more of Cargo's features and how to use community `crate`s via crates.io.

## Concept

We've been using `cargo new` and `cargo run` since Chapter 1. Actually, `cargo run` does two things: first it **compiles** your code, then it **runs** the compiled executable. To compile without running, use `cargo build` — it just produces the executable, placed in the `target/debug/` folder.

This episode covers more of Cargo's features, especially bringing in external `crate`s.

### debug build vs release build

`cargo build` and `cargo run` default to **debug mode** — fast to compile but slow to run (no optimizations). When it's time to ship your program, add `--release`:

```bash
cargo build --release
```

This produces an optimized executable, placed in `target/release/` instead of `target/debug/`. The difference can be enormous — some programs run several times faster in release mode.

### Cargo.toml

Every Cargo project's root has a `Cargo.toml`. TOML is a configuration format designed to be easy to read and write.

A typical `Cargo.toml`:

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2024"

[dependencies]
```

- `[package]`: the project's basic information (name, version, Rust edition)
- `[dependencies]`: the external `crate`s this project uses

The `edition` here is a Rust **version number** — not the compiler's version, but the **language specification's version**. Rust publishes a new edition every few years (2015, 2018, 2021, 2024), each possibly adjusting some syntax or default behaviors. `crate`s written using different editions interoperate fine, so compatibility isn't a worry. `cargo new` sets the newest edition for you automatically.

### Adding External `crate`s

Want to use `crate`s others have written? The simplest way:

```bash
cargo add rand
```

This automatically adds a line like the following to `Cargo.toml`'s `[dependencies]`:

```toml
[dependencies]
rand = "0.10"
```

The actual version number depends on the latest release when you run `cargo add` — it may differ from what's written here.

### crates.io

[crates.io](https://crates.io) is Rust's official `crate` registry. You can search for `crate`s, check download counts, and read documentation. Every `crate` page has:

- Usage instructions and version history
- A link to auto-generated documentation on [docs.rs](https://docs.rs).
- Download counts (a rough gauge of popularity).

### Version Semantics for Dependencies

There are several ways to specify a `crate`'s version in `[dependencies]`:

- `"^1.0"` (or simply `"1.0"`): any version compatible with `1.x.y`, but never up to `2.0`.
- `"=1.0.0"`: locked to **exactly** this version.
- `">=1.2, <1.5"`: a range.

Most of the time the default `^` is fine; Cargo picks a suitable version for you. For more detail, see [the official documentation](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html).

### Cargo features

Some `crate`s offer optional functionality, enabled via `features`:

```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] }
```

Now `serde`'s `#[derive(Serialize, Deserialize)]` becomes usable, while unneeded features stay out of the compilation.

## Example Code

Generating random numbers with the `rand` `crate`:

```rust,editable
// First run: cargo add rand
# extern crate rand;

use rand::RngExt;

fn main() {
    let mut rng = rand::rng();

    let n: u32 = rng.random_range(1..=100);
    println!("Random number: {}", n);

    let coin: bool = rng.random();
    if coin {
        println!("Heads!");
    } else {
        println!("Tails!");
    }
}
```

## Recap

- `cargo build --release` produces an optimized executable, suited for shipping.
- `Cargo.toml` uses TOML format; `[package]` holds project info, `[dependencies]` the external `crate`s.
- `edition` is the Rust language specification's version (2015, 2018, 2021, 2024); `crate`s written using different editions interoperate.
- `cargo add <crate>` is the fastest way to add an external `crate`.
- [crates.io](https://crates.io) is Rust's official registry; [docs.rs](https://docs.rs) hosts auto-generated docs.
- The version `"1.0"` equals `"^1.0"`, allowing compatible upgrades; `"=1.0.0"` requires exactly that version.
- `features` switch on a `crate`'s optional functionality.
