# `Fn` / `FnMut` / `FnOnce`

## Goal of This Episode
Understand that `Fn`, `FnMut`, and `FnOnce` are `trait`s rather than types, grasp their inheritance relationships, and learn to choose the right closure `trait`.

## Concept

### They're `trait`s, Not Types

We've been saying `FnOnce`, `FnMut`, and `Fn` for several episodes without formally explaining — they are in fact **`trait`s**. Like Chapter 5's `Clone` and `Display`, `Fn` / `FnMut` / `FnOnce` are `trait`s defined in the standard library. Each closure's anonymous `struct` automatically `impl`s the corresponding `trait`s (last episode's inference rules decide which).

So what do these `trait`s look like?

- `FnOnce(Args) -> Ret`: callable at least once (may consume itself).
- `FnMut(Args) -> Ret`: callable repeatedly (may modify internal state).
- `Fn(Args) -> Ret`: callable repeatedly through a shared reference to itself.

Watch out! `fn(i32) -> i32` (lowercase) is the function pointer **type**, while `Fn(i32) -> i32` (capitalized) is a **`trait`**. Two entirely different things.

### The Inheritance Relationships

The three `trait`s form supertrait relationships:

```ignore
Fn : FnMut : FnOnce
```

Meaning:
- Everything implementing `Fn` automatically implements `FnMut` and `FnOnce`.
- Everything implementing `FnMut` automatically implements `FnOnce`.
- But `FnOnce` doesn't imply `FnMut`, nor `FnMut` imply `Fn`.

Why this direction?

- **`Fn` → `FnMut`**: if a closure runs with just `&self`, using `&mut self` certainly works too (it simply uses a mutable reference where a shared one would have sufficed).
- **`FnMut` → `FnOnce`**: if a closure runs with `&mut self`, handing it `self` (full ownership) certainly works — owning a thing includes being able to modify it. It's just that after the call the `struct` is consumed, so no second call.

The reverse doesn't hold — a closure that must consume itself (`FnOnce`) can't promise repeated calls (`FnMut`).

### Accepting Closures with `impl Trait`

Remember Chapter 5's `impl Trait`? Use it to accept closure parameters:

```rust,noplayground
fn call_once(f: impl FnOnce() -> String) -> String {
    f()
}

fn call_many_times(mut f: impl FnMut()) {
    f();
    f();
    f();
}

fn call_twice(f: impl Fn() -> i32) -> i32 {
    f() + f()
}
#
# fn main() {}
```

Note the `mut` on the `FnMut` parameter — calling an `FnMut` closure needs `&mut self`, so `f` itself must be `mut`.

### Design Principle: Pick the Bound Accepting the Most Closures

When designing a function that takes a closure, choose the `trait` bound **accepting the widest range of closures**:

1. Try `FnOnce` first — if you only call it once.
2. Move to `FnMut` — if you need repeated calls.
3. Only then `Fn` — if you need repeated calls without a mutable reference to the closure value.

Why? Because `FnOnce` accepts every closure (all closures are at least `FnOnce`), while `Fn` accepts only closures callable through a shared reference. The widest bound gives callers maximum freedom.

In practice `Fn` is rarely needed — most functions calling a closure repeatedly do fine with `FnMut` (which also accepts `Fn` closures). Use `Fn` when the function needs to call the closure without a mutable reference to the closure value.

### Function Pointers Implement All Three `trait`s Too

Ordinary functions (and function pointers `fn`) automatically implement `Fn`, `FnMut`, and `FnOnce`. So a function name can be passed anywhere these three `trait`s are accepted.

## Example Code

```rust,editable
// Only one call needed → FnOnce (accepts the most closures)
fn consume_and_print(f: impl FnOnce() -> String) {
    let result = f();
    println!("Result: {}", result);
}

// Repeated calls needed → FnMut
fn repeat_three_times(mut f: impl FnMut()) {
    f();
    f();
    f();
}

// Repeated calls without a mutable reference to the closure value → Fn
fn sum_two_calls(f: impl Fn(i32) -> i32, x: i32) -> i32 {
    f(x) + f(x)
}

fn main() {
    // FnOnce: the closure consumes a captured value
    let name = String::from("Rust");
    consume_and_print(|| {
        let s = name; // Moves name
        format!("Hello, {}!", s)
    });

    // FnMut: the closure modifies a captured variable
    let mut count = 0;
    repeat_three_times(|| {
        count += 1;
        println!("Call number {}", count);
    });
    println!("Called {} times in total", count);

    // Fn: the closure only reads
    let multiplier = 3;
    let result = sum_two_calls(|x| x * multiplier, 5);
    println!("sum_two_calls result: {}", result);

    // Ordinary functions can be passed in too
    fn double(x: i32) -> i32 {
        x * 2
    }
    let result2 = sum_two_calls(double, 10);
    println!("With an ordinary function: {}", result2);

    // An Fn closure also fits an FnOnce parameter (since Fn: FnMut: FnOnce)
    let greeting = String::from("Hi");
    consume_and_print(|| {
        format!("{}, world!", greeting) // Only reads greeting — it's Fn
    });
    // greeting survives, since the closure merely borrowed it
    println!("greeting is still here: {}", greeting);
}
```

## Recap

- `Fn`, `FnMut`, `FnOnce` are **`trait`s**, not types; `fn` is the function pointer type.
- The inheritance: `Fn` ⊂ `FnMut` ⊂ `FnOnce` (`FnOnce` accepts every closure).
- Accept closure parameters with `impl FnOnce()` / `impl FnMut()` / `impl Fn()`.
- `FnMut` parameters need `mut`.
- Design principle for closure-taking functions: **start with `FnOnce`**, switch to `FnMut` for repeated calls, and use `Fn` when calls must not require a mutable reference to the closure value.
- Function pointers automatically implement `Fn` + `FnMut` + `FnOnce`.
