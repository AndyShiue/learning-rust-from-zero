# `Drop`

## Goal of This Episode

Learn to define cleanup behavior for when a value leaves scope with the `Drop` `trait`, plus how to release resources early by hand.

## Concept

So far we know that a value can't be used once it leaves its scope. But Rust actually does one more thing behind the scenes — when a value leaves scope, Rust automatically **drops** it, releasing the resources it held (memory included). Most of the time you needn't care, but sometimes you want something extra to happen at the moment a value is dropped: printing a message, closing a file, cleaning up temp data, and so on.

### The `Drop` `trait`

The `Drop` `trait` lets you customize "what to do when dropped":

```rust,noplayground
# struct MyType { name: String }
#
impl Drop for MyType {
    fn drop(&mut self) {
        println!("MyType was dropped!");
    }
}
#
# fn main() {}
```

Rust **calls `drop` automatically** when the value leaves scope. You can't call `x.drop()` yourself — Rust forbids it, because a value being `drop`ped and then automatically `drop`ped again would cause trouble.

### Releasing Early by Hand

To release a value early, use `drop(value)`:

```rust,editable
struct MyType { name: String }

impl Drop for MyType {
    fn drop(&mut self) {
        println!("MyType was dropped!");
    }
}

fn main() {
    let x = MyType { name: String::from("Ming") };
    drop(x); // Dropped early
    // x can't be used anymore
}
```

`drop` is a function (not a method) — it takes ownership of the value, letting it leave scope and triggering `Drop`.

### Contained Values Are Dropped Automatically

When a value is `drop`ped, Rust also automatically cleans up the values inside it that need to be `drop`ped, so you usually don't need to clean them up one by one inside your `drop` implementation. This mechanism isn't limited to `struct`s: values inside `tuple`s, fields carried by the current variant of an `enum`, elements of arrays, and elements inside a `Vec` are also cleaned up automatically when needed.

```rust,editable
struct Item(&'static str);

impl Drop for Item {
    fn drop(&mut self) {
        println!("Dropping item: {}", self.0);
    }
}

enum Package {
    Single(Item),
    Bundle(Vec<Item>),
}

impl Drop for Package {
    fn drop(&mut self) {
        println!("Dropping package");
    }
}

fn main() {
    let package = Package::Bundle(vec![
        Item("book"),
        Item("pen"),
    ]);

    drop(package);
}
```

Here we only call `drop(package)`, but the `Vec<Item>` and every `Item` inside it are `drop`ped automatically as well.

### Types with `Drop` Can't Be Partially Moved

An important restriction. If a `struct` implements `Drop`, you can't move values out of its fields:

```rust,compile_fail
# #![allow(unused_variables)]
#
struct Resource {
    name: String,
    id: i32,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("Releasing {}", self.name);
    }
}

fn main() {
    let r = Resource { name: String::from("A"), id: 1 };
    let n = r.name; // Compile error! No partial moves
}
```

Why? Because `drop` needs the complete `self`. If you moved `name` away, `self.name` wouldn't exist when `drop` runs — unsafe. So Rust forbids partial moves on types with `Drop`.

## Example Code

```rust,editable
struct Resource {
    name: String,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("Releasing resource: {}", self.name);
    }
}

fn main() {
    let a = Resource { name: String::from("database connection") };
    let b = Resource { name: String::from("file handler") };

    println!("Two resources created");

    // Manually release a early
    drop(a);
    println!("a has been released early");

    // a can't be used anymore
    // println!("{}", a.name); // Compile error!

    println!("Next, b will be released automatically when main ends");

    // Scope demonstration
    {
        let c = Resource { name: String::from("a temporary resource") };
        println!("c lives in this scope");
    } // c gets dropped automatically here

    println!("c has been released; b is still around");
} // b gets dropped automatically here
```

## Recap

- The `Drop` `trait` customizes cleanup when a value leaves scope.
- Rust **calls `.drop()` automatically** at scope exit; manual calls are forbidden.
- To release early, use `drop(value)`.
- When a value is `drop`ped, Rust usually also cleans up the values inside it that need to be `drop`ped.
- **Types with `Drop` can't be partially moved** — `drop` needs the complete `self`.
