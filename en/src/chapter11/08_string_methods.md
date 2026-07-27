# String Methods

## Goal of This Episode

Meet the most commonly used methods on `&str` and `String`, and Rust strings' relationship with UTF-8.

## Concept

When you read and write files, the content usually comes as strings, and you'll need all kinds of methods to work with them — searching, splitting, trimming, replacing, and so on. We've used `.trim()`, `.parse()`, and `.chars()` before, but `&str` and `String` carry a great many more useful methods. This episode covers the most common ones.

### Searching

```rust,noplayground
# fn main() {
    let s = "hello, world!";

    s.contains("world");    // true
    s.starts_with("hello"); // true
    s.ends_with("!");       // true
    s.find("world");        // Some(7) — position of the first occurrence (byte index)
# }
```

### Trimming and Replacing

```rust,noplayground
# fn main() {
    "  hello  ".trim();       // "hello"
    "  hello  ".trim_start(); // "hello  "
    "  hello  ".trim_end();   // "  hello"

    "hello world".replace("world", "Rust"); // "hello Rust"
# }
```

### Splitting

```rust,noplayground
# fn main() {
    let parts: Vec<&str> = "a,b,c".split(',').collect();
    // ["a", "b", "c"]

    let words: Vec<&str> = "hello  world".split_whitespace().collect();
    // ["hello", "world"]
# }
```

`split` returns an iterator, usually paired with `collect`.

### Iterating Character by Character

```rust,editable
fn main() {
    for c in "hello".chars() {
        println!("{}", c);
    }
}
```

`.chars()` returns an iterator of Unicode characters. There's also `.bytes()` for raw bytes.

### Case

```rust,noplayground
# fn main() {
    "Hello".to_uppercase(); // "HELLO"
    "Hello".to_lowercase(); // "hello"
# }
```

### `len` Counts Bytes

```rust,noplayground
# fn main() {
    "hello".len();         // 5
    "hello".is_empty();    // false
    "hello".repeat(3);     // "hellohellohello"

    // note: .len() returns the byte count, not the character count
    "你好".len();           // 6 (UTF-8 bytes)
    "你好".chars().count(); // 2 (characters)
# }
```

## Example Code

```rust,editable
fn main() {
    let sentence = "  Hello, Rust World!  ";

    // trim whitespace
    let trimmed = sentence.trim();
    println!("trimmed: '{}'", trimmed);

    // search
    println!("contains Rust: {}", trimmed.contains("Rust"));
    println!("position of Rust: {:?}", trimmed.find("Rust"));

    // split
    let words: Vec<&str> = trimmed.split_whitespace().collect();
    println!("word count: {}", words.len());
    for word in &words {
        println!("  {}", word);
    }

    // replace
    let replaced = trimmed.replace("Rust", "World");
    println!("after replacing: {}", replaced);

    // UTF-8
    let chinese = "你好世界";
    println!("bytes: {}", chinese.len());                // 12
    println!("characters: {}", chinese.chars().count()); // 4

    for (i, c) in chinese.chars().enumerate() {
        println!("character {}: {}", i + 1, c);
    }
}
```

## Recap

- `contains`, `starts_with`, `ends_with`, `find`: searching
- `trim`, `trim_start`, `trim_end`: trimming whitespace
- `replace`: replacing
- `split`, `split_whitespace`: splitting; they return iterators.
- `chars`: iterate by character; `bytes`: iterate by byte.
- `len` returns the byte count; use `.chars().count()` for characters.
