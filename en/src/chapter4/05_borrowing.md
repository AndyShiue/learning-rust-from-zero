# Borrowing: `&`

## Goal of This Episode

Learn to borrow values with `&` — letting others read your data without a move or a `clone`.

## Concept

### Both move and `clone` Have Costs

So far we've learned two ways to deal with ownership:

- **move**: hand it over and it's gone; the original variable can't be used.
- **`clone`**: replicate the data (true for every type we've met so far) — but if the data is large, replication is wasteful.

Is there a way to **neither hand it over nor replicate it — just lend it out for a look**?

Yes! That's **borrowing**, using the `&` symbol.

### `&` Means "Borrow"

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
    let p = Point { x: 1, y: 2 };
    let r: &Point = &p; // r is a reference to p; p remains the owner
# }
```

`&p` means: "I'm not taking ownership of `p` — I'm just borrowing it for a look." `p` is still there and remains usable afterward; as for the restrictions during a borrow, we'll lay those out later.

The thing `&p` produces (that is, `r`) is called a **reference**, with the type written `&Point`. And "looking at someone's data through a reference without taking ownership" is what we call **borrowing**. Borrowing and references are two sides of one coin: **borrowing** is the act of "taking something for a look," and a **reference** is the pass that act hands you — holding it lets you go look at the data. From here on, the word "reference" usually means a value borrowed with `&`.

### Function Parameters with `&` Don't Move

```rust,editable
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn print_point(p: &Point) {
    println!("({}, {})", p.x, p.y);
}

fn main() {
    let p1 = Point { x: 10, y: 20 };
    print_point(&p1); // Passing &p1 — just borrowing, not moving
    println!("{:?}", p1); // p1 is still here!
}
```

Note two places:

1. The parameter type is written `&Point` (with a leading `&`).
2. The call passes `&p1` (also with `&`).

The function merely "borrows" `p1` for a look and hands it back when done — `p1`'s ownership never changes.

### Those Earlier `&`s Were References All Along!

Remember `&[i32]` (slices) and `&str` (string slices)? At the time, we said not to dig too deep. Now we can explain — those `&`s are borrows!

- `&[i32]` is a reference to a stretch of array data; it doesn't own it.
- `&str` is a reference to a stretch of string data; it doesn't own it.

So for a function like this:

```rust,noplayground
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}
#
# fn main() {}
```

`for x in nums` walks every element of the slice, just like iterating an array before. The function only borrows a slice of the array — it never moves the whole array away.

### `*` Dereferencing

`&` is "borrow"; conversely, `*` is "follow the reference back to the original value," called **dereferencing**:

```rust,editable
fn main() {
    let x = 42;
    let r = &x;
    println!("{}", *r); // 42, same as x
}
```

Most of the time, though, you won't write `*` by hand — Rust dereferences automatically when you access fields with `.`, call methods, or use `println!`. Knowing it exists is enough for now; next episode will use it.

Note: the `&[T]` and `&str` we met earlier are special — you can't use `*` on them to get a value out. The reason comes later; just know it for now.

### Every `&T` Is `Copy`

Last episode we learned `Copy` — some types copy automatically on assignment rather than moving. Whatever `T` is, `&T` is `Copy`. After all, a reference is just a borrow — copying a reference doesn't affect the original data; it just means one more onlooker:

```rust,editable
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let s = Point { x: 0, y: 0 };
    let r1 = &s;
    let r2 = r1; // Copies the reference; not a move
    println!("{:?}, {:?}", r1, r2); // Both r1 and r2 are usable
}
```

Note: `Point` itself isn't `Copy` (assignment moves it), but `&Point` is `Copy`.

### `&` References Are Read-only

When borrowing with `&`, you **can only read, not modify**. If you want to borrow something in order to change it — that's next episode.

## Example Code

```rust,editable
#[derive(Debug, Clone)]
struct Point {
    x: i32,
    y: i32,
}

// Borrowing; no move
fn print_point(p: &Point) {
    println!("({}, {})", p.x, p.y);
}

// A slice parameter is a reference
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn main() {
    let p1 = Point { x: 10, y: 20 };

    // Borrowing: pass &p1, and p1 isn't moved
    print_point(&p1);
    print_point(&p1); // You can borrow many times!
    println!("p1 is still here: {:?}", p1);

    // Array slices are borrows too
    let numbers = [1, 2, 3, 4, 5];
    let total = sum(&numbers);
    println!("Total = {}", total);
    println!("numbers is still here: {:?}", numbers);

    // &str is a borrow as well
    let greeting: &str = "Hello";
    println!("{}", greeting);
    println!("{}", greeting); // Usable many times
}
```

## Recap

- `&` is borrowing — **no ownership transfer**; the original variable stays usable.
- Write parameters as `&Type` and pass `&value` at the call site.
- Borrowing can happen many times, unlike a move which happens once.
- `*` is dereferencing — following a reference to the original value (though Rust usually does it for you).
- `&[T]` and `&str` are special references; `*` can't extract a value from them.
- Every `&T` is `Copy` — copying a reference doesn't affect the original data.
- `&` references are **read-only**; you can't modify what you borrowed.
