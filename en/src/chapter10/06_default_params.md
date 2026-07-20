# Default Parameters

## Goal of This Episode

Learn where type parameters and `const` generic parameters can have defaults, and how to define them.

## Concept

### Default Type Parameters

On declarations for `struct`s, `enum`s, `union`s, type aliases, and `trait`s, a type parameter that is almost always the same type can have a default. When that argument is omitted while using the type or `trait`, the default applies. Generic parameters on functions and methods cannot have defaults.

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

`const` generic parameters can also have defaults on the same kinds of type and `trait` declarations. They cannot have defaults on functions or methods either.

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

- Type parameters can have defaults on `struct`, `enum`, `union`, type alias, and `trait` declarations.
- `const` generic parameters can have defaults in the same places.
- Function and method generic parameters cannot have defaults.
- The syntax is `<T = String>`, `<Rhs = Self>`, or `<const N: usize = 1024>`.
- Leave it out and the default applies; specify it and it's overridden.
- `PartialEq<Rhs = Self>` is the standard library's classic example.
- Parameters with defaults must come after parameters without them.
