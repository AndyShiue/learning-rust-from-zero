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

The `Deref` trait from Episode 23 uses an associated type:

```rust,noplayground
trait Deref {
    type Target;
    fn deref(&self) -> &Self::Target;
}
#
# fn main() {}
```

`type Target` determines what type dereferencing yields. For instance, `Box<T>`'s implementation is `type Target = T` — dereferencing a `Box<i32>` yields an `i32`. Same reasoning as `Container`'s `type Item`: a `Box<i32>` dereferences to an `i32` and nothing else, hence an associated type rather than a generic parameter.

### Specifying Associated Types in `trait` Bounds

You can pin down an associated type's concrete type inside a `trait` bound:

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
- `Deref`'s `type Target` is an associated type too — `Box<T>` has `Target = T`, meaning dereferencing yields `T`.
- In a `trait` bound, `Container<Item = i32>` pins the associated type.
- A `trait` bound can also require the associated type to implement a `trait`: `Container<Item: Display>`.
