# The Borrowing Rules

## Goal of This Episode

Understand Rust's borrowing rules: at any one time, either one `&mut` or many `&`s — plus the problem of dangling references.

## Concept

### Why Do We Need Rules?

Last episode we learned `&mut` mutable borrowing. But what would happen if Rust allowed multiple mutable references at once?

Imagine your keychain. Lending it to many people **to look at** (`&`) is fine — everyone just looks; nothing on the keychain changes. But lend it to two people **to modify** at once (`&mut`) — A is adding a new key while B is removing it — and the result becomes unpredictable.

That, too, is a **data race**, and it leads to all kinds of weird bugs. So Rust lays down strict borrowing rules.

### Rule 1: Only One `&mut` at a Time

At any single moment, a value can have at most **one** mutable reference:

```rust,compile_fail
# #![allow(unused_variables)]
#
# fn main() {
    let mut x = 10;
    let r1 = &mut x;
    let r2 = &mut x; // Compile error! There's already a &mut
    *r1 += 1;
# }
```

### Rule 2: `&` and `&mut` Can't Coexist

If someone is reading (`&`), no one may be modifying (`&mut`) — and vice versa:

```rust,compile_fail
# #![allow(unused_variables)]
#
# fn main() {
    let mut x = 10;
    let r1 = &x;     // Read-only borrow
    let r2 = &mut x; // Compile error! There's already a &, so no &mut
    println!("{}", r1);
# }
```

### Rule 3: Multiple `&`s Can Coexist

Many simultaneous readers is no problem at all:

```rust,editable
fn main() {
    let x = 10;
    let r1 = &x;
    let r2 = &x;
    let r3 = &x;
    println!("{} {} {}", r1, r2, r3); // Totally fine
}
```

### Dangling References

One more important rule: **a reference must point to a value that's still valid**. If a reference will still be used but the value it points to has become invalid, it becomes a **dangling reference** — pointing at a place that no longer exists. Rust stops this at compile time.

We learned earlier that a move makes the original variable unusable. So while a value is still borrowed by a reference, you can't move it away:

```rust,compile_fail
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    let r = &p;

    let p2 = p; // Compile error! p is still borrowed by r
    println!("{:?}", r);
}
```

`r` still uses the borrowed value later, but `let p2 = p;` would move `p` away, making `p` unusable from that line on. Rust won't let you keep a reference that will still be used while invalidating the original variable.

Likewise, you can't move a non-`Copy` value out from behind a reference:

```rust,compile_fail
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    let r = &p;

    let moved = *r; // Compile error! Can't move a Point out from behind a &Point
    println!("{:?}", moved);
}
```

`*r` follows the reference to the original value. But `Point` doesn't implement `Copy`; storing it into `moved` would mean moving the `Point` out. That would make `r` a dangling reference — `r` still exists, but the value it borrowed has been carried off — so Rust forbids this too. Of course, if the value behind `*r` were a `Copy` type like `i32`, it's a different story: Rust copies it instead of moving, so no rule is broken.

Worth noting: a borrow doesn't live from the reference's creation all the way to the closing brace. Once the reference is used for the last time, the borrow ends:

```rust,editable
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 1, y: 2 };
    let r = &p;

    println!("{:?}", r); // r's last use

    let moved = p; // OK: the borrow has already ended
    println!("{:?}", moved);
}
```

Besides the move issue, another common dangling reference happens when a reference "escapes" from an inner scope:

```rust,compile_fail
# fn main() {
    let r;
    {
        let x = 42;
        r = &x; // x lives only inside these braces
    } // x is dropped here
    println!("{}", r); // Compile error! The x that r points to no longer exists
# }
```

`x` is dropped when the braces close, yet `r` tries to use it outside — Rust says no.

Another common case is a function trying to return a reference to a local variable:

```rust,compile_fail
fn bad() -> &i32 {
    let x = 42;
    &x // x is dropped when the function ends; the reference would point to a vanished value
}
#
# fn main() {}
```

Same reasoning: `x` disappears after the function ends, and the returned reference would point to a value that doesn't exist.

As for how Rust tracks "is this reference still valid" — that's the concept of **lifetimes**, coming later. For now, remember: **a reference must point to a value that's still valid**.

## Example Code

```rust,editable
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    // Multiple immutable borrows: OK
    let p = Point { x: 1, y: 2 };
    let r1 = &p;
    let r2 = &p;
    println!("r1 = {:?}, r2 = {:?}", r1, r2);

    // One mutable reference: OK
    let mut p2 = Point { x: 10, y: 20 };
    {
        let r3 = &mut p2;
        r3.x += 5;
        println!("After modifying: {:?}", r3);
    } // r3 leaves scope; the mutable borrow ends

    // The mutable borrow has ended; & borrowing is allowed now
    let r4 = &p2;
    println!("Read-only borrow: {:?}", r4);

    // Demo: multiple simultaneous read-only borrows
    let nums = [10, 20, 30, 40, 50];
    let slice1 = &nums[0..3];
    let slice2 = &nums[2..5];
    println!("slice1 = {:?}", slice1);
    println!("slice2 = {:?}", slice2);
}
```

## Recap

- Unrestricted borrowing would also cause **data races**, so Rust lays down borrowing rules.
- **Only one `&mut` at a time** — two simultaneous mutable references are forbidden.
- **`&` and `&mut` can't coexist** — either everyone reads, or exactly one person modifies.
- **Multiple `&`s can coexist** — many simultaneous readers are fine.
- **Dangling references**: a reference must point to a valid value — during a borrow you can't move the original, nor move a non-`Copy` value out from behind a reference.
- A borrow ends after the reference's last use; afterward you can borrow again or move the original.
- A reference can't outlive the value it points to — whether the value left its scope or a function returned a reference to a local.
- These rules let Rust prevent data races at compile time; later we'll learn lifetimes for tracking reference validity more precisely.
