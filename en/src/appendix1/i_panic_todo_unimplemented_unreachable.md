# `panic!` / `todo!` / `unimplemented!` / `unreachable!`

## Goal of This Episode

Meet four macros that trigger a panic, and learn when each is appropriate.

> This episode is a general supplement, tied to no particular chapter.

## Concept

You've probably noticed the `!` after names like `println!()` and `format!()`. In Rust, things with a `!` in their name are **macros** — not quite functions, though for now knowing how to use them is enough; how macros work comes later.

This episode introduces four commonly used macros that trigger a panic as soon as execution reaches them. A panic interrupts normal execution; in the programs we've written so far, an unhandled panic ends the program. All four panic, but their semantics differ — and so does the message they send to whoever reads the code.

### `panic!("message")`

The most basic "something went wrong; panic now." For errors you can't handle:

```rust,should_panic
# fn main() {
    panic!("Something that shouldn't happen just happened!");
# }
```

Formatted messages work: `panic!("Couldn't find id: {}", id);`

### `todo!()`

"Not finished yet — placeholder for now." The development favorite: scaffold the program's structure first, fill in details later:

```rust,noplayground
fn calculate_tax(income: f64) -> f64 {
    todo!() // To be implemented later
}
#
# fn main() {}
```

It compiles, but execution reaching it panics with "not yet implemented."

### `unimplemented!()`

"This isn't implemented." Similar to `todo!()`, but with different semantics — `todo!()` clearly signals "will do later," while `unimplemented!()` makes **no promise it ever will be**. Maybe there's no plan, no current need, or it's a `trait`-required method meaningless for this type:

```rust,editable
trait Foo {
    fn bar(&self) -> u8;
    fn baz(&self);
}

struct MyStruct;

impl Foo for MyStruct {
    fn bar(&self) -> u8 {
        1 + 1
    }

    fn baz(&self) {
        // baz is meaningless for MyStruct, but the trait demands a definition
        unimplemented!()
    }
}

fn main() {}
```

### `unreachable!()`

"This line should never execute." When you're certain some logic can't be reached, mark it:

```rust,editable
fn main() {
    let direction = "north";
    match direction {
        "north" | "south" | "east" | "west" => println!("A valid direction"),
        _ => unreachable!("There are only four directions; this can't be reached"),
    }
}
```

If it does get reached, your assumption was wrong — and the panic surfaces that bug for you.

### The Four Compared

- `panic!` — something's wrong. For unhandleable errors.
- `todo!` — not written yet; will be implemented. A development placeholder.
- `unimplemented!` — not implemented, no promise it will be. Maybe unneeded; maybe `trait`-required but meaningless.
- `unreachable!` — shouldn't get here. Marks logically impossible branches.

## Example Code

```rust,editable
enum Shape {
    Circle(f64),
    Rectangle(f64, f64),
    Triangle(f64, f64, f64),
}

fn area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle(r) => 3.14159 * r * r,
        Shape::Rectangle(w, h) => w * h,
        Shape::Triangle(_, _, _) => todo!("Triangle area to be implemented later"),
    }
}

fn describe_score(score: u32) -> &'static str {
    match score {
        90..=100 => "Excellent",
        80..=89 => "Good",
        70..=79 => "Fair",
        60..=69 => "Passing",
        0..=59 => "Failing",
        _ => unreachable!("Scores should be between 0-100"),
    }
}

trait Storage {
    fn save(&mut self, data: &str);
    fn load(&self) -> String;
}

struct LocalStorage;

impl Storage for LocalStorage {
    fn save(&mut self, data: &str) {
        println!("Saving locally: {}", data);
    }

    fn load(&self) -> String {
        // The trait demands a definition, but LocalStorage doesn't need this feature
        unimplemented!()
    }
}

fn main() {
    // todo! — the development placeholder
    let circle = Shape::Circle(5.0);
    println!("Circle area: {}", area(&circle));

    let rect = Shape::Rectangle(3.0, 4.0);
    println!("Rectangle area: {}", area(&rect));

    // Uncommenting the next line panics with the todo! message
    // let tri = Shape::Triangle(3.0, 4.0, 5.0);
    // println!("Triangle area: {}", area(&tri));

    // unreachable! — the branch that shouldn't be reached
    let grade = describe_score(85);
    println!("The grade for 85 points: {}", grade);

    // unimplemented! — the unimplemented feature
    let mut storage = LocalStorage;
    storage.save("hello");
    // storage.load(); // Uncommenting panics: not implemented

    // panic! — trigger a panic
    // panic!("Panicking on purpose!");
    println!("The program ended normally");
}
```

## Recap

- `panic!("msg")` is the basic way to trigger a panic, for unhandleable errors.
- `todo!()` is the development placeholder, clearly saying "will implement later."
- `unimplemented!()` says "not implemented," promising nothing — maybe unneeded, maybe `trait`-required but meaningless for the type.
- `unreachable!()` marks logically unreachable code paths.
- All four panic; the difference lies in the **intent** conveyed — picking the right one makes code more expressive.
