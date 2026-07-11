# `Rc` under Multithreading

## Goal of This Episode

Understand why `Rc` can't cross `Thread`s at all — neither `Send` nor `Sync`.

## Concept

### `Rc` Is Not `Sync`

`Rc`'s reference count, like `RefCell`'s `borrow` count, is an ordinary integer — no atomic operations. If several `Thread`s `clone` or `drop` through `&Rc<T>` simultaneously, the count's increments and decrements can trample each other, corrupting the count — releasing the data early, or never releasing it.

So `Rc` isn't `Sync`, for the same reason as `RefCell`.

### `Rc` Isn't Even `Send`

Last episode said `RefCell` is `Send`, since after a move one `Thread` alone owns it. `Rc` is different.

`Rc`'s whole design is multiple `Rc`s pointing at one piece of data. Move one `Rc` to another `Thread`, and its `clone`s may remain on the original `Thread`. Both sides operating on the reference count simultaneously can wreck the counter.

The problem isn't the move itself, but that **after the move, two `Thread`s still share one counter**.

```rust,compile_fail
use std::rc::Rc;

fn main() {
    let a = Rc::new(42);
    let b = a.clone(); // a and b share the data and the counter

    // If a moved to another thread,
    // b would remain on the original — both sides touching the counter at once, boom
    std::thread::spawn(move || {
        println!("{}", a);
    });
    // Compile error! Rc<i32> is not Send
}
```

### `Rc` Can't Cross `Thread`s, Period

`Rc` is neither `Send` nor `Sync`. It can't move to other `Thread`s, nor share references among them. Sharing data across `Thread`s takes a different tool.

## Example Code

```rust,editable
use std::rc::Rc;
use std::thread;

fn main() {
    // Rc works normally in a single thread
    let a = Rc::new(String::from("hello"));
    let b = a.clone();
    println!("a = {}, b = {}", a, b);
    println!("Count = {}", Rc::strong_count(&a));

    // But it can't cross threads — the following won't compile:

    // let data = Rc::new(42);
    // thread::spawn(move || {
    //     println!("{}", data);
    // });
    // Compile error: Rc<i32> is not Send

    println!("Rc is single-threaded only");
}
```

## Recap

- `Rc`'s reference count is an ordinary integer, not atomic — so not `Sync`.
- `Rc` isn't even `Send`: after moving an `Rc` to another `Thread`, its `clone`s may remain behind, and both sides touching the counter at once breaks it.
- In short: `Rc` cannot cross `Thread`s at all.
