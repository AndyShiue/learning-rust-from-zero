# `Copy`

## Goal of This Episode

Understand the `Copy` `trait` — why integers, floats, booleans, and characters don't move on assignment.

## Concept

### Last Episode's Question

Last episode we found that `struct` values move when assigned or passed into functions, but integers don't:

```rust,editable
fn main() {
    let a = 42;
    let b = a;
    println!("{}", a); // Completely fine!
}
```

Why? The answer is the **`Copy` `trait`**.

### What Is `Copy`?

`Copy` is a special `trait`. If a type implements `Copy`, then on assignment or when passed into a function, Rust automatically makes a copy instead of moving.

`Copy` means copying the value is a simple, mechanical operation, so Rust can do it automatically on assignment or when passing the value into a function — no need to write `.clone()`.

### Which Types Have `Copy` Automatically?

These types are born with `Copy`:

- Integers: `i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128`, `isize`, `usize`.
- Floats: `f32`, `f64`.
- Booleans: `bool`.
- Characters: `char`.
- ...and plenty of other types.

Additionally, **tuples** and **arrays** are `Copy` as a whole if every element inside is `Copy`:

```rust,editable
fn main() {
    let t = (1, true, 'a');  // (i32, bool, char) → all Copy → the tuple is Copy too
    let t2 = t;
    println!("{:?}", t);     // OK!

    let arr = [1, 2, 3];     // [i32; 3] → i32 is Copy → the array is Copy too
    let arr2 = arr;
    println!("{:?}", arr);   // OK!
}
```

That's why in the code you wrote in earlier chapters, integers, tuples, and arrays could be freely assigned to multiple variables and passed into multiple functions without any trouble.

Beyond `Copy`: when every type in a tuple implements `Clone`, the tuple automatically implements `Clone` too. In fact, tuples behave this way for some other `trait`s — for those `trait`s, if all the elements implement one, the tuple as a whole does too. We won't belabor this point again.

### Your Own Types Can Take `Copy` Too

If every value in your type has a `Copy` type, your type can take `#[derive(Copy, Clone)]`:

```rust,noplayground
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
#
# fn main() {}
```

Note: `Copy` requires `Clone`. When using `derive`, the usual approach is `#[derive(Copy, Clone)]`; writing only `#[derive(Copy)]` without a `Clone` implementation is a compile error.

Why? Because Rust decrees: anything that can be copied must also be `clone`-able. `Copy` is "automatic copying"; `Clone` is "calling `.clone()` by hand." If something can't even be `clone`d manually, it certainly shouldn't be copied automatically. So `Copy` requires `Clone` first.

Once added, `Point` behaves just like an integer — assignment doesn't move:

```rust,editable
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p1 = Point { x: 1, y: 2 };
    let p2 = p1; // Automatically copied; p1 survives!
    println!("{:?}", p1); // OK
}
```

### The Difference between copy and `clone`

| | copy | `clone` |
|---|---|---|
| Triggered by | Automatic (assignment, passing into functions) | Manual (`.clone()`) |
| Can customize its behavior | No | Yes, through the implementation of `.clone()` |
| Prerequisite to implement | All contents must be `Copy` | None |

In short: **copy is automatic duplication; `clone` is called by hand, and what it does is up to the type.**

## Example Code

```rust,editable
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}

fn print_point(p: Point) {
    println!("The function received: ({}, {})", p.x, p.y);
}

fn double(n: i32) -> i32 {
    n * 2
}

fn main() {
    // Integers copy automatically
    let a = 42;
    let b = a;
    println!("a = {}, b = {}", a, b); // Both usable

    // bool is Copy too
    let flag = true;
    let flag2 = flag;
    println!("flag = {}, flag2 = {}", flag, flag2);

    // Passing an integer into a function doesn't move it
    let x = 10;
    let result = double(x);
    println!("x = {}, result = {}", x, result);

    // A custom struct with Copy added doesn't move either
    let p1 = Point { x: 3, y: 7 };
    let p2 = p1;     // Automatically copied
    print_point(p1); // p1 remains usable
    println!("p1 = {:?}", p1); // Still works!
    println!("p2 = {:?}", p2);
}
```

## Don't Slap `Copy` on Your Types Casually

Having read this episode, you might think: "So why don't I just add `#[derive(Copy, Clone)]` to every `struct` from now on?"

**Please don't.** Here's why: once `Copy` is on, code using your type comes to depend on the "auto-copy on assignment" behavior. If one day you need to modify the `struct` and add a non-`Copy` field, you'll have to remove `Copy`.

And then the trouble starts: with `Copy` gone, every `let p2 = p1;` flips from "automatic copy" to "move," and `p1` stops being usable. All the code using this type may break — potentially in many, scattered places.

So the good habit is: **only add `Copy` when you're sure the type will never gain a non-`Copy` field.** Something like `Point { x: i32, y: i32 }` is a great fit. When unsure, add only `Clone` — write `.clone()` manually when you need it, and future changes won't ripple through other code.

## Recap

- **`Copy`** is a `trait` that makes a type copy automatically on assignment and function calls, instead of moving.
- Primitive types like `i32`, `f64`, `bool`, `char` have `Copy` innately.
- Tuples and arrays are `Copy` when all their elements are.
- Tuples behave this way for some `trait`s (`Copy`, `Clone`, etc.): for those `trait`s, if all elements implement one, the tuple does too.
- Custom `struct`s can take `#[derive(Copy, Clone)]`, but every field must be a `Copy` type.
- `Copy` requires `Clone`; when using `derive`, both are usually listed together.
- **`Copy` = automatic copying; `Clone` = calling `.clone()` by hand**
- Don't add `Copy` casually — removing it later breaks all the code that relied on auto-copying. When unsure, just add `Clone`.
