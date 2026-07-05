# Moves and `Clone`

## Goal of This Episode

Understand Rust's move semantics — both assignment and passing into a function transfer ownership — and replicate data with `Clone`.

## Concept

### Move: Hand It Over and It's Gone

Last episode we learned `trait`s; now let's see what ownership looks like in code.

In Rust, when you assign a `struct` value to another variable, the original variable **can no longer be used**. This is the "handing over the keychain" from Episode 1:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
    let p1 = Point { x: 1, y: 2 };
    let p2 = p1; // Ownership of p1 moves to p2
    // From here on, p1 can't be used anymore!
# }
```

This behavior is called a **move**. The Rust compiler checks this at compile time — if you try to use the original variable after a move, the compiler reports an error outright.

### Passing into a Function Is Also a Move

It's not just assignment — passing a value into a function moves it too:

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn print_point(p: Point) {
    println!("({}, {})", p.x, p.y);
}

fn main() {
    let p1 = Point { x: 1, y: 2 };
    print_point(p1); // p1 gets moved into the function
    // p1 can't be used anymore!
}
```

Because a function's parameter is like a new variable — the value gets "handed" to it.

### `Clone`: Replication

If you need to keep the original value and also want a replica, use **`Clone`**.

First, add `#[derive(Clone)]` to your type (throwing in `Debug` too, why not):

```rust,noplayground
#[derive(Debug, Clone)]
struct Point {
    x: i32,
    y: i32,
}
#
# fn main() {}
```

Then replicate the value with `.clone()`:

```rust,editable
#[derive(Debug, Clone)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p1 = Point { x: 1, y: 2 };
    let p2 = p1.clone();  // Replicate p1; p1 survives
    println!("{:?}", p1); // OK! p1 is still usable
    println!("{:?}", p2); // p2 is an independent replica
}
```

Recall Episode 1's analogy: `clone` is "replicating the entire keychain and safe." Each variable owns its own data, with no interference.

### Integers Don't Move?

You may notice integers behave differently:

```rust,editable
fn main() {
    let a = 42;
    let b = a;
    println!("{}", a); // This actually works!
}
```

Why don't integers move? We'll answer that next episode.

## Example Code

```rust,editable
#[derive(Debug, Clone)]
struct Point {
    x: i32,
    y: i32,
}

fn print_point(p: Point) {
    println!("The function received the point: ({}, {})", p.x, p.y);
}

fn main() {
    let p1 = Point { x: 10, y: 20 };

    // Use clone to make a replica so p1 doesn't get moved away
    let p2 = p1.clone();
    println!("p1 = {:?}", p1);
    println!("p2 = {:?}", p2);

    // Passing into a function moves too, so clone first
    print_point(p1.clone());
    println!("p1 is still here: {:?}", p1);

    // Without cloning, passing it in moves p1 away
    print_point(p1);
    // Uncommenting the line below makes the compiler report an error:
    // println!("p1 is gone: {:?}", p1);
}
```

## Recap

- `let p2 = p1;` **moves** — afterward `p1` can't be used.
- Passing a value into a function is also a move.
- `#[derive(Clone)]` + `.clone()` makes an independent replica.
- After a `clone`, the original variable remains usable.
- Integers (`i32` and friends) don't move — next episode explains why.
