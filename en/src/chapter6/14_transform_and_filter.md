# Transforming and Filtering

## Goal of This Episode

Learn the iterator's most-used transformation and filtering methods, and how chained calls build powerful data pipelines.

## Concept

### `.map(f)` — Transforming Each Element

`map` applies a closure to each element, producing transformed new elements:

```rust,noplayground
# fn main() {
    let doubled: Vec<i32> = vec![1, 2, 3].iter().map(|x| x * 2).collect();
    // [2, 4, 6]
# }
```

Careful! `.iter()` produces `&T`, so the closure's parameter is `&i32`. If you'd rather not deal with references, pair it with `.copied()` (coming right up).

### `.flat_map(f)` — `map` + `flatten`

`flat_map` equals `map` followed by `flatten` (last episode's). Each element becomes an iterator via the closure, and everything gets squashed flat:

```rust,noplayground
# fn main() {
    let words = vec!["abc", "de", "f"];
    let chars: Vec<char> = words.iter().flat_map(|s| s.chars()).collect();
    // ['a', 'b', 'c', 'd', 'e', 'f']
# }
```

Remember `and_then` on `Option` and `Result` from Episode 7? What `flat_map` does on iterators is essentially the same — "transform, and since the result is itself a container, flatten."

### `.filter(pred)` — Filtering Elements

`filter` keeps only the elements for which the closure returns `true`:

```rust,noplayground
# fn main() {
    let evens: Vec<&i32> = vec![1, 2, 3, 4, 5].iter().filter(|&&x| x % 2 == 0).collect();
    // [&2, &4]
# }
```

`filter`'s closure receives `&&T` (`.iter()` already gives `&T`, and `filter` borrows once more, making `&&T`). This trips up beginners regularly, but it becomes second nature with practice.

### `.copied()` and `.cloned()`

When an iterator produces references (`&T`) but you want values (`T`), these two methods copy each element out:

- `.copied()` — requires `T: Copy`; copies each `&T` into a `T`.
- `.cloned()` — requires `T: Clone`; calls `.clone()` on each `&T` to get a `T`.

```rust,noplayground
# fn main() {
    let numbers = vec![1, 2, 3];
    let owned: Vec<i32> = numbers.iter().copied().collect();
    // From &i32 to i32
# }
```

`.copied()` often pairs with `.filter()`, dodging the `&&T` annoyance:

```rust,noplayground
# fn main() {
    let evens: Vec<i32> = vec![1, 2, 3, 4, 5]
        .iter()
        .copied()
        .filter(|x| x % 2 == 0)
        .collect();
    // [2, 4] — much cleaner!
# }
```

### `.rev()` — Reversing the Iteration Order

```rust,noplayground
# fn main() {
    let reversed: Vec<i32> = (1..=5).into_iter().rev().collect();
    // [5, 4, 3, 2, 1]
# }
```

`.rev()` requires the iterator to implement the `DoubleEndedIterator` `trait` — meaning it can take elements from both ends. `Vec`, arrays, and the like support it, but iterators from `from_fn` don't (no concept of a "tail end").

### The Power of Chaining

Iterator methods chain freely into data-processing pipelines:

```rust,noplayground
# fn main() {
#     let names = vec!["Andy", "Bob", "Cindy", "David"];
    let result: Vec<String> = names
        .iter()
        .enumerate()
        .filter(|(_, name)| name.len() > 3)
        .map(|(i, name)| format!("#{}: {}", i + 1, name))
        .collect();
# }
```

Each step does one small thing; strung together, they accomplish very complex operations. And because iterators are lazy (next episode), no extra `Vec`s materialize along the way.

## Example Code

```rust,editable
fn main() {
    let scores = vec![55, 82, 91, 47, 73, 88, 69, 95];

    // map — 5 bonus points per score (a curve adjustment)
    let adjusted: Vec<i32> = scores.iter().map(|s| s + 5).collect();
    println!("After the bonus: {:?}", adjusted);

    // flat_map — splitting each word into characters
    let words = vec!["Rust", "rocks"];
    let all_chars: Vec<char> = words.iter().flat_map(|w| w.chars()).collect();
    println!("All the characters: {:?}", all_chars);

    // flat_map resembling and_then — keep successful parses, drop failures
    let inputs = vec!["42", "not_a_number", "7"];
    let parsed: Vec<i32> = inputs.iter().flat_map(|s| s.parse::<i32>()).collect();
    println!("Successfully parsed: {:?}", parsed);

    // filter — sifting out the passing scores
    let passing: Vec<i32> = scores.iter().copied().filter(|&s| s >= 60).collect();
    println!("Passing: {:?}", passing);

    // copied — from &i32 to i32
    let max_score: Option<i32> = scores.iter().copied().max();
    println!("\nHighest score: {:?}", max_score);

    // cloned — from &String to String
    let names = vec![String::from("Alice"), String::from("Bob")];
    let cloned_names: Vec<String> = names.iter().cloned().collect();
    println!("cloned: {:?}", cloned_names);
    println!("The originals remain: {:?}", names);

    // rev — reversing
    let countdown: Vec<i32> = (1..=5).into_iter().rev().collect();
    println!("\nCountdown: {:?}", countdown);

    // Chained combinations
    println!("\n--- Chained combinations ---");
    let long_words: Vec<&str> = vec!["hi", "hello", "hey", "howdy", "greetings"]
        .into_iter()
        .filter(|w| w.len() >= 4)
        .collect();
    println!("4+ letters: {:?}", long_words);

    // filter + map combined
    let words = vec!["hello", "hi", "hey", "howdy", "greetings"];
    let long_upper: Vec<String> = words
        .iter()
        .filter(|w| w.len() >= 4)
        .map(|w| w.to_uppercase())
        .collect();
    println!("\n4+ letters, uppercased: {:?}", long_upper);
}
```

## Recap

- `.map(f)` transforms each element; `.filter(pred)` drops the non-qualifying ones.
- `.flat_map(f)` = `.map(f)` + `.flatten()` — conceptually like `and_then` on `Option` / `Result`.
- `.copied()` turns each `&T` into `T` (requires `T: Copy`); `.cloned()` is similar but uses `Clone`.
- `.rev()` reverses the iteration order, requiring `DoubleEndedIterator`.
- These methods chain freely into clear data-processing pipelines.
- Pairing with `.copied()` dodges `filter`'s pesky `&&T` problem.
