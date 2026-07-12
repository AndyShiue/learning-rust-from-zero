# Lazy Evaluation

## Goal of This Episode

Understand the lazy nature of iterators — `.map(f)` and `.filter(pred)` don't run immediately; they build nested structures that `.collect()` or `for` later pulls through one by one.

## Concept

### Iterators Are Lazy

This may be the most important idea in all of Chapter 6: **an iterator's transformation methods don't execute immediately**.

```rust,editable
fn main() {
    let v = vec![1, 2, 3, 4, 5];
    let iter = v.iter().map(|x| {
        println!("Processing {}", x);
        x * 2
    });
    // Up to this point, nothing has been printed!
}
```

`map` hasn't "run through" the elements. It merely built a new iterator structure recording "what to do later." Only when someone calls a "consuming" method — `collect()`, `for`, `sum()` — do elements get pulled through one at a time.

### Russian Nesting Dolls

Each call to `.map(f)` or `.filter(pred)` really "wraps another layer" around the iterator. Like Russian nesting dolls:

```rust,noplayground
# fn main() {
#     let v = vec![2, 7, 1, 8, 2, 8];
    v.iter()                 // Innermost: the original iterator
        .filter(|x| **x > 2) // Second layer: a Filter struct holding inner + closure
        .map(|x| x * 10);    // Third layer: a Map struct holding inner + closure
# }
```

Each layer is a `struct` holding the inner iterator and its own closure. The standard library's `Map` and `Filter` look roughly like:

```rust,noplayground
struct Map<I, F> {
    iter: I, // The inner iterator
    f: F,    // The closure to apply
}

struct Filter<I, P> {
    iter: I,      // The inner iterator
    predicate: P, // The filtering-condition closure
}
#
# fn main() {}
```

Their `.next()` implementations are intuitive too:

```rust,noplayground
# struct Map<I, F> {
#     iter: I, // The inner iterator
#     f: F,    // The closure to apply
# }
#
# struct Filter<I, P> {
#     iter: I,      // The inner iterator
#     predicate: P, // The filtering-condition closure
# }
#
// Map's next(): fetch one element from inside, apply the closure
impl<B, I: Iterator, F: FnMut(I::Item) -> B> Iterator for Map<I, F> {
    type Item = B;
    fn next(&mut self) -> Option<B> {
        let x = self.iter.next()?; // Ask the inner layer for an element
        Some((self.f)(x))          // Apply the closure and return
    }
}

// Filter's next(): keep fetching from inside until something qualifies
impl<I: Iterator, P: FnMut(&I::Item) -> bool> Iterator for Filter<I, P> {
    type Item = I::Item;
    fn next(&mut self) -> Option<I::Item> {
        loop {
            let x = self.iter.next()?; // Ask the inner layer for an element
            if (self.predicate)(&x) {
                return Some(x);        // Qualifies — return it
            }
            // Doesn't qualify; ask for the next one
        }
    }
}
#
# fn main() {}
```

So the whole chain is a stack of `struct`s wrapped together — call the outermost `.next()`, it asks the layer inside, which asks the layer further in, all the way to the bottom.

### Pull-based: One Element at a Time

When you call `.collect()` or run a `for` loop, the outermost iterator starts "pulling":

1. The outermost (`Map`) asks the second layer (`Filter`): "Give me the next element."
2. Filter asks the innermost (the original iterator): "Give me the next element."
3. The innermost returns `Some(&1)`.
4. Filter checks: `1 > 2`? Fails. Ask again.
5. The innermost returns `Some(&2)`.
6. Filter checks: `2 > 2`? Fails. Ask again.
7. The innermost returns `Some(&3)`.
8. Filter checks: `3 > 2`? Passes! Hand it to Map.
9. Map applies the closure: `3 * 10 = 30`, returning `Some(30)`.

Each element is processed **all the way through** — not "all the `filter`s first, then all the `map`s." Which means **no intermediate `Vec` is ever needed**.

### Infinite Iterators

Thanks to laziness, iterators can be **infinite**. Both `std::iter::repeat` and `std::iter::from_fn` can produce iterators that never return `None`:

```rust,noplayground
use std::iter;

fn main() {
    // Forever producing 1, 2, 3, 4, 5, ...
    let mut n = 0;
    let naturals = iter::from_fn(move || {
        n += 1;
        Some(n)
    });
}
```

This doesn't loop forever, because iterators are lazy — with nobody calling `.next()`, nothing happens.

### Taming Infinite Iterators with `.take(n)`

`.take(n)` extracts finitely many elements from an infinite iterator:

```rust,noplayground
# use std::iter;
#
# fn main() {
#     // Forever producing 1, 2, 3, 4, 5, ...
#     let mut n = 0;
#     let naturals = iter::from_fn(move || {
#         n += 1;
#         Some(n)
#     });
    let first_ten: Vec<i32> = naturals.take(10).collect();
    // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# }
```

That's the power of lazy evaluation — describe a "conceptually infinite" computation first, and decide how much to take at the end.

### Accidentally Forgot to Consume?

Because iterators are lazy, writing `.map(f)` but forgetting `.collect()` or `for` means nothing happens. The Rust compiler warns you:

```ignore
warning: unused `Map` that must be used
note: iterators are lazy and do nothing unless consumed
```

Seeing this warning tells you: you forgot to consume the iterator.

## Example Code

```rust,editable
use std::iter;

fn main() {
    // The laziness demo: map doesn't run immediately
    println!("--- The laziness demo ---");
    let v = vec![1, 2, 3];
    let iter = v.iter().map(|x| {
        println!("  Processing {}", x);
        x * 2
    });
    println!("map is built, but hasn't run yet...");
    println!("Now collecting:");
    let result: Vec<i32> = iter.collect();
    println!("Result: {:?}", result);

    // Pull-based: filter + map handling one element at a time
    println!("\n--- The pull-based demo ---");
    let data = vec![1, 2, 3, 4, 5, 6];
    let processed: Vec<i32> = data
        .iter()
        .filter(|&&x| {
            println!("  filter checking {}", x);
            x % 2 == 0
        })
        .map(|&x| {
            println!("  map processing {}", x);
            x * 10
        })
        .collect();
    println!("Result: {:?}", processed);
    // Watch the printed order! filter and map run interleaved

    // Building an infinite iterator with from_fn (the first 10 primes)
    let mut candidate = 1;
    let primes: Vec<i32> = iter::from_fn(move || {
        loop {
            candidate += 1;
            let is_prime = (2..candidate).into_iter().all(|d| candidate % d != 0);
            if is_prime {
                return Some(candidate);
            }
        }
    })
    .take(10)
    .collect();
    println!("\nThe first 10 primes: {:?}", primes);

    // No intermediate Vecs — everything in one pipeline
    println!("\n--- Zero intermediate Vecs ---");
    let sum_of_even_squares: i32 = (1..=100)
        .into_iter()
        .filter(|x| x % 2 == 0)
        .map(|x| x * x)
        .sum();
    println!("Sum of squares of the evens in 1~100: {}", sum_of_even_squares);
    // No intermediate Vec was ever built; every element was processed one at a time
}
```

## Recap

- `Iterator` methods like `.map(f)` / `.filter(pred)` are **lazy** — nothing runs immediately.
- Each transformation call "wraps another `struct` layer" outside (Russian nesting dolls).
- Consumption (`.collect()`, `for`, `.sum()`, etc.) is what triggers execution.
- Execution is **pull-based** — one element pulled at a time, passing through every layer, no intermediate `Vec`s.
- Thanks to laziness, iterators can be **infinite**.
- Use `.take(n)` to extract finitely many elements from an infinite iterator.
- Forget to consume an iterator, and the compiler warns you.

Congratulations on finishing Chapter 6! 🎉 From function pointers through the three `Fn` `trait`s of closures to the lazy evaluation of iterators — this chapter combined ownership, `trait`s, generics, and everything before it, showing off the power of functional programming in Rust. You can now write clean, efficient data-processing pipelines with no intermediate staging. Next chapter: Cargo, `crate`s, and the `mod` system — taking your code from a single file to a real project structure!
