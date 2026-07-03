# Iterating over Arrays

## Goal of This Episode

Use a `for` loop to walk through every element in an array.

## Main Text

Last episode we learned to fetch values one at a time with `arr[0]`, `arr[1]`. But if an array has 100 elements, you can't write 100 lines, right? That's when we use a `for` loop to **iterate** over the whole array.

### Basic Syntax

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];

    for x in arr {
        println!("{}", x);
    }
}
```

`for x in arr` means: "Take the elements of `arr` out one by one, putting each into `x`, then run the code in the curly braces."

### Computing with the Elements

```rust,editable
fn main() {
    let scores = [80, 95, 72, 88, 100];

    for score in scores {
        if score >= 90 {
            println!("{} points → Excellent!", score);
        } else {
            println!("{} points → Keep it up!", score);
        }
    }
}
```

### Summing All the Elements

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];
    let mut total = 0;

    for x in arr {
        total += x;
    }

    println!("Total: {}", total);
}
```

First create a mutable accumulator with `let mut total = 0;`, then add each value onto it in the loop.

### `for` `in` a Range vs `for` `in` an Array

The `for i in 0..5` from Chapter 1 iterates over a **range of numbers**. This episode's `for x in arr` iterates over an **array**. Same syntax — only the thing after `in` differs:

```rust,editable
fn main() {
    let arr = [10, 20, 30];

    // Iterating over a range: i is 0, 1, 2 in turn
    for i in 0..3 {
        println!("Index {}: {}", i, arr[i]);
    }

    // Iterating over the array: x is 10, 20, 30 in turn
    for x in arr {
        println!("Value: {}", x);
    }
}
```

When walking an array, `for x in arr` is cleaner, safer, and faster than using indices — no worrying about going out of bounds. For when you need both the index and the value, we'll learn a better way later.

## Recap

- `for x in arr { ... }` iterates over each element of the array.
- Inside the loop you can compute, test, and accumulate with each element.
- `for x in arr` (over an array) and `for i in 0..n` (over a range) share the same syntax; only the thing after `in` differs.
- When iterating over an array, `for x in arr` beats indexing: cleaner, safer, faster.
