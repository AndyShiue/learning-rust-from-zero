# Ignoring Multiple Values with `..`

## Goal of This Episode

Learn to use `..` to ignore multiple unneeded values in a `struct` or tuple at once.

## Concept

Last episode we ignored one value with `_`. But what if a `struct` has many fields and you only care about one or two? Writing `_` for every unwanted field is tedious.

Rust provides `..` (two dots), meaning "I don't want any of the rest."

### In a `match` on a `struct`

```rust,editable
struct Player {
    id: i32,
    hp: i32,
    mp: i32,
    level: i32,
}

fn main() {
    let p = Player { id: 1, hp: 0, mp: 50, level: 10 };

    match p {
        Player { hp: 0, .. } => println!("This player is down!"),
        Player { level, .. } => println!("Level {}", level),
    }
}
```

`Player { hp: 0, .. }` means "`hp` is 0; I don't care about the other fields." No need to write `_` for every unwanted field.

`enum` `struct` variants can be matched this way too — exactly the same usage.

### In a `match` on a Tuple

```rust,editable
fn main() {
    let scores = (90, 85, 78, 92, 88);

    match scores {
        (first, ..) => println!("First subject: {}", first),
    }

    match scores {
        (.., last) => println!("Last subject: {}", last),
    }

    match scores {
        (first, .., last) => println!("First subject {}, last subject {}", first, last),
    }
}
```

`(first, ..)` takes only the first, `(.., last)` only the last, and `(first, .., last)` the head and tail.

Tuple `struct`s and `enum` tuple variants can be matched similarly, e.g. `MyStruct(first, ..)` or `MyEnum::Variant(first, ..)`.

### In Arrays and Slices

Episode 13 covered slice patterns; `..` works just as nicely in arrays and slices:

```rust,editable
fn main() {
    let data: &[i32] = &[10, 20, 30, 40, 50];

    match data {
        [first, .., last] => println!("Head = {}, tail = {}", first, last),
        [only] => println!("Just one: {}", only),
        [] => println!("Empty"),
    }
}
```

### Note: `..` Can Appear Only Once

`..` can appear only once within one layer of a pattern — with two, Rust wouldn't know how to distribute the values in between.

## Example Code

```rust,editable
struct Player {
    id: i32,
    hp: i32,
    mp: i32,
    level: i32,
}

fn main() {
    // .. on a struct
    let p1 = Player { id: 1, hp: 100, mp: 50, level: 10 };

    match p1 {
        Player { hp, .. } => println!("HP = {}", hp),
    }

    let p2 = Player { id: 2, hp: 0, mp: 30, level: 5 };

    match p2 {
        Player { hp: 0, .. } => println!("This player is already down!"),
        Player { level, .. } => println!("Level {}", level),
    }

    // .. on a tuple
    let scores = (90, 85, 78, 92, 88);

    match scores {
        (first, ..) => println!("First subject: {}", first),
    }

    match scores {
        (.., last) => println!("Last subject: {}", last),
    }

    match scores {
        (first, .., last) => println!("First subject {}, last subject {}", first, last),
    }

    // .. on a slice
    let data: &[i32] = &[10, 20, 30, 40, 50];

    match data {
        [first, .., last] => println!("Head = {}, tail = {}", first, last),
        [only] => println!("Just one: {}", only),
        [] => println!("Empty"),
    }
}
```

## Recap

- `..` ignores multiple fields or values at once.
- On a struct in `match`: `Player { hp, .. }` takes only `hp` and ignores the rest; same for `enum` `struct` variants.
- On a tuple: `(first, ..)` takes only the first, `(.., last)` only the last; tuple `struct`s and `enum` tuple variants use similar syntax.
- In arrays and slices: `[first, ..]` takes the first; `[first, .., last]` takes head and tail.
- `..` can appear only once per layer of a pattern.
