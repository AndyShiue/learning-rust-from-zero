# `extern crate`

## Goal of This Episode

Understand the difference between `extern crate` and `use`, and why some examples in this tutorial still contain `extern crate`.

> This episode supplements **Chapter 7**.

## Main Text

Chapter 7 introduced adding external `crate`s with Cargo. For example, to use `rand`, first run:

```bash
cargo add rand
```

Cargo adds `rand` to `Cargo.toml`. In newer Rust editions, that is enough to use it directly in your program:

```rust,noplayground
# extern crate rand;
#
use rand::RngExt;

fn main() {
    let mut rng = rand::rng();
    let n = rng.random_range(1..=100);
    println!("{}", n);
}
```

An ordinary Cargo project does not need an additional `extern crate rand;` line.

### What Does `extern crate` Do?

`extern crate` explicitly tells the compiler to load an external `crate`:

```rust,ignore
extern crate rand;
```

It does not download or install `rand`, however, and it cannot replace the dependency in `Cargo.toml`. Cargo or another build tool must still make the external `crate` available first.

### Aliasing an External `crate` with `as`

`extern crate` can also give the external `crate` a name to use in the current scope:

```rust,ignore
extern crate rand as random;
```

The general form is:

```rust,ignore
extern crate a as b;
```

Here:

- `a` is the name of the external `crate`.
- `b` is the name introduced into the current scope by this declaration.

For example, after aliasing `rand` as `random`, you can use it through the name `random`:

```rust,editable
extern crate rand as random;

use random::RngExt;

fn main() {
    let mut rng = random::rng();
    let n = rng.random_range(1..=100);
    println!("{}", n);
}
```

In an ordinary Cargo project using a newer Rust edition, however, if you only want an alias, you can usually use the `use ... as ...` syntax introduced in Chapter 7:

```rust,ignore
use rand as random;
```

The difference is that `extern crate rand as random;` explicitly loads the external `crate` and introduces the name `random`, while `use rand as random;` aliases a `crate` that is already available.

### `extern crate` Is Not the Same as `use`

These two lines do different jobs:

```rust,ignore
extern crate rand;

use rand::RngExt;
```

- `extern crate rand;` explicitly loads the external `crate` named `rand`.
- `use rand::RngExt;` brings the `RngExt` `trait` from `rand` into the current scope.

In other words, `extern crate` deals with the external `crate` itself, while `use` deals with how names are used in the program.

### Why Does This Tutorial Still Use It?

You may already have seen this in the tutorial's examples:

```rust,ignore
extern crate rand;
```

That does not mean ordinary Cargo projects written with newer Rust editions still require it. **This tutorial includes `extern crate` so that its internal tests pass.**

The tutorial uses `mdbook test` to compile and test the Rust code in the book automatically. Before running the tests, it compiles the external `crate`s required by the examples, then uses `-L` to tell the test tool where to find the compiled output.

However, `-L` only provides a search path. Unlike Cargo, it does not pass complete information for every dependency. The examples therefore use `extern crate rand;` to tell the compiler explicitly to load `rand`, allowing the internal tests to find and use it.

This is a special requirement of the tutorial's testing setup, not the usual style in newer Rust editions. If you copy an example into your own Cargo project and have already added the dependency with `cargo add rand`, you can usually remove `extern crate rand;`.

## Recap

- `extern crate name;` explicitly tells the compiler to load an external `crate`.
- `extern crate a as b;` explicitly loads external `crate` `a` and introduces it as `b` in the current scope; in newer Rust editions, use `use a as b;` when only an alias is needed.
- `extern crate` does not download a package and cannot replace the dependency in `Cargo.toml`.
- `extern crate` and `use` have different purposes: the former deals with an external `crate`, while the latter brings names into scope.
- Ordinary Cargo projects using newer Rust editions usually do not need `extern crate`.
- This tutorial includes `extern crate` so that its internal tests using `mdbook test -L` can find external `crate`s.
