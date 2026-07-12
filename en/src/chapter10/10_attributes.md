# A Tour of attributes

## Goal of This Episode

Survey Rust's common attributes and understand the difference between outer and inner ones.

## Concept

### outer vs inner

- **outer attribute** `#[...]`: goes above an item and decorates that item.
- **inner attribute** `#![...]`: goes inside an item (usually at the top of a file) and decorates the enclosing item as a whole.

```rust,noplayground
#![allow(dead_code)] // inner: applies to the whole mod

#[derive(Debug)]     // outer: applies to the struct below
struct Point { x: i32, y: i32 }
#
# fn main() {}
```

The difference is one exclamation mark `!`.

### derive

```rust,noplayground
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
struct Color(u8, u8, u8);
#
# fn main() {}
```

### Warning Control

```rust,ignore
#[allow(dead_code)]        // don't warn about unused code
#[allow(unused_variables)] // don't warn about unused variables
#[warn(missing_docs)]      // turn on the "missing docs" warning
#[deny(unsafe_code)]       // upgrade "uses unsafe" to an error
```

### Conditional Compilation

```rust,ignore
#[cfg(target_os = "windows")]
fn windows_only() { /* ... */ }

#[cfg(test)]
mod tests { /* ... */ }
```

### Testing

```rust,noplayground
#[test]
fn test_add() { assert_eq!(1 + 1, 2); }

#[test]
#[should_panic]
fn test_panic() { panic!("on purpose"); }

#[test]
#[ignore]
fn slow_test() { /* skip for now */ }
#
# fn main() {}
```

### Performance Hints

When a function is called, the program has to jump to the function's location, run it, then jump back. **`inline`** is an optimization: the compiler "pastes" the function's code directly into the call site, saving the jumping around.

```rust,ignore
#[inline]         // suggest the compiler inline this function
#[inline(always)] // force inlining
#[inline(never)]  // forbid inlining
```

Most of the time you don't need to write these by hand — the compiler decides on its own. They're only needed for small functions called across `crate`s, or in performance-critical spots.

### Memory Layout

Rust's compiler freely rearranges a `struct`'s fields in memory and adjusts alignment to save space. But if you're interoperating with C, C `struct`s have fixed layout rules — `#[repr(C)]` tells Rust "lay this out by C's rules":

```rust,ignore
#[repr(C)]  // use C's memory layout
#[repr(u8)] // enum underlying type (from last episode)
```

### Other Common Ones

`#[must_use]` on a function or type makes the compiler warn if a caller receives the return value but doesn't use it. `Result` carries `#[must_use]` — that's why you see a warning when you don't handle a `Result`.

```rust,noplayground
#[must_use]
fn compute() -> i32 { 42 }

fn main() {
    compute(); // warning: unused return value
    let _ = compute(); // OK: explicitly ignore with let _
}
```

```rust,ignore
#[non_exhaustive] // tell other crates this enum / struct may gain new items later
#[deprecated]     // mark as deprecated
#[deprecated(since = "2.0", note = "use new_function instead")]
```

### Doc Comments Are Attribute Shorthand

```rust,ignore
/// This is a function
fn foo() {}

// is the same as
#[doc = "This is a function"]
fn foo() {}
```

`///` is just shorthand for `#[doc = "..."]`. Likewise, `//!` is shorthand for `#![doc = "..."]` — used at the top of a file to document a whole `mod` or `crate`.

## Example Code

```rust,editable
#![allow(dead_code)]

#[derive(Debug, Clone, PartialEq)]
struct Config {
    name: String,
    value: i32,
}

#[must_use]
fn create_config(name: &str, value: i32) -> Config {
    Config { name: String::from(name), value }
}

#[deprecated(note = "use create_config instead")]
fn make_config() -> Config {
    create_config("default", 0)
}

#[cfg(target_os = "linux")]
fn linux_only() {
    println!("only runs on Linux");
}

fn main() {
    let c = create_config("test", 42);
    println!("{:?}", c);
}
```

## Recap

- `#[...]` (outer) decorates the item below it; `#![...]` (inner) decorates the item containing it.
- `#[derive(...)]`: auto-implement `trait`s.
- `#[allow/warn/deny(...)]`: control warnings.
- `#[cfg(...)]`: conditional compilation.
- `#[test]` / `#[should_panic]` / `#[ignore]`: test-related
- `#[must_use]`: warn when the return value is ignored.
- `#[deprecated]`: mark as deprecated.
- `///` is shorthand for `#[doc = "..."]`; `//!` is shorthand for `#![doc = "..."]`.
