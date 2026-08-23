# GAT

## Goal of This Episode

Understand generic associated types (GATs), and learn to express "the return type changes with each borrow" using an associated type that takes a lifetime parameter.

> This episode supplements **Chapter 5's associated types** and this appendix's HRTB episode.

## Concept

Chapter 5 introduced associated types, and `Iterator` is built the same way:

```rust,ignore
trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;
}
```

Each implementor picks one `Item`. If some iterator's `Item` is `i32`, for instance, every subsequent call to `next` returns the same type, `Option<i32>`.

But what if `next` wants to return a value **borrowed from the iterator itself**? Each `&mut self` borrow may have a different lifetime, so `Item` has to change along with that borrow. An ordinary associated type has nowhere to put this lifetime parameter.

### Associated Types Can Take Generic Parameters Too

GATs let an associated type carry generic parameters of its own:

```rust,noplayground
trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}
#
# fn main() {}
```

GAT is short for **generic associated type**. `Item` here no longer stands for a single type but for a whole family of types:

```rust,ignore
Self::Item<'a_short_borrow>
Self::Item<'a_long_borrow>
```

On each call to `next`, the `'a` in `&'a mut self` decides which `Item<'a>` this particular call uses.

### What Is `where Self: 'a`?

`Item<'a>` may borrow data inside `Self`. For that borrow to be valid throughout `'a`, `Self` itself must of course outlive `'a`:

```rust,ignore
type Item<'a>
where
    Self: 'a;
```

This is exactly Chapter 5's lifetime bound. It doesn't say `Self` must always be `'static`; it says that whenever an `'a` is chosen, every lifetime contained in the `Self` used on that occasion must live at least until `'a` ends.

### An Iterator That Lends Out Its Own Data

The `Lines` below owns a batch of `String`s and returns one `&str` from them on each `next`:

```rust,editable
trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}

struct Lines {
    data: Vec<String>,
    position: usize,
}

impl LendingIterator for Lines {
    type Item<'a> = &'a str
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
        let position = self.position;
        self.position += 1;
        self.data.get(position).map(String::as_str)
    }
}

fn main() {
    let mut lines = Lines {
        data: vec![
            String::from("first line"),
            String::from("second line"),
        ],
        position: 0,
    };

    while let Some(line) = lines.next() {
        println!("{line}");
    }
}
```

In this implementation `Item<'a>` is `&'a str`. The returned string slice borrows `lines.data`, and the duration of that borrow is tied precisely to this particular `&'a mut self`.

### Why Can't an Ordinary `Iterator` Express This?

Forcing this into an ordinary `Iterator`, you'd want to write:

```rust,compile_fail
struct Lines {
    data: Vec<String>,
    position: usize,
}

impl Iterator for Lines {
    type Item = &str;

    fn next(&mut self) -> Option<Self::Item> {
        let position = self.position;
        self.position += 1;
        self.data.get(position).map(String::as_str)
    }
}
#
# fn main() {}
```

`type Item = &str` has no source for its lifetime. `Iterator::Item` is a fixed type chosen once at implementation time; it can't express "this `&str`'s lifetime comes from the `&mut self` of each call."

A standard `Iterator` can of course return references to data **outside** the iterator — `slice.iter()`'s `Item`, for instance, is an `&'data T` already determined when the iterator is created. GATs solve a different problem: an output that borrows directly from the `self` of each call.

### Each Lent Value Has to Be Done With First

Because `next`'s output borrows `&mut self`, the iterator can't be mutably borrowed again while that output is still in use:

```rust,compile_fail
# trait LendingIterator {
#     type Item<'a> where Self: 'a;
#     fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
# }
#
# struct Lines { data: Vec<String>, position: usize }
#
# impl LendingIterator for Lines {
#     type Item<'a> = &'a str where Self: 'a;
#     fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
#         let p = self.position;
#         self.position += 1;
#         self.data.get(p).map(String::as_str)
#     }
# }
#
# fn main() {
    let mut lines = Lines {
        data: vec![String::from("one"), String::from("two")],
        position: 0,
    };

    let first = lines.next().expect("there should be a first line");
    let second = lines.next().expect("there should be a second line");
    println!("{first}, {second}");
# }
```

`first` is used all the way through the final `println!`, so its borrow of `lines` hasn't ended yet and the second `next()` can't borrow `lines` again. This isn't a flaw in GATs — it's them faithfully expressing a lending API's borrow relationships.

### GATs Aren't Limited to Lifetimes

The "generic" in the name is meant seriously: an associated type can carry type or `const` parameters as well, such as `type Buffer<T>` or `type Array<const N: usize>`. Lifetime parameters, though, best showcase what ordinary associated types can't do, and they're the form you'll most often need to read in library APIs.

## Example Code

```rust,editable
trait View {
    type Output<'a>
    where
        Self: 'a;

    fn view<'a>(&'a self) -> Self::Output<'a>;
}

struct Document {
    title: String,
    body: String,
}

impl View for Document {
    type Output<'a> = (&'a str, &'a str)
    where
        Self: 'a;

    fn view<'a>(&'a self) -> Self::Output<'a> {
        (&self.title, &self.body)
    }
}

fn print_view<T: View>(value: &T)
where
    for<'a> T::Output<'a>: std::fmt::Debug,
{
    println!("{:?}", value.view());
}

fn main() {
    let document = Document {
        title: String::from("GAT"),
        body: String::from("associated types can take generic parameters too"),
    };

    print_view(&document);
}
```

## Recap

- A GAT is an associated type that takes generic parameters.
- `type Item<'a>` stands for a whole family of types varying with `'a`, not a single fixed type.
- `where Self: 'a` guarantees that when the output borrows `Self`, `Self` is still valid throughout `'a`.
- A lending iterator lets each output borrow that call's `&mut self`; an ordinary `Iterator::Item` can't express this relationship.
- While a lent output is still in use, the borrow of `self` is still live as well.
- GATs often turn up alongside HRTBs in advanced `trait` bounds.
