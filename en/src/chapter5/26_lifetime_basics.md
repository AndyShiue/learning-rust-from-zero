# Lifetime Basics

## Goal of This Episode

Understand why lifetime annotations `'a` are needed, and learn to annotate lifetimes when a function returns a reference.

## Concept

When Chapter 4 covered borrowing, we planted a seed: "you can't return a reference to a local variable." Time to face this properly.

### Problem 1: Returning a Reference to a Local Variable

```rust,compile_fail
fn make_greeting() -> &str {
    let s = String::from("Hi there");
    &s // Compile error!
} // s is released here; the returned reference would point to memory that no longer exists
#
# fn main() {}
```

This one's easy to grasp — `s` is gone once the function ends, so returning a reference to it is meaningless. Rust blocks it outright.

### Problem 2: Several References — Which One Gets Returned?

But this case is subtler:

```rust,compile_fail
fn longer(a: &str, b: &str) -> &str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}
#
# fn main() {}
```

This fails to compile too. `a` and `b` are references passed in from outside — they don't vanish when the function ends. So why not?

Because when Rust checks the **call site**, it needs to know how long the returned reference can "live." Consider:

```rust,ignore
# fn main() {
    let s1 = String::from("hello world");
    let result;
    {
        let s2 = String::from("hi");
        result = longer(&s1, &s2);
    } // s2 is released here
    println!("{}", result); // Can result still be used or not?
# }
```

If `longer` returned `a` (i.e. `&s1`), `result` is safe — `s1` is still alive. But if it returned `b` (i.e. `&s2`), `result` is a dangling reference — `s2` has been released.

The catch: **when checking `longer`'s call site, the compiler does not look at `longer`'s body**. It reads only the signature. And the signature says `-> &str` — nothing tells it whose lifespan the return value is tied to.

### The Lifetime Annotation `'a`

The fix is a lifetime annotation, explicitly describing the relationship between the return value and the parameters:

```rust,noplayground
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}
#
# fn main() {}
```

`'a` is a **lifetime parameter** (like a type parameter `T`, but starting with `'`). The signature tells Rust: "`a`, `b`, and the return value are all annotated with the same `'a`. So the return value's lifespan can't exceed the **shorter** of `a` and `b`." Note that lifetime parameters go inside `<>` just like type parameters. When both are present, **lifetimes come first**: `fn foo<'a, T>(x: &'a T) -> &'a T`.

### Why the Shorter One?

Because `a` and `b` share one `'a`, Rust takes their **intersection** — the stretch of time during which both are still alive.

Back to the example:

```rust,editable
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}

fn main() {
    let s1 = String::from("hello world"); // s1 lives longer
    let result;
    {
        let s2 = String::from("hi");      // s2 lives shorter
        result = longer(&s1, &s2);
        println!("{}", result);           // ✅ Both s1 and s2 are alive here
    } // s2 is released here
    // println!("{}", result);            // ❌ No! 'a is the intersection of s1 and s2, and s2 is dead
}
```

`'a` gets inferred as `s2`'s lifespan (the shorter one), so `result` is usable only while `s2` is still alive.

### `&'a mut T`

Mutable references can carry lifetime annotations too, written `&'a mut T` — the `'a` slots between `&` and `mut`. `'a` likewise describes how long the reference may live.

```rust,noplayground
fn replace<'a>(target: &'a mut String, new_value: &str) {
    target.clear();
    target.push_str(new_value);
}
#
# fn main() {}
```

### Lifetimes Don't Change Lifespans

**Key idea**: lifetime annotations never make any reference live longer or shorter. They only **describe** relationships that already exist, helping the compiler check. Just as a type annotation doesn't change a value's contents.

### Not Every Function Needs Annotations

If a function has just one reference parameter, Rust can usually infer on its own (next episode covers the details):

```rust,noplayground
fn first_char(s: &str) -> &str {
    &s[..1] // The return value obviously lives as long as s; no manual annotation needed
}
#
# fn main() {}
```

### The `'static` Lifetime

One special lifetime exists: `'static`, meaning "lives until the program ends."

String literals are `'static` — the type of `"hello"` is `&'static str`, because string literals are baked into the code and exist for the program's entire run.

## Example Code

```rust,editable
// Returning a reference requires lifetime annotations
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}

// The return value relates only to a; b has no bearing
fn always_first<'a>(a: &'a str, _b: &str) -> &'a str {
    a
}

fn main() {
    // Example 1: both parameters live equally long
    let s1 = String::from("a rather long string");
    let s2 = String::from("short");
    let result = longer(&s1, &s2);
    println!("The longer one is: {}", result);

    // Example 2: the parameters have different lifespans
    let s3 = String::from("hello world");
    let r;
    {
        let s4 = String::from("hi");
        r = longer(&s3, &s4);
        println!("Inside the scope: {}", r); // ✅ Both s3 and s4 are alive
    }
    // println!("{}", r); // ❌ Compile error! s4 was released; r's lifetime is too short

    // Example 3: the return value borrows only one parameter
    let s5 = String::from("I get returned");
    let r2;
    {
        let s6 = String::from("I don't");
        r2 = always_first(&s5, &s6);
    }
    // r2 borrows only s5, so s6 being released doesn't matter
    println!("{}", r2); // ✅ s5 is alive; r2 is usable

    // The 'static lifetime
    let s: &'static str = "I'm a static string, alive until the program ends";
    println!("{}", s);
}
```

## Recap

- When a function returns a reference, Rust needs to know how long it can live — that's what lifetime annotations are for.
- `'a` is a lifetime parameter describing lifespan relationships between references.
- When several parameters share one `'a`, Rust takes the intersection (the shorter one).
- Lifetime annotations **don't change lifespans** — they only describe existing relationships.
- `'static` means "lives until the program ends" — string literals have type `&'static str`.
