# Default Parameters

## Goal of This Episode

Learn to set default values for generic parameters and `const` generics.

## Concept

### Default Type Parameters in Generics

Sometimes a generic parameter is "almost always the same value." Rust lets you give it a default — leave it unspecified and the default applies.

Take the standard library's `PartialEq` as an example:

```rust,noplayground
trait PartialEq<Rhs = Self> {
    fn eq(&self, other: &Rhs) -> bool;
}
#
# fn main() {}
```

`Rhs = Self` means: if you don't specify `Rhs`, it defaults to `Self`. So `impl PartialEq for Point` is the same as `impl PartialEq<Point> for Point` — by default, you compare against your own type.

If you occasionally want to compare against a different type, just override it:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl PartialEq<(i32, i32)> for Point {
    fn eq(&self, other: &(i32, i32)) -> bool {
        self.x == other.0 && self.y == other.1
    }
}
#
# fn main() {}
```

### Defining Your Own

Use `=` in the generic definition to give a default:

```rust,noplayground
struct Container<T = String> {
    value: T,
}

fn main() {
    let c: Container = Container { value: String::from("hello") }; // T defaults to String
    let c2: Container<i32> = Container { value: 42 };              // specified manually
}
```

### Defaults for `const` generics

```rust,noplayground
struct Buffer<const N: usize = 1024> {
    data: [u8; N],
}

fn main() {
    let buf: Buffer = Buffer { data: [0; 1024] };     // N defaults to 1024
    let small: Buffer<64> = Buffer { data: [0; 64] }; // specified manually
}
```

### Parameters with Defaults Must Come Last

```rust,noplayground
struct Pair<T, U = T> { // OK: U has a default and comes after T
    first: T,
    second: U,
}
#
# fn main() {}
```

## Example Code

```rust,editable
struct Pair<T, U = T> {
    first: T,
    second: U,
}

impl<T: std::fmt::Debug, U: std::fmt::Debug> Pair<T, U> {
    fn show(&self) {
        println!("({:?}, {:?})", self.first, self.second);
    }
}

fn main() {
    // U uses the default (= T = i32)
    let p1: Pair<i32> = Pair { first: 1, second: 2 };
    p1.show();

    // specify U manually
    let p2: Pair<i32, &str> = Pair { first: 42, second: "hello" };
    p2.show();
}
```

## Recap

- Generic parameters can have defaults: `<T = String>`, `<Rhs = Self>`.
- So can `const` generics: `<const N: usize = 1024>`.
- Leave it out and the default applies; specify it and it's overridden.
- `PartialEq<Rhs = Self>` is the standard library's classic example.
- Parameters with defaults must come after parameters without them.
