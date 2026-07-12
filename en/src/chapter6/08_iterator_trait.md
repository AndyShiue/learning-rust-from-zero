# The `Iterator` `trait`

## Goal of This Episode

Meet the heart of the `Iterator` `trait` — implement just the `next` method, and dozens of useful methods come free.

## Concept

### The Definition of `Iterator`

The core of the `Iterator` `trait` couldn't be simpler:

```rust,noplayground
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}
#
# fn main() {}
```

That's it. One required method, `next`, which on each call returns:

- `Some(value)` — there's a next element.
- `None` — the iteration is over.

Remember associated types from Chapter 5? `type Item` is one — "the element type this iterator produces."

### Calling `next` by Hand

You can call `.next()` manually to fetch elements one at a time:

```rust,editable
fn main() {
    let v = vec![10, 20, 30];
    let mut iter = v.iter();

    println!("{:?}", iter.next()); // Some(&10)
    println!("{:?}", iter.next()); // Some(&20)
    println!("{:?}", iter.next()); // Some(&30)
    println!("{:?}", iter.next()); // None
}
```

Note `iter` must be `mut`, since every `.next()` advances internal state.

### Implement Only `next`; the Rest Come Free

The `Iterator` `trait` supplies a wealth of **default implementations** (remember Chapter 5?). Since every iteration operation boils down to "keep calling `next` until `None`," implementing `next` alone makes dozens of methods — `map`, `filter`, `count`, `sum`, and more — automatically available.

### A Custom `Iterator`

Let's build our own iterator. Say we want a "countdown timer":

```rust,noplayground
struct Countdown {
    value: i32,
}

impl Iterator for Countdown {
    type Item = i32;

    fn next(&mut self) -> Option<i32> {
        if self.value > 0 {
            let current = self.value;
            self.value -= 1;
            Some(current)
        } else {
            None
        }
    }
}
#
# fn main() {}
```

With `next` implemented, `map`, `filter`, `sum`, `collect`, and dozens more become automatically available. The coming episodes cover them one by one.

### The Standard Library's `Iterator` Factories

The standard library offers convenient functions for creating iterators:

- `std::iter::repeat(value)` — repeats one value endlessly
- `std::iter::from_fn(closure)` — a closure decides what each `.next()` returns.

```rust,editable
use std::iter;

fn main() {
    // Endlessly producing 42
    let mut repeater = iter::repeat(42);
    println!("{:?}", repeater.next()); // Some(42)
    println!("{:?}", repeater.next()); // Some(42) (never None)

    // Producing increasing numbers with a closure
    let mut n = 0;
    let mut counter = iter::from_fn(move || {
        n += 1;
        Some(n)
    });
    println!("{:?}", counter.next()); // Some(1)
    println!("{:?}", counter.next()); // Some(2)
}
```

Note that iterators from `repeat` and `from_fn` may be **infinite** — never returning `None`. Episode 15 explores this property in depth.

## Example Code

```rust,editable
use std::iter;

// A custom iterator: the Fibonacci sequence (infinite!)
struct Fibonacci {
    a: u64,
    b: u64,
}

impl Fibonacci {
    fn new() -> Fibonacci {
        Fibonacci { a: 0, b: 1 }
    }
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<u64> {
        let current = self.a;
        let new_b = self.a + self.b;
        self.a = self.b;
        self.b = new_b;
        Some(current) // Never returns None
    }
}

fn main() {
    // Calling .next() of a Vec's .iter() by hand
    let names = vec!["Alice", "Bob", "Charlie"];
    let mut name_iter = names.iter();
    println!("First: {:?}", name_iter.next());
    println!("Second: {:?}", name_iter.next());
    println!("Third: {:?}", name_iter.next());
    println!("Done: {:?}", name_iter.next());

    // A custom Iterator: Fibonacci (calling next by hand)
    println!("\nFibonacci:");
    let mut fib = Fibonacci::new();
    println!("{:?}", fib.next()); // Some(0)
    println!("{:?}", fib.next()); // Some(1)
    println!("{:?}", fib.next()); // Some(1)
    println!("{:?}", fib.next()); // Some(2)
    println!("{:?}", fib.next()); // Some(3)
    println!("{:?}", fib.next()); // Some(5)
    // Never None — an infinite iterator

    // std::iter::repeat: endless repetition
    let mut threes = iter::repeat(3);
    println!("\nrepeat(3):");
    println!("{:?}", threes.next()); // Some(3)
    println!("{:?}", threes.next()); // Some(3)
    println!("{:?}", threes.next()); // Some(3) (never None)

    // std::iter::from_fn: a closure controls the output
    let mut n = 0;
    let mut squares = iter::from_fn(|| {
        n += 1;
        if n <= 3 {
            Some(n * n)
        } else {
            None
        }
    });
    println!("\nfrom_fn (the first 3 squares):");
    println!("{:?}", squares.next()); // Some(1)
    println!("{:?}", squares.next()); // Some(4)
    println!("{:?}", squares.next()); // Some(9)
    println!("{:?}", squares.next()); // None
}
```

## Recap

- The core of the `Iterator` `trait` is `next(&mut self) -> Option<Self::Item>`.
- Implement `.next()` alone and receive dozens of default implementations free (covered in coming episodes).
- Implementing `Iterator` for your own type is easy — define `type Item` and `next`.
- `std::iter::repeat(value)` builds an endlessly repeating iterator.
- `std::iter::from_fn(closure)` controls each produced value with a closure.
- Iterators may be infinite (never returning `None`).
