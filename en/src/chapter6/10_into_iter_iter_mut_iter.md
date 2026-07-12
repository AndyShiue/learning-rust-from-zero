# `into_iter` / `iter_mut` / `iter`

## Goal of This Episode

Get the three iteration modes straight — consuming, mutable borrowing, and borrowing — and their relationship to the ownership system.

## Concept

### Three Ways to Iterate

We touched earlier on the difference between `for x in v` and `for x in &v`. Today, we'll complete the picture by introducing `Vec`'s three iteration methods:

| Method | Produced type | Meaning | Is the `Vec` still usable after? |
|------|---------|------|-------------------|
| `.into_iter()` | `T` | Consumes the whole collection | ✗ No |
| `.iter_mut()` | `&mut T` | Mutably borrows each element | ✓ Yes (now modified) |
| `.iter()` | `&T` | Borrows each element | ✓ Yes |

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
        *score += 10; // score is a &mut i32
    }
    println!("{:?}", scores); // [70, 80, 90]
}
```

`.iter_mut()` returns `&mut T`, letting you modify each element in place.

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

### The Correspondence

These three methods map onto the three ownership operations from Chapter 4:

| Ownership concept | Iteration method | for shorthand |
|-----------|---------|-----------|
| `T` (moved ownership) | `.into_iter()` | `for x in v` |
| `&mut T` (mutable borrow) | `.iter_mut()` | `for x in &mut v` |
| `&T` (borrow) | `.iter()` | `for x in &v` |

### The `IntoIterator` behind It

Last episode showed `for x in something` calls `something.into_iter()`. So how do the three `for` forms work?

Because `Vec<T>`, `&mut Vec<T>`, and `&Vec<T>` each implement `IntoIterator`:

```rust,ignore
impl<T> IntoIterator for Vec<T> {
    type Item = T;
    fn into_iter(self) -> ... { /* Consumes the Vec, producing T */ }
}

impl<'a, T> IntoIterator for &'a mut Vec<T> {
    type Item = &'a mut T;
    fn into_iter(self) -> ... { /* Same as .iter_mut(), producing &mut T */ }
}

impl<'a, T> IntoIterator for &'a Vec<T> {
    type Item = &'a T;
    fn into_iter(self) -> ... { /* Same as .iter(), producing &T */ }
}
```

So `for x in v`, `for x in &mut v`, and `for x in &v` use the `IntoIterator` implementations for `Vec<T>`, `&mut Vec<T>`, and `&Vec<T>`, respectively, ultimately yielding `T`, `&mut T`, and `&T`.

Most collection types (`Vec`, arrays...) follow this pattern — implementing `IntoIterator` three times, for themselves, `&mut self`, and `&self`.

### Which to Choose?

- Taking ownership of the elements → `.into_iter()`.
- Modifying in place → `.iter_mut()`.
- Only reading → `.iter()` (most common).

The principle is ownership's own: don't take permissions you don't need.

## Example Code

```rust,editable
fn main() {
    // .into_iter() — consuming ownership
    let words = vec![
        String::from("hello"),
        String::from("world"),
    ];
    println!("--- .into_iter() (consuming) ---");
    for word in words.into_iter() {
        println!("Received: {}", word); // word is a String (owned)
    }
    // println!("{:?}", words); // Compile error! words was consumed

    // .iter_mut() — mutable borrowing, in-place modification
    let mut prices = vec![100, 200, 300];
    println!("\n--- .iter_mut() (modifying) ---");
    println!("Before the discount: {:?}", prices);
    for price in prices.iter_mut() {
        *price = *price * 8 / 10; // 20% off
    }
    println!("After the discount: {:?}", prices);

    // .iter() — borrowing
    let animals = vec![
        String::from("cat"),
        String::from("dog"),
        String::from("rabbit"),
    ];

    println!("\n--- .iter() (borrowing) ---");
    for animal in animals.iter() {
        println!("Animal: {}", animal);
    }
    println!("animals is still here: {:?}", animals);

    // The shorthand correspondences
    println!("\n--- The shorthands ---");
    let owned = vec![1, 2, 3];

    // for x in owned equals for x in owned.into_iter()
    for x in owned {
        print!("{} ", x);
    }
    println!("← owned (consuming)");
    // owned is no longer usable

    let mut mutable = vec![1, 2, 3];
    // for x in &mut mutable equals for x in mutable.iter_mut()
    for x in &mut mutable {
        *x *= 10;
    }
    println!("{:?} ← &mut mutable (mutable borrowing)", mutable);

    let borrowed = vec![1, 2, 3];
    // for x in &borrowed equals for x in borrowed.iter()
    for x in &borrowed {
        print!("{} ", x);
    }
    println!("← &borrowed (borrowing)");
    println!("borrowed is still here: {:?}", borrowed);
}
```

## Recap

- `.into_iter()` produces `T`, consuming the whole collection and taking ownership.
- `.iter_mut()` produces `&mut T`, allowing in-place modification.
- `.iter()` produces `&T`, borrowing elements; the collection is unaffected.
- `for x in v` = `.into_iter()`, `for x in &mut v` = `.iter_mut()`, `for x in &v` = `.iter()`.
- Selection principle: take no more permission than needed — `.into_iter()` to consume, `.iter_mut()` to modify, `.iter()` to read.
