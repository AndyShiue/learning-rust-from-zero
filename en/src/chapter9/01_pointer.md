# Pointers

## Goal of This Episode

Understand the concept of memory addresses, and what a pointer is at the low level.

## Concept

In earlier chapters, using `&T`, `Box<T>`, and `Rc<T>`, we cared about "who owns the data" and "who's borrowing." This episode switches angles — what are these things actually in memory?

The DST introduction in Appendix I touched on DSTs and fat pointers. If that felt hazy at the time, that's normal — we hadn't formally introduced pointers yet. This episode fills in that foundation.

> This chapter uses a simplified model of memory and addresses. What compilers and hardware do during actual execution is much more complex, but we will not go into those details here.

### Memory Addresses

While a program runs, every variable sits somewhere in memory, and every location has a number — its **address**. What `&x` obtains is `x`'s address. The `{:p}` format prints it out for inspection:

```rust,editable
fn main() {
    let x: i32 = 42;
    println!("{:p}", &x); // e.g. 0x7ffd5e8a3b4c
}
```

That hexadecimal number is `x`'s address in memory.

### The True Face of `&T`

The value `&x` produces is, generally speaking, `x`'s memory address. What the `&T` type stores is, at bottom, that address-number. When you pass `&x` into a function, what's passed isn't `x`'s contents — it's `x`'s address.

### Pointer Sizes

In most cases, an `&T` occupies 8 bytes — the size of one address on a 64-bit system. Verify with `std::mem::size_of`:

```rust,editable
use std::mem::size_of;

fn main() {
    println!("{}", size_of::<i32>());          // 4
    println!("{}", size_of::<[i32; 1000]>());  // 4000
    println!("{}", size_of::<&i32>());         // 8
    println!("{}", size_of::<&[i32; 1000]>()); // 8
    println!("{}", size_of::<Box<i32>>());     // 8
}
```

The `&T` and `Box<T>` values above all point to `Sized` types. Under this condition, they are the same size because they only store addresses. Data an `&T` points at may be on the stack or the heap, while an owning `Box<T>` always points into the heap. Wherever they point, the address itself is one size. So when `T` is large, passing an address is lighter than copying the whole `T` — at the cost of an extra layer of indirection on every access.

### Dereferencing

With an address in hand, what can we do? The `*` operator **dereferences**, fetching the contents at the address:

```rust,editable
fn main() {
    let x = 42;
    let r = &x;
    println!("{}", *r); // Fetching the value via the address: 42
}
```

Dereferencing isn't free. Most of the time the cost is tiny, but knowing it exists is worthwhile.

### Fat Pointers

The DST introduction in Appendix I explained that `[T]` and `str` are types of indeterminate size, unable to sit directly in variables, usually handled through `&[T]`, `&str`, `Box<[T]>`, and the like. But with no fixed size, an address alone isn't enough. Picture it: you're handed an address and told a contiguous run of `i32` data starts there — but where does it end? Memory itself won't say; an address is only a starting point. So besides the address, a length must also be recorded to know how far the data extends. Hence `&[T]` and `&str` occupy 16 bytes:

```rust,editable
use std::mem::size_of;

fn main() {
    println!("{}", size_of::<&i32>());   // 8 (address)
    println!("{}", size_of::<&[i32]>()); // 16 (address + length)
    println!("{}", size_of::<&str>());   // 16 (address + length)
}
```

## Example Code

```rust,editable
use std::mem::size_of;

fn main() {
    let x: i32 = 42;
    let r: &i32 = &x;

    // Printing the address
    println!("x's address: {:p}", &x);
    println!("The value r stores: {:p}", r); // Same as above

    // Dereferencing
    println!("x's value obtained through r: {}", *r);

    // Smart pointers dereference too
    let b = Box::new(99);
    println!("The value in the Box: {}", *b);

    // Pointer sizes
    println!("--- Ordinary pointers ---");
    println!("i32 size: {} bytes", size_of::<i32>());
    println!("&i32 size: {} bytes", size_of::<&i32>());
    println!("[i32; 1000] size: {} bytes", size_of::<[i32; 1000]>());
    println!("&[i32; 1000] size: {} bytes", size_of::<&[i32; 1000]>());
    println!("Box<i32> size: {} bytes", size_of::<Box<i32>>());

    // Fat pointers
    println!("--- Fat pointers ---");
    println!("&[i32] size: {} bytes", size_of::<&[i32]>());
    println!("&str size: {} bytes", size_of::<&str>());
    println!("Box<[i32]> size: {} bytes", size_of::<Box<[i32]>>());
}
```

## Recap

- At the low level, `&T` is a memory address — essentially a number.
- On 64-bit systems, in most cases `&T` and `Box<T>` are 8 bytes — one address's size.
- `*` dereferences, fetching the contents at an address, with one layer of indirection as its cost.
- `&[T]` and `&str` are fat pointers, occupying 16 bytes (address + length), since DSTs have no fixed size.
