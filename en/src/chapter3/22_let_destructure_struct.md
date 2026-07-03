# Destructuring `struct`s with `let`

## Goal of This Episode

Learn to use `let` to break a `struct`'s fields apart directly, assigning them to variables.

## Concept

Last episode we destructured tuples with `let`; now let's destructure `struct`s. The idea is exactly the same — one `let` splits the `struct`'s fields apart:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
#     let p = Point { x: 6, y: 7 };
    let Point { x, y } = p;
# }
```

This line puts the value of `p.x` into the variable `x` and `p.y` into `y`. It uses field shorthand (from Episode 11), so `x` is both the field name and the variable name.

If you want a variable name different from the field name, use the `field_name: variable_name` form:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
#     let p = Point { x: 6, y: 7 };
    let Point { x: px, y: py } = p;
    // The variables are now called px and py
# }
```

The `..` from earlier works too, taking only the fields you need:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
#     let p = Point { x: 6, y: 7 };
    let Point { x, .. } = p;
    // Take only x; ignore the other fields
# }
```

Tuple `struct`s can be destructured too — nearly identical to tuple patterns, just with the type name in front:

```rust,editable
struct Pair(i32, i32);

fn main() {
    let p = Pair(1, 2);
    let Pair(a, b) = p;
}
```

## Example Code

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

struct Rectangle {
    x: i32,
    y: i32,
    width: i32,
    height: i32,
}

fn main() {
    let p = Point { x: 5, y: 10 };

    // let destructuring a struct (with field shorthand)
    let Point { x, y } = p;
    println!("x = {}, y = {}", x, y);

    // With different variable names
    let p2 = Point { x: 3, y: 7 };
    let Point { x: px, y: py } = p2;
    println!("px = {}, py = {}", px, py);

    // With .. to take only some fields
    let rect = Rectangle { x: 0, y: 0, width: 100, height: 50 };
    let Rectangle { width, height, .. } = rect;
    println!("Width {}, height {}", width, height);
    let area = width * height;
    println!("Area = {}", area);
}
```

## Recap

- `let Point { x, y } = p;` splits a `struct`'s fields into separate variables.
- `..` ignores fields you don't need.
- Tuple `struct`s destructure too: `let Pair(a, b) = p;`.
- `let` destructuring is extremely handy for pulling data out of a `struct`.
