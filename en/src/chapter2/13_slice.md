# Slices: `&[T]`

## Goal of This Episode

Use a slice to grab part of an array — like looking at what's inside through a window.

## Main Text

Sometimes you don't need the whole array, just a stretch of it. Say, out of a 5-element array, you only want elements 2 through 4. That's when you use a **slice**.

### Basic Syntax

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];
    let slice = &arr[1..4];
    println!("{:?}", slice);
}
```

Like arrays and tuples, slices can only be printed with `{:?}`, not `{}`.

`&arr[1..4]` means: "Starting at index 1, up to just **before** index 4."

- Index 1 → value 2 (included).
- Index 2 → value 3 (included).
- Index 3 → value 4 (included).
- Index 4 → value 5 (**not included**).

So the result is `[2, 3, 4]`.

### The Range Notations

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];

    let a = &arr[0..3];  // [1, 2, 3]       from 0 up to 3 (3 excluded)
    let b = &arr[0..=2]; // [1, 2, 3]       from 0 to 2 (2 included)
    let c = &arr[2..];   // [3, 4, 5]       from 2 to the end
    let d = &arr[..3];   // [1, 2, 3]       from the start up to 3 (3 excluded)
    let e = &arr[..];    // [1, 2, 3, 4, 5] the whole array

    println!("{:?}", a);
    println!("{:?}", b);
    println!("{:?}", c);
    println!("{:?}", d);
    println!("{:?}", e);
}
```

- `1..4` → from 1 up to 4 (4 excluded).
- `1..=3` → from 1 to 3 (3 **included**) — remember `..=` from Chapter 1, Episode 20? Same usage.
- `2..` → from 2 to the end.
- `..3` → from the start up to 3 (3 excluded).
- `..` → the whole thing.

### A Slice Is a "Window," Not a "Copy"

Here's an important idea: a slice does **not** copy the data out. It "points at a stretch of the original array." Like looking at things in a room through a window — the things are still in the room; you're just viewing them through the window.

```rust,editable
fn main() {
    let arr = [10, 20, 30, 40, 50];
    let slice = &arr[1..4];

    println!("Array: {:?}", arr);
    println!("Slice: {:?}", slice);
}
```

### What's That `&`?

You may have noticed the `&` in front of the slice. That symbol stands for "borrowing," one of Rust's most important concepts. No need to dig deep right now — just remember "slices need `&`," and we'll explain in detail later.

For now, all you need to know: when writing a slice, put `&` in front.

### The Type of a Slice

Remember that an array's type is `[i32; 5]` (the type includes the length)? A slice's type is `&[i32]` — **no length**:

```rust,editable
fn main() {
    let arr: [i32; 5] = [1, 2, 3, 4, 5];
    let slice: &[i32] = &arr[1..4];
    println!("{:?}", slice);
}
```

`&[i32]` means "a slice of `i32`s," regardless of length. This is the biggest difference between slices and arrays — an array's length is part of its type (`[i32; 3]` and `[i32; 5]` are different types), but a slice doesn't care about length: `&[i32]` can point to a contiguous stretch of any length.

### Iterating over a Slice

Slices can be walked with `for` too:

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];
    let slice = &arr[1..4];

    for x in slice {
        println!("{}", x);
    }
}
```

### Compound Types

Having learned slices, let's take stock: so far we've met two categories of types.

**Primitive types:** `i32`, `f64`, `bool`, `char`, and so on — each value is a single standalone thing.

**Compound types:** types that combine other types. We've now learned three:

- **tuple**: `(i32, f64, bool)` — can hold different types.
- **array**: `[i32; 5]` — one type, fixed length.
- **slice**: `&[i32]` — one type, any length.

The types inside a compound type don't have to be primitive — compound types can nest inside other compound types:

```rust,editable
fn main() {
    // An array holding tuples
    let pairs: [(i32, bool); 3] = [(1, true), (2, false), (3, true)];
    println!("{:?}", pairs);

    // A tuple holding arrays
    let t: ([i32; 3], [i32; 3]) = ([1, 2, 3], [4, 5, 6]);
    println!("{:?}", t);

    // An array holding arrays
    let grid: [[i32; 2]; 3] = [[1, 2], [3, 4], [5, 6]];
    println!("{:?}", grid);

    // Slices are compound types too
    let arr: [i32; 5] = [10, 20, 30, 40, 50];
    let slice: &[i32] = &arr[1..4];
    println!("{:?}", slice);

    // A tuple holding slices
    let pair: (&[i32], &[i32]) = (&arr[..2], &arr[3..]);
    println!("{:?}", pair);
}
```

## Recap

- A slice takes part of an array with `&arr[start..end]` or `&arr[start..=end]`.
- `start..end` means "start included, end excluded."
- `start..=end` means "both start and end included."
- A slice is a "window" onto the array, not a copy.
- A slice's type is `&[i32]` (no length); an array's type is `[i32; 5]` (with length).
- The leading `&` stands for borrowing — detailed explanation coming later.
- Slices can be iterated with `for` as well.
- Tuples, arrays, and slices are all **compound types** — they can contain other types, including compound ones.
