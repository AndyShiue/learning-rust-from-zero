# `enum` (C-style)

## Goal of This Episode

Learn to use an `enum` to define a fixed set of options, so a variable can only be one of those values.

## Concept

Last episode we learned `struct` — for defining new types that "group several values together." This episode covers another way to define a new type: `enum`.

Sometimes we want to express "this thing can only be one of a few options." For instance, a traffic light can only be red, yellow, or green.

An `enum` (enumeration) is for defining exactly this kind of "pick one of several" type. Like a `struct`, defining an `enum` tells Rust: "I want a new type whose value can only be one of these options." The simplest `enum` looks like this:

```rust,editable
enum Color {
    Red,
    Green,
    Blue,
}

fn main() {}
```

Each option is called a **variant**. To create an `enum` value, use the `TypeName::VariantName` syntax:

```rust,editable
enum Color {
    Red,
    Green,
    Blue,
}

fn main() {
    let c = Color::Red;
}
```

Note the two colons `::` in the middle — in Rust this is the "path operator," meaning "the `Red` under `Color`."

This most basic kind of `enum` — where no variant carries any extra data — is sometimes called a C-style `enum`, because that's what `enum`s are like in the C language.

## Example Code

```rust,editable
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn main() {
    let _dir = Direction::Up;

    // We can't do much with enums yet
    // Next episode we'll learn match, which lets us act on an enum's value
    // For now, here's how to create different enum values

    let _d1 = Direction::Down;
    let _d2 = Direction::Left;
    let _d3 = Direction::Right;

    println!("Direction is set!");
    println!("(Next episode, match lets us act based on the direction)");
}
```

## Recap

- Like `struct`, an `enum` is a way to define a new type.
- `struct`: groups several values together; `enum`: picks one from several options.
- Use `::` to name a specific variant, e.g. `Direction::Up`.
- Every variant of a C-style `enum` carries no extra data.
- Like `struct`s, `enum` definitions generally go outside `fn main()`, above or below.
- We can't directly print an `enum`'s value yet (we can once we learn `match` next episode).
