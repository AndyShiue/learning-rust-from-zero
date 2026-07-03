# Tuple `struct`s and Unit `struct`s

## Goal of This Episode

Learn to define `struct`s without field names using tuple `struct`s, and `struct`s with no fields at all using unit `struct`s.

## Concept

Last episode's `struct`s gave every field a name. But sometimes the fields' meanings are already obvious, and no naming is needed. That's when you can use a **tuple `struct`** — it looks like a hybrid of a tuple and a `struct`.

```rust,editable
struct Point(i32, i32);

fn main() {}
```

Create a value with `Point(3, 7)` — note that `Point` here is both the **name of the type** and the **name used when creating values**. Access values with `.0`, `.1`, just like a tuple.

The named-field `struct` from last episode works the same way: `Point` is both the type name and the name used when writing `Point { x: 1, y: 2 }` to create a value.

There's an even more extreme case: a `struct` with no fields at all, called a **unit `struct`**. It's usually used as a "marker" — signaling some identity or role while carrying no data of its own.

```rust,editable
struct Marker;

fn main() {}
```

## Example Code

```rust,editable
// Tuple struct: fields have no names; access by position
struct Point(i32, i32);

// Another tuple struct example
struct Color(i32, i32, i32);

// Unit struct: no fields at all
struct Marker;

fn main() {
    let p: Point = Point(3, 7);
    println!("x = {}, y = {}", p.0, p.1);

    let red: Color = Color(255, 0, 0);
    println!("R={}, G={}, B={}", red.0, red.1, red.2);

    // Creating a unit struct needs no parentheses or braces
    let _m: Marker = Marker;
    println!("Marker created! (It carries no data)");
}
```

## Recap

- **Tuple `struct`**: `struct Point(i32, i32);`, with values accessed via `.0`, `.1`.
- **Unit `struct`**: `struct Marker;`, with no fields whatsoever.
- Tuple `struct`s suit cases where field meanings are obvious and names are unnecessary.
- Unit `struct`s work as markers, carrying no data.
- Even if two tuple `struct`s have exactly the same field types, they are different types (e.g. `Point(i32, i32)` and `Size(i32, i32)` are not interchangeable).
