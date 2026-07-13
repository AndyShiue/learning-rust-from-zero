# Multiline Strings & Raw String Literals

## Goal of This Episode

Learn to write multiline strings, line-continuation backslashes, and raw strings free of escape characters in Rust.

> This episode supplements **Chapter 1**.

## Concept

Programming regularly involves multiline text, file paths, or strings full of special characters. Rust provides some handy syntax for these situations.

### Multiline Strings

In Rust, string literals can span lines directly:

```rust,noplayground
# fn main() {
    let poem = "Moonlight before my bed,
like frost upon the ground.";
# }
```

The newlines get included in the string as-is.

### The Line Continuation `\`

If you want a long string split across source lines but **without** newlines in the result, end the line with `\`. It swallows the newline and the next line's leading whitespace:

```rust,noplayground
# fn main() {
    let long = "This is a very long sentence, \
                yet really just one line.";
    // Result: "This is a very long sentence, yet really just one line."
# }
```

### Raw String Literals

Sometimes strings hold lots of backslashes (Windows paths, say), and escaping each is a chore. The `r"..."` syntax skips escaping entirely:

```rust,noplayground
# fn main() {
    let path = r"C:\Users\test\documents";
    // No need for "C:\\Users\\test\\documents"
# }
```

### Raw Strings Containing Quotes

What if the raw string needs double quotes inside? Use the `r#"..."#` syntax:

```rust,noplayground
# fn main() {
    let json = r#"{"name": "Andy", "age": 29}"#;
# }
```

What if the string even contains `"#`? Add more `#` layers:

```rust,noplayground
# fn main() {
    let tricky = r##"There's a "#" symbol here"##;
# }
```

You can use up to 255 `#` characters, as long as the opening and closing counts match.

## Example Code

```rust,editable
fn main() {
    // A multiline string
    let haiku = "An old pond—
a frog leaps in,
the sound of water";
    println!("Haiku:\n{}", haiku);
    println!("---");

    // The line continuation: \ swallows the newline and leading whitespace
    let sentence = "Rust is a programming language focused on safety, \
                    performance, and concurrency.";
    println!("{}", sentence);
    println!("---");

    // Raw strings: no escape processing
    let win_path = r"C:\Users\Andy\Desktop\project";
    println!("Path: {}", win_path);

    // Great for regular expressions and similar
    let pattern = r"\d+\.\d+";
    println!("Regex: {}", pattern);

    // A raw string containing double quotes
    let json = r#"{"name": "Ming", "score": 95}"#;
    println!("JSON: {}", json);

    // Multiple #s — for when the string contains "#
    let code_sample = r##"
        let s = r#"hello"#;
        println!("{}", s);
    "##;
    println!("Code sample: {}", code_sample);

    // Raw strings can span lines too
    let html = r#"
<html>
    <body>
        <h1>Hello, Rust!</h1>
    </body>
</html>
"#;
    println!("{}", html);
}
```

## Recap

- String literals can span lines directly; the newlines are preserved.
- A `\` at line's end continues to the next line, dropping the newline and the next line's leading whitespace.
- `r"..."` is a raw string, processing no escapes at all (`\n`, `\\`, etc. stay verbatim).
- `r#"..."#` lets a raw string contain double quotes.
- A raw string can use up to 255 `#` characters (`r##"..."##`, `r###"..."###`, and so on), as long as the opening and closing counts match.
- Raw strings shine for Windows paths, regular expressions, JSON, embedded code, and the like.
