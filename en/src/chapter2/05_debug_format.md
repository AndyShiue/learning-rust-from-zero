# `{:?}` and the `Debug` Format

## Goal of This Episode

Use `{:?}` to print tuples and other things that "can't be printed with `{}`."

## Main Text

So far we've printed everything with `{}`:

```rust,editable
fn main() {
    let x = 42;
    println!("{}", x); // ✅ 42
}
```

Numbers, `bool`s, and other basic types work fine with `{}`. But try printing a tuple with `{}`:

```rust,compile_fail
fn main() {
    let t = (1, 2, 3);
    println!("{}", t); // ❌ Compile error!
}
```

The compiler spits out a pile of error messages. In short: "This type doesn't implement `Display` — I don't know how to print it in a 'nice-looking way.'"

### The Fix: Use `{:?}`

```rust,editable
fn main() {
    let t = (1, 2, 3);
    println!("{:?}", t); // ✅ (1, 2, 3)
}
```

`{:?}` is the **`Debug` format**. It's not a "pretty format" for end users — it's a "debugging format" for developers.

### `Display` `{}` vs `Debug` `{:?}`

For simple types like numbers and `bool`s, `{}` and `{:?}` print the same thing. So what's the point of `{:?}`?

**It can print things `{}` can't — like tuples.** Tuples only have a `Debug` format, not a `Display` format.

### The Pretty Version: `{:#?}`

If the data is complex (say, tuples nested in tuples), you can use `{:#?}` to print a "prettified `Debug` format":

```rust,editable
fn main() {
    let data = ((1, 2), (3, 4), (5, 6));
    println!("{:#?}", data);
}
```

### A Handy Trick: the `dbg!` Macro

Rust also has a very convenient debugging tool, `dbg!`:

```rust,noplayground
fn main() {
    let x = 5;
    dbg!(x);
    dbg!(x + 1);
}
```

It prints the file name, the line and column, and the value — super convenient:

```ignore
[src/main.rs:3:5] x = 5
[src/main.rs:4:5] x + 1 = 6
```

## Recap

- `{}` is the `Display` format, meant for end users, but not every type supports it.
- `{:?}` is the `Debug` format, meant for developers; compound types like tuples support it.
- `{:#?}` is the prettified `Debug` format — clearer for complex data.
- `dbg!` is a great helper for quick debugging; it prints the file name plus the line and column.
