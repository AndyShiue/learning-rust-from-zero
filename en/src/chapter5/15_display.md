# The `Display` `trait`

## Goal of This Episode

Learn to implement the `Display` `trait` for custom types, the difference between `Display` and `Debug`, and the relationship between `Display` and `ToString`.

## Concept

In Chapter 2 we learned `{:?}` for printing tuples, arrays, and `struct`s with `#[derive(Debug)]`. But `{:?}` is the developer-facing "`Debug` format." To print a custom type with `{}`, you need to implement the `Display` `trait`.

### `Display` vs `Debug`

- **`Debug`** (`{:?}`): a format for developers, auto-generated with `#[derive(Debug)]`.
- **`Display`** (`{}`): a format for end users, which **must be implemented by hand** — it can't be `derive`d.

Why keep them separate? Developers need to see all the fields and type information (the `Debug` format), while users just need readable text. Different needs, so one `trait` can't serve both.

### Implementing `Display`

```rust,noplayground
use std::fmt::Display;
use std::fmt::Formatter;
use std::fmt::Result;
#
# struct Point {
#     x: i32,
#     y: i32,
# }

impl Display for Point {
    fn fmt(&self, f: &mut Formatter) -> Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}
#
# fn main() {}
```

The `fmt` method receives a `&mut Formatter`, and you write your desired format into it with the `write!` macro. `write!` works almost exactly like `println!`, except its first argument is the `&mut Formatter`.

### The Relationship between `Display` and `ToString`

Rust has a `ToString` `trait` with just one method:

```rust,ignore
fn to_string(&self) -> String;
```

Here's the point — **you never implement `ToString` yourself**. The standard library contains this code:

```rust,ignore
impl<T: Display> ToString for T {
    fn to_string(&self) -> String {
        // Internally uses Display's fmt method to produce the string
        // ...
    }
}
```

It means: "For **every** type `T` that implements `Display`, automatically implement `ToString`." This is called a **blanket implementation** — like a blanket, covering every qualifying type.

So implement `Display`, and your type automatically gains the `.to_string()` method — nothing extra to do.

## Example Code

```rust,editable
use std::fmt::Display;
use std::fmt::Formatter;

#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

// Implementing Display by hand
impl Display for Point {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

#[derive(Debug)]
struct Color {
    r: u8,
    g: u8,
    b: u8,
}

impl Display for Color {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "R{}G{}B{}", self.r, self.g, self.b)
    }
}

fn main() {
    let p = Point { x: 3, y: 7 };

    // The Debug format (for developers)
    println!("Debug: {:?}", p);

    // The Display format (for users)
    println!("Display: {}", p);

    // Display grants .to_string() automatically
    let s = p.to_string();
    println!("to_string: {}", s);

    let c = Color { r: 255, g: 128, b: 0 };
    println!("Debug: {:?}", c);
    println!("Display: {}", c);
    println!("to_string: {}", c.to_string());
}
```

## Recap

- The `Display` `trait` lets your type print with the `{}` format.
- `Debug` (`{:?}`) is for developers and can be `derive`d; `Display` (`{}`) is for users and must be hand-implemented.
- How: `impl Display for MyType`, writing the format with `write!` inside `fmt`.
- Implementing `Display` grants `.to_string()` automatically (a blanket implementation).
