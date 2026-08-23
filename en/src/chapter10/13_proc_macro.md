# Proc Macros

## Goal of This Episode

Meet the three kinds of proc macros and understand how they work. This episode is only a rough introduction to the concept and skeleton of proc macros — it won't walk you through writing a complete one. If you need that, search for a dedicated tutorial.

## Concept

### What Is a proc macro

Last episode's `macro_rules!` expands code via pattern matching. But some things it can't do — like reading a `struct`'s field names to generate code automatically. How does `#[derive(Debug)]` know what fields your `struct` has? The answer is **proc macros** (procedural macros).

A proc macro receives your code as input (a stream of tokens) and produces new code (also a stream of tokens).

### `TokenStream`

A proc macro's input and output are both `TokenStream`s — sequences of Rust code tokens. When `struct Foo { x: i32 }` comes in, the proc macro sees a stream of tokens: `struct`, `Foo`, `{`, `x`, `:`, `i32`, `}`.

### The Three Kinds of proc macros

**1. `derive` macros**

Used with `#[derive(...)]` — the most common kind.

```rust,ignore
#[proc_macro_derive(MyDerive)]
pub fn my_derive(input: TokenStream) -> TokenStream {
    // input: the code of the struct / enum marked with #[derive(MyDerive)]
    // return: new code to "attach" alongside (the original struct / enum isn't replaced)
    TokenStream::new()
}
```

Usage: `#[derive(MyDerive)] struct Foo { x: i32 }`

**2. attribute macros**

Custom attributes.

```rust,ignore
#[proc_macro_attribute]
pub fn my_attr(attr: TokenStream, item: TokenStream) -> TokenStream {
    // attr: the attribute's arguments
    // item: the entire item being marked
    // return: "replaces" the original item
    item
}
```

Usage: `#[my_attr(some_arg)] fn my_function() { ... }`

**3. function-like macros**

Look like function calls.

```rust,ignore
#[proc_macro]
pub fn my_macro(input: TokenStream) -> TokenStream {
    // input: whatever is inside the parentheses
    // return: the expanded code
    input
}
```

Usage: `my_macro!(any tokens);`

### How the Three Differ

- **`derive`**: **attaches** new code; doesn't replace the original `struct` / `enum`.
- **Attribute**: **replaces** the marked item.
- **Function-like**: the contents in the brackets get **expanded** into new code.

### A Separate `crate`

Proc macros must be defined in their own `crate`, with this in `Cargo.toml`:

```toml
[lib]
proc-macro = true
```

### `syn` and `quote`

In practice, two community `crate`s almost always come along:
- **`syn`**: parses a `TokenStream` into structured data (e.g. knowing "this is a `struct` with one field named `x`").
- **`quote`**: conveniently generates a `TokenStream` from structured data.

Without them you'd be handling tokens one by one — very painful.

## Example Code

Here are minimal skeletons for the three kinds of proc macros (they need to live in a separate proc-macro `crate`):

```rust,ignore
use proc_macro::TokenStream;

// 1. derive macro
#[proc_macro_derive(MyDerive)]
pub fn my_derive(input: TokenStream) -> TokenStream {
    // parse input with syn, generate code with quote
    TokenStream::new() // generates nothing
}

// 2. attribute macro
#[proc_macro_attribute]
pub fn my_attr(_attr: TokenStream, item: TokenStream) -> TokenStream {
    item // returned untouched
}

// 3. function-like macro
#[proc_macro]
pub fn my_macro(input: TokenStream) -> TokenStream {
    input // returned untouched
}
```

And here's the usage side (in another `crate`):

```rust,ignore
// suppose the proc-macro crate is called my_macros
use my_macros::{MyDerive, my_attr, my_macro};

#[derive(MyDerive)]
struct Foo { x: i32 }

#[my_attr]
fn hello() {
    println!("hello");
}

fn main() {
    hello();
    my_macro!(any tokens can go here);
}
```

## Recap

- Proc macros come in three kinds: `derive`, attribute, and function-like.
- At heart they are compile-time functions that take a `TokenStream` and return a `TokenStream`.
- `derive` attaches code, attribute replaces the item, function-like expands its contents.
- They must be defined in a separate `crate` (`proc-macro = true`).
- `syn` (parsing) and `quote` (generation) are the usual companions.
