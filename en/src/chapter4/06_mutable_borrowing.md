# Mutable Borrowing: `&mut`

## Goal of This Episode

Learn to borrow a value with `&mut` and modify it — changing someone's data without a move.

## Concept

### Last Episode's Limitation

Last episode we learned `&` borrowing, but the resulting reference was read-only — look, don't touch. What if we want to borrow someone's thing in order to modify it?

### `&mut` Is "Borrow to Modify"

```rust,editable
fn main() {
    let mut x = 10;
    let r: &mut i32 = &mut x; // A mutable reference
    *r = 20;                  // Modify x's value through r
}
```

Key points:

1. The original variable must be `let mut` (you're going to change it).
2. Borrow with `&mut x`.
3. To modify the value through the reference, write `*r` (last episode's dereferencing — following the reference to the original value).

### `&mut` in Function Parameters

The more common usage is in functions:

```rust,editable
fn add_ten(n: &mut i32) {
    *n += 10;
}

fn main() {
    let mut x = 5;
    add_ten(&mut x);
    println!("{}", x); // 15
}
```

The function receives an `&mut i32` — a **mutable reference**. Through `*n` it can modify the original value. The call passes `&mut x`.

### Mutable Borrows of `struct`s

Same story with `struct`s:

```rust,noplayground
# #[derive(Debug)]
# struct Point {
#     x: i32,
#     y: i32,
# }
#
fn move_right(p: &mut Point) {
    p.x += 1; // No * needed for struct fields; Rust handles it
}
#
# fn main() {}
```

Note: when modifying a `struct`'s fields, you don't write `(*p).x += 1` — just `p.x += 1`. As mentioned last episode, Rust auto-dereferences.

## Example Code

```rust,editable
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

// Modifying an integer through a mutable reference
fn add_ten(n: &mut i32) {
    *n += 10;
}

// Modifying a struct's fields through a mutable reference
fn move_right(p: &mut Point) {
    p.x += 1;
}

fn move_up(p: &mut Point) {
    p.y += 1;
}

fn main() {
    // Modifying an integer
    let mut score = 80;
    println!("Before: {}", score);
    add_ten(&mut score);
    println!("After: {}", score);

    // Modifying a struct
    let mut pos = Point { x: 0, y: 0 };
    println!("Starting position: {:?}", pos);

    move_right(&mut pos);
    move_right(&mut pos);
    move_up(&mut pos);
    println!("After moving: {:?}", pos);

    // Modifying directly with &mut
    let mut val = 100;
    let r = &mut val;
    *r += 50;
    println!("val = {}", val);
}
```

## Recap

- `&mut` is a mutable borrow — once borrowed, the original value can be modified.
- The original variable must be `let mut`.
- Write parameters as `&mut Type` and pass `&mut value` when calling.
- Modifying `struct` fields works directly as `r.field` (auto-dereferencing).
- Next episode covers the important restrictions on mutable borrows.
