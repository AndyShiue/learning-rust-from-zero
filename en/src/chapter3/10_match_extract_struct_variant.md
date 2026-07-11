# Destructuring `struct` Variants with `match`

## Goal of This Episode

Learn to destructure `enum` `struct` variants with `match`, extracting the named fields inside.

## Concept

Episode 9 covered destructuring tuple variants (by position); now let's destructure `struct` variants (by field name).

The syntax uses `field_name: variable_name` inside the pattern:

```rust,noplayground
# enum Shape {
#     Circle { radius: f64 },
#     Rectangle { width: i32, height: i32 },
# }
# fn main() {
#     let s = Shape::Circle { radius: 42.0 };
    match s {
        Shape::Circle { radius: r } => println!("Radius {}", r),
        Shape::Rectangle { width: w, height: h } => println!("{}x{}", w, h),
    }
# }
```

`radius: r` means "take the value of the `radius` field and call it `r`." Left of the colon is the field name; right of it is a variable name of your choosing.

This looks a lot like the syntax for creating a `struct` variant, just in the opposite direction: creating "puts values in," while `match` "takes values out."

## Example Code

```rust,editable
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: i32, height: i32 },
}

fn main() {
    let s = Shape::Rectangle { width: 10, height: 5 };

    match s {
        Shape::Circle { radius: r } => {
            println!("This is a circle, radius = {}", r);
            let area = r * r * 3.14159;
            println!("Area roughly {}", area);
        }
        Shape::Rectangle { width: w, height: h } => {
            println!("This is a rectangle");
            println!("Width = {}, height = {}", w, h);
            let area = w * h;
            println!("Area = {}", area);
            let perimeter = 2 * (w + h);
            println!("Perimeter = {}", perimeter);
        }
    }
}
```

## Ordinary `struct`s Work the Same Way

It's not just `enum` `struct` variants — ordinary named-field `struct`s can be destructured the same way:

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 3, y: 0 };

    match p {
        Point { x: 0, y: 0 } => println!("The origin"),
        Point { x: a, y: 0 } => println!("On the x-axis, x = {}", a),
        Point { x: 0, y: b } => println!("On the y-axis, y = {}", b),
        Point { x: a, y: b } => println!("At ({}, {})", a, b),
    }
}
```

Exactly the same syntax — `TypeName { field_name: variable_name }`.

Notice the patterns above mix **fixed values** and **variables**: in `Point { x: 0, y: b }`, `x: 0` is a fixed value (it only matches when `x` equals 0), while `y: b` is a variable (take `y`'s value and call it `b`). This trick is very common in `match`. `match` compares the patterns top to bottom in order. As soon as one matches, the code on the right runs, and then execution leaves the whole `match` — no further comparisons.

## Recap

- In a `match`, destructure `struct` variants with `field_name: variable_name`.
- `Shape::Circle { radius: r }` → take the `radius` field and call it `r`.
- Left of the colon is the field name (must match the definition); right of it is your chosen variable name.
- Ordinary named-field `struct`s can be destructured in a `match` the same way.
- Patterns can mix fixed values and variables: `Point { x: 0, y: b }` means "`x` must be 0; take `y` out as `b`."
- `match` compares top to bottom; on the first success it runs that arm and exits the `match`.
- All fields must be written out (for now — we'll learn how to ignore them later).
