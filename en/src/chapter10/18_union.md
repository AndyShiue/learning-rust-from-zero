# `union`

## Goal of This Episode

Meet `union` — where all fields share the same block of memory.

## Concept

### What Is a `union`

Each field of a `struct` occupies its own block of memory. A `union` is different — **all fields share the same block of memory**:

```rust,noplayground
union IntOrBool {
    i: i32,
    b: bool,
}
#
# fn main() {}
```

`IntOrBool` is 4 bytes, enough to hold either its 4-byte `i32` or its 1-byte `bool`. `i` and `b` occupy the same memory — writing to `i` overwrites the contents of `b`.

### Writing Needs No `unsafe`; Reading Does

```rust,noplayground
# union IntOrBool {
#     i: i32,
#     b: bool,
# }
#
# fn main() {
    let u = IntOrBool { i: 1 };
    let value = unsafe { u.i }; // reading requires unsafe
# }
```

Why does reading require `unsafe`? Because Rust doesn't know which field you last wrote. A `bool` in memory **must be 0 or 1**. If you write 42 through `i` and read it back through `b`, that memory contains 42 — not a valid value for a `bool`. That's **undefined behavior**. When reading a `union` field, you must guarantee yourself that the memory's contents are valid for the type you're reading — the compiler can't check this, hence the `unsafe`.

### How It Differs from `enum`

| | `enum` | `union` |
|--|--|--|
| Knows the current variant | Has a discriminant | Doesn't know; you track it yourself |
| Reading | Safe | Requires `unsafe` |

### The Use Case: FFI

In pure Rust you'll almost never need a `union` — `enum`s are safer and nicer. The main reason `union` exists is interoperating with C: C has `union`s, and you need Rust's `union` to match their memory layout.

## Example Code

```rust,editable
union IntOrBool {
    i: i32,
    b: bool,
}

fn main() {
    // writing needs no unsafe
    let u = IntOrBool { b: true };

    // reading does
    unsafe {
        // wrote b, reading b — fine
        println!("b = {}", u.b);
    }

    let v = IntOrBool { i: 42 };
    unsafe {
        println!("i = {}", v.i);
        // never do this:
        // println!("b = {}", v.b);
        // a bool must be 0 or 1, but this memory holds 42 → undefined behavior!
    }

    // IntOrBool is 4 bytes
    println!("size: {} bytes", std::mem::size_of::<IntOrBool>()); // 4
}
```

## Recap

- All of a `union`'s fields share the same block of memory.
- Writing needs no `unsafe`; reading does — Rust doesn't know which field is stored inside.
- When reading, you must guarantee the memory is valid for the type — a `bool` must be 0 or 1; writing 42 then reading `b` is undefined behavior.
- Unlike an `enum`: a `union` has no discriminant and doesn't track the current variant.
- Its main use is FFI (matching C's `union`s).
