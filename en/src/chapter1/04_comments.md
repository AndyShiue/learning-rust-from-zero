# Comments

## Goal of This Episode

Learn to write notes (comments) inside your code, so you and others can tell what you're doing.

## Main Text

When writing code, sometimes you'll want to jot a note beside it, reminding yourself "here's what this part does." That's what **comments** are for.

Comments are never executed by the computer — they exist purely for humans to read.

### Single-line Comments

Start with `//`, and the rest of the line becomes a comment:

```rust,editable
fn main() {
    // This is a comment; the computer ignores this line
    let x = 5; // You can also put one after code
    println!("{}", x);
}
```

Running this still prints just `5` — those two comments have no effect on the program at all.

### Multi-line Comments

If you want to write a longer note, you can wrap it in `/* */`:

```rust,editable
fn main() {
    /* 
        This is a multi-line comment
        It can span several lines
        The computer ignores all of it
    */
    let x = 10;
    println!("{}", x);
}
```

### When Should You Write Comments?

- When the logic of a piece of code isn't obvious.
- When you're worried you'll forget what it does when you come back a few days later.
- When you want to temporarily stop a line of code from running (i.e., "comment it out").

```rust,editable
fn main() {
    let x = 5;
    // println!("{}", x); // Not printing for now, but don't want to delete it
    println!("Program finished");
}
```

Now `println!("{}", x);` won't be executed, but you can bring it back to life at any time by removing the `//`.

### A Small Reminder

You don't need a comment on every line! Good code should be clear enough on its own. Comments are for the "non-obvious" spots — not for explaining every single line.

## Recap

- `//` is a single-line comment; `/* */` is a multi-line comment.
- Comments are for humans; the computer ignores them completely.
- You can use comments to temporarily "switch off" a line of code without deleting it.
- Good code should be clear on its own; save comments for the non-obvious parts.
