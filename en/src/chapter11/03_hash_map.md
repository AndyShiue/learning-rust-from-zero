# `HashMap<K, V>`

## Goal of This Episode

Learn to store and look up key-value data with `HashMap`.

## Concept

### Motivation

If you want to look up a score by name or a user by ID, a `Vec` can certainly do it — store a pile of `(name, score)` tuples and walk from the start until you find the matching name. But the more data, the slower that gets.

`HashMap<K, V>` solves this. It uses a hash function to map keys to memory locations, so no matter how much data it holds, looking up a key takes nearly constant time.

### Creation and Basic Operations

```rust,editable
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();
    scores.insert("Alice", 95);
    scores.insert("Bob", 80);

    println!("{:?}", scores.get("Alice")); // Some(&95)
    println!("{:?}", scores.get("Eve"));   // None
}
```

`insert` puts a pair in; `get` looks up and returns `Option<&V>` (`None` if the key doesn't exist); `remove` deletes and returns `Option<V>` (`Some(removed value)` if the key existed, `None` otherwise).

Calling `insert` again with the same key overwrites the old value.

### Building from an `Iterator` with `collect`

```rust,noplayground
use std::collections::HashMap;

fn main() {
    let scores: HashMap<&str, i32> = vec![("Alice", 95), ("Bob", 80)]
        .into_iter()
        .collect();
}
```

### Iterating

```rust,editable
use std::collections::HashMap;

fn main() {
    let scores: HashMap<&str, i32> = vec![("Alice", 95), ("Bob", 80)]
        .into_iter()
        .collect();
    for (name, score) in &scores {
        println!("{}: {}", name, score);
    }
}
```

Note that the iteration order is **not fixed** — it can differ between runs. If you need a fixed order, use `BTreeMap` (introduced later).

### What `Hash` Is

A `HashMap` needs to find the value for a key quickly. Its trick: feed the key into a **hash function** to compute a number (the hash value), and use that number to decide where in memory the value goes. On lookup, it hashes the key again and jumps straight to that location — no scanning one by one.

So the key type must implement the `Hash` trait — which tells the `HashMap` how to hash that type.

### Key Requirements: `Eq + Hash`

Besides `Hash`, keys also need `Eq`. Different keys can land in the same location, so the `HashMap` needs `==` to confirm the key it found is really the one you asked for.

Most basic types (integers, `bool`, `char`, `&str`, `String`) already implement `Eq + Hash`. `f64` has no `Eq` (because of `NAN`), so it can't be a key.

### Implementing `Hash` for Your Own Types

`Hash` can be derived:

```rust,noplayground
use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq, Hash)]
struct Student {
    name: String,
    grade: i32,
}

fn main() {
    let mut map = HashMap::new();
    map.insert(Student { name: String::from("Alice"), grade: 90 }, "honors");
}
```

Note that you need `PartialEq`, `Eq`, and `Hash` all together — since `Eq: PartialEq`, all three are required.

As a rule of thumb, whenever you `derive` `PartialEq` and `Eq`, it's a good idea to `derive` `Hash` along with them. It costs nothing extra, and your type won't need revisiting later when it has to serve as a `HashMap` key.

### The `entry` API

"Leave it if present, insert if not" is a very common need:

```rust,noplayground
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();
    scores.insert("Alice", 95);

    scores.entry("Alice").or_insert(0); // Alice exists — untouched
    scores.entry("Eve").or_insert(0);   // Eve doesn't — insert 0
}
```

`or_insert` returns a `&mut V`, so you can modify it directly. This is especially handy for counting:

```rust,noplayground
# use std::collections::HashMap;
#
# fn main() {
    let words = vec!["hello", "world", "hello", "rust"];
    let mut counts = HashMap::new();

    for word in words {
        let count = counts.entry(word).or_insert(0);
        *count += 1;
    }
    // {"hello": 2, "world": 1, "rust": 1}
# }
```

### Other Common Methods

`HashMap` has a few more methods you'll use often:

- `contains_key(&key)`: checks whether a key exists, returns `bool`.
- `len()`: how many key-value pairs there are.
- `is_empty()`: whether it's empty.
- `keys()`: an iterator over all keys
- `values()`: an iterator over all values

## Example Code

```rust,editable
use std::collections::HashMap;

fn main() {
    // count how many times each character appears
    let text = "hello world";
    let mut char_counts = HashMap::new();

    for c in text.chars() {
        if c == ' ' { continue; }
        let count = char_counts.entry(c).or_insert(0);
        *count += 1;
    }

    // print the results (order not fixed)
    for (ch, count) in &char_counts {
        println!("'{}': {} times", ch, count);
    }

    // find the most frequent character
    if let Some((ch, count)) = char_counts.iter().max_by_key(|(_, count)| *count) {
        println!("most frequent is '{}', {} times", ch, count);
    }
}
```

## Recap

- `HashMap<K, V>` looks up values by key in nearly constant time regardless of size.
- `insert` adds, `get` looks up (returns `Option<&V>`), `remove` deletes.
- Keys must implement `Eq + Hash`; `Hash` can be `derive`d.
- `f64` can't be a key (no `Eq`).
- `entry().or_insert()` is the idiom for "insert only if absent"; it returns `&mut V`.
- Iteration order is not fixed.
