# Aggregation

## Goal of This Episode

Learn to "fold" an entire sequence into one value with the iterator's aggregation methods.

## Concept

### What Is Aggregation?

Recent episodes covered creating iterators and `collect`ing them into collections. But sometimes you don't want a collection — you want a **single value**: a sum, a maximum, a count... That's aggregation.

### `.count()` — How Many Are There

```rust,noplayground
# fn main() {
    let names = vec!["Alice", "Bob", "Charlie"];
    let count = names.iter().count(); // 3
# }
```

### `.sum()` and `.product()`

```rust,noplayground
# fn main() {
    let total: i32 = (1..=10).into_iter().sum();         // 55
    let factorial: i64 = (1..=10).into_iter().product(); // 3628800
# }
```

Like `.collect()`, `.sum()` and `.product()` need the return type specified — usually via a type annotation.

### `.min()` and `.max()`

```rust,noplayground
# fn main() {
    let v = vec![3, 1, 4, 1, 5, 9, 2, 6];
    let smallest = v.iter().min(); // Some(&1)
    let largest = v.iter().max();  // Some(&9)
# }
```

They return `Option`, since the iterator might be empty (returning `None` if so).

### `.fold(init, f)` — the Most General Aggregation

`fold` is the "boss" of all aggregation methods. Its type:

```rust,ignore
fn fold<B>(self, init: B, f: impl FnMut(B, Self::Item) -> B) -> B;
```

It takes an initial value `init` (of type `B`) and a closure; each step combines the "accumulated value" and the "current element" into a new accumulated value:

```rust,noplayground
# fn main() {
    let sum = (1..=5).into_iter().fold(0, |acc, x| acc + x);
    // Steps: 0+1=1, 1+2=3, 3+3=6, 6+4=10, 10+5=15
# }
```

In fact, every other method in this episode can be built from `fold`:

```rust,noplayground
# fn main() {
    // count = fold from 0, +1 each step
    let count = (1..=5).into_iter().fold(0, |acc, _x| acc + 1);

    // sum = fold from 0, adding each element
    let sum = (1..=5).into_iter().fold(0, |acc, x| acc + x);

    // product = fold from 1, multiplying by each element
    let product = (1..=5).into_iter().fold(1, |acc, x| acc * x);

    // min / max are left to reduce below — fold makes them awkward
# }
```

`fold` can do more flexible things. String numbers together? Track multiple values at once? All possible:

```rust,noplayground
# fn main() {
    let text = (1..=5).into_iter().fold(String::new(), |mut acc, x| {
        if !acc.is_empty() {
            acc.push_str(", ");
        }
        acc.push_str(&x.to_string());
        acc
    });
    // "1, 2, 3, 4, 5"
# }
```

### `.reduce(f)` — `fold` without an Initial Value

`reduce` resembles `fold`, but uses the first element as the initial value:

```rust,noplayground
# fn main() {
    let product = vec![2, 3, 4].into_iter().reduce(|acc, x| acc * x);
    // Some(24): 2*3=6, 6*4=24
# }
```

Since there may be no first element (an empty iterator), `reduce` returns an `Option`.

Implementing `min` and `max` with `reduce` is very natural:

```rust,noplayground
# fn main() {
    let min = vec![3, 1, 4, 1, 5].into_iter()
        .reduce(|a, b| if a < b { a } else { b });
    // Some(1)

    let max = vec![3, 1, 4, 1, 5].into_iter()
        .reduce(|a, b| if a > b { a } else { b });
    // Some(5)
# }
```

Since `reduce` itself returns `Option`, an empty iterator automatically gets `None` — whereas `fold` requires special handling for the empty case.

## Example Code

```rust,editable
fn main() {
    let scores = vec![85, 92, 78, 95, 88, 76, 91];

    // .count()
    let total = scores.iter().count();
    println!("{} scores in total", total);

    // .sum()
    let sum: i32 = scores.iter().sum();
    println!("Total: {}", sum);

    // .min() / .max()
    let min = scores.iter().min();
    let max = scores.iter().max();
    println!("Lowest: {:?}, highest: {:?}", min, max);

    // .product()
    let factorial: i64 = (1..=10).into_iter().product();
    println!("\n10! = {}", factorial);

    // .fold() — computing an average
    let (count2, sum2) = scores.iter().fold((0, 0), |(c, s), &score| {
        (c + 1, s + score)
    });
    println!("\nAverage via fold: {} / {} = {}", sum2, count2, sum2 / count2);

    // .fold() — stringing numbers together
    let nums = vec![1, 2, 3, 4, 5];
    let formatted = nums.iter().fold(String::new(), |mut acc, &n| {
        if !acc.is_empty() {
            acc.push_str(" → ");
        }
        acc.push_str(&n.to_string());
        acc
    });
    println!("Joined: {}", formatted);

    // .reduce() — finding the longest string
    let words = vec!["cat", "elephant", "dog", "hippopotamus"];
    let longest = words
        .iter()
        .reduce(|a, b| if a.len() >= b.len() { a } else { b });
    println!("\nThe longest word: {:?}", longest);

    // .reduce() returns Option (the empty-iterator case)
    let empty: Vec<i32> = vec![];
    let result = empty.into_iter().reduce(|a, b| a + b);
    println!("reduce of an empty Vec: {:?}", result);
}
```

## Recap

- `.count()` counts the elements.
- `.sum()` and `.product()` compute total and product; annotate the return type.
- `.min()` and `.max()` return `Option`, since the iterator may be empty.
- `.fold(init, |acc, x| ...)` is the most general aggregation — accumulating step by step from an initial value and a closure.
- `.reduce(|acc, x| ...)` is like `fold` but seeds with the first element, returning `Option`.
- Aggregation methods consume the whole iterator, producing one single value.
