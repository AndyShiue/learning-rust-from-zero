# `dyn Trait` Basics

## Goal of This Episode

Learn to use `dyn Trait` to store values of different types in the same place, and understand how dynamic dispatch works.

## Concept

### The Problem: Different Types in the Same Place

In Chapter 5 we learned `impl Trait`, which lets you write `fn print_it(x: &impl Display)` so a function accepts any type that implements `Display`. But what if you want to put values of different types into the same `Vec`?

```rust,noplayground
trait Describe {
    fn describe(&self) -> String;
}

struct Cat;
struct Dog;

impl Describe for Cat {
    fn describe(&self) -> String {
        String::from("a cat")
    }
}

impl Describe for Dog {
    fn describe(&self) -> String {
        String::from("a dog")
    }
}
#
# fn main() {}
```

`Cat` and `Dog` are different types — you can't write `Vec<impl Describe>` to put them together. `impl Trait` decides on a concrete type at compile time, and every element in a `Vec` must be the same type.

### Enter `dyn Trait`

`dyn Describe` means "some type that implements `Describe`, but I don't know which one specifically."

But since we don't know what it actually is, the size of `dyn Describe` isn't fixed — `Cat` might take 1 byte while `Dog` takes 100 bytes, and the compiler can't know at compile time which one it'll be. So `dyn Describe` is a DST (which we learned about in the last episode of Appendix I) and must live behind a pointer:

- `&dyn Describe` — borrowed.
- `Box<dyn Describe>` — owned

```rust,editable
trait Describe {
    fn describe(&self) -> String;
}

struct Cat;
struct Dog;

impl Describe for Cat {
    fn describe(&self) -> String {
        String::from("a cat")
    }
}

impl Describe for Dog {
    fn describe(&self) -> String {
        String::from("a dog")
    }
}

fn main() {
    let animals: Vec<Box<dyn Describe>> = vec![
        Box::new(Cat),
        Box::new(Dog),
    ];

    for animal in &animals {
        println!("{}", animal.describe());
    }
}
```

By the same logic, function return types can use `dyn Trait` too:

```rust,noplayground
# trait Describe {
#     fn describe(&self) -> String;
# }
#
# struct Cat;
# struct Dog;
#
# impl Describe for Cat {
#     fn describe(&self) -> String {
#         String::from("a cat")
#     }
# }
#
# impl Describe for Dog {
#     fn describe(&self) -> String {
#         String::from("a dog")
#     }
# }
#
fn make_animal(is_cat: bool) -> Box<dyn Describe> {
    if is_cat {
        Box::new(Cat)
    } else {
        Box::new(Dog)
    }
}
#
# fn main() {}
```

`impl Trait` can't do this — the two branches of the `if` return different types, and the compiler can't decide at compile time which one it would be.

### Fat Pointers: Address + vtable

In the last episode of Appendix I we learned that `&[T]` is a fat pointer (address + length). `&dyn Trait` is also a fat pointer, but it stores something different:

```ignore
&[T]         = [data address][length]
&dyn Trait   = [data address][vtable pointer]
```

The vtable (virtual method table) is a table holding function pointers to all of this concrete type's methods for this `trait`. `Cat`'s vtable has a pointer to `Cat::describe`; `Dog`'s vtable has a pointer to `Dog::describe`.

When you call `animal.describe()`, Rust looks up "which function is `describe`" in the vtable, then calls it.

```rust,editable
use std::mem::size_of;

trait Describe {
    fn describe(&self) -> String;
}

fn main() {
    println!("{}", size_of::<&i32>());          // 8
    println!("{}", size_of::<&dyn Describe>()); // 16 (address + vtable pointer)
    println!("{}", size_of::<&[i32]>());        // 16 (address + length)
}
```

### Dynamic Dispatch vs Static Dispatch

**Static dispatch** (`impl Trait` / generics): the compiler knows the concrete type and generates a separate copy of the function's code for each type. This is called **monomorphization**. Method calls jump straight to the right function — fast, but if there are many types, the code gets bigger.

```rust,editable
use std::fmt::Display;

fn print_it(x: &impl Display) {
    println!("{}", x);
}

fn main() {
    print_it(&42);      // the compiler generates print_it::<i32>
    print_it(&"hello"); // the compiler generates print_it::<&str>
}
```

**Dynamic dispatch** (`dyn Trait`): the compiler generates only one copy of the code, and at runtime the function to call is looked up through the vtable. There's only one copy of the code, but every call pays an extra vtable lookup.

| | Static dispatch (impl Trait / generics) | Dynamic dispatch (dyn Trait) |
|--|--|--|
| Decided at | Compile time | Runtime |
| Amount of code | One copy per type | Just one copy |
| Call speed | Fast (direct call) | Slightly slower (vtable lookup) |
| Can mix different types | No | Yes |

Most of the time, static dispatch is all you need. Reach for `dyn Trait` only when you need to put different types in the same place.

### `Box<dyn Fn()>` vs `impl Fn()`

Chapter 6 covered closures. `Box<dyn Fn()>` lets you unify different closures into a single type:

```rust,editable
fn main() {
    let callbacks: Vec<Box<dyn Fn()>> = vec![
        Box::new(|| println!("hello")),
        Box::new(|| println!("world")),
    ];

    for cb in &callbacks {
        cb();
    }
}
```

`Vec<impl Fn()>` can't do this, because every closure is its own distinct anonymous type.

### Lifetime Bounds on `dyn Trait`

`dyn Trait` can take a lifetime bound, written `dyn Trait + 'a` and read as `dyn (Trait + 'a)` — it means the same thing as `T: Trait + 'a` in generics; `dyn` turns that bound into a type.

In certain positions, if you don't write a lifetime bound, the compiler fills in a default. The default for `Box<dyn Trait>` is `'static`, so the full spelling is `Box<dyn Trait + 'static>`. The `+ 'static` means the concrete type inside can't contain any non-`'static` references. Take a look at this example:

```rust,compile_fail
# trait Describe {
#     fn describe(&self) -> String;
# }
#
struct Foo<'a>(&'a str);

impl<'a> Describe for Foo<'a> {
    fn describe(&self) -> String { String::from(self.0) }
}

// This function doesn't compile!
// Box<dyn Describe> = Box<dyn Describe + 'static>
// but Foo borrows s, and s isn't 'static
fn make_box(s: &str) -> Box<dyn Describe> {
    Box::new(Foo(s))
}
#
# fn main() {}
```

If you need to store a type that holds references, write the lifetime explicitly to override the default `'static`:

```rust,noplayground
# trait Describe {
#     fn describe(&self) -> String;
# }
# struct Foo<'a>(&'a str);
# impl<'a> Describe for Foo<'a> {
#     fn describe(&self) -> String { String::from(self.0) }
# }
#
fn make_box<'a>(s: &'a str) -> Box<dyn Describe + 'a> {
    Box::new(Foo(s))
}
```

`&'a dyn Trait` defaults to `&'a (dyn Trait + 'a)` — that one rarely needs special handling.

### `trait` Upcasting

If `trait B` is a subtrait of `trait A` (`trait B: A`), then `dyn B` can be converted to `dyn A`:

```rust,noplayground
trait Animal {
    fn name(&self) -> &str;
}

trait Pet: Animal {
    fn owner(&self) -> &str;
}

fn print_animal_name(a: &dyn Animal) {
    println!("{}", a.name());
}

fn example(pet: &dyn Pet) {
    print_animal_name(pet); // dyn Pet → dyn Animal, OK
}
#
# fn main() {}
```

A `Pet` is always an `Animal`, so of course a `dyn Pet` can be used as a `dyn Animal`.

## Example Code

```rust,editable
trait Describe {
    fn describe(&self) -> String;
}

struct Cat { name: String }
struct Dog { name: String }

impl Describe for Cat {
    fn describe(&self) -> String {
        format!("the cat {}", self.name)
    }
}

impl Describe for Dog {
    fn describe(&self) -> String {
        format!("the dog {}", self.name)
    }
}

fn make_animal(is_cat: bool, name: &str) -> Box<dyn Describe> {
    if is_cat {
        Box::new(Cat { name: String::from(name) })
    } else {
        Box::new(Dog { name: String::from(name) })
    }
}

fn main() {
    let animals: Vec<Box<dyn Describe>> = vec![
        Box::new(Cat { name: String::from("Mimi") }),
        Box::new(Dog { name: String::from("Blackie") }),
        make_animal(true, "Kitty"),
        make_animal(false, "Rex"),
    ];

    for animal in &animals {
        println!("{}", animal.describe());
    }

    println!(
        "size of &dyn Describe: {} bytes",
        std::mem::size_of::<&dyn Describe>()
    );
}
```

## Recap

- `dyn Trait` means "some type that implements `Trait`; which one specifically is unknown."
- `dyn Trait` is a DST and must live behind a pointer: `&dyn Trait`, `Box<dyn Trait>`.
- `&dyn Trait` is a fat pointer: data address + vtable pointer.
- Dynamic dispatch (`dyn Trait`) looks up methods through the vtable; static dispatch (`impl Trait`) is decided at compile time.
- Most of the time use static dispatch; use `dyn Trait` only when mixing different types.
- `Box<dyn Fn()>` can unify different closures into one type.
- `Box<dyn Trait>` implicitly defaults to `+ 'static` in some positions; `dyn Trait + 'a` reads as `dyn (Trait + 'a)` — `dyn` turns a `trait` bound into a type.
- `dyn SubTrait` can be converted to `dyn SuperTrait` (trait upcasting).
