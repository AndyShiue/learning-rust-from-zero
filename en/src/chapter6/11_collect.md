# Collecting

## Goal of This Episode

Learn to collect an iterator into various collection types with `.collect()`.

## Concept

We wouldn't ordinarily spend this many episodes introducing methods, but iterators are simply too important — among the tools most used in everyday Rust — so the next few episodes take their time. Even then, plenty of methods will inevitably be missed. When you need more, consult [the official documentation's `Iterator` `trait` page](https://doc.rust-lang.org/std/iter/trait.Iterator.html).

### `.collect()` — the Iterator's Terminus

We've been building iterators, but an iterator is itself **lazy** (Episode 15 goes deep on this) — nothing actually runs until someone "pulls" on it. `.collect()` is the most common pull: gather all the iterator's elements into a collection.

```rust,noplayground
# fn main() {
    let v: Vec<i32> = (1..=5).into_iter().collect();
# }
```

### Collecting into a `String`

`.collect()` isn't limited to `Vec`. If the iterator produces `char`s or `&str`s, it can collect straight into a `String`:

```rust,editable
fn main() {
    let chars = vec!['R', 'u', 's', 't'];
    let word: String = chars.into_iter().collect();
    println!("{}", word); // "Rust"
}
```

### `.last()` — Taking the Final Element

`.last()` consumes the whole iterator and returns the final element (an `Option<T>`):

```rust,editable
fn main() {
    let v = vec![10, 20, 30];
    let last = v.iter().last();
    println!("{:?}", last); // Some(&30)
}
```

Note it must walk the entire iterator to know which element is last.

## Example Code

```rust,editable
fn main() {
    // Basic collect — Range into Vec
    let numbers: Vec<i32> = (1..=10).into_iter().collect();
    println!("1 through 10: {:?}", numbers);

    // The turbofish syntax
    let numbers2 = (1..=5).into_iter().collect::<Vec<i32>>();
    println!("turbofish: {:?}", numbers2);

    // Collecting into a String
    let greeting: String = vec!['h', 'e', 'l', 'l', 'o'].into_iter().collect();
    println!("String: {}", greeting);

    // .last()
    let last_num = (1..=100).into_iter().last();
    println!("\nThe last of 1..=100: {:?}", last_num);

    let empty: Vec<i32> = vec![];
    let last_empty = empty.iter().last();
    println!("last of an empty Vec: {:?}", last_empty);
}
```

## Recap

- `.collect()` gathers an iterator's elements into a target collection type.
- Tell Rust the target type with an annotation `let v: Vec<i32>` or the turbofish `.collect::<Vec<i32>>()`.
- Collection targets include `Vec`, `String`, and many other types.
- `.last()` consumes the whole iterator, returning the final element wrapped in `Some`.
