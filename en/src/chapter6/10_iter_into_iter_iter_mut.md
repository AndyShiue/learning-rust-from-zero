# `iter` / `into_iter` / `iter_mut`

## Goal of This Episode

Get the three iteration modes straight — borrowing, consuming, mutably borrowing — and their relationship to the ownership system.

## Concept

### Three Ways to Iterate

We touched earlier on the difference between `for x in &v` and `for x in v`. Today, a formal introduction to `Vec`'s three methods:

| Method | Produced type | Meaning | Is the `Vec` still usable after? |
|------|---------|------|-------------------|
| `.iter()` | `&T` | Borrows each element | ✓ Yes |
| `.into_iter()` | `T` | Consumes the whole collection | ✗ No |
| `.iter_mut()` | `&mut T` | Mutably borrows each element | ✓ Yes (now modified) |

### `.iter()` — Just Looking

```rust,editable
fn main() {
    let names = vec![String::from("Alice"), String::from("Bob")];
    for name in names.iter() {
        println!("{}", name); // name is a &String
    }
    println!("names is still here: {:?}", names); // Fine — only borrowed
}
```

`.iter()` returns an iterator of `&T`. The collection is untouched, still there afterward.

### `.into_iter()` — Taking Everything

```rust,compile_fail
# fn main() {
    let names = vec![String::from("Alice"), String::from("Bob")];
    for name in names.into_iter() {
        println!("{}", name); // name is a String (owned)
    }
    println!("{:?}", names); // Compile error! names was consumed
# }
```

`.into_iter()` hands over each element's ownership. The collection itself is consumed, unusable afterward.

In fact, `for name in names` equals `for name in names.into_iter()`.

### `.iter_mut()` — Borrowing to Modify

```rust,editable
fn main() {
    let mut scores = vec![60, 70, 80];
    for score in scores.iter_mut() {
        *score += 10;  // score is a &mut i32
    }
    println!("{:?}", scores);  // [70, 80, 90]
}
```

`.iter_mut()` returns `&mut T`, letting you modify each element in place.

### The Correspondence

These three methods map onto the three ownership operations from Chapter 4:

| Ownership concept | Iteration method | for shorthand |
|-----------|---------|-----------|
| `&T` (shared borrow) | `.iter()` | `for x in &v` |
| `T` (moved ownership) | `.into_iter()` | `for x in v` |
| `&mut T` (mutable borrow) | `.iter_mut()` | `for x in &mut v` |

### The `IntoIterator` behind It

Last episode showed `for x in something` calls `something.into_iter()`. So how do the three `for` forms work?

Because `Vec<T>`, `&Vec<T>`, and `&mut Vec<T>` each implement `IntoIterator`:

```rust,ignore
impl<T> IntoIterator for Vec<T> {
    type Item = T;
    fn into_iter(self) -> ... { /* Consumes the Vec, producing T */ }
}

impl<'a, T> IntoIterator for &'a Vec<T> {
    type Item = &'a T;
    fn into_iter(self) -> ... { /* Same as .iter(), producing &T */ }
}

impl<'a, T> IntoIterator for &'a mut Vec<T> {
    type Item = &'a mut T;
    fn into_iter(self) -> ... { /* Same as .iter_mut(), producing &mut T */ }
}
```

So `for x in &v` actually calls `into_iter()` on `&v` (of type `&Vec<T>`), hitting the `&Vec<T>` `impl` and ultimately yielding `&T`.

Most collection types (`Vec`, arrays...) follow this pattern — implementing `IntoIterator` three times, for themselves, `&self`, and `&mut self`.

### Which to Choose?

- Only reading → `.iter()` (most common).
- Taking ownership of the elements → `.into_iter()`.
- Modifying in place → `.iter_mut()`.

The principle is ownership's own: don't take permissions you don't need.

## Example Code

```rust,editable
fn main() {
    // .iter() — read-only borrowing
    let animals = vec![
        String::from("cat"),
        String::from("dog"),
        String::from("rabbit"),
    ];

    println!("--- .iter() (borrowing) ---");
    for animal in animals.iter() {
        println!("Animal: {}", animal);
    }
    println!("animals is still here: {:?}", animals);

    // .iter_mut() — mutable borrowing, in-place modification
    let mut prices = vec![100, 200, 300];
    println!("\n--- .iter_mut() (modifying) ---");
    println!("Before the discount: {:?}", prices);
    for price in prices.iter_mut() {
        *price = *price * 8 / 10; // 20% off
    }
    println!("After the discount: {:?}", prices);

    // .into_iter() — consuming ownership
    let words = vec![
        String::from("hello"),
        String::from("world"),
    ];
    println!("\n--- .into_iter() (consuming) ---");
    for word in words.into_iter() {
        println!("Received: {}", word); // word is a String (owned)
    }
    // println!("{:?}", words); // Compile error! words was consumed

    // The shorthand correspondences
    println!("\n--- The shorthands ---");
    let nums = vec![1, 2, 3];

    // for x in &nums equals for x in nums.iter()
    for x in &nums {
        print!("{} ", x);
    }
    println!("← &nums (borrowing)");

    // for x in nums equals for x in nums.into_iter()
    for x in nums {
        print!("{} ", x);
    }
    println!("← nums (consuming)");
    // nums is no longer usable
}
```

## Recap

- `.iter()` produces `&T`, borrowing elements; the collection is unaffected.
- `.into_iter()` produces `T`, consuming the whole collection and taking ownership.
- `.iter_mut()` produces `&mut T`, allowing in-place modification.
- `for x in &v` = `.iter()`, `for x in v` = `.into_iter()`, `for x in &mut v` = `.iter_mut()`.
- Selection principle: take no more permission than needed — `.iter()` to read, `.iter_mut()` to modify, `.into_iter()` to consume.
