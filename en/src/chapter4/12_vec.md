# `Vec` Basics

## Goal of This Episode

Learn to use `Vec` — an array that can grow dynamically.

## Concept

### The Limits of Arrays

In Chapter 2 we learned arrays, `[i32; 5]` — but an array's size is fixed, settled at declaration, with no adding or removing afterward.

What if we need a collection whose **size can change**? Say, a user entering data record by record, or a program accumulating results as it runs.

That calls for **`Vec`**. A `Vec` is like a **stretchable array**, with its data on the heap.

### Creating a `Vec`

The simplest way is the `vec!` macro:

```rust,noplayground
# fn main() {
    let nums = vec![1, 2, 3, 4, 5];
# }
```

That creates a `Vec` holding five `i32`s. Rust infers the type from the values you put in.

Like the array's `[0; 5]`, `vec!` supports the "repeat N times" form too:

```rust,noplayground
# fn main() {
    let zeros = vec![0; 10]; // ten 0s
# }
```

You can also create an empty `Vec` and add items one by one:

```rust,noplayground
# fn main() {   
    let mut nums = Vec::new();
    nums.push(10);
    nums.push(20);
# }
```

Rust infers the type at your first `push`.

### Indexing and Iterating

Indexing a `Vec` works like an array, with `[i]`:

```rust,editable
fn main() {
    let nums = vec![10, 20, 30];
    println!("{}", nums[0]); // 10
    println!("{}", nums[2]); // 30
}
```

Iterating also works like arrays, with `for`:

```rust,editable
fn main() {
    let nums = vec![10, 20, 30];
    for n in &nums {
        println!("{}", n);
    }
}
```

Note: we iterate with `&nums` (borrowing) so `nums` doesn't get moved away. Details next episode.

### `push`: Adding New Elements

```rust,editable
fn main() {
    let mut fruits = Vec::new();
    fruits.push("apple");
    fruits.push("banana");
    fruits.push("cherry");
    println!("{:?}", fruits);
}
```

`push` appends the new element at the end. Note that the `Vec` must be `let mut` to `push`.

### `len`: Getting the Length

```rust,editable
fn main() {
    let nums = vec![1, 2, 3];
    println!("Length: {}", nums.len());
}
```

## Example Code

```rust,editable
fn main() {
    // Creating with vec!
    let scores = vec![85, 92, 78, 95, 88];
    println!("Scores: {:?}", scores);
    println!("First entry: {}", scores[0]);
    println!("{} entries in total", scores.len());

    // An empty Vec, filled with push
    let mut names = Vec::new();
    names.push("Ming");
    names.push("Hana");
    names.push("Wang");
    println!("Roster: {:?}", names);

    // Iterating
    println!("Listing one by one:");
    for name in &names {
        println!("  - {}", name);
    }

    // Iterating with for and summing
    let nums = vec![10, 20, 30, 40, 50];
    let mut total = 0;
    for x in &nums {
        total += x;
    }
    println!("Total = {}", total);

    // A Vec can keep growing
    let mut growing = Vec::new();
    for i in 0..5 {
        growing.push(i * 10);
    }
    println!("Built dynamically: {:?}", growing);
}
```

## Recap

- **`Vec`** is a dynamically growable array whose data lives on the heap.
- `vec![1, 2, 3]` creates a `Vec` with initial values; `vec![0; 10]` creates ten 0s (like the array's `[0; 10]`).
- `Vec::new()` creates an empty `Vec`.
- `push` appends an element at the end (requires `let mut`).
- Index with `v[0]`, `v[1]`, etc.; get the length with `v.len()` (a method returning the element count).
- Iterate with `for x in &v` (borrowing, no move).
- `Vec` handles a lot like an array, but its size can change.
