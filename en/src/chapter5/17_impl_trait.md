# The `impl Trait` Syntax

## Goal of This Episode

Learn `impl Trait` as shorthand for `trait` bounds, and its different meanings in parameter versus return position.

## Concept

We've learned `trait` bounds: `fn foo<T: Display>(x: &T)`. Rust also offers a more concise form: `impl Trait`.

### `impl Trait` in Parameter Position

```rust,noplayground
# use std::fmt::Display;
#
fn show(x: &impl Display) {
    println!("{}", x);
}
#
# fn main() {}
```

This is almost fully equivalent to `fn show<T: Display>(x: &T)` — both say "`x`'s type must implement `Display`," and it's terser.

### Each `impl Trait` Is an Independent Type

Important idea: each `impl Trait` in the parameters stands for an **independent** type.

```rust,noplayground
# use std::fmt::Display;
#
fn show_two(a: &impl Display, b: &impl Display) {
    println!("{} {}", a, b);
}
#
# fn main() {}
```

`a` and `b` may be **different types** — as long as both implement `Display`. Say, `a` an `i32` and `b` a `String`.

If you require `a` and `b` to be **the same type**, use a named type parameter:

```rust,noplayground
# use std::fmt::Display;
#
fn show_same<T: Display>(a: &T, b: &T) {
    println!("{} {}", a, b);
}
#
# fn main() {}
```

### `impl Trait` in Return Position

`impl Trait` also works on return values:

```rust,noplayground
# use std::fmt::Display;
#
fn greeting() -> impl Display {
    String::from("Hello")
}
#
# fn main() {}
```

This says "I'll return some type implementing `Display`, without telling you which one." The caller knows only that the return value supports `Display`'s methods (like `println!("{}", greeting())`), not whether it's a `String` or something else.

## Example Code

```rust,editable
use std::fmt::Display;

// impl Trait in parameter position
fn show(x: &impl Display) {
    println!("Showing: {}", x);
}

// Each impl Trait is an independent type; a and b may differ
fn show_pair(a: &impl Display, b: &impl Display) {
    println!("{} and {}", a, b);
}

// Requiring the same type: use generics
fn show_same<T: Display>(a: &T, b: &T) {
    println!("{} and {}", a, b);
}

// impl Trait in return position
fn make_greeting(name: &str) -> impl Display {
    let mut s = String::from("Hello, ");
    s.push_str(name);
    s.push_str("!");
    s
}

fn main() {
    // Parameter position
    show(&42);
    show(&String::from("hello"));

    // The two parameters may have different types
    show_pair(&42, &"hello");

    // Requiring the same type
    show_same(&10, &20);
    // show_same(&10, &"hello"); // Compile error! i32 and &str differ

    // Returning impl Trait
    let greeting = make_greeting("world");
    println!("{}", greeting);

    // greeting's type is `impl Display`, not `String`
    // So you can't use it as a String:
    // greeting.push_str("!!!"); // Compile error! impl Display has no push_str method
    // We know it is a String, but the compiler sees only Display
}
```

## Recap

- `fn foo(x: &impl Display)` is shorthand for `fn foo<T: Display>(x: &T)`.
- Each `impl Trait` parameter is its own type — two `impl Display`s may differ.
- To force the same type, use a named type parameter `<T: Display>`.
- `-> impl Trait` in return position hides the concrete type; callers know only which `trait` it implements.
