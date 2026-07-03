# Combining and Slicing

## Goal of This Episode

Learn to combine and trim iterators with `zip`, `enumerate`, `chain`, `take`, `skip`, and `flatten`.

## Concept

### `.zip(iter)` — Pairing Two Iterators

`zip` pairs two iterators "zipper-style," producing tuples:

```rust,noplayground
# fn main() {
    let names = vec!["Alice", "Bob", "Charlie"];
    let scores = vec![90, 85, 92];
    let paired: Vec<_> = names.iter().zip(scores.iter()).collect();
    // [("Alice", 90), ("Bob", 85), ("Charlie", 92)]
# }
```

If the two iterators differ in length, `zip` stops when the shorter one ends.

### `.enumerate()` — Bringing the Index Along

```rust,noplayground
# fn main() {
    let names = vec!["Alice", "Bob", "Charlie"];
    for (i, name) in names.iter().enumerate() {
        println!("Number {}: {}", i, name);
    }
# }
```

`enumerate` wraps each element in an `(index, element)` tuple, indices starting at 0.

### `.chain(iter)` — Joining Two Iterators

`chain` connects two iterators end to end:

```rust,noplayground
# fn main() {
    let first = vec![1, 2, 3];
    let second = vec![4, 5, 6];
    let all: Vec<i32> = first.into_iter().chain(second.into_iter()).collect();
    // [1, 2, 3, 4, 5, 6]
# }
```

### `.take(n)` — Only the First n

```rust,noplayground
# fn main() {
    let first_three: Vec<i32> = (1..=100).into_iter().take(3).collect();
    // [1, 2, 3]
# }
```

### `.skip(n)` — Skipping the First n

```rust,noplayground
# fn main() {
    let after_skip: Vec<i32> = (1..=10).into_iter().skip(7).collect();
    // [8, 9, 10]
# }
```

### `.flatten()` — Squashing Nested Structures

If an iterator's elements are themselves iterators (or `Option`s, `Vec`s, etc.), `flatten` squashes one layer:

```rust,noplayground
# fn main() {
    let nested = vec![vec![1, 2], vec![3, 4], vec![5]];
    let flat: Vec<i32> = nested.into_iter().flatten().collect();
    // [1, 2, 3, 4, 5]
# }
```

`Option` can be `flatten`ed too — `Some(value)` is taken out; `None` is ignored:

```rust,noplayground
# fn main() {
    let options = vec![Some(1), None, Some(3), None, Some(5)];
    let values: Vec<i32> = options.into_iter().flatten().collect();
    // [1, 3, 5]
# }
```

That works because `Option` also implements `IntoIterator`.

## Example Code

```rust,editable
fn main() {
    // zip — pairing names with scores
    let students = vec!["Ming", "Hua", "Mei"];
    let grades = vec![88, 95, 72];
    println!("--- zip ---");
    for (name, grade) in students.iter().zip(grades.iter()) {
        println!("{}: {} points", name, grade);
    }

    // enumerate — with indices
    println!("\n--- enumerate ---");
    let fruits = vec!["apple", "banana", "cherry"];
    for (i, fruit) in fruits.iter().enumerate() {
        println!("Number {}: {}", i + 1, fruit);
    }

    // chain — joining two Vecs
    let morning = vec!["meeting", "writing the report"];
    let afternoon = vec!["coding", "code review"];
    let all_tasks: Vec<&&str> = morning.iter().chain(afternoon.iter()).collect();
    println!("\nToday's schedule: {:?}", all_tasks);

    // take and skip
    let numbers: Vec<i32> = (1..=20).into_iter().collect();
    let first_five: Vec<&i32> = numbers.iter().take(5).collect();
    let last_five: Vec<&i32> = numbers.iter().skip(15).collect();
    println!("\nFirst 5: {:?}", first_five);
    println!("After skipping 15: {:?}", last_five);

    // take + skip combined: the middle stretch
    let middle: Vec<&i32> = numbers.iter().skip(5).take(5).collect();
    println!("Numbers 6~10: {:?}", middle);

    // flatten — squashing a nested Vec
    let matrix = vec![
        vec![1, 2, 3],
        vec![4, 5, 6],
        vec![7, 8, 9],
    ];
    let flat: Vec<i32> = matrix.into_iter().flatten().collect();
    println!("\nFlattened matrix: {:?}", flat);

    // flatten — filtering Options
    let maybe_values = vec![Some(10), None, Some(30), None, Some(50)];
    let real_values: Vec<i32> = maybe_values.into_iter().flatten().collect();
    println!("The ones with values: {:?}", real_values);

    // zip + map combined — the iterator's map arrives next episode
    println!("\n--- zip + map ---");
    let prices = vec![100, 200, 300];
    let quantities = vec![2, 1, 4];
    let grand_total: i32 = prices.iter()
        .zip(quantities.iter())
        .map(|(p, q)| p * q)
        .sum();
    println!("Grand total: {}", grand_total);
}
```

## Recap

- `.zip(iter)` pairs two iterators into tuples, going by the shorter one.
- `.enumerate()` attaches a 0-based index to each element.
- `.chain(iter)` joins two iterators end to end.
- `.take(n)` keeps only the first n elements; `.skip(n)` skips the first n.
- `.flatten()` squashes one layer of nesting (`Vec<Vec<T>>` → `Vec<T>`; works on `Option` too).
- These methods combine freely into powerful data-processing pipelines.
