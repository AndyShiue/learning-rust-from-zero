# `Ordering` and Sorting

## Goal of This Episode

Meet `Ordering`, the `min`/`max` family of functions, the sorting methods, and how `Reverse` works.

## Concept

### `Ordering`

Chapter 5 covered the `Ord` `trait` — types implementing `Ord` can be compared. `Ord`'s core method is `cmp`, which compares two values and returns `std::cmp::Ordering` — an `enum` with just three values:

```rust,editable
use std::cmp::Ordering;

fn main() {
    match 5.cmp(&3) {
        Ordering::Less => println!("smaller"),
        Ordering::Equal => println!("equal"),
        Ordering::Greater => println!("greater"),
    }
}
```

### `min` / `max`

`std::cmp::min(a, b)` and `std::cmp::max(a, b)` return the smaller or larger of two values, requiring the type to implement `Ord`:

```rust,editable
use std::cmp;

fn main() {
    println!("{}", cmp::min(3, 7)); // 3
    println!("{}", cmp::max(3, 7)); // 7
}
```

### The Trouble with Floats

`f64` doesn't implement `Ord` (Chapter 5 mentioned why: comparing `NAN` with anything is `false`), so you can't use `cmp::min` on it directly.

`f64` only has `PartialOrd`, whose method `partial_cmp` returns `Option<Ordering>` instead of `Ordering` — when `NAN` shows up there's no way to compare, so it can only return `None`.

In that case use `min_by` / `max_by` with custom comparison logic:

```rust,editable
use std::cmp;

fn main() {
    let smaller = cmp::min_by(3.0_f64, 2.5, |a, b| {
        a.partial_cmp(b).unwrap() // if you're sure NAN can't appear, unwrap the Ordering
    });
    println!("{}", smaller); // 2.5

    let bigger = cmp::max_by(3.0_f64, 2.5, |a, b| {
        a.partial_cmp(b).unwrap()
    });
    println!("{}", bigger); // 3
}
```

The closure passed to `min_by` / `max_by` returns an `Ordering` — you decide how to compare.

### `min_by_key` / `max_by_key`

Compare by some key:

```rust,editable
use std::cmp;

fn main() {
    let short = cmp::min_by_key("hello", "hi", |s| s.len());
    println!("{}", short); // "hi"
}
```

### Sorting

`Vec` and slices provide several sorting methods:

```rust,editable
fn main() {
    let mut nums = vec![3, 1, 4, 1, 5];

    // sort: ascending, requires Ord
    nums.sort();
    println!("{:?}", nums); // [1, 1, 3, 4, 5]

    // sort_by: custom comparison; pass a closure returning Ordering
    nums.sort_by(|a, b| b.cmp(a));
    println!("{:?}", nums); // [5, 4, 3, 1, 1]

    // sort_by_key: sort by a key
    let mut words = vec!["banana", "apple", "fig"];
    words.sort_by_key(|w| w.len());
    println!("{:?}", words); // ["fig", "apple", "banana"]
}
```

### `Reverse`

`std::cmp::Reverse` flips the sort order:

```rust,editable
use std::cmp::Reverse;

fn main() {
    let mut nums = vec![3, 1, 4, 1, 5];
    nums.sort_by_key(|&x| Reverse(x));
    println!("{:?}", nums); // [5, 4, 3, 1, 1]
}
```

How does that work? `Reverse` is really just a newtype:

```rust,ignore
pub struct Reverse<T>(pub T);
```

Its `Ord` implementation flips the comparison around:

```rust,ignore
impl<T: Ord> Ord for Reverse<T> {
    fn cmp(&self, other: &Reverse<T>) -> Ordering {
        other.0.cmp(&self.0) // note: other compared against self — reversed
    }
}
```

Normally `5.cmp(&3)` returns `Greater`, but `Reverse(5).cmp(&Reverse(3))` internally does `3.cmp(&5)` and returns `Less`. `sort_by_key` orders by the keys' `cmp`, and once the key is wrapped in `Reverse`, the comparison logic reverses automatically.

Compared to `sort_by(|a, b| b.cmp(a))`, the `Reverse` spelling makes the intent clearer.

## Example Code

```rust,editable
use std::cmp::{self, Reverse};

fn main() {
    // min / max
    println!("min(10, 20) = {}", cmp::min(10, 20));
    println!("max(10, 20) = {}", cmp::max(10, 20));

    // floats need min_by / max_by
    let smaller = cmp::min_by(1.5_f64, 2.3, |a, b| {
        a.partial_cmp(b).unwrap()
    });
    println!("min_by(1.5, 2.3) = {}", smaller);

    // sorting
    let mut scores = vec![85, 92, 78, 95, 88];
    scores.sort();
    println!("ascending: {:?}", scores);

    scores.sort_by_key(|&s| Reverse(s));
    println!("descending: {:?}", scores);

    // sort by string length
    let mut names = vec!["Alice", "Bob", "Charlie", "Dave"];
    names.sort_by_key(|n| n.len());
    println!("by length: {:?}", names);
}
```

## Recap

- `Ordering` has three values: `Less`, `Equal`, `Greater`.
- `cmp::min` / `cmp::max` take the smaller/larger of two values and require `Ord`.
- `f64` has no `Ord`; use `min_by` / `max_by` with custom comparison.
- `min_by_key` / `max_by_key` compare by a key.
- `sort()` sorts ascending, `sort_by()` takes custom comparison, `sort_by_key()` sorts by key.
- `Reverse` is a tuple `struct` whose `Ord` implementation flips the comparison, so sort results reverse with it.
