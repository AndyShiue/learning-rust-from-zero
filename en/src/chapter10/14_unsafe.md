# `unsafe`

## Goal of This Episode

Understand what `unsafe` means, what it lets you do, and what to watch out for when writing `unsafe` code.

## Concept

### Why `unsafe` Exists

Rust's safety guarantees rest on certain **assumptions** — for example, that a `&mut T` is always exclusive, or that a reference always points to valid data. The compiler checks those assumptions for you.

But some operations are impossible for the compiler to verify. Rust doesn't forbid you from doing them — it asks you to explicitly say "I take responsibility for this part." That's `unsafe`.

### Rust's Safety Guarantees

Safe Rust guarantees the following things **can never happen**, no matter how your code is written:

- No access to memory that has already been freed.
- No data races (multiple threads reading and writing simultaneously with at least one writer).
- No dangling references.
- No value getting `drop`ped twice.
- No reads of uninitialized memory.
- No type confusion (e.g. reading the bytes of an `isize` as a pointer).

The responsibility of `unsafe` code is this: even while bypassing the compiler's checks, it must ensure that **all** of these guarantees still hold.

### `unsafe` Blocks

Wrap code needing `unsafe` operations in `unsafe { }`. `unsafe` is not "turn off all checks" — borrowing rules and type checking still apply inside an `unsafe` block. It merely unlocks a few specific extra operations.

### The Five `unsafe` Operations

1. **Dereferencing raw pointers** (`*const T`, `*mut T`)
2. **Calling `unsafe` functions**
3. **Manually implementing an `unsafe trait`**
4. **Accessing `static mut` variables**
5. **Accessing a `union`'s fields**

### Raw Pointers

A raw pointer is a pointer with no borrow-rule protection. **Creating** one doesn't require `unsafe`; **using** it (dereferencing) does:

```rust,editable
fn main() {
    let x = 42;
    let ptr: *const i32 = &raw const x; // creating: no unsafe needed

    let value = unsafe { *ptr }; // dereferencing: unsafe needed
    println!("{}", value); // 42
}
```

You can also convert a reference into a raw pointer with `as`:

```rust,noplayground
# fn main() {
    let x = 42;
    let ptr = &x as *const i32; // &i32 to *const i32
# }
```

But `&raw const x` and `&raw mut x` are better — they take a raw pointer straight from the variable without creating a reference first. Sometimes merely creating the reference can itself break the rules (e.g. taking `&` of uninitialized memory); `&raw` sidesteps that problem.

### `unsafe fn`

If a function's safety must be guaranteed by its caller, mark it `unsafe fn`:

```rust,noplayground
unsafe fn dangerous(ptr: *const i32) -> i32 {
    unsafe { *ptr }
}

fn main() {
    let x = 42;
    let value = unsafe { dangerous(&raw const x) };
}
```

Note: since the Rust 2024 edition, `unsafe` operations require an `unsafe { }` block even inside an `unsafe fn` — so every `unsafe` operation is explicitly marked.

### `unsafe trait`

Some `trait`s can only be implemented correctly by satisfying conditions the compiler can't check automatically:

```rust,noplayground
unsafe trait MyGuarantee {
    fn check(&self) -> bool;
}

unsafe impl MyGuarantee for i32 {
    fn check(&self) -> bool { *self >= 0 }
}
#
# fn main() {}
```

An `unsafe trait` means: "implementing this `trait` requires satisfying conditions the compiler cannot check." You implement it with `unsafe impl`, signaling that you guarantee those conditions hold.

`Send` and `Sync` are `unsafe trait`s — the compiler implements them automatically when appropriate, but if you implement them manually, you must guarantee thread safety yourself.

Note: **calling** an `unsafe trait`'s methods doesn't require `unsafe` — the danger lies in the implementation, not the use.

### The `unsafe` Boundary

`unsafe` code must guarantee: **no matter what safe code calls it, it can never cause undefined behavior.**

Take the standard library's `Vec`: it uses `unsafe` internally to manage memory, but exposes a safe API. No matter how you use `Vec`'s safe API, you cannot trigger undefined behavior.

### Guidelines for Writing `unsafe` Code

- **Keep `unsafe` blocks as small as possible** — wrap only the lines that truly need it.
- **Write `// SAFETY:` comments** — explain why this `unsafe` operation is correct.
- **Mind the borrowing rules** — even with raw pointers, rules like "`&mut` must be exclusive" still hold semantically.
- **Uphold type invariants** — e.g. a `String` is always valid UTF-8; a `bool` is always 0 or 1.
- **Consider panic safety** — if the `unsafe` block contains operations that can panic, make sure the data structure remains valid after a panic.
- **Test with Miri** — `cargo +nightly miri test` can detect many `unsafe` problems.

### Common Uses

- Implementing data structures (linked lists, the internals of `Vec`)
- Interoperating with C
- Performance-critical sections

## Example Code

```rust,editable
fn main() {
    // raw pointers
    let mut x = 42;
    let ptr_const: *const i32 = &raw const x;
    let ptr_mut: *mut i32 = &raw mut x;

    unsafe {
        println!("read: {}", *ptr_const);
        *ptr_mut = 100;
        println!("after write: {}", *ptr_mut);
    }

    // unsafe fn
    unsafe fn add_one(ptr: *mut i32) {
        unsafe { *ptr += 1; }
    }

    let mut val = 10;
    // SAFETY: ptr points to a valid, initialized i32, and no other references exist
    unsafe { add_one(&raw mut val); }
    println!("val = {}", val);
}
```

## Recap

- `unsafe` lets you do things the compiler can't verify, but it doesn't turn off all checks.
- The five `unsafe` operations: dereferencing raw pointers, calling `unsafe fn`s, implementing `unsafe trait`s, accessing `static mut`, accessing `union` fields.
- Raw pointers `*const T` / `*mut T`: pointers without borrow-rule protection, not guaranteed to point to valid data. Creating them needs no `unsafe`; dereferencing does.
- `&raw const x` / `&raw mut x`: take a raw pointer directly, without going through a reference.
- Since the 2024 edition, `unsafe fn` bodies also require `unsafe { }` blocks.
- With `unsafe trait`s the danger is in implementing, not using (calling methods needs no `unsafe`).
- The `unsafe` boundary: no matter what safe code calls it, it must never cause undefined behavior.
