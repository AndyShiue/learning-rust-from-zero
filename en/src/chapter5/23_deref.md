# `Deref` and Auto-dereferencing

## Goal of This Episode

Understand the `Deref` `trait` and Rust's auto-dereferencing mechanism, and why smart pointers can directly call the inner type's methods.

## Concept

### Using `*` on a Smart Pointer

So far we've only used `*` on ordinary references (`&T`). But `*` works on other types too:

```rust,editable
fn main() {
    let b = Box::new(42);
    let val: i32 = *b; // Take the value out of the Box
    println!("{}", val); // 42
}
```

`*b` yields the `i32` inside the `Box`. This works because `Box<T>` implements a `trait` called `Deref`.

### The `Deref` `trait` and Smart Pointers

`Deref` tells Rust: "When you need to dereference me, here's how." Both `Box<T>` and `Rc<T>` implement `Deref`. In Rust, we often call **types that implement `Deref`** **smart pointers**.

### What Happens behind `*v`

When you use `*` on a type implementing `Deref`, Rust actually expands it like this:

```rust,ignore
*v
// Is equivalent to
*(Deref::deref(&v))
```

`Deref::deref` takes `&Self` and returns a reference (e.g. `&T`); the outer `*` then unwraps that reference to get the `T` itself.

Taking the `Box<i32>` from before:

```rust,ignore
let b = Box::new(42);

*b
// Expands to *(Deref::deref(&b))
// Deref::deref(&b) returns &i32
// One more * yields i32
```

So dereferencing a `Box<T>` ultimately yields a `T`. Same for `Rc<T>`: dereferencing an `Rc<T>` yields a `T`.

### `DerefMut`

`DerefMut` is the mutable version of `Deref`. When you write through a mutable smart pointer, Rust expands with `DerefMut`:

```rust,ignore
*v = new_value
// Is equivalent to
*(DerefMut::deref_mut(&mut v)) = new_value
```

`DerefMut::deref_mut` returns `&mut T`; the outer `*` unwraps it so a value can be written. For example:

```rust,editable
fn main() {
    let mut b = Box::new(0);
    *b = 42;
    println!("{}", *b); // 42
}
```

`Box<T>` implements both `Deref` and `DerefMut`, so it can be read and written. `Rc<T>` implements only `Deref` — modifying the contents through `*` isn't allowed.

### `Deref` Coercion

**`Deref` coercion** is Rust's mechanism of automatically converting reference types through `Deref` when needed. It's not limited to method calls — anywhere types need to match can trigger it.

For example, a function accepts `&i32`, and you can pass in a `&Box<i32>` directly; Rust converts `&Box<i32>` to `&i32` through `Deref` automatically:

```rust,editable
fn show(val: &i32) {
    println!("{}", val);
}

fn main() {
    let b = Box::new(42);
    show(&b); // Deref coercion: &Box<i32> auto-converts to &i32
}
```

`Deref` coercion can chain, too. For instance, `&Box<Box<i32>>` first `deref`s to `&Box<i32>`, then to `&i32`. `DerefMut` behaves likewise.

### Auto-dereferencing in Method Calls

Method calls have their own separate mechanism. We saw earlier that `(&a).method()` can be shortened to `a.method()` — if `method` takes `&self`, Rust adds the `&` for you. Conversely, if you have a `&T` or a smart pointer and the method is defined on `T`, Rust adds the `*` for you too.

When you call a method with `.`, Rust tries adding `&`, adding `*`, or combinations of both, layer by layer, until it finds a type with a matching method. If `a` is a `&Box<i32>` and you call a method defined on `i32` that takes `&self`, Rust does `(&**a).method()` — first `*a` to get `Box<i32>`, then `*` again to get `i32`, then `&` back to get `&i32` matching `&self`.

Some simpler examples:

```rust,ignore
let boxed = Box::new(String::from("hello"));

// What you write:
boxed.len()

// What Rust actually does:
(*boxed).len()
// *boxed yields String, String has len() — found it
```

With multiple layers of wrapping, Rust peels them one by one:

```rust,ignore
let double_boxed = Box::new(Box::new(String::from("hello")));

// What you write:
double_boxed.len()

// What Rust actually does:
(**double_boxed).len()
// *double_boxed yields Box<String>, which has no len()
// One more * yields String, which has len() — found it
```

`Rc` works the same way:

```rust,editable
use std::rc::Rc;

fn main() {
    let rc = Rc::new(vec![1, 2, 3]);
    println!("{}", rc.len()); // Auto-dereferences, calling Vec's len()
}
```

### Priority When Method Names Collide

Rust searches for methods from the outside in: the outer smart pointer's own methods take priority over the inner type's.

A common example is `clone`. `Rc` itself has a `clone` method (cutting an extra key and bumping the reference count), and `T` may have a `clone` method too (doing whatever `T` defines). Calling `.clone()` directly gets you `Rc`'s `clone`:

```rust,noplayground
use std::rc::Rc;

fn main() {
    let a = Rc::new(String::from("hello"));
    let b = a.clone(); // Rc's clone: bumps the count, doesn't replicate the String
}
```

If you want the inner `String`'s `clone`, spell it out:

```rust,noplayground
# use std::rc::Rc;
#
# fn main() {
#     let a = Rc::new(String::from("hello"));
    let c = (*a).clone(); // String's clone: truly replicates the String
# }
```

## Example Code

```rust,editable
use std::rc::Rc;

fn show(val: &i32) {
    println!("Value: {}", val);
}

fn main() {
    // *Box<T> yields T (Deref)
    let b = Box::new(42);
    let val: i32 = *b;
    println!("Dereferenced the Box: {}", val);

    // DerefMut: writing a value through *
    let mut b = Box::new(0);
    *b = 42;
    println!("After writing: {}", *b);

    // Deref coercion: &Box<i32> auto-converts to &i32
    let b = Box::new(99);
    show(&b);

    // Auto-dereferencing: a Box<String> calls String's methods directly
    let boxed = Box::new(String::from("hello"));
    println!("Length of the string in the Box: {}", boxed.len());
    // Equivalent to (*boxed).len()

    // Rc works the same
    let rc = Rc::new(vec![10, 20, 30]);
    println!("Length of the Vec in the Rc: {}", rc.len());

    // clone priority
    let a = Rc::new(String::from("shared"));
    let b = a.clone();       // Rc's clone (fast; only bumps the count)
    let c = (*a).clone();    // String's clone (slow; replicates the whole String)
    println!("a = {}, b = {}, c = {}", a, b, c);
    println!("Rc count = {}", Rc::strong_count(&a)); // 2, not 3
}
```

## Recap

- In Rust, types implementing `Deref` are commonly called smart pointers; `*v` expands to `*(Deref::deref(&v))`, so dereferencing a `Box<T>` yields a `T`.
- `DerefMut` is `Deref`'s mutable version; `*v = value` expands to `*(DerefMut::deref_mut(&mut v)) = value`.
- `Deref` coercion: Rust auto-converts references through `Deref` when types don't match — not limited to method calls (e.g. `&Box<i32>` → `&i32`).
- Method-call auto-dereferencing is a separate mechanism: calling with `.` makes Rust try adding `&`, `*`, or combinations to find the matching method.
- On name collisions the outer layer wins — `Rc`'s `clone` beats `String`'s `clone`.
