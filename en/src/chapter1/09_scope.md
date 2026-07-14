# Scope

## Goal of This Episode

Understand the "region" created by curly braces `{}`, and why a variable can't be used once you're outside its braces.

## Main Text

This episode covers a very important concept — **scope**.

### What Is a Scope?

You can think of a pair of curly braces `{}` as a room. Things created inside the room can't be seen once you leave it.

Take a look at this example:

```rust,editable
fn main() {
    {
        let y = 10;
        println!("{}", y);
    }
}
```

So far so good.

### What Happens Outside the Braces?

Now try using `y` outside the braces:

```rust,compile_fail
fn main() {
    {
        let y = 10;
        println!("{}", y);
    }
    println!("{}", y); // This line causes an error!
}
```

You'll get a compile error — Rust is telling you: "I can't find this thing called `y`."

Why? Because `y` was created inside that pair of curly braces, and the moment you step outside them, `y` is gone. It's like putting a chair in a room: once the door is closed, you can't see that chair from the hallway.

### Why Have Scopes at All?

This is actually a good thing. It keeps your variables from wandering into places they shouldn't be. Imagine if every variable were usable anywhere in the program — once the program got big, it would be utter chaos. Scopes keep things neat and organized for you.

### Not Just Standalone Braces

The `if` we learned last episode has curly braces too, right? Well, the braces of an `if` also form a scope — variables inside can't be seen from outside. When you see `{}`, the inside is often a scope. It's a very consistent rule in Rust.

## Recap

- Curly braces `{}` often enclose a scope.
- A variable created inside a scope disappears once you leave the `{}` — it can't be used anymore.
- An `if` forms its own scope.
