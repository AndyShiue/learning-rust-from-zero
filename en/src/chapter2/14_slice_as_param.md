# Slices as Parameters

## Goal of This Episode

Use a slice `&[i32]` as a function parameter, so arrays of any length can be passed in.

## Main Text

Last episode we learned slices. This episode covers a super-practical application: **using slices as function parameters**.

### First, the Problem

Suppose you want to write a function that sums an array. If you use an array as the parameter:

```rust,compile_fail
fn sum(nums: [i32; 5]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn main() {
    let a = [1, 2, 3, 4, 5];
    println!("{}", sum(a)); // ✅ Works

    let b = [1, 2, 3];
    println!("{}", sum(b)); // ❌ Nope! b has 3 elements, but the function wants 5
}
```

The problem is `[i32; 5]` — you've hard-coded the length as 5. A 3-element array can't get in.

### The Solution: Use a Slice

```rust,editable
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn main() {
    let a = [1, 2, 3, 4, 5];
    let b = [10, 20, 30];
    let c = [7];

    println!("Sum of a: {}", sum(&a)); // 15
    println!("Sum of b: {}", sum(&b)); // 60
    println!("Sum of c: {}", sum(&c)); // 7
}
```

Change the parameter type from `[i32; 5]` to `&[i32]`, and the function accepts slices of **any length**!

When calling, add `&`: `sum(&a)` means "pass in a slice of `a`."

### You Can Pass Part of a Slice Too

Since the parameter is `&[i32]`, you can pass not only whole arrays but also slices of them:

```rust,editable
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn main() {
    let arr = [1, 2, 3, 4, 5];

    println!("All: {}", sum(&arr));            // 15
    println!("First three: {}", sum(&arr[..3])); // 6
    println!("Last three: {}", sum(&arr[2..]));  // 12
}
```

That's the power of slices — one function, many uses.

### Why Are Slices Better Than Fixed-length Arrays?

| Fixed length `[i32; 5]` | Slice `&[i32]` |
|---|---|
| Accepts exactly 5 elements only | Any length works |
| Changing length means rewriting the function | One function covers all |

In practice, nearly every function that takes an array uses a slice parameter.

## Recap

- Use `&[i32]` instead of `[i32; 5]` for parameters to accept any length.
- When calling, `&arr` and `&arr[1..4]` both work.
- Slice parameters make functions more flexible and more general.
- This is the most common style in real-world Rust.
