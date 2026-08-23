# `use` Bounds

## Goal of This Episode

Understand which generic parameters the hidden type behind a return-position `impl Trait` captures, learn to restrict the capture set explicitly with `use<...>`, and get to know RPITIT in `trait` methods.

> This episode supplements **Chapter 5's `impl Trait` and lifetimes**.

## Concept

Chapter 5 showed `impl Trait` used in return position:

```rust,noplayground
fn numbers() -> impl Iterator<Item = i32> {
    [1, 2, 3].into_iter()
}
#
# fn main() {}
```

The `impl Iterator<Item = i32>` the caller sees is an **opaque type**: the interface deliberately doesn't reveal its concrete identity. The concrete type the function body picks for it is called the **hidden type**; in this example that's `std::array::IntoIter<i32, 3>`. A hidden type isn't necessarily nameless — it's simply concealed by the opaque return type.

If the function has generic parameters, may the hidden type use them? That's the question "capturing" answers.

### The Hidden Type Really Does Borrow the Parameter

```rust,editable
fn words<'a>(text: &'a str) -> impl Iterator<Item = &'a str> {
    text.split_whitespace()
}

fn main() {
    let text = String::from("Rust lifetime capture");

    for word in words(&text) {
        println!("{word}");
    }
}
```

What's actually returned is a `SplitWhitespace<'a>`, holding a reference to `text` inside. So the hidden type must be able to use — that is, **capture** — `'a`.

In Rust's 2024 edition, a return-position `impl Trait` captures every lifetime, type, and `const` generic parameter available in scope by default.

### Capturing More Than Actually Needed

But "permitted to capture" shows up in the caller's borrow checking. Even if the current hidden type never uses a parameter, a public signature that lets it capture one forces the caller to treat the return value as though it might have:

```rust,compile_fail
fn greeting<'a>(_name: &'a str) -> impl Fn() {
    || println!("Hello!")
}

fn main() {
    let name = String::from("Ming");
    let greet = greeting(&name);

    drop(name);
    greet();
}
```

The closure doesn't use `name` at all, yet under the 2024 edition's default rule the `impl Fn()` is permitted to capture `'a`. So a caller looking only at the signature conservatively assumes `greet` may still borrow `name`, and won't let us `drop(name)` first.

### `use<...>` Specifies the Capture Set

A `use<...>` bound lists exactly which generic parameters the hidden type may capture:

```rust,editable
fn greeting<'a>(_name: &'a str) -> impl Fn() + use<> {
    || println!("Hello!")
}

fn main() {
    let name = String::from("Ming");
    let greet = greeting(&name);

    drop(name);
    greet();
}
```

`use<>` is empty, meaning the hidden type may capture no generic parameter at all. The signature now guarantees explicitly that `greet` has nothing to do with `'a`, so the caller can release `name` first.

The `use` here is nothing like the `use std::...` that imports names. It appears in an `impl Trait`'s bound list, and its job is to list the capture set.

### List What You Need to Capture

If the hidden type really does use `'a` but the signature says `use<>`, the function itself won't compile:

```rust,compile_fail
fn text_length<'a>(text: &'a str) -> impl Fn() -> usize + use<> {
    move || text.len()
}
#
# fn main() {}
```

The closure holds `text`, so the hidden type uses `'a`. Just add `'a` to the capture set:

```rust,editable
fn text_length<'a>(text: &'a str) -> impl Fn() -> usize + use<'a> {
    move || text.len()
}

fn main() {
    let text = String::from("the captured data");
    let get_length = text_length(&text);
    println!("{}", get_length());
}
```

`use<'a>` says the hidden type may use `'a`. This time `get_length` really does borrow `text`, so `text` can't be released while it's alive.

### Type and `const` Generics Can Be Captured Too

`use<...>` isn't just for lifetimes; type parameters and `const` parameters go in it as well:

```rust,editable
fn repeat<T, const N: usize>(value: T) -> impl Iterator<Item = T> + use<T, N>
where
    T: Clone,
{
    std::iter::repeat_n(value, N)
}

fn main() {
    let values: Vec<_> = repeat::<_, 3>(String::from("Rust")).collect();
    println!("{values:?}");
}
```

For now an `impl Trait` may have at most one `use<...>`, and every type and `const` generic parameter in scope must be listed. Furthermore, if another part of the return type already uses some lifetime, that must go into `use<...>` too. In `impl Iterator<Item = &'a str> + use<'a>`, for instance, `Item = &'a str` already uses `'a`, so it can't be rewritten as `use<>`. Lifetimes in the list come before type and `const` generic parameters. If the list is incomplete or misordered, the compiler will say so outright.

### `trait` Methods Can Return `impl Trait` Too: RPITIT

Methods in `trait` definitions and `trait` implementations can use `impl Trait` in return position as well. This is called return-position `impl Trait` in `trait`, abbreviated **RPITIT**:

```rust,editable
trait Words {
    fn words<'a>(
        &'a self,
    ) -> impl Iterator<Item = &'a str> + use<'a, Self>;
}

struct Sentence(String);

impl Words for Sentence {
    fn words<'a>(
        &'a self,
    ) -> impl Iterator<Item = &'a str> + use<'a> {
        self.0.split_whitespace()
    }
}

fn main() {
    let sentence = Sentence(String::from("return position impl trait"));
    let words: Vec<_> = sentence.words().collect();

    println!("{words:?}");
}
```

The `impl Iterator` returned by `Words::words` is an opaque type; the compiler treats an RPITIT in a `trait` definition as an anonymous associated type. Each `trait` implementation gets to pick its own hidden concrete type for it; the `Sentence` above picks `SplitWhitespace<'a>`, while the caller relies only on the promise `Iterator<Item = &'a str>`.

The `use<'a, Self>` in the `trait` definition captures the `'a` with which the method borrows `self`, plus the `trait`'s implicit type parameter `Self`. As things stand, writing `use<...>` on the RPITIT of a `trait`'s associated function requires listing all of that `trait`'s generic parameters, `Self` included. By the time we reach `impl Words for Sentence`, `Self` is definitively the concrete `Sentence`, so the implementation side only needs `use<'a>`.

Even when the return value doesn't use `self` at all, `use<...>` in a `trait` definition can't omit `Self`:

```rust,compile_fail
trait FixedNumbers {
    // Compile error: the trait's `Self` isn't listed in `use<...>`.
    fn numbers(&self) -> impl Iterator<Item = i32> + use<>;
}
#
# fn main() {}
```

An RPITIT's callers can only use the bounds the `trait` signature has promised. Even if the iterator some implementation actually returns also implements `DoubleEndedIterator`, a generic caller still can't call `.rev()` on it directly; if that capability is needed, the `trait` should use a `DoubleEndedIterator` bound from the start, or switch to a named associated type.

A method returning an opaque type can't be dynamically dispatched through `dyn Trait`, so a `trait` containing such a method usually isn't `dyn` compatible. Adding `where Self: Sized` to the method keeps the `trait`'s other methods usable through `dyn Trait`, though this RPITIT method itself still won't be. `async fn` in `trait`s is built on the same mechanism and can be understood conceptually as returning `impl Future<Output = T>`.

### When Is It Worth Writing?

For an ordinary function that really does return an iterator, closure, or `Future` borrowing its parameters, the default capture is usually exactly right — there's no need to write `use<...>` every time.

When a function **takes a parameter carrying a lifetime but the return value is actually unrelated to it**, the default capture may leave callers thinking the return value still holds a reference, delaying release of the original value. Here `use<>` states the API's promise more precisely and lets callers use or release the original value sooner.

## Example Code

```rust,editable
fn borrowed_words<'a>(
    text: &'a str,
) -> impl Iterator<Item = &'a str> + use<'a> {
    text.split_whitespace()
}

fn fixed_numbers<'a>(
    _label: &'a str,
) -> impl Iterator<Item = i32> + use<> {
    [1, 2, 3].into_iter()
}

fn main() {
    let text = String::from("one two three");
    let words: Vec<_> = borrowed_words(&text).collect();
    println!("Borrowed text: {words:?}");

    let label = String::from("never used by the iterator");
    let numbers = fixed_numbers(&label);

    // use<> guarantees numbers didn't capture label's lifetime.
    drop(label);
    println!("Fixed numbers: {:?}", numbers.collect::<Vec<_>>());
}
```

## Recap

- A return-position `impl Trait` is an opaque type at the interface, backed by a hidden concrete type the function body decides on.
- Capturing a generic parameter means the hidden type is permitted to use it.
- Rust's 2024 edition captures every lifetime, type, and `const` generic parameter in scope by default.
- `impl Trait + use<'a, T, N>` lists exactly which parameters may be captured; `use<>` captures none.
- If the hidden type really uses a parameter that wasn't listed, the function itself fails to compile.
- A return-position `impl Trait` in a `trait` method is called an RPITIT; using `use<...>` there requires listing `Self` and all of that `trait`'s generic parameters.
- Precisely ruling out unnecessary lifetime capture keeps callers' reference lifetimes from being conservatively extended.
