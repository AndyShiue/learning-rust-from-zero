# Capital `Self`

## Goal of This Episode

Learn to use capital `Self` as an alias for "the type currently being `impl`ed," making code more concise.

## Concept

Last episode we wrote code like this inside an `impl`:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn new(x: i32, y: i32) -> Point {
        Point { x, y }
    }
}
#
# fn main() {}
```

Notice that the name `Point` appears three times: `impl Point`, `-> Point`, `Point { x, y }`. If the type name were long (say `Rectangle`), repeating it would get wordy.

Rust provides capital `Self` (note the capital S!), which inside an `impl` block stands for "the type currently being `impl`ed." So the code above can become:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn new(x: i32, y: i32) -> Self {
        Self { x, y }
    }
}
#
# fn main() {}
```

`Self` is an alias for `Point`. Two benefits:

1. More concise, especially with long type names.
2. If you rename the type later, nothing inside the `impl` needs changing.

**Keep these apart:**

- Lowercase `self`: "this value itself" (a method's first parameter).
- Capital `Self`: "the current type."

## Example Code

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    // Self in place of Point
    fn new(x: i32, y: i32) -> Self {
        Self { x, y }
    }

    fn origin() -> Self {
        Self { x: 0, y: 0 }
    }

    // Self works in methods too
    fn flip(self) -> Self {
        Self { x: self.y, y: self.x }
    }

    fn sum(self) -> i32 {
        self.x + self.y
    }
}

// enums can use Self too
enum Light {
    Red,
    Yellow,
    Green,
}

impl Light {
    fn next(self) -> Self {
        match self {
            Self::Red => Self::Green,
            Self::Green => Self::Yellow,
            Self::Yellow => Self::Red,
        }
    }

    fn is_stop(self) -> bool {
        match self {
            Self::Red => true,
            Self::Yellow => true,
            Self::Green => false,
        }
    }
}

fn main() {
    // A struct using Self
    let p = Point::new(3, 7);
    println!("Original: ({}, {})", p.x, p.y);

    let p2 = Point::new(3, 7);
    let flipped = p2.flip();
    println!("Flipped: ({}, {})", flipped.x, flipped.y);

    let p3 = Point::origin();
    println!("Origin: ({}, {})", p3.x, p3.y);

    // An enum using Self
    let light = Light::Red;
    let stop = light.is_stop();
    println!("Need to stop? {}", stop);

    let light2 = Light::Red;
    let next_light = light2.next();
    let stop2 = next_light.is_stop();
    println!("Does the next light require stopping? {}", stop2);
}
```

## Recap

- Capital `Self` inside an `impl` block stands for "the current type," so it can appear where a type is needed.
- `Self` works in parameter types, return types `-> Self`, construction `Self { ... }`, and `enum` variants `Self::Red`.
- Lowercase `self` = the value itself; capital `Self` = the type itself.
- `Self` works in both `struct` and `enum` `impl`s.
- Using `Self` makes code more concise and easier to maintain.

Congratulations on finishing Chapter 3! 🎉 In this chapter you learned `struct`s, `enum`s, pattern matching (`match`, `if let`, `while let`, `let...else...`), destructuring, associated functions, and methods. You can now organize data and behavior with Rust's type system. Next chapter, we enter Rust's most central and most distinctive concept — ownership!
