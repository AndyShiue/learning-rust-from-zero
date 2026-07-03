# `char`

## Goal of This Episode

Meet the `char` type — the type for holding "a single character."

## Main Text

We've used strings before (text wrapped in double quotes `"`). Today let's meet a smaller unit — the **character** (char).

### What Is a `char`?

A `char` is **one character**. Note: "one," not a string of them.

```rust,editable
fn main() {
    let c = 'A';
    let c2 = '你';
    let c3 = '🦀';

    println!("{}", c);
    println!("{}", c2);
    println!("{}", c3);
}
```

### Single Quotes vs Double Quotes

This matters:

- **Single quotes `'`** → `char`; holds exactly **one** character.
- **Double quotes `"`** → a string; can hold many characters.

```rust,editable
fn main() {
    let c = 'A';     // char, one character
    let s = "Hello"; // string, five characters
}
```

If you put more than one character inside single quotes, Rust reports an error:

```rust,compile_fail
# fn main() {
    let c = 'AB'; // ❌ Error! A char can hold only one character
# }
```

### Unicode

Rust's `char` supports **Unicode**, so it's not just English letters — Chinese, Japanese, even emoji all work:

```rust,editable
fn main() {
    let letter = 'R';
    let chinese = '美';
    let japanese = 'の';
    let emoji = '😊';

    println!("{} {} {} {}", letter, chinese, japanese, emoji);
}
```

Each of these is a legal `char`.

### Type Annotation

If you want to annotate the type explicitly:

```rust,editable
fn main() {
    let c: char = 'Z';
    println!("{}", c);
}
```

Usually there's no need, though — Rust sees single quotes and knows it's a `char`.

## Recap

- `char` is the "one character" type, wrapped in **single quotes**: `'A'`, `'你'`, `'🦀'`.
- It supports Unicode: Chinese, Japanese, and emoji are all legal `char`s.
- Single quote `'` = `char` (one character); double quote `"` = string (a sequence of characters). Don't mix them up.
