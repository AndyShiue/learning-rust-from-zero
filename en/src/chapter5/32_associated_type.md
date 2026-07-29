# Associated Types

## Goal of This Episode

Learn to define associated types in a `trait`, and understand how they differ from generic parameters.

## Concept

In Episode 18 we learned multi-parameter `trait`s: `trait Convert<T>`. But sometimes a type parameter isn't "open" — a given type will only ever have one sensible implementation.

### The Problem: Multi-parameter `trait`s Are Too Permissive

Picture a "container" `trait`. What element type does the container hold? With a multi-parameter `trait`:

```rust,noplayground
trait Container<T> {
    fn first(&self) -> Option<&T>;
}
#
# fn main() {}
```

But that means one type could implement both `Container<i32>` and `Container<String>` at the same time — while a container usually has just one element type.

### Associated Types: a One-to-one Relationship

Associated types solve this:

```rust,noplayground
trait Container {
    type Item;
    // To use Self's associated type, write Self::Type
    fn first(&self) -> Option<&Self::Item>;
}
#
# fn main() {}
```

`type Item;` declares an associated type. Implementations must specify what it is:

```rust,noplayground
# trait Container {
#     type Item;
#     fn first(&self) -> Option<&Self::Item>;
# }
#
# struct NumberList {
#     data: Vec<i32>,
# }
#
impl Container for NumberList {
    type Item = i32;
    fn first(&self) -> Option<&i32> {
        self.data.first()
    }
}
#
# fn main() {}
```

Once `Self` (`NumberList`) and the angle-bracket parameters (none here) are fixed, `Item` is uniquely determined as `i32` — no ambiguity.

### The Difference from Generic Parameters

You can picture a `trait` as a function that takes some "inputs" and determines some "outputs":

- **Inputs**: `Self` (who implements the `trait`) and the type parameters in angle brackets (`<T>`).
- **Outputs**: associated types (`type Item`).

Inputs determine outputs — once "who" (`Self`) and "the angle-bracket parameters" are fixed, the associated type is uniquely determined.

For example, the `T` in `Convert<T>` is an input, so the same `Self` with different `T`s can have different implementations: `i32` can implement both `Convert<String>` and `Convert<(i32,)>`.

But `Container`'s `Item` is an output. Once `Self` is fixed as `NumberList`, `Item` can have **only one answer** — `i32`.

Which to use? If "once all inputs are fixed, only one sensible answer remains," put it in an associated type (output). If "the same inputs can pair with several different answers," put it in the angle brackets (input).

### `Deref` Has an Associated Type Too

The `Deref` `trait` from Episode 23 uses an associated type:

```rust,noplayground
trait Deref {
    type Target;
    fn deref(&self) -> &Self::Target;
}
#
# fn main() {}
```

`type Target` is the type reached by dereferencing.

For example, if `p` is a `Box<i32>` and we write:

```rust,noplayground
# fn main() {
#     let p = Box::new(10);
    let n = *p;
# }
```

Rust treats the `*p` part roughly like this:

```rust,noplayground
# use std::ops::Deref;
#
# fn main() {
#     let p = Box::new(10);
    let n = *p.deref();
# }
```

`deref` takes `&self`, so `p.deref()` borrows the smart pointer first, then returns a reference to the inner value: `&Self::Target`. Finally, the outer `*` follows that reference.

For `Box<i32>`, `Self::Target` is `i32`, so `.deref()` returns `&i32`. Since `i32` is `Copy`, `let n = *p;` can create another `i32`.

This is the same reasoning as `Container`'s `type Item`: once `Self` is fixed as `Box<i32>`, `Target` has only one answer — `i32`. That is why `Target` is an associated type rather than a generic parameter.

### `DerefMut` Uses the Same `Target`

The mutable version is `DerefMut`. In simplified form, it looks like this:

```rust,noplayground
# trait Deref {
#     type Target;
#     fn deref(&self) -> &Self::Target;
# }
#
trait DerefMut: Deref {
    fn deref_mut(&mut self) -> &mut Self::Target;
}
#
# fn main() {}
```

`DerefMut` does not declare another associated type. It uses `Self::Target` from `Deref`.

That matters because immutable dereferencing and mutable dereferencing must reach the same kind of inner value. If `Box<String>` has `Target = String`, then `.deref()` returns `&String`, and `.deref_mut()` returns `&mut String`.

For example:

```rust,noplayground
# fn main() {
#     let mut p = Box::new(String::from("hello"));
    *p = String::from("world");
# }
```

Since the left side is `*p`, Rust needs mutable access to the inner value. It treats that part roughly like this:

```rust,noplayground
# use std::ops::DerefMut;
#
# fn main() {
#     let mut p = Box::new(String::from("hello"));
    *p.deref_mut() = String::from("world");
# }
```

`deref_mut` takes `&mut self`, so `p.deref_mut()` mutably borrows the smart pointer first, then returns a mutable reference to the inner value: `&mut Self::Target`. Finally, the outer `*` follows that mutable reference, so the assignment can replace the inner `String`.

### Specifying Associated Types in `trait` Bounds

You can specify an associated type's concrete type inside a `trait` bound:

```rust,ignore
fn print_first<C: Container<Item = i32>>(c: &C) { ... }
#
# fn main() {}
```

`Container<Item = i32>` means "implements `Container`, with `Item` being `i32`."

If you only want to require the associated type to implement some `trait`, you can write the `trait` bound right after it:

```rust,ignore
fn print_first<C: Container<Item: Display>>(c: &C) { ... }
#
# fn main() {}
```

`Item: Display` means "`Container`'s `Item` must implement `Display`."

## Example Code

```rust,editable
use std::fmt::Display;

// A container trait defined with an associated type
trait Container {
    type Item;

    fn first(&self) -> Option<&Self::Item>;
    fn last(&self) -> Option<&Self::Item>;
    fn len(&self) -> usize;
}

struct NumberList {
    data: Vec<i32>,
}

impl Container for NumberList {
    type Item = i32; // Specifying the associated type

    fn first(&self) -> Option<&i32> {
        self.data.first()
    }

    fn last(&self) -> Option<&i32> {
        self.data.last()
    }

    fn len(&self) -> usize {
        self.data.len()
    }
}

struct WordList {
    words: Vec<String>,
}

impl Container for WordList {
    type Item = String; // A different type, a different Item

    fn first(&self) -> Option<&String> {
        self.words.first()
    }

    fn last(&self) -> Option<&String> {
        self.words.last()
    }

    fn len(&self) -> usize {
        self.words.len()
    }
}

// Using the associated type in a trait bound
fn print_first_item<C>(c: &C)
where
    C: Container,
    C::Item: Display,
{
    match c.first() {
        Some(item) => println!("The first element: {}", item),
        None => println!("The container is empty"),
    }
}

fn main() {
    let nums = NumberList { data: vec![10, 20, 30] };
    let words = WordList {
        words: vec![
            String::from("hello"),
            String::from("world"),
        ],
    };

    println!("Number container length: {}", nums.len());
    print_first_item(&nums);

    println!("Word container length: {}", words.len());
    print_first_item(&words);

    // last
    match nums.last() {
        Some(n) => println!("The last number: {}", n),
        None => println!("Empty"),
    }
}
```

## Recap

- `type Item;` defines an associated type in a `trait`.
- The `Self::Item` syntax reads `Self`'s associated type within the `trait` definition.
- Implementations specify the concrete type with `type Item = i32;`.
- **Input vs output**: `Self` and the angle-bracket parameters are inputs; associated types are outputs. Inputs determine outputs.
- `Deref`'s `type Target` is an associated type too — `Box<T>` has `Target = T`, meaning dereferencing reaches `T`.
- `DerefMut` uses the same `Self::Target` and returns `&mut Self::Target`.
- In a `trait` bound, `Container<Item = i32>` specifies the associated type.
- A `trait` bound can also require the associated type to implement a `trait`: `Container<Item: Display>`.
