# Escape Characters

## Goal of This Episode

Learn to use the backslash `\` to insert newlines, tabs, and other special characters into strings.

## Main Text

Sometimes you want to put something "special" in a string — a newline, a tab, or a double quote itself. That's when you need **escape characters**.

### `\n` — Newline

```rust,editable
fn main() {
    println!("First line\nSecond line");
}
```

`\n` tells Rust: "Break the line here." It doesn't literally print the two characters `\n` — it produces an actual line break.

### `\t` — Tab

```rust,editable
fn main() {
    println!("Name\tScore");
    println!("Ming\t85");
    println!("Hua\t92");
}
```

`\t` inserts a tab space.

### `\\` — the Backslash Itself

What if you want to print the backslash `\` itself? Since `\` is already taken as the start of escape sequences, you need two backslashes:

```rust,editable
fn main() {
    println!("File path: C:\\Users\\Andy");
}
```

### `\"` — Double Quote

Strings are wrapped in `"`, so what if the string needs a `"` inside it?

```rust,editable
fn main() {
    println!("He said: \"Hello!\"");
}
```

`\"` tells Rust: "This double quote is part of the string's content, not the end of the string."

### Using Them in a `char`

Escape characters work inside a `char` too:

```rust,editable
fn main() {
    let newline: char = '\n';
    let tab: char = '\t';
    let backslash: char = '\\';

    print!("A{}B{}C{}", newline, tab, backslash);
}
```

### `\'` — Single Quote

Inside a char, if you want to represent the single quote itself, you have to escape it:

```rust,editable
fn main() {
    let quote: char = '\'';
    println!("{}", quote);
}
```

Because a char is wrapped in `'`, putting a `'` inside requires `\'`.

### When You Don't Need to Escape

Inside a string (`""`), single quotes don't need escaping — use them directly:

```rust,editable
fn main() {
    println!("It's a test"); // ' needs no escaping inside a string
}
```

Likewise, inside a char (`''`), double quotes don't need escaping:

```rust,editable
fn main() {
    let c: char = '"'; // " needs no escaping inside a char
    println!("{}", c);
}
```

In short: **only the symbol doing the wrapping needs escaping; the other one doesn't.**

### At a Glance

| Escape | Effect |
|----------|------|
| `\n` | newline |
| `\t` | tab |
| `\\` | backslash `\` |
| `\"` | double quote `"` |
| `\'` | single quote `'` |

## Recap

- Escape characters start with `\` and stand for special characters: `\n` (newline), `\t` (tab), `\\` (backslash).
- `\"` represents a double quote inside a string; `\'` represents a single quote inside a char.
- Escape characters work in both strings and `char`s.
- Rule of thumb: only the wrapping symbol needs escaping; the other one doesn't.
