# The `cfg!` Macro

## Goal of This Episode

Learn to use `cfg!` to choose logic at runtime based on conditions, and how it differs from `#[cfg]`.

## Concept

### `cfg!` Returns a `bool`

Last episode covered `#[cfg(...)]` — conditional compilation, where code that doesn't match the condition is removed wholesale. But sometimes you just want to take different branches based on a condition, without removing whole blocks of code. That's what `cfg!` does:

```rust,editable
fn main() {
    if cfg!(target_os = "windows") {
        println!("you're on Windows");
    } else {
        println!("you're not on Windows");
    }
}
```

### How It Differs from `#[cfg]`

| | `#[cfg(...)]` | `cfg!(...)` |
|--|--|--|
| Effect | Conditional compilation: whole block kept or removed | Returns a `bool` |
| Timing | Non-matching code disappears, never compiled | Both sides are compiled; the branch is picked at runtime |

An important difference: with `#[cfg]`, the non-matching block doesn't exist at all — even calls to nonexistent functions inside it won't error. But `cfg!` compiles both sides — if one side has a compile error, it errors regardless of whether the condition holds.

```rust,ignore
// #[cfg] version: on Windows, linux_only() isn't compiled — no error
#[cfg(target_os = "linux")]
fn linux_only() { /* Linux-specific functionality */ }

// cfg! version: both sides get compiled
if cfg!(target_os = "linux") {
    // linux_only(); // if the function doesn't exist, this is a compile error even on Windows!
}
```

### Common Conditions

`#[cfg]` and `cfg!` accept the same conditions:

- `target_os = "windows"` / `"linux"` / `"macos"`
- `target_arch = "x86_64"` / `"aarch64"`.
- `debug_assertions` — `true` in debug mode
- `feature = "my_feature"` — Cargo features
- `test` — `true` during `cargo test`

## Example Code

```rust,editable
fn main() {
    if cfg!(debug_assertions) {
        println!("debug mode");
    } else {
        println!("release mode");
    }

    let os = if cfg!(target_os = "windows") {
        "Windows"
    } else if cfg!(target_os = "linux") {
        "Linux"
    } else if cfg!(target_os = "macos") {
        "macOS"
    } else {
        "other"
    };
    println!("operating system: {}", os);
}
```

## Recap

- `cfg!(...)` returns a `bool`; both sides of the code are compiled, and the choice happens at runtime.
- `#[cfg(...)]` is conditional compilation; non-matching code is removed wholesale.
- Both accept the same conditions: `target_os`, `debug_assertions`, `feature`, `test`, etc.
