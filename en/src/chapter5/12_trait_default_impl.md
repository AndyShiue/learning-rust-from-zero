# `trait`s with Multiple Methods and Default Implementations

## Goal of This Episode

Learn to define multiple methods in a `trait`, and use default implementations so implementers only override what they need.

## Concept

When Chapter 4 introduced `trait`s, ours had just one method each. In fact a `trait` can have many methods, and some can come with a **default implementation** — a pre-written "generic version" that implementers can override if they don't like it.

### Multiple Methods

```rust,noplayground
trait Describe {
    fn name(&self) -> String;
    fn description(&self) -> String;
}
#
# fn main() {}
```

When implementing, every method must be provided:

```rust,ignore
# trait Describe {
#     fn name(&self) -> String;
#     fn description(&self) -> String;
# }
#
# struct Cat;
#
impl Describe for Cat {
    fn name(&self) -> String { ... }
    fn description(&self) -> String { ... }
}
#
# fn main() {}
```

### Default Implementations

Some methods can ship with a sensible default version:

```rust,noplayground
trait Describe {
    fn name(&self) -> String;

    fn description(&self) -> String {
        let n = self.name();
        let mut result = String::from("I am ");
        result.push_str(&n);
        result
    }
}
#
# fn main() {}
```

`description` has a default implementation that calls `.name()` to build the string. When implementing `Describe`, you only need to supply `.name()` — `description()` automatically uses the default.

Of course, you can also override the default with your own version.

## Example Code

```rust,editable
trait Describe {
    // A method that must be implemented
    fn name(&self) -> String;

    // A default implementation: usable as-is, or overridable
    fn description(&self) -> String {
        let n = self.name();
        let mut result = String::from("I am ");
        result.push_str(&n);
        result
    }
}

struct Cat {
    nickname: String,
}

struct Dog {
    nickname: String,
}

// Cat implements only name; description uses the default
impl Describe for Cat {
    fn name(&self) -> String {
        self.nickname.clone()
    }
}

// Dog overrides description
impl Describe for Dog {
    fn name(&self) -> String {
        self.nickname.clone()
    }

    fn description(&self) -> String {
        let n = self.name();
        let mut result = String::from("Woof! My name is ");
        result.push_str(&n);
        result.push_str(", and I'm a dog!");
        result
    }
}

fn main() {
    let cat = Cat { nickname: String::from("Tangerine") };
    let dog = Dog { nickname: String::from("Shiba") };

    // Cat uses the default description
    println!("{}", cat.name());
    println!("{}", cat.description());

    // Dog uses its custom description
    println!("{}", dog.name());
    println!("{}", dog.description());
}
```

## Recap

- A `trait` can define multiple methods.
- Methods can have a **default implementation** — write `{ ... }` after the method instead of `;`.
- Default implementations can call other methods of the same `trait`.
- When implementing a `trait`, methods with defaults may be skipped (using the default) or overridden.
