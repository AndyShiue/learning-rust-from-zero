# Destructuring in Function Parameters

## Goal of This Episode

Learn to destructure tuples or `struct`s directly in a function's parameter position.

## Concept

We've learned to destructure in `let`, `match`, and `for`. Well, **function parameters can destructure too**!

Suppose you have a function that receives a tuple `(i32, i32)` representing coordinates. Rather than splitting it apart inside the function, split it right in the parameter position:

```rust,noplayground
fn print_point((x, y): (i32, i32)) {
    println!("({}, {})", x, y);
}
#
# fn main() {}
```

Note the syntax: `(x, y)` is the pattern, and `: (i32, i32)` is the type annotation. Pattern and type are separated by `:`.

Calling works as usual — pass a tuple in:

```rust,editable
fn print_point((x, y): (i32, i32)) {
    println!("({}, {})", x, y);
}
fn main() {
    print_point((3, 7));
}
```

`struct`s can be destructured in the parameter position too:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
fn print_point_struct(Point { x, y }: Point) {
    println!("({}, {})", x, y);
}
#
# fn main() {}
```

## Example Code

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

// A function destructuring tuples in its parameters
fn add_coordinates((x1, y1): (i32, i32), (x2, y2): (i32, i32)) -> (i32, i32) {
    (x1 + x2, y1 + y2)
}

// A function destructuring a struct in its parameter
// Of course, you could also choose to use match here
fn describe_point(Point { x, y }: Point) {
    if x == 0 && y == 0 {
        println!("The origin");
    } else if x == 0 {
        println!("On the y-axis, y = {}", y);
    } else if y == 0 {
        println!("On the x-axis, x = {}", x);
    } else {
        println!("An ordinary point ({}, {})", x, y);
    }
}

fn main() {
    // Passing tuples to the function
    let a = (1, 2);
    let b = (3, 4);
    let result = add_coordinates(a, b);
    println!("({}, {}) + ({}, {}) = ({}, {})", a.0, a.1, b.0, b.1, result.0, result.1);

    // Passing structs to the function
    let p = Point { x: 0, y: 5 };
    describe_point(p);

    let origin = Point { x: 0, y: 0 };
    describe_point(origin);
}
```

## Why Can Tuples and `struct`s Be Destructured with `let`?

You might wonder: why is it that tuples and `struct`s can be destructured directly in `let`, `for`, and function parameters?

```rust,compile_fail
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# enum Shape {
#     Circle { radius: f64 },
#     Rectangle { width: i32, height: i32 },
# }
#
# fn main() {
#     let p = Point { x: 6, y: 7 };
#     let s = Shape::Circle { radius: 6.7 };
    let (x, y) = (1, 2);    // OK
    let Point { x, y } = p; // OK
    let Shape::Circle { radius } = s; // Not allowed!
# }
```

The answer: **the tuple and `struct` patterns used in this episode cannot fail to match**. Any `(i32, i32)` matches `(x, y)`, and any `Point` matches `Point { x, y }`.

`enum`s are different. A `Shape` might be a `Circle` or a `Rectangle`. If you write `let Shape::Circle { radius } = s;` but `s` is actually a `Rectangle`, it fails. Rust doesn't allow patterns that can fail in a `let`.

Patterns that always succeed are called **irrefutable patterns**; ones that can fail are **refutable patterns**. `let`, `for`, and function parameters accept only irrefutable patterns.

What other irrefutable patterns are there?

```rust,editable
fn main() {
    let arr = [1, 2, 3];
    let [head, ..] = arr;
    println!("The first element is {}", head);
}
```

`arr` has type `[i32; 3]`; the compiler can see at a glance that it always has three elements, so `[head, ..]` always matches — it's also an irrefutable pattern, and `let` destructuring works. Conversely, with a slice `&[i32]` it wouldn't: a slice might be empty, making `[head, ..]` refutable on slices, and `let` can't take it.

Want to handle refutable patterns? Next episode covers `if let`.

## Recap

- Function parameters can destructure with patterns directly: `fn foo((x, y): (i32, i32))`.
- Both tuples and `struct`s can be destructured in the parameter position.
- Calls look the same as always; destructuring is the function's internal business.
- `let`, `for`, and function parameters accept only patterns that can't fail (irrefutable patterns), so this episode's `(x, y)` and `Point { x, y }` work, but `Shape::Circle { radius }` doesn't.
