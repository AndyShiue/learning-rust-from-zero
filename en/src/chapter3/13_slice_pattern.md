# Slice Patterns

## Goal of This Episode

Learn to destructure arrays and slices with slice patterns.

## Concept

### Pattern Matching on Arrays

Last episode we learned to destructure tuples — and we can pattern-match arrays and slices too! Use a slice pattern like `[a, b, c]` to compare each element of an array:

```rust,editable
fn main() {
    let rgb = [255, 128, 0];

    match rgb {
        [255, 0, 0] => println!("Pure red"),
        [0, 255, 0] => println!("Pure green"),
        [0, 0, 255] => println!("Pure blue"),
        [r, g, b] => println!("Custom color: R={}, G={}, B={}", r, g, b),
    }
}
```

As in recent episodes, patterns can mix "fixed values" and "variables." Fixed values do the comparing; variables catch the data.

### Slices Work Too

It's not just fixed-length arrays — slices (`&[T]`) can use slice patterns as well. The difference is that a slice's length is unknown at compile time, so you can match with patterns of different lengths. The `_` in the last arm below means "everything else"; Episode 15 covers it properly:

```rust,noplayground
fn describe(numbers: &[i32]) {
    match numbers {
        [] => println!("Empty"),
        [x] => println!("Just one element: {}", x),
        [x, y] => println!("Two elements: {} and {}", x, y),
        [x, y, z] => println!("Three elements: {}, {}, {}", x, y, z),
        _ => println!("More than three elements"),
    }
}
#
# fn main() {}
```

A fixed-length array always has its fixed length — for an `[i32; 3]`, arms like `[]` or `[x]` can never match. Only slices need to account for varying lengths.

## Example Code

```rust,editable
fn describe(data: &[i32]) {
    match data {
        [] => println!("An empty slice"),
        [only] => println!("Just one element: {}", only),
        [first, second] => println!("Two elements: {} and {}", first, second),
        _ => println!("Many elements; the first is {}", data[0]),
    }
}

fn main() {
    // Slice pattern on a fixed-length array
    let rgb = [255, 128, 0];

    match rgb {
        [255, 0, 0] => println!("Pure red"),
        [0, 255, 0] => println!("Pure green"),
        [0, 0, 255] => println!("Pure blue"),
        [r, g, b] => println!("Custom color: R={}, G={}, B={}", r, g, b),
    }

    println!("---");

    // Slice patterns on slices — matching different lengths
    describe(&[]);
    describe(&[42]);
    describe(&[1, 2]);
    describe(&[10, 20, 30, 40, 50]);
}
```

## Recap

- With arrays, `match` can use slice patterns like `[a, b, c]`, similar to tuple patterns.
- Slices `&[T]` have no fixed length, so patterns of different lengths can match (`[]`, `[x]`, `[x, y]`...).
