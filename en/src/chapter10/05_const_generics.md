# `const` Generics

## Goal of This Episode

Learn to use constant values as generic parameters and handle arrays of any length.

## Concept

### The Problem: A Function over Arrays of Any Length

`[i32; 3]` and `[i32; 5]` are different types — the length is part of the type. If you want a function that prints an array of any length, surely you don't have to write one per length?

### `const` generics

Generic parameters aren't limited to types — they can also be **constant values**:

```rust,editable
fn print_array<const N: usize>(arr: [i32; N]) {
    for x in arr {
        println!("{}", x);
    }
}

fn main() {
    print_array([1, 2, 3]);        // N = 3
    print_array([10, 20, 30, 40]); // N = 4
}
```

`<const N: usize>` declares a constant generic parameter `N` of type `usize`. Like a type parameter `<T>`, the compiler generates one copy of the code for each distinct `N`.

### How It Differs from Slices

You might think: why not just pass `&[i32]`? True — if all you need is to read a sequence of data, slices are more flexible. But `const` generics can do things slices can't:

**Returning a fixed-length array:**

```rust,noplayground
fn zeros<const N: usize>() -> [i32; N] {
    [0; N]
}

fn main() {
    let a: [i32; 3] = zeros();
    let b: [i32; 10] = zeros();
}
```

A slice can't be returned as `[T]` (a DST), but `[T; N]` can.

**Guaranteeing lengths at the type level:**

```rust,noplayground
fn add_arrays<const N: usize>(a: [i32; N], b: [i32; N]) -> [i32; N] {
    let mut result = [0; N];
    for i in 0..N {
        result[i] = a[i] + b[i];
    }
    result
}
#
# fn main() {}
```

The two parameters are guaranteed at compile time to have the same length. Slices can't do that.

### On `struct`s

```rust,noplayground
struct Matrix<const ROWS: usize, const COLS: usize> {
    data: [[f64; COLS]; ROWS],
}
#
# fn main() {}
```

### Expression Syntax

If the value in a `const` generic position isn't a simple literal or path, wrap it in `{}`:

```rust,noplayground
fn example<const N: usize>() -> [i32; N] { [0; N] }

fn main() {
    let a = example::<3>();         // literal, no {} needed
    let b = example::<{ 1 + 2 }>(); // expression, needs {}
}
```

### Combined with `const fn`

The `const fn` we just learned can also supply a `const` generic's value:

```rust,noplayground
const fn double(n: usize) -> usize { n * 2 }

fn zeros<const N: usize>() -> [i32; N] { [0; N] }

fn main() {
    let c = zeros::<{ double(3) }>(); // [i32; 6], a const fn as the value
}
```

## Example Code

```rust,editable
fn sum<const N: usize>(arr: [i32; N]) -> i32 {
    let mut total = 0;
    for i in 0..N {
        total += arr[i];
    }
    total
}

fn filled<T: Copy, const N: usize>(value: T) -> [T; N] {
    [value; N]
}

fn main() {
    println!("sum([1, 2, 3]) = {}", sum([1, 2, 3]));
    println!("sum([10, 20]) = {}", sum([10, 20]));

    let ones: [i32; 5] = filled(1);
    println!("{:?}", ones);

    let hellos: [&str; 3] = filled("hello");
    println!("{:?}", hellos);

    // expression syntax
    let zeros: [i32; { 2 + 3 }] = filled(0);
    println!("{:?}", zeros);
}
```

## Recap

- Generic parameters can be constant values: `<const N: usize>`.
- The most common use: handling arrays of any length, `[T; N]`.
- Compared to slices: `const` generics can return fixed-length arrays and guarantee lengths at the type level.
- Wrap expressions in `{}`: `Foo::<{ 1 + 2 }>`.
- They combine nicely with `const fn`.
