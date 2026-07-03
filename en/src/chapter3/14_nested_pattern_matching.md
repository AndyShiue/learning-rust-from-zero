# Nested Pattern Matching

## Goal of This Episode

Learn to destructure deeper structures within a `match` — nested pattern matching.

## Concept

So far our `match`es have destructured just one layer. But what if the data structure is nested? Say, a tuple wrapping an `enum`, or an `enum` wrapping another `struct`?

Rust's pattern matching can destructure several layers at once — like peeling an onion, reaching in layer by layer.

For instance, given a tuple `(i32, Shape)`, you can destructure both the tuple and the `Shape` inside it in one `match`:

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

fn main() {
    let data = (666, Shape::Circle(42.0));
    match data {
        (id, Shape::Circle(r)) => println!("#{} is a circle with radius {}", id, r),
        (id, Shape::Rectangle(w, h)) => println!("#{} is a rectangle {}x{}", id, w, h),
    }
}
```

In a single pattern, the outer layer destructures the tuple to get `id` and the `Shape`, and the inner layer destructures the `Shape` to get the data inside. All in one line!

## Example Code

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

struct Point {
    x: i32,
    y: i32,
}

fn main() {
    // Example 1: a tuple wrapping an enum
    let data = (1, Shape::Circle(5.0));

    match data {
        (id, Shape::Circle(r)) => {
            println!("Shape #{} is a circle with radius {}", id, r);
        }
        (id, Shape::Rectangle(w, h)) => {
            println!("Shape #{} is a rectangle {}x{}", id, w, h);
        }
    }

    // Example 2: a tuple wrapping a struct
    let item = ("origin", Point { x: 0, y: 0 });

    match item {
        (name, Point { x, y }) => {
            println!("{}: coordinates ({}, {})", name, x, y);
        }
    }
}
```

## Recap

- Rust's pattern matching can destructure multiple layers of nesting.
- One pattern can destructure tuple + `enum`, tuple + `struct`, and so on, all at once.
- Nested destructuring saves you from writing multiple `match`es — everything comes out in one go.
- The syntax simply nests patterns layer by layer, mirroring the data's structure.
