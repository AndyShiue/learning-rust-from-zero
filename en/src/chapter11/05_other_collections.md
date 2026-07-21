# A Brief Look at Other Collections

## Goal of This Episode

Meet `BTreeMap`, `BTreeSet`, and `VecDeque`.

## Concept

`HashMap` and `HashSet` are the most commonly used collections, but the standard library has other options.

### `BTreeMap`

The difference from `HashMap`: the keys are **ordered**. Iteration follows the keys' sort order, not a random one:

```rust,editable
use std::collections::BTreeMap;

fn main() {
    let mut scores = BTreeMap::new();
    scores.insert("Charlie", 70);
    scores.insert("Alice", 90);
    scores.insert("Bob", 85);

    for (name, score) in &scores {
        println!("{}: {}", name, score);
    }
    // always alphabetical: Alice, Bob, Charlie
}
```

The cost: keys must implement `Ord` (rather than `Hash + Eq`). On lookup speed, `HashMap` is nearly constant regardless of size; `BTreeMap` gets slightly slower with more data, but it's still fast.

### `BTreeSet`

`BTreeSet` is a keys-only `BTreeMap`, in the same relationship as `HashSet` is to `HashMap`. Elements are ordered, and iteration outputs them in order:

```rust,editable
use std::collections::BTreeSet;

fn main() {
    let mut set = BTreeSet::new();
    set.insert(3);
    set.insert(1);
    set.insert(2);

    for x in &set {
        print!("{} ", x);
    }
    // 1 2 3
}
```

All of `HashSet`'s set operations (intersection, union, etc.) exist on `BTreeSet` too.

### Which One When

- Don't care about order → `HashMap` / `HashSet` (faster).
- Need ordered iteration, or need the smallest/largest key → `BTreeMap` / `BTreeSet`.

### `VecDeque`

A `Vec` can only `push` / `pop` efficiently at the tail. `insert` or `remove` at the head means shifting every later element over by one — the more data, the slower.

`VecDeque` (a double-ended queue) is efficient at both the head and the tail, with nearly constant speed no matter the size:

```rust,editable
use std::collections::VecDeque;

fn main() {
    let mut deque = VecDeque::new();
    deque.push_back(1);
    deque.push_back(2);
    deque.push_front(0);

    println!("{:?}", deque); // [0, 1, 2]

    deque.pop_front(); // removes 0
    deque.pop_back();  // removes 2
    println!("{:?}", deque); // [1]
}
```

### When to Use `VecDeque`

When you need a first-in-first-out (FIFO) queue, or frequent operations at both ends. If you only touch the tail, `Vec` is enough.

## Example Code

```rust,editable
use std::collections::{BTreeMap, VecDeque};

fn main() {
    // BTreeMap: ordered key-value
    let mut scores = BTreeMap::new();
    scores.insert("Charlie", 70);
    scores.insert("Alice", 90);
    scores.insert("Bob", 85);
    scores.insert("Dave", 60);

    // always prints alphabetically
    for (name, score) in &scores {
        println!("{}: {}", name, score);
    }

    // VecDeque: double-ended queue
    let mut queue = VecDeque::new();
    queue.push_back("first");
    queue.push_back("second");
    queue.push_back("third");

    // take from the front — first in, first out
    while let Some(item) = queue.pop_front() {
        println!("processing: {}", item);
    }
}
```

## Recap

- `BTreeMap`: iteration follows key order; keys must implement `Ord`.
- `BTreeSet`: iteration follows element order; elements must implement `Ord`.
- Use the `BTree` family for ordered iteration; otherwise the `Hash` family (faster).
- `VecDeque`: double-ended queue, fast at both ends.
- `Vec` is only fast at the tail; head operations are slow (all elements shift).
