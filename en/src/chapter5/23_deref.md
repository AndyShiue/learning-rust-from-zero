# `Deref`

## Goal of This Episode

Understand the `Deref` `trait`, the `DerefMut` `trait`, Rust's `deref` coercion, and why smart pointers can often be used like the values inside them.

## Concept

### Using `*` on an `Rc`

So far we've used `*` mostly on ordinary references (`&T`). But `*` also works on some smart pointers:

```rust,editable
use std::rc::Rc;

fn main() {
    let value = Rc::new(42);
    let number: i32 = *value;

    println!("{}", number); // 42
}
```

`Rc<i32>` is not an `i32`, but Rust can use the key to reach the `i32` inside. Here, `i32` is `Copy`, so assigning `*value` into `number` creates another `i32` value.

If the inner value isn't `Copy` — say a `String` — you can't move it out this way, just as you'd expect from how borrowing worked in Chapter 4:

```rust,compile_fail
use std::rc::Rc;

fn main() {
    let text = Rc::new(String::from("hello"));
    let moved: String = *text; // Compile error!
}
```

There may be other `Rc` values that open the same heap data. Moving the inner `String` out would leave those `Rc` values with a key to an empty safe, so Rust forbids it.

### The `Deref` `trait`

The mechanism behind this is the `Deref` `trait`. We do not need its exact definition yet; the important idea is simpler:

`Deref` tells Rust how to borrow through a value. For example, `Rc<i32>` can borrow through to the `i32` inside, producing an `&i32`.

That reference is the important part. `Deref` gives Rust a **reference** to the inner value. It does not, by itself, give ownership of the inner value.

`Rc<T>` and `Box<T>` both implement `Deref`. Types like these — whose whole job is to be the key to some inner value, managing it and letting Rust reach it through `Deref` — are commonly called **smart pointers**. Some other standard library types (like `String` and `Vec<T>`) implement `Deref` too, even though being a key isn't their main job; in this episode we focus on smart pointers.

### What Happens behind `*v`

When you use `*` on a type implementing `Deref`, the useful mental model is:

```rust,ignore
*v
// roughly: borrow through v, then follow that reference
```

For the earlier `Rc<i32>` example:

```rust,ignore
let value = Rc::new(42);

*value
// roughly:
// borrow through value to get &i32
// then follow that &i32
```

Because `i32` is `Copy`, this can produce another `i32` value. If the inner value is not `Copy`, like `String`, ordinary `Deref` does not let you move it out.

### `deref` Coercion

**`deref` coercion** is Rust's mechanism for automatically converting reference types through `Deref` when needed.

For example, this function expects an `&i32`:

```rust,editable
use std::rc::Rc;

fn show(n: &i32) {
    println!("{}", n);
}

fn main() {
    let value = Rc::new(42);

    show(&value); // &Rc<i32> automatically becomes &i32
}
```

`show` needs `&i32`, but `&value` is `&Rc<i32>`. Since `Rc<i32>` implements `Deref` in a way that lets Rust borrow the inner `i32`, Rust can convert:

```rust,ignore
&Rc<i32> -> &i32
```

This conversion happens at the reference level. No ownership moves.

`deref` coercion can also chain:

```rust,editable
use std::rc::Rc;

fn show(n: &i32) {
    println!("{}", n);
}

fn main() {
    let value = Rc::new(Box::new(42));

    show(&value); // &Rc<Box<i32>> -> &Box<i32> -> &i32
}
```

Rust first goes through the `Rc`, then through the `Box`, until the reference type matches what the function expects.

### Auto-dereferencing in Method Calls

Method calls have their own auto-dereferencing behavior. When you call a method with `.`, Rust tries the outer type first. If it cannot find a matching method there, it goes one layer inward and tries again.

For example:

```rust,editable
use std::rc::Rc;

fn main() {
    let numbers = Rc::new(vec![10, 20, 30]);

    println!("{}", numbers.len()); // calls Vec<i32>'s .len()
}
```

`Rc<Vec<i32>>` itself does not define `.len()`, but `Vec<i32>` does. Rust can use the `Rc` key, borrow the inner `Vec<i32>`, and call `.len()` on that.

With multiple layers, Rust can go inward one layer at a time:

```rust,ignore
let numbers = Rc::new(Box::new(vec![10, 20, 30]));

numbers.len()
// Rust can go through Rc, then Box, then find Vec's .len()
```

This is why smart pointers often feel like the value inside them: method calls can automatically borrow through the smart pointer.

### `DerefMut`

`DerefMut` is the mutable version of `Deref`. It tells Rust how to borrow through a value mutably: from a mutable smart pointer to a mutable reference of the inner value.

`Rc<T>` does not implement `DerefMut`, because there may be other `Rc` values that open the same heap data. Ordinary `Rc<T>` provides shared read access, not unrestricted mutable access. `Rc<T>` cannot prove that it is the only key to the heap data; if `DerefMut` were allowed, the same heap data could end up with several `&mut T` references at the same time.

`Box<T>`, however, has one key and no reference counter, so a mutable `Box<T>` can provide mutable access to the inner value:

```rust,editable
fn main() {
    let mut text = Box::new(String::from("hello"));

    text.push_str(" world");
    println!("{}", text);

    *text = String::from("replaced");
    println!("{}", text);
}
```

The call to `.push_str()` mutably borrows the inner `String`. The assignment through `*text` replaces the inner `String`. Both are normal `DerefMut` behavior: Rust gets a `&mut String` through the `Box`.

### Priority When Method Names Collide

Rust searches for methods from the outside in. The outer smart pointer's own methods take priority over the inner type's methods.

A common example is `.clone()`. `Rc` itself has a `.clone()` method: it creates another `Rc` for the same heap data and increments the reference count. The inner value may also have its own `.clone()` method.

Calling `.clone()` directly creates another `Rc`:

```rust,noplayground
use std::rc::Rc;

fn main() {
    let a = Rc::new(String::from("hello"));
    let b = a.clone(); // Rc's .clone(): bumps the count, doesn't create a new String
}
```

If you want the inner `String`'s own `.clone()`, spell that out:

```rust,noplayground
# use std::rc::Rc;
#
# fn main() {
#     let a = Rc::new(String::from("hello"));
    let c = (*a).clone(); // String's .clone(): creates a new String
# }
```

### One Special Thing about `Box<T>`

Everything above treats `Deref` as borrowing through a smart pointer. That is the right general model.

`Box<T>` has one extra ability: when you own the `Box<T>`, Rust lets you move the inner `T` out with `*box_value`:

```rust,editable
fn main() {
    let boxed = Box::new(String::from("owned"));
    let text: String = *boxed; // OK: moves the String out of the Box

    println!("{}", text);
}
```

This is special support for `Box<T>`. It is **not** what ordinary `Deref` types can do:

```rust,compile_fail
use std::rc::Rc;

fn main() {
    let shared = Rc::new(String::from("shared"));
    let text: String = *shared; // Compile error!
}
```

So keep the general rule simple: `Deref` lets Rust borrow through a value. Moving a non-`Copy` value out with `*` is a special `Box<T>` ability.

## Example Code

```rust,editable
use std::rc::Rc;

fn show(n: &i32) {
    println!("value: {}", n);
}

fn main() {
    // Rc<i32>: * reaches the i32. Since i32 is Copy, this creates another i32 value.
    let shared = Rc::new(42);
    let number: i32 = *shared;
    println!("number: {}", number);

    // Deref coercion: &Rc<i32> -> &i32
    show(&shared);

    // Deref coercion can chain: &Rc<Box<i32>> -> &Box<i32> -> &i32
    let nested = Rc::new(Box::new(99));
    show(&nested);

    // Method-call auto-deref: Rc<Vec<i32>> can call Vec<i32>'s methods.
    let numbers = Rc::new(vec![10, 20, 30]);
    println!("length: {}", numbers.len());

    // DerefMut: Box<String> can mutably borrow the inner String.
    let mut text = Box::new(String::from("hello"));
    text.push_str(" world");
    println!("{}", text);

    *text = String::from("replaced");
    println!("{}", text);

    // Method-name priority: Rc's .clone() wins over String's .clone().
    let a = Rc::new(String::from("shared"));
    let b = a.clone();    // Rc .clone(): bumps the count
    let c = (*a).clone(); // String .clone(): creates a new String
    println!("a = {}, b = {}, c = {}", a, b, c);
    println!("Rc count = {}", Rc::strong_count(&a)); // 2, not 3

    // Box<T> special case: owning a Box lets you move T out.
    let boxed = Box::new(String::from("owned"));
    let owned: String = *boxed;
    println!("moved out of Box: {}", owned);
}
```

## Recap

- `Deref` is mainly about borrowing through a value: it lets Rust get a reference to the inner value.
- `*v` on a `Deref` type is "borrow, then follow the reference"; whether you can copy, mutate, or move afterward is decided by the inner type and how the expression is used.
- `deref` coercion automatically converts references such as `&Rc<i32>` to `&i32`; it can chain through multiple layers.
- Method-call auto-dereferencing lets smart pointers call methods of the inner value.
- `DerefMut` gives mutable access to the inner value; `Box<T>` supports it, while `Rc<T>` does not.
- On method-name collisions, the outer type wins; `Rc`'s `.clone()` is chosen before the inner value's `.clone()`.
- Moving a non-`Copy` value out with `*box_value` is special support for `Box<T>`, not ordinary `Deref` behavior.
