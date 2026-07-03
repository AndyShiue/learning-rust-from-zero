# `struct` (Named Fields)

## Goal of This Episode

Learn to use a `struct` to group several related values together into a custom type.

## Concept

So far, every type we've used has been built into Rust: `i32`, `f64`, `bool`, `char`, plus tuples, arrays, and slices. But in real programming, you'll need to **define new types of your own**.

A `struct` is one of the ways Rust lets you define a new type. Defining a `struct` tells Rust: "I want a new type, and it contains these fields."

For example, a "point" has an x coordinate and a y coordinate. We could represent it with a tuple `(i32, i32)`, but tuples only offer `.0` and `.1` — you can't tell which is `x` and which is `y`. With a `struct`, every field gets a name.

The syntax for defining a `struct`:

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn main() {}
```

`struct` definitions generally go outside `fn main()`, so other functions can use them too. Above or below is fine (like functions, they're not restricted by definition order).

To create a `struct` value, use the `TypeName { field_name: value }` syntax. To read a value, use `.field_name`. To modify a `struct`'s fields, the variable must be `mut`.

## Example Code

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 3, y: 7 };
    println!("The x coordinate is {}", p.x);
    println!("The y coordinate is {}", p.y);

    // Point is a type, just like i32, and can be used in type annotations
    let p2: Point = Point { x: 100, y: 200 };
    println!("p2's coordinates are ({}, {})", p2.x, p2.y);

    // With mut, a struct's values can be modified
    let mut q = Point { x: 0, y: 0 };
    q.x = 10;
    q.y = 20;
    println!("q's coordinates are ({}, {})", q.x, q.y);
}
```

## Extra: Trailing Commas

Notice that in the `struct` definition, even the last field has a comma after it:

```rust,editable
struct Point {
    x: i32,
    y: i32, // ← This comma is optional
}

fn main() {}
```

Rust allows a comma after the last item in `struct` definitions, `struct` creation, function calls, and more. This is called a **trailing comma**. Adding it is never an error, and the benefit is that when you add a field later, you don't have to go back and add a comma to the previous line — and the git diff stays cleaner.

The Rust community convention is to **include the trailing comma**.

## Recap

- A `struct` lets you define a custom type with named fields.
- `struct` definitions generally go outside `fn main()`; above or below both work (like functions).
- Syntax for creating a `struct` value: `Point { x: 1, y: 2 }`.
- Read a field's value with `.field_name`, e.g. `p.x`.
- To modify a `struct`'s fields, the variable must be `mut`.
- The comma after the last field (trailing comma) is optional; convention is to include it.
