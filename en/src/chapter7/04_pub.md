# `pub` Visibility

## Goal of This Episode

Fully understand Rust's visibility rules, and master `pub`'s various usages.

## Main Text

Episode 2 mentioned that a `mod`'s contents are private by default. This episode lays out the visibility rules completely.

### Private by Default

Rust's philosophy is **closed by default** — everything starts private, and you must open it explicitly with `pub`. The exact opposite of languages that default to public.

```rust,compile_fail
mod secrets {
    fn hidden() {
        // The outside can't see me
    }

    pub fn visible() {
        // The outside may call me
        hidden(); // Calls within the same mod are fine
    }
}

fn main() {
    secrets::visible(); // OK
    secrets::hidden();  // Compile error! hidden is private
}
```

You might wonder: neither `fn main()` nor `mod secrets` has `pub`, so why can `main` see `secrets`? Because both are defined in the root `mod` — members of the same `mod` see each other, no `pub` required. `pub` exists to let **other `mod`s** see your things.

### `pub fn`

A function with `pub` is publicly exposed. Nothing more to say.

### `pub struct` — Fields Marked Individually

`pub` on a `struct` only makes the **type** public — the fields stay private! Each field needs its **own** `pub`:

```rust,compile_fail
mod user {
    pub struct Profile {
        pub name: String,  // Externally readable/writable
        pub email: String, // Externally readable/writable
        age: u32,          // Private! Invisible outside
    }

    impl Profile {
        pub fn new(name: String, email: String, age: u32) -> Profile {
            Profile { name, email, age }
        }

        pub fn age(&self) -> u32 {
            self.age // Read-only access exposed via a method
        }
    }
}

fn main() {
    let p = user::Profile::new(
        String::from("Yaju"),
        String::from("yaju@senpai.com"),
        24,
    );
    println!("Name: {}", p.name);  // OK, name is pub
    println!("Age: {}", p.age()); // OK, accessed via the method
    println!("{}", p.age);         // Compile error! The age field is private
}
```

This design matters — it lets you control which fields to expose and which to hide. If a `struct` has any private field, outsiders can't construct it directly with `StructName { ... }`; they must go through a constructor you provide.

Tuple `struct`s are the same — fields default to private, each needing its own `pub`:

```rust,compile_fail
# #![allow(unused_variables)]
#
mod geometry {
    pub struct Point(pub f64, pub f64); // Both fields public
    pub struct Id(u64);                 // The field is private!
}

fn main() {
    let p = geometry::Point(1.0, 2.0); // OK, the fields are pub
    println!("x = {}", p.0);

    let id = geometry::Id(42); // Compile error! Id's field is private
}
```

### `pub enum` — Variants Automatically Public

`enum`s differ from `struct`s: once the `enum` itself is `pub`, all variants are **automatically public**.

```rust,editable
mod status {
    pub enum Color {
        Red,
        Green,
        Blue,
    }
}

fn main() {
    let c = status::Color::Red; // Every variant is available
    match c {
        status::Color::Red => println!("Red"),
        status::Color::Green => println!("Green"),
        status::Color::Blue => println!("Blue"),
    }
}
```

Which makes sense — publishing an `enum` while hiding some variants would make correct `match`ing impossible; better not to publish at all.

### `pub trait` and `impl`

Once a `trait` has `pub`, the `fn`s inside **neither need nor may** take individual `pub`s — their visibility follows the `trait`. A public `trait` means public `fn`s; a private `trait`, private `fn`s. Sensible: a `trait` is a "contract," and publishing the contract means publishing all its clauses — how else would anyone implement it?

```rust,editable
mod animal {
    pub trait Speak {
        fn speak(&self); // No pub needed; follows the trait
    }

    pub struct Dog;

    impl Speak for Dog {
        fn speak(&self) {
            println!("Woof!");
        }
    }
}

fn main() {
    use animal::Speak; // The trait must be in scope to call its methods
    let d = animal::Dog;
    d.speak();
}
```

Note the line `use animal::Speak;` — even though `Dog` implements `Speak`, you still must bring the `Speak` `trait` into scope to call its methods. Remove that line and `d.speak()` fails to compile. That's Rust's rule: **a `trait`'s methods are callable only after the `trait` is `use`d in.**

```rust,compile_fail
mod animal {
    pub trait Speak {
        fn speak(&self); // No pub needed; follows the trait
    }

    pub struct Dog;

    impl Speak for Dog {
        fn speak(&self) {
            println!("Woof!");
        }
    }
}

fn main() {
    // No use animal::Speak;
    let d = animal::Dog;
    d.speak(); // Compile error! Speak isn't in scope
}
```

The `impl` block itself **neither needs nor may take `pub`**. For `impl Type` (not `impl Trait for Type`), each `fn` inside controls its own visibility with `pub`:

```rust,noplayground
mod shapes {
    pub struct Circle {
        pub radius: f64,
    }

    impl Circle {
        pub fn area(&self) -> f64 {
            std::f64::consts::PI * self.radius * self.radius
        }

        // A private method, usable only within the mod
        fn internal_check(&self) -> bool {
            self.radius > 0.0
        }
    }
}
#
# fn main() {}
```

### `pub(crate)`, `pub(super)`, `pub(in path)`

Sometimes you don't want full publicity, yet other `mod`s within the `crate` should have access. Rust offers fine-grained control:

- `pub(crate)`: visible throughout the `crate`, invisible outside (to other `crate`s).
- `pub(super)`: visible only to the parent `mod`.
- `pub(in crate::some::path)`: visible only to the named `mod` path — the finest control.

```rust,compile_fail
mod database {
    // Callable anywhere within the crate, but if this is a library,
    // users of your library can't see this function
    pub(crate) fn connect() -> String {
        String::from("connected")
    }

    // Note queries itself is pub — if this mod weren't pub,
    // things inside marked pub(super) would be pointless,
    // since the outside can't even see the mod, let alone its contents.
    pub mod queries {
        // Only the database mod (the parent) can see this
        pub(super) fn raw_query() -> String {
            String::from("SELECT * FROM users")
        }

        pub fn safe_query() -> String {
            let raw = raw_query(); // Calls within the same mod are fine
            format!("SAFE: {}", raw)
        }
    }
}

// A pub(in path) example
mod app {
    pub mod api {
        pub mod internal {
            // Only app::api can see this function
            pub(in crate::app::api) fn secret_key() -> &'static str {
                "super-secret"
            }
        }

        pub fn get_key() -> &'static str {
            internal::secret_key() // OK, we're inside app::api
        }
    }
}

// app::api::internal::secret_key() is invisible here,
// since pub(in crate::app::api) restricts access to app::api only

// Note: pub(in path) must name a mod that contains you
// (one of the layers outward), not an unrelated path:
//     pub(in crate::some_unrelated_mod) fn foo() {}
// The compiler errors; you cannot open visibility to a mod that does not contain you.

fn main() {
    let conn = database::connect();          // OK, we're in the same crate
    let q = database::queries::safe_query(); // OK, pub
    println!("{}, {}", conn, q);
    database::queries::raw_query();          // Error: pub(super) is parent-only
}
```

### Everything You Make Public, Taken Together, Is Your API

The set of things you open up with `pub` — functions, types, methods, `trait`s — together form the `crate`'s **API**. API (application programming interface) means "**the interface a piece of code exposes for others to call**": others see, and should depend on, only your public face; the private implementation details hidden behind `pub` are beyond their reach, and yours to change freely later. From Chapter 1 to now, every `String::new()`, `vec.push(x)`, and `iter.map(...)` you wrote was a call into the standard library's API — the standard library marked those functions and methods `pub` for you, hiding its internals completely. The only difference: before, you were the API's **user**; from this chapter on, you're also an API **designer**.

## Recap

- Rust makes **everything private by default**; publicity requires an explicit `pub`.
- `pub struct` publicizes only the type name; every field needs its **own** `pub` (tuple `struct`s too).
- A `struct` with private fields can't be constructed directly from outside; provide a constructor.
- A `pub enum`'s variants are **automatically public**.
- In `impl Trait for T`, the `fn`s' visibility follows the `trait` — no `pub`; in `impl T`, each `fn` takes its own `pub`.
- `pub(crate)`: visible within the `crate`, not outside.
- `pub(super)`: visible only to the parent `mod`.
- `pub(in path)`: visible only to the named `mod` path.
- Everything `pub`, taken together, **is your API**; the rest is implementation detail. The standard library is itself an API — this chapter turns you from the API's "user" into its "designer."
