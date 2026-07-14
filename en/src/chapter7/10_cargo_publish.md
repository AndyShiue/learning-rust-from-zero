# `cargo publish`

## Goal of This Episode

Learn to publish your library to crates.io, making it available to Rust developers worldwide.

## Concept

So far we've learned to organize code, write documentation, and use other people's `crate`s. This episode flips the direction — publishing a project of your own.

### Account Setup

First, you need a crates.io account:

1. Go to [crates.io](https://crates.io) and log in with a GitHub account.
2. On the account settings page, generate an **API Token**.
3. In the terminal, run:

```bash
cargo login
```

After pressing enter, the terminal prompts you to paste the token — paste it, press enter again, done. The token is stored locally and used automatically for future publishes.

### Preparing `Cargo.toml`

Before publishing, `Cargo.toml` needs some required metadata:

```toml
[package]
name = "my-awesome-lib"
version = "0.1.0"
edition = "2024"
description = "A wonderful math utility library"
license = "MIT"
repository = "https://github.com/yourname/my-awesome-lib"
readme = "README.md"
keywords = ["math", "utility"]
categories = ["mathematics"]
```

Per [the official documentation](https://doc.rust-lang.org/cargo/reference/publishing.html), fill in before publishing:

- `license` (or `license-file`): the open-source license (e.g. `MIT`, `Apache-2.0`, `MIT OR Apache-2.0`).
- `description`: a one-line summary
- `homepage`: the project homepage URL
- `repository`: the source repository URL
- `readme`: the README file's path

Recommended but not required:

- `keywords`: search keywords (up to 5)
- `categories`: categories (must match crates.io's category list)

### Pre-publish Checks

Before publishing, `cargo package` checks for problems:

```bash
cargo package
```

This simulates the packaging process, checking for missing required fields and other issues.

### Publish!

Once everything's ready:

```bash
cargo publish
```

Done! Your project is now on crates.io, and anyone can `cargo add my-awesome-lib`.

### The Version Update Flow

After publishing, to release an update:

1. Modify the code.
2. Bump `version` in `Cargo.toml`, following [SemVer (semantic versioning)](https://semver.org/).
3. `cargo publish` again.

SemVer's rules:

- **Before 1.0** (`0.x.y`): the whole API is considered unstable; any release may break things.
- **After 1.0**:
  - Bug fixes: `1.0.0` → `1.0.1` (patch).
  - New features (backward compatible): `1.0.1` → `1.1.0` (minor).
  - Breaking changes: `1.1.0` → `2.0.0` (major) — the first number changes.

Why does SemVer fuss so much over "breaking changes"? Because once you've published, **your public API (especially the `pub` things) is no longer just your own business** — other people's programs `use` your functions and depend on your type and method declarations. Your public API becomes **a promise to your users**: the surface they depend on isn't yours to change on a whim.

The promise **isn't limited to `pub` things: documented behavior can be part of it too**. Private implementation details remain yours to change as long as those promises still hold. So the question most worth asking before publishing or updating: "Do I really want to maintain this `pub` long-term?" The more you publish, the more you promise, and the less room remains for changing things without breaking someone. Keeping the unnecessary private (or `pub(crate)`) preserves your future freedom to change.

**Note**: published versions **can't be deleted or overwritten**. If a version turns out badly broken, `cargo yank` marks it as discouraged — but those already using it are unaffected:

```bash
cargo yank --version 0.1.0
```

### Best Done Before Publishing

- Write a good `README.md` (shown on the `crate`'s crates.io page).
- Run `cargo test` and confirm all tests pass.
- Write doc comments with `///` (last episode's lesson).
- Make sure there's example code.
- Check the docs look right with `cargo doc --open`.

## Example Code

The complete structure of a small library ready for publishing:

```ignore
my-math-lib/
├── Cargo.toml
├── README.md
└── src/
    └── lib.rs
```

**Cargo.toml:**

```toml
[package]
name = "my-math-lib"
version = "0.1.0"
edition = "2024"
description = "Simple math utility functions"
license = "MIT"
homepage = "https://example.com/my-math-lib"
repository = "https://github.com/example/my-math-lib"
readme = "README.md"
keywords = ["math", "utility"]
categories = ["mathematics"]
```

**src/lib.rs:**

```rust,noplayground
//! # My Math Lib
//!
//! Provides simple, handy math functions.

/// Computes the greatest common divisor.
///
/// # Examples
///
/// ```
/// use my_math_lib::gcd;
///
/// assert_eq!(gcd(12, 8), 4);
/// ```
pub fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        let temp = b;
        b = a % b;
        a = temp;
    }
    a
}

/// Computes the least common multiple.
///
/// # Examples
///
/// ```
/// use my_math_lib::lcm;
///
/// assert_eq!(lcm(4, 6), 12);
/// ```
pub fn lcm(a: u64, b: u64) -> u64 {
    if a == 0 || b == 0 {
        return 0;
    }
    a / gcd(a, b) * b
}

/// Determines whether a number is prime.
///
/// # Examples
///
/// ```
/// use my_math_lib::is_prime;
///
/// assert!(is_prime(7));
/// assert!(!is_prime(4));
/// ```
pub fn is_prime(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    let mut i: u64 = 2;
    while i * i <= n {
        if n % i == 0 {
            return false;
        }
        i += 1;
    }
    true
}
#
# fn main() {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_gcd() {
        assert_eq!(gcd(12, 8), 4);
        assert_eq!(gcd(7, 3), 1);
        assert_eq!(gcd(0, 5), 5);
    }

    #[test]
    fn test_lcm() {
        assert_eq!(lcm(4, 6), 12);
        assert_eq!(lcm(0, 5), 0);
    }

    #[test]
    fn test_is_prime() {
        assert!(!is_prime(0));
        assert!(!is_prime(1));
        assert!(is_prime(2));
        assert!(is_prime(17));
        assert!(!is_prime(15));
    }
}
```

The publishing command sequence:

```bash
cargo test       # Confirm the tests pass
cargo doc --open # Check the docs
cargo package    # Simulate packaging
cargo publish    # Publish for real!
```

## Recap

- Log into crates.io with GitHub, generate an API token, then configure with `cargo login`.
- Before publishing, `Cargo.toml` should have `license`, `description`, `homepage`, `repository`, `readme`.
- `cargo package` checks for problems before publishing.
- `cargo publish` publishes to crates.io for real.
- Bump the `version` field for updates, following SemVer (semantic versioning).
- Your public API (especially the `pub` things) is a **promise to your users**; SemVer's three numbers exist to tell users "did this update touch that promise" — removing a `pub` is a breaking change (major), pure additions are backward compatible (minor). Documented behavior can also be part of the promise; private implementation details may change as long as the promises still hold.
- Published versions can't be deleted; `cargo yank` merely marks them as discouraged.
- Writing the README, doc comments, and tests before publishing is basic respect for your users.

Congratulations on finishing Chapter 7! 🎉 By this point, we've covered Rust's major concepts — ownership, borrowing, generics, `trait`s, lifetimes, closures, iterators, plus the module system and how to build and publish Cargo projects. You can now stand on your own. If there's an idea in your head, now is a great time to build it!

Even so, Rust has many more distinctive and powerful features. The chapters ahead continue with important topics not yet covered, aiming to give you a more complete, well-rounded understanding of Rust.
