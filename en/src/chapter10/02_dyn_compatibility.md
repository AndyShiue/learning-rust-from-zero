# `dyn` compatibility

## Goal of This Episode

Understand which `trait`s can be used with `dyn` and which can't, and the reasons behind it.

## Concept

### Not Every `trait` Works with `dyn`

Last episode we learned `dyn Trait`. But if you try to write `dyn Clone`, you get a compile error. That's because `Clone` is not **`dyn` compatible**.

### The Core Idea: `impl Trait for dyn Trait`

To understand dyn compatibility, first think about how `dyn Trait` works. The compiler automatically generates an:

```rust,ignore
impl Trait for dyn Trait {
    fn method(&self, ...) {
        // look up the vtable, call the actual implementation
    }
}
```

In this auto-generated `impl`, `Self` = `dyn Trait`. And `dyn Trait` is a DST — its size isn't fixed; it's not `Sized`.

If some of a `trait`'s methods can't work when `Self = dyn Trait`, that `trait` isn't `dyn` compatible. Concretely, there are a few situations:

### Restriction 1: `Self` Can't Appear in Types Other Than `self`

```rust,ignore
trait Compare {
    fn compare(&self, other: &Self) -> bool;
}

impl Compare for Cat {
    fn compare(&self, other: &Cat) -> bool { ... }
}

impl Compare for Dog {
    fn compare(&self, other: &Dog) -> bool { ... }
}
```

`compare`'s second parameter is `&Self`. When you use `dyn Compare`, the concrete type has been erased — you don't know whether it's a `Cat` or a `Dog` inside. But `Cat::compare` expects a `&Cat`, and `Dog::compare` expects a `&Dog`.

If someone passes in a `Dog`, but the function found through the vtable is `Cat::compare`, the function would treat the `Dog`'s data as a `Cat` — the types get mixed up.

To guarantee no mix-up, the compiler would need a runtime check that "the concrete type of the `y` being passed in matches the concrete type of `x`." But the whole point of `dyn` is that the concrete type has been erased — the compiler no longer knows what it originally was, so it can't do that check. So Rust simply forbids it.

### Restriction 2: Methods Can't Have Generic Parameters

```rust,noplayground
trait Converter {
    fn convert<U>(&self) -> U;
}
#
# fn main() {}
```

A vtable is a fixed-size table of function pointers. But a generic method is a different function for each different `U` — `convert::<i32>` and `convert::<String>` are two different function pointers. A vtable can't hold infinitely many versions.

The main issue is that the vtable has to be built by whoever compiles the `impl` — because only that side knows the concrete type of `Self`. But when the `impl` is compiled, you don't know which `U`s users will pick later, so the vtable can't possibly prepare every version in advance.

### Restriction 3: The `trait` Itself Can't Require `Self: Sized`

Back to the opening question — why doesn't `dyn Clone` work? Besides returning `Self`, `Clone` actually has `Sized` as a supertrait:

```rust,noplayground
trait Clone: Sized {
    fn clone(&self) -> Self;
}
#
# fn main() {}
```

`Clone: Sized` means "any type implementing Clone must be Sized." But `dyn Clone` is a DST — not `Sized`. So `impl Clone for dyn Clone` can't even exist, and therefore neither can `dyn Clone`.

### The Escape Hatch: `where Self: Sized`

If only some of a `trait`'s methods are `dyn` compatible and others aren't, you can add `where Self: Sized` to all the others to opt them out:

```rust,noplayground
trait MyTrait {
    fn normal(&self) -> String; // callable on dyn MyTrait
    fn special(&self) -> Self   // returns Self, not dyn compatible
        where Self: Sized;      // add this to opt it out
}
#
# fn main() {}
```

`where Self: Sized` means "this method can only be called when `Self` is `Sized`." `dyn MyTrait` isn't `Sized`, so this method can't be called on `dyn MyTrait` — but the `trait` itself remains `dyn` compatible, and the other methods can still be used through `dyn MyTrait`.

```rust,ignore
let x: &dyn MyTrait = &something;
x.normal(); // OK
// x.special(); // compile error: dyn MyTrait is not Sized
```

The full rules of `dyn` compatibility are actually more intricate than this episode covers, but these get you most of the way there.

## Example Code

```rust,editable
// A dyn compatible trait
trait Greet {
    fn greet(&self) -> String;
}

struct Alice;
struct Bob;

impl Greet for Alice {
    fn greet(&self) -> String { String::from("Hi, I'm Alice!") }
}

impl Greet for Bob {
    fn greet(&self) -> String { String::from("Hey, I'm Bob!") }
}

// A trait that mixes in where Self: Sized
trait Animal {
    fn name(&self) -> &str;

    // This method isn't dyn compatible (returns Self); opt out with where Self: Sized
    fn duplicate(&self) -> Self
    where
        Self: Sized + Clone;
}

#[derive(Clone)]
struct Cat { name: String }

impl Animal for Cat {
    fn name(&self) -> &str { &self.name }
    fn duplicate(&self) -> Self
    where
        Self: Sized + Clone,
    {
        self.clone()
    }
}

fn main() {
    // dyn Greet: different types in the same Vec
    let greeters: Vec<Box<dyn Greet>> = vec![
        Box::new(Alice),
        Box::new(Bob),
    ];

    for g in &greeters {
        println!("{}", g.greet());
    }

    // dyn Animal: name() works, duplicate() doesn't
    let cat = Cat { name: String::from("Mimi") };
    let animal: &dyn Animal = &cat;
    println!("animal: {}", animal.name());  // OK
    // animal.duplicate(); // compile error: dyn Animal is not Sized

    // But duplicate can be called on the concrete type
    let cat2 = cat.duplicate();
    println!("copy: {}", cat2.name());
}
```

## Recap

- Not every `trait` can be used with `dyn` — it must be `dyn` compatible.
- The core idea: the compiler auto-generates `impl Trait for dyn Trait`, where `Self` = `dyn Trait` (a DST).
- `Self` can't appear in types other than `self` — the concrete type has been erased.
- Methods can't have generic parameters — the vtable is fixed-size and can't hold infinitely many versions.
- The trait can't require `Self: Sized` — `dyn Trait` is a DST, not `Sized`.
- Adding `where Self: Sized` to individual methods opts them out of `dyn`, keeping the `trait` itself `dyn` compatible.
