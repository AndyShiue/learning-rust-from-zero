# Lifetime Elision Rules

## Goal of This Episode

Understand Rust's lifetime elision rules, and why most of the time you needn't write lifetime annotations by hand.

## Concept

Last episode, we only wrote `'a` by hand for cases like `longer`, where the return value might come from different reference parameters. What about other functions that return references? Do they all need annotations too?

Good news: mostly not. Rust has a set of **elision rules** that fill in lifetime annotations for you automatically.

### The Three Elision Rules

The Rust compiler tries inferring lifetimes with these three rules:

**Rule 1: each position in the parameters that can hold a lifetime gets its own independent lifetime**

```rust,ignore
fn foo(a: &str, b: &str)
// The compiler sees: fn foo<'a, 'b>(a: &'a str, b: &'b str)
```

**Rule 2: if after Rule 1 there is exactly one input lifetime, the return value's lifetime equals it**

```rust,ignore
fn first_word(s: &str) -> &str
// Rule 1: fn first_word<'a>(s: &'a str) -> &str
// Rule 2: only one input lifetime 'a → fn first_word<'a>(s: &'a str) -> &'a str
```

That's why `first_word` above needs no `'a` — with just one input lifetime, Rule 2 handles it.

Note that one parameter can carry several input lifetimes — e.g. `&'a &'b T` (a reference to a reference) has two (`'a` and `'b`). With two or more input lifetimes, Rule 2 no longer applies.

**Rule 3: if there's a `&self` or `&mut self` parameter, the return value's lifetime equals `self`'s**

```rust,ignore
impl MyStruct {
    fn name(&self) -> &str { ... }
    // The compiler sees: fn name<'a>(&'a self) -> &'a str
}
```

### When Do the Rules Fall Short?

When there are several reference parameters and it's unclear which one the return value's lifetime binds to — exactly the situation of last episode's `longer` function. That's when manual annotation becomes mandatory.

### Summary

- One reference parameter → almost never needs writing.
- A method returning part of `&self` → no writing needed.

## Example Code

```rust,editable
// Rule 2: one input lifetime, inferred automatically
fn trim_hello(s: &str) -> &str {
    if s.len() >= 5 {
        &s[5..]
    } else {
        s
    }
}

struct Article {
    title: String,
    content: String,
}

impl Article {
    fn new(title: String, content: String) -> Article {
        Article { title, content }
    }

    // Rule 3: with a &self parameter, the return's lifetime binds to self
    fn title(&self) -> &str {
        &self.title
    }

    fn summary(&self) -> &str {
        &self.content
    }
}

// Multiple reference parameters + returning a reference → manual annotation needed
fn pick_longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() {
        a
    } else {
        b
    }
}

fn main() {
    // Rule 2: no lifetime to write
    let greeting = String::from("Hello, world!");
    let trimmed = trim_hello(&greeting);
    println!("{}", trimmed);

    // Rule 3: methods taking references need no lifetimes
    let article = Article::new(
        String::from("Rust lifetimes"),
        String::from("Not as scary as they seem"),
    );
    println!("Title: {}", article.title());
    println!("Summary: {}", article.summary());

    // Multiple reference parameters: manual annotation
    let a = String::from("hello");
    let b = String::from("hi");
    let result = pick_longer(&a, &b);
    println!("The longer one: {}", result);
}
```

## Recap

- Rust has three **elision rules** that fill in lifetime annotations automatically most of the time.
- Rule 1: each lifetime-capable position in the parameters gets its own independent lifetime.
- Rule 2: exactly one input lifetime → the return value's lifetime automatically equals it.
- Rule 3: a method with `&self` or `&mut self` → the return value's lifetime automatically equals `self`'s.
