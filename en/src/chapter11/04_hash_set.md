# `HashSet<T>`

## Goal of This Episode

Learn to work with set operations using `HashSet`.

## Concept

### Motivation

A `HashMap` stores key-value pairs, but sometimes you only care about "is it there or not" and not any associated value — say, tracking which users are online, or which words have appeared. That's what `HashSet` is for.

### The Essence

A `HashSet` is really just a `HashMap` with only keys and no values. So its elements likewise require `Eq + Hash`.

### Basic Operations

```rust,editable
use std::collections::HashSet;

fn main() {
    let mut fruits = HashSet::new();
    fruits.insert("apple");
    fruits.insert("banana");
    fruits.insert("apple"); // duplicate — won't be added

    println!("{}", fruits.contains("apple")); // true
    println!("{}", fruits.len());             // 2

    fruits.remove("banana");
}
```

### Building from an `Iterator`

```rust,editable
use std::collections::HashSet;

fn main() {
    let nums: HashSet<i32> = vec![1, 2, 3, 2, 1].into_iter().collect();
    println!("{:?}", nums); // {1, 2, 3} — duplicates removed automatically
}
```

### Set Operations

This is where `HashSet` shines:

```rust,noplayground
use std::collections::HashSet;

fn main() {
    let a: HashSet<i32> = [1, 2, 3].into_iter().collect();
    let b: HashSet<i32> = [2, 3, 4].into_iter().collect();

    // intersection: in both
    let intersection: HashSet<_> = a.intersection(&b).copied().collect();
    // {2, 3}

    // union: everything combined
    let union_set: HashSet<_> = a.union(&b).copied().collect();
    // {1, 2, 3, 4}

    // difference: in a but not in b
    let diff: HashSet<_> = a.difference(&b).copied().collect();
    // {1}

    // symmetric difference: in exactly one side
    let sym_diff: HashSet<_> = a.symmetric_difference(&b).copied().collect();
    // {1, 4}
}
```

### Operators

The advanced language features chapter covered operator overloading — `HashSet` puts it to use. You can apply `&` `|` `-` `^` to references of two `HashSet`s for set operations:

```rust,noplayground
# use std::collections::HashSet;
#
# fn main() {
#     let a: HashSet<i32> = [1, 2, 3].into_iter().collect();
#     let b: HashSet<i32> = [2, 3, 4].into_iter().collect();
    let intersection = &a & &b; // intersection
    let union_set    = &a | &b; // union
    let diff         = &a - &b; // difference
    let sym_diff     = &a ^ &b; // symmetric difference
# }
```

### Other Relations

```rust,editable
use std::collections::HashSet;

fn main() {
    let small: HashSet<i32> = [1, 2].into_iter().collect();
    let big: HashSet<i32> = [1, 2, 3, 4].into_iter().collect();

    println!("{}", small.is_subset(&big));   // true
    println!("{}", big.is_superset(&small)); // true
    println!("{}", small.is_disjoint(&big)); // false (they intersect)
}
```

### Iterating

Like `HashMap`, iteration order isn't fixed:

```rust,noplayground
# use std::collections::HashSet;
#
# fn main() {
#     let fruits = HashSet::<&str>::new();
    for fruit in &fruits {
        println!("{}", fruit);
    }
# }
```

## Example Code

```rust,editable
use std::collections::HashSet;

fn main() {
    let class_a: HashSet<&str> = ["Alice", "Bob", "Charlie", "Dave"].into_iter().collect();
    let class_b: HashSet<&str> = ["Charlie", "Dave", "Eve", "Frank"].into_iter().collect();

    println!("Class A: {:?}", class_a);
    println!("Class B: {:?}", class_b);

    // people in both classes
    let both = &class_a & &class_b;
    println!("in both: {:?}", both);

    // everyone
    let all = &class_a | &class_b;
    println!("everyone: {:?}", all);

    // people only in class A
    let only_a = &class_a - &class_b;
    println!("only in A: {:?}", only_a);

    // removing duplicates
    let words = vec!["hello", "world", "hello", "rust", "world"];
    let unique: HashSet<_> = words.into_iter().collect();
    println!("unique words: {:?}", unique);
}
```

## Recap

- `HashSet<T>` is a keys-only `HashMap`; elements don't repeat.
- Elements must implement `Eq + Hash`.
- `insert` adds, `contains` checks, `remove` removes.
- Set operations: `intersection`, `union`, `difference`, `symmetric_difference`.
- Operators work too: `&` (intersection), `|` (union), `-` (difference), `^` (symmetric difference).
- `is_subset`, `is_superset`, `is_disjoint` test the other relations.
