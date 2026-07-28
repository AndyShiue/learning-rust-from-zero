# `struct` Update Syntax

## Goal of This Episode

Learn to build a new `struct` instance quickly from an existing one with the `..` syntax, and understand how `Copy` fields differ from moved fields.

> This episode supplements **Chapter 3**.

## Concept

Remember writing out every field when creating a `struct`? If you only want one or two fields changed with the rest as-is, spelling everything out each time is tedious. Rust provides **`struct` update syntax** — `..` "fills in the remaining fields."

### Basic Syntax

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
#     let p1 = Point { x: 0, y: 100 };
    let p2 = Point { x: 10, ..p1 };
# }
```

Meaning: `p2`'s `x` becomes `10`, and the remaining fields move over from `p1`.

`..p1` must go last, preceded by a comma (when other fields come before it).

### The copy vs move Difference

An important detail here. `..p1` is not "`clone` the whole `struct`" — it works **field by field**:

- Fields whose type implements `Copy` (like `i32`, `f64`, `bool`) get **copied**.
- Fields whose type **lacks** `Copy` (like `String`) get **moved**.

Meaning: if `..p1` moves some of `p1`'s non-`Copy` fields, those fields can no longer be accessed through `p1` afterward.

### Pairing with `Default`

If your `struct` implements the `Default` `trait`, `..` paired with its `default()` builds an instance "specifying just a few fields, defaults for the rest":

```rust,noplayground
# #[derive(Default)]
# struct Config {
#     debug: bool,
#     id: i32,
# }
#
# fn main() {
    let config = Config { debug: true, ..Config::default() };
# }
```

Especially nice for `struct`s with many fields.

## Example Code

```rust,editable
#[derive(Debug)]
struct Config {
    width: u32,
    height: u32,
    fullscreen: bool,
    title: String,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            width: 800,
            height: 600,
            fullscreen: false,
            title: String::from("My App"),
        }
    }
}

#[derive(Debug, Clone, Copy)]
struct Point {
    x: f64,
    y: f64,
}

fn main() {
    // Basic usage: changing just one field
    let p1 = Point { x: 1.0, y: 2.0 };
    let p2 = Point { x: 10.0, ..p1 };
    println!("p1 = {:?}", p1); // p1 still works, since f64 is Copy
    println!("p2 = {:?}", p2);

    // With Default: specifying only the fields you want changed
    let custom = Config {
        width: 1920,
        height: 1080,
        ..Config::default()
    };
    println!("Custom settings: {:?}", custom);

    // All defaults
    let default_config = Config { ..Config::default() };
    println!("Default settings: {:?}", default_config);

    // Watch the move semantics!
    let c1 = Config {
        width: 1024,
        height: 768,
        fullscreen: true,
        title: String::from("Game"),
    };
    let c2 = Config {
        fullscreen: false,
        ..c1 // title (String) gets moved!
    };
    // println!("{}", c1.title); // Compile error! title has been moved
    println!("c1.width = {}", c1.width);  // But the Copy fields remain usable
    println!("c2 = {:?}", c2);
}
```

## Recap

- `let p2 = Point { x: 1, ..p1 };` fills `p2`'s remaining fields from `p1`.
- `..source` must come last.
- `Copy`-typed fields are copied; non-`Copy` fields are moved.
- If every field is `Copy`, the original `struct` stays usable.
- If a non-`Copy` field was moved, that field of the original `struct` is off-limits.
- `..Config::default()` suits "mostly defaults, a few changes" nicely.
