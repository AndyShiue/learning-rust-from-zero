# `RefCell<T>`

## Goal of This Episode

Learn to have the borrowing rules checked at runtime with `RefCell<T>`, and combine it with `Rc` for mutable shared data.

## Concept

Last episode's `Cell<T>` uses `.get()` to read the inner value, but `.get()` requires `T` to be `Copy`. What if you want to modify a `String` or a `Vec` and borrow the inner value to read or write it?

### `RefCell`: Runtime Borrow Checking

`RefCell<T>` is like `Cell` — letting you modify values without needing `&mut`. The differences:

- `Cell<T>`: uses `.get()` / `.set()`; `.get()` requires `T` to be `Copy`, with **zero cost** (compiles down to the same as direct access).
- `RefCell<T>`: uses `.borrow()` and `.borrow_mut()` to obtain values that behave like shared and mutable references, `T` **doesn't need** `Copy`, but there's a **runtime cost** (every borrow gets checked against the rules).

```rust,editable
use std::cell::RefCell;

fn main() {
    let x = RefCell::new(String::from("hello"));
    x.borrow_mut().push_str(" world"); // Modify the String inside
    println!("{}", x.borrow());        // Borrow to read
}
```

### Runtime Checking

Ordinary `&` and `&mut` have the borrowing rules checked at **compile time**. `RefCell` moves that check to **runtime**. The rules are identical (one `&mut` or many `&`s) — but a violation isn't a compile error, it's a **panic**.

```rust,should_panic
# #![allow(unused_variables)]
#
# use std::cell::RefCell;
#
# fn main() {
    let x = RefCell::new(42);
    let a = x.borrow();     // An immutable borrow
    let b = x.borrow_mut(); // Panic! An immutable borrow already exists
# }
```

So `RefCell` doesn't "bypass" the borrowing rules — it "defers the check."

### `Rc` + `RefCell`: Mutable Shared Data

`Rc<T>` can share data but not modify it. `RefCell<T>` can modify but not share. Combine them:

```rust,noplayground
use std::rc::Rc;
use std::cell::RefCell;

fn main() {
    let shared = Rc::new(RefCell::new(vec![1, 2, 3]));
}
```

Now several `Rc` values share the same data, and `borrow_mut()` allows modifying it.

## Example Code

```rust,editable
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    // Basic RefCell usage
    let data = RefCell::new(String::from("hello"));

    // An immutable borrow
    {
        let borrowed = data.borrow();
        println!("Reading: {}", borrowed);
    } // borrowed leaves scope, releasing the borrow

    // A mutable borrow
    {
        let mut borrowed_mut = data.borrow_mut();
        borrowed_mut.push_str(" world");
    } // borrowed_mut leaves scope, releasing the borrow

    println!("After modifying: {}", data.borrow());

    // Violating the borrowing rules → panic!
    // Uncommenting the block below panics at runtime
    // {
    //     let r1 = data.borrow();      // An immutable borrow
    //     let r2 = data.borrow_mut();  // A simultaneous mutable borrow → panic!
    // }

    // Rc + RefCell: mutable shared data
    let shared = Rc::new(RefCell::new(vec![1, 2, 3]));

    let a = shared.clone();
    let b = shared.clone();

    // Modify through a
    a.borrow_mut().push(4);

    // The change is visible through b
    println!("Reading through b: {:?}", b.borrow());

    // Modify through b
    b.borrow_mut().push(5);

    // Visible through a too
    println!("Reading through a: {:?}", a.borrow());
}
```

## Recap

- `RefCell<T>` is like `Cell` — modifying values without needing `&mut`.
- `RefCell<T>` moves the borrowing-rule check from compile time to runtime.
- `.borrow()` obtains a value that behaves like a shared reference; `.borrow_mut()` obtains one that behaves like a mutable reference.
- `.borrow()` and `.borrow_mut()` don't require `T` to be `Copy`, unlike `Cell<T>`'s `.get()`.
- `Cell` is zero-cost; `RefCell` pays a runtime check on every borrow.
- Violating the borrowing rules **panics** (not a compile error).
- The `Rc<RefCell<T>>` combo: mutable shared data.
