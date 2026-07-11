# Destructuring Tuple Variants with `match`

## Goal of This Episode

Learn to destructure `enum` tuple variants with `match`, extracting the data they carry.

## Concept

In Episode 7 we learned to create `enum` variants that carry data, but we've had no way to get the data back out. Now we finally can!

Inside a `match` pattern, you can use a variable name to "catch" the data inside a variant:

```rust,noplayground
# enum Shape {
#     Circle(f64),
#     Rectangle(i32, i32),
# }
# fn main() {
#     let s = Shape::Circle(42.0);
    match s {
        Shape::Circle(r) => println!("The radius is {}", r),
        Shape::Rectangle(w, h) => println!("Width {}, height {}", w, h),
    }
# }
```

The `r` in `Shape::Circle(r)` isn't a fixed name — you can pick anything. It means: "If `s` is a `Circle`, take the `f64` inside and call it `r`."

This move is called **destructuring** — taking a compound thing apart and pulling out its pieces. `match` doesn't just check "which variant is it"; it can simultaneously destructure the data inside for you to use.

## Example Code

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(i32, i32),
}

fn main() {
    let s = Shape::Circle(5.0);

    match s {
        Shape::Circle(r) => {
            println!("This is a circle");
            println!("The radius is {}", r);
            let area = r * r * 3.14159;
            println!("The area is roughly {}", area);
        }
        Shape::Rectangle(w, h) => {
            println!("This is a rectangle");
            println!("Width {}, height {}", w, h);
            let area = w * h;
            println!("The area is {}", area);
        }
    }

    // One more example
    let action = Action::Move(3, -2);

    match action {
        Action::Stop => println!("Standing still"),
        Action::Move(dx, dy) => {
            println!("Moving {} along x and {} along y", dx, dy);
        }
    }
}

enum Action {
    Stop,
    Move(i32, i32),
}
```

## Recap

- **Destructuring**: taking a compound thing apart to get at the pieces inside.
- In a `match` pattern, variable names inside the parentheses destructure a tuple variant.
- `Shape::Circle(r)` → take the value inside `Circle` and call it `r`.
- `Shape::Rectangle(w, h)` → call the two values inside `Rectangle` `w` and `h`.
- The variable names are yours to choose.
- `match` still has to cover every variant.
