# Lifetimes on Types

## Goal of This Episode

Learn to annotate lifetimes on `struct`s and `enum`s that contain references, and simplify annotations with the anonymous lifetime `'_`.

## Concept

Until now, our `struct`s and `enum`s have owned their own data (`String`, `i32`, etc.). But sometimes you want them to borrow someone else's data — say, storing an `&str` instead of a `String`.

### References inside Types

```rust,compile_fail
struct Excerpt {
    text: &str, // Compile error!
}
#
# fn main() {}
```

This errors, because Rust needs to know: "How long can this `&str` live?" If the borrowed data is released, the reference in the `struct` becomes dangling.

The fix is a lifetime parameter:

```rust,noplayground
struct Excerpt<'a> {
    text: &'a str,
}
#
# fn main() {}
```

`'a` tells Rust: "This `struct` may not outlive the data it borrows."

Same for `enum`s — if a variant carries a reference, it needs a lifetime:

```rust,noplayground
enum Token<'a> {
    Word(&'a str),
    Number(i32),
}
#
# fn main() {}
```

`Token::Word` borrows a piece of text, so a `Token` can't outlive that text. `Token::Number` contains no references, but since it shares the `enum` with `Word`, creating `Token::Number(42)` still requires an `'a` — it just has no practical effect for `Number`.

### Using a Type with a Lifetime

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
# fn main() {
    let novel = String::from("A very long story...");
    let excerpt = Excerpt { text: &novel };
# }
```

`excerpt` borrows `novel`'s data, so `excerpt` can't live longer than `novel`.

### The Anonymous Lifetime `'_`

When a lifetime can be inferred, you can simplify with `'_`:

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
fn print_excerpt(e: &Excerpt<'_>) {
    println!("{}", e.text);
}
#
# fn main() {}
```

`'_` tells Rust "I know a lifetime belongs here — infer it yourself." Remember the type placeholder `_` from Episode 5? `'_` is its lifetime counterpart.

### `impl` for a `struct` with a Lifetime

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
impl<'a> Excerpt<'a> {
    fn text(&self) -> &str {
        self.text
    }
}
#
# fn main() {}
```

Just like `impl` on a generic `struct` — `impl<'a>` declares the lifetime parameter, and `Excerpt<'a>` uses it.

Note that `fn text(&self) -> &str` needs no lifetime annotations at all — last episode's third elision rule kicks in: with `&self` on a method, the return value's lifetime automatically equals `self`'s.

### Lifetime-carrying Types as Function Parameters

If a function receives a type carrying a lifetime, `'_` lets the compiler infer:

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
fn into_text(e: Excerpt<'_>) -> &str {
    e.text
}
#
# fn main() {}
```

Note you can't just write `Excerpt` with nothing attached — `Excerpt` has a mandatory lifetime parameter, just as `Vec` has a mandatory type parameter; it can't be omitted. But `'_` lets the compiler infer it.

Written out in full:

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
fn into_text<'a>(e: Excerpt<'a>) -> &'a str {
    e.text
}
#
# fn main() {}
```

The elision rules see `Excerpt<'_>` carrying one input lifetime, and Rule 2 sets the return value's lifetime to the same one.

Note that `e` itself isn't a reference — `e` gets `drop`ped when the function ends. But the returned `&'a str` doesn't borrow `e`; it borrows the text stored inside `e` — text whose lifespan is `'a`, unrelated to `e`'s own.

## Example Code

```rust,editable
// A struct holding a reference needs a lifetime annotation
struct Excerpt<'a> {
    text: &'a str,
    page: i32,
}

impl<'a> Excerpt<'a> {
    fn new(text: &'a str, page: i32) -> Excerpt<'a> {
        Excerpt { text, page }
    }

    fn text(&self) -> &str {
        self.text
    }

    fn summary(&self) -> String {
        let mut s = String::from("Page ");
        let page_str = self.page.to_string();
        s.push_str(&page_str);
        s.push_str(": ");
        s.push_str(self.text);
        s
    }
}

// Using the anonymous lifetime '_
fn print_excerpt(e: &Excerpt<'_>) {
    println!("[p.{}] {}", e.page, e.text);
}

fn main() {
    let novel = String::from("A long, long time ago, there was a programmer...");

    // excerpt borrows novel's data
    let excerpt = Excerpt::new(&novel[..15], 1);
    println!("{}", excerpt.text());
    println!("{}", excerpt.summary());

    // A function using the anonymous lifetime
    print_excerpt(&excerpt);

    // excerpt can't outlive novel
    // If novel were dropped, excerpt would become unusable
}
```

## Recap

- A `struct` holding references must annotate lifetimes: `struct Excerpt<'a> { text: &'a str }`.
- The lifetime guarantees the `struct` won't outlive the data it borrows.
- `'_` is the anonymous lifetime, letting the compiler infer (the lifetime version of `_`).
- `impl` for a lifetime-carrying `struct`: `impl<'a> Excerpt<'a> { ... }`.
