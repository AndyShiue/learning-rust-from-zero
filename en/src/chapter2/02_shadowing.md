# Shadowing

## Goal of This Episode

Re-declare a variable of the same name with `let` (shadowing), and see the key difference from `mut`.

## Main Text

Rust has a really interesting feature called **shadowing**. In short: you can use `let` to declare a variable with the same name again, and the new one "covers up" the old one.

```rust,editable
fn main() {
    let x = 5;
    let x = x + 1;
    println!("x = {}", x);
}
```

The second line, `let x = x + 1;`, is really saying: "I want to create a **brand-new** `x`, whose value is the old `x` plus 1." The old `x` gets covered up, and from then on `x` is 6.

You can even shadow several times in a row:

```rust,editable
fn main() {
    let x = 1;
    let x = x + 1; // x = 2
    let x = x * 3; // x = 6
    println!("x = {}", x);
}
```

### Shadowing vs `mut`: the Biggest Difference

"Wait — how is this different from `mut`? Aren't both just changing the value?"

The biggest difference: **shadowing can change the type; `mut` can't.**

```rust,editable
fn main() {
    // Shadowing: can go from a number to a string
    let x = 5;
    let x = "hello";
    println!("x = {}", x);
}
```

Perfectly legal! Because the second `let x` is a **brand-new variable** that just happens to share the name.

But try it with `mut`:

```rust,compile_fail
fn main() {
    let mut x = 5;
    x = "hello"; // ❌ Compile error! Can't stuff a string into an i32
}
```

`mut` only lets you change the "value" — the type stays locked. Shadowing creates an entirely new variable, so the type can be completely different.

### Practical Use

The most common use of shadowing is "converting the type while keeping the name":

```rust,editable
fn main() {
    let input = "42"; // This is a string
    let input = input.trim().parse::<i32>().expect("Please enter a number"); // Converted to a number, still called input
    println!("input + 1 = {}", input + 1);
}
```

Without shadowing, you'd have to invent two different names, like `input_str` and `input_num` — a bit long-winded.

### Shadowing and Scope

Remember scopes from Chapter 1, Episode 9? Shadowing works inside curly braces `{}` too — and once you leave the braces, the shadowing ends and the old variable "comes back":

```rust,editable
fn main() {
    let x = 1;
    {
        let x = 2; // From this line on inside the block, x is shadowed as 2
        println!("Inside the block, x = {}", x); // 2
    }
    println!("Outside the block, x = {}", x);     // 1
}
```

The `let x = 2` inside the braces creates a new `x`, shadowing the outer `x`. But this shadowing is only effective inside the braces — the moment you leave them, the new `x` vanishes and the original `x` (with value 1) is usable again.

This is completely different from `mut`. If you change the value in a block with `mut`, the value really has changed once you leave the block:

```rust,editable
fn main() {
    let mut x = 1;
    {
        x = 2; // Directly changing the value; not shadowing
    }
    println!("x = {}", x); // 2
}
```

So, once more with emphasis: shadowing **creates a new variable**, while `mut` **changes the old variable's value**. The difference is especially clear where scopes are involved.

## Recap

- Re-declaring a variable of the same name with `let` is called shadowing.
- The new variable covers up the old one.
- The biggest difference from `mut`: **shadowing can change the type**.
- In reality, each `let` creates an entirely new variable — the names just match.
- A variable shadowed inside braces vanishes once you exit them, and the original "comes back."
