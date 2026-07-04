# Compound Assignment Operators

## Goal of This Episode

Learn to update a variable's value using shorthand like `+=` and `-=`.

## Main Text

Last episode we learned `let mut`, which makes variables changeable. Today let's learn a lazier way to write updates.

### What Does `x = x + 5` Mean?

First, a very important idea. Suppose you have a variable `x` that's 10, and you want to add 5 to it:

```rust,editable
fn main() {
    let mut x = 10;
    x = x + 5;
    println!("{}", x); // 15
}
```

Here `x` appears on both the left and right sides of `=`. This is not the mathematical statement "`x` equals `x + 5`" (which makes no sense in math, right?). In programming it means: **first compute the right side, `x + 5` (that is, 10 + 5 = 15), then store the result back into the `x` on the left**. So `x` goes from 10 to 15.

### The `+=` Shorthand

That line actually has a shorter way of being written:

```rust,editable
fn main() {
    let mut x = 10;
    x += 5;
    println!("{}", x); // 15
}
```

`x += 5` means exactly `x = x + 5`, just more concise.

### The Other Compound Assignment Operators

Subtraction, multiplication, division, and remainder all have corresponding shorthands:

```rust,editable
fn main() {
    let mut a = 20;
    
    a -= 3;
    println!("20 - 3 = {}", a); // 17
    
    a *= 2;
    println!("17 * 2 = {}", a); // 34
    
    a /= 4;
    println!("34 / 4 = {}", a); // 8 (integer division)
    
    a %= 3;
    println!("8 % 3 = {}", a);  // 2
}
```

### At a Glance

| Shorthand | Equivalent to |
|------|--------|
| `x += 5` | `x = x + 5` |
| `x -= 5` | `x = x - 5` |
| `x *= 5` | `x = x * 5` |
| `x /= 5` | `x = x / 5` |
| `x %= 5` | `x = x % 5` |

### A Small Reminder

To use these operators, the variable must be declared with `let mut`, because you are **changing** its value.

## Recap

- The compound assignment operators: `+=`, `-=`, `*=`, `/=`, `%=`.
- `x += 5` is shorthand for `x = x + 5` — compute the right side first, then store it back on the left.
- Requirement: the variable must be declared with `let mut`.
