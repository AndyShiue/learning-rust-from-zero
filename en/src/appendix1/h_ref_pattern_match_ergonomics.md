# `ref` Patterns and `match` Ergonomics

## Goal of This Episode

Learn what the `ref` keyword does in pattern matching, and why modern Rust hardly ever needs a hand-written `ref`.

> This episode supplements **Chapter 3**.

## Concept

This episode covers syntax you may have seen in older code but will hardly ever use in modern Rust: `ref`. Understanding its existence and mechanics helps you read other people's code.

### What Is `ref`?

In a pattern, `ref` makes the bound variable a reference instead of taking ownership:

```rust,noplayground
# fn main() {
    let val = String::from("hello");
    let ref r = val; // r's type is &String
    // Equivalent to: let r = &val;
# }
```

You might think: why not just write `&val`? Right — in a `let` binding, the two are fully equivalent. `ref` earns its keep mainly inside `match`.

### `ref` in `match`

In the old days (before Rust 1.26), borrowing instead of moving inside a `match` required a hand-written `ref`:

```rust,editable
fn main() {
    let opt = Some(String::from("hello"));
    match opt {
        Some(ref s) => println!("{}", s), // Borrowed, not moved
        None => println!("nothing"),
    }
    // opt remains usable, since we only borrowed the value inside
}
```

Without the `ref`, `s` would take the `String`'s ownership, and `opt` would be unusable afterward.

### `match` Ergonomics (Rust 1.26+)

Starting with Rust 1.26, the compiler got smarter. When you `match` a **reference**, the bindings inside automatically become references:

```rust,editable
fn main() {
    let opt = Some(String::from("hello"));
    match &opt {     // Note the &opt here
        Some(s) => { // s is automatically &String; no ref needed
            println!("{}", s);
        }
        None => println!("nothing"),
    }
    // opt remains usable!
}
```

This is what's called **`match` ergonomics**: the effect you used to have to spell out with `ref`, the compiler now gives you automatically once it sees you `match` a reference (`&opt`).

### So Is `ref` Still Needed?

Hardly ever. In 99% of cases, just `match` a reference (`match &value`) and the compiler handles the rest. But when reading old code, you should at least know what a `ref` is doing.

## Example Code

```rust,editable
fn main() {
    // ===== ref basics =====
    let name = String::from("Rust");
    let ref r = name; // r: &String
    println!("The ref binding: {}", r);
    println!("The original remains usable: {}", name);

    // ===== The old style: ref in match to avoid the move =====
    let data = Some(String::from("important data"));

    match data {
        Some(ref s) => println!("Old-style borrow: {}", s),
        None => println!("Empty"),
    }
    println!("data remains: {:?}", data); // No move, thanks to ref

    // ===== The new style: match ergonomics =====
    let data2 = Some(String::from("a new world"));

    match &data2 {   // Matching a reference
        Some(s) => { // s is automatically &String
            println!("New-style borrow: {}", s);
        }
        None => println!("Empty"),
    }
    println!("data2 remains: {:?}", data2);

    // ===== A more elaborate example =====
    let pairs = vec![
        (String::from("Taipei"), 25),
        (String::from("Tokyo"), 10),
        (String::from("New York"), 5),
    ];

    // match ergonomics also makes destructuring in for loops natural
    for (city, temp) in &pairs {
        // city: &String, temp: &i32 (automatically borrowed)
        println!("{} is {} degrees", city, temp);
    }
    println!("pairs remains, {} entries in total", pairs.len());
}
```

## Recap

- `let ref x = val;` equals `let x = &val;` — identical in a `let`.
- In a `match`, `Some(ref x)` borrows the inner value rather than moving it.
- **`match` ergonomics (Rust 1.26+)**: matching a reference makes the pattern's variables automatically references.
- Modern Rust hardly needs a manual `ref` — `match &value` suffices.
- `for (k, v) in &collection` benefits from `match` ergonomics too: `k` and `v` are automatically references.
- Knowing `ref` is mostly for reading older code.
