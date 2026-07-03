# `From<T>` / `Into<T>`

## Goal of This Episode

Learn type conversion with the standard library's `From` and `Into` traits, and understand the "implement `From`, get `Into` free" mechanism.

## Concept

Last episode we defined our own `Convert<T>` `trait`. As it happens, Rust's standard library already has a more complete conversion mechanism: `From` and `Into`.

### From

The definition of `From<T>` (simplified):

```rust,noplayground
trait From<T> {
    fn from(value: T) -> Self;
}
#
# fn main() {}
```

It means: "I can be converted from a `T`."

You've certainly seen this:

```rust,noplayground
# fn main() {
    let s = String::from("hello");
# }
```

That's `String` implementing `From<&str>` — converting from `&str` to `String`.

### Into

`Into<T>` is `From` in the opposite direction:

```rust,noplayground
trait Into<T> {
    fn into(self) -> T;
}
#
# fn main() {}
```

The key point: **implement `From`, and you get `Into` automatically.** No need to implement `Into` yourself.

Another blanket implementation — Rust has a rule saying "if `Y: From<X>`, then `X` automatically implements `Into<Y>`."

### `TryFrom` / `TryInto`

Some conversions can fail — say, turning a huge `i64` into an `i32` might overflow. For those, use `TryFrom` and `TryInto`, which return a `Result` instead of a bare value.

As with `From` / `Into`, implementing `TryFrom` grants `TryInto` automatically.

## Example Code

```rust,editable
use std::fmt::Display;
use std::fmt::Formatter;

struct Celsius {
    value: f64,
}

struct Fahrenheit {
    value: f64,
}

impl Display for Celsius {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{}°C", self.value)
    }
}

impl Display for Fahrenheit {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{}°F", self.value)
    }
}

// Implementing From: converting Celsius into Fahrenheit
impl From<Celsius> for Fahrenheit {
    fn from(c: Celsius) -> Fahrenheit {
        Fahrenheit {
            value: c.value * 1.8 + 32.0,
        }
    }
}

fn main() {
    // String::from — what we've used all along
    let s = String::from("hello");
    println!("{}", s);

    // Our custom From
    let boiling = Celsius { value: 100.0 };
    println!("Celsius: {}", boiling);
    let f = Fahrenheit::from(Celsius { value: 100.0 });
    println!("Fahrenheit: {}", f);

    // Into comes free (no separate implementation needed)
    let body_temp = Celsius { value: 37.0 };
    let f2: Fahrenheit = body_temp.into();
    println!("Body temperature: {}", f2);

    // A TryFrom example: i32 to u8 can fail
    let big: i32 = 300;
    let result = u8::try_from(big);
    match result {
        Ok(n) => println!("Conversion succeeded: {}", n),
        Err(e) => println!("Conversion failed: {:?}", e),
    }

    let small: i32 = 42;
    let ok = u8::try_from(small);
    match ok {
        Ok(n) => println!("Conversion succeeded: {}", n),
        Err(e) => println!("Conversion failed: {:?}", e),
    }
}
```

## Recap

- `From<T>` defines "converted from a `T`": `String::from("hello")` is exactly this.
- Implement `From` and `Into` comes automatically — no separate implementation.
- `.into()` is `.from()`'s reverse direction: `let f: Fahrenheit = celsius.into();`.
- `TryFrom` / `TryInto` handle fallible conversions, returning a `Result`.
- Implementing `TryFrom` grants `TryInto` automatically too.
