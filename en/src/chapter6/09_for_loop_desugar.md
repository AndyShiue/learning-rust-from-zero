# What `for` Loops Really Are

## Goal of This Episode

Unmask the `for` loop, and see that underneath it's really the combination `IntoIterator` + `while let`.

## Concept

### `for` Loops Aren't Magic

We've been using `for` loops since Chapter 1:

```rust,editable
fn main() {
    let v = vec![1, 2, 3];
    for x in v {
        println!("{}", x);
    }
}
```

Looks simple, right? But what's actually happening underneath?

### Desugaring the Loop

The compiler actually transforms the `for` loop above into this:

```rust,editable
fn main() {
    let v = vec![1, 2, 3];
    let mut iter = v.into_iter();
    while let Some(x) = iter.next() {
        println!("{}", x);
    }
}
```

Three steps:

1. Call `v.into_iter()` to turn `v` into an iterator.
2. Call `iter.next()` repeatedly.
3. Destructure with `while let Some(x)` (remember Chapter 3's `while let`?), ending when `None` arrives.

### The `IntoIterator` `trait`

`IntoIterator` is a `trait` defining "how to turn oneself into an iterator":

```rust,noplayground
trait IntoIterator {
    type Item;
    type IntoIter: Iterator<Item = Self::Item>;
    fn into_iter(self) -> Self::IntoIter;
}
#
# fn main() {}
```

Any type implementing `IntoIterator` works with `for` loops. `Vec`, arrays, a string slice's `.chars()`... all thanks to implementing this `trait`.

### `Iterator` Implements `IntoIterator` Too

A very convenient design: every `Iterator` automatically implements `IntoIterator` (its `into_iter()` simply returns itself). So an iterator can be thrown straight into `for`:

```rust,editable
fn main() {
    let v = vec![1, 2, 3];
    let iter = v.iter(); // This is an Iterator
    for x in iter {      // Iterators implement IntoIterator too
        println!("{}", x);
    }
}
```

## Example Code

```rust,editable
fn main() {
    // A regular for loop
    let fruits = vec!["apple", "banana", "orange"];
    println!("--- The for loop ---");
    for fruit in fruits {
        println!("Fruit: {}", fruit);
    }

    // Manually desugared into while let (fully equivalent)
    let fruits = vec!["apple", "banana", "orange"];
    println!("\n--- Desugared by hand ---");
    let mut iter = fruits.into_iter();
    while let Some(fruit) = iter.next() {
        println!("Fruit: {}", fruit);
    }

    // A custom iterator (Iterator auto-implements IntoIterator, so for works)
    println!("\n--- A custom Iterator ---");
    let countdown = Countdown { value: 5 };
    for n in countdown {
        print!("{} ", n);
    }
    println!("Liftoff!");

    // An iterator itself can go into for
    println!("\n--- An Iterator straight into for ---");
    let numbers = vec![10, 20, 30, 40, 50];
    for n in numbers.iter() {
        if *n > 20 {
            println!("Greater than 20: {}", n);
        }
    }

    // Ranges implement IntoIterator too
    println!("\n--- Range ---");
    for i in 1..=5 {
        print!("{} ", i);
    }
    println!();
}

// A custom iterator
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
```

## Recap

- `for x in v` is shorthand; desugared, it's `v.into_iter()` + `while let Some(x) = iter.next()`.
- The `IntoIterator` `trait` defines "how to turn oneself into an iterator."
- Any type implementing `IntoIterator` works with `for` loops.
- Every `Iterator` implements `IntoIterator` automatically.
- Writing `for i in 1..5` or `for i in 1..=5` works precisely because ranges implement `IntoIterator`.
