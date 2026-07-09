# `parse`

## Goal of This Episode

Learn to convert text the user typed in into a number.

## Main Text

Just like last episode, feel free to copy the syntax in this episode as-is — you don't need to fully understand what every line does. We'll come back and explain once we've learned more concepts.

Last episode we learned to read the user's input, but what comes in is **text**. If the user types `42`, to Rust that's a piece of text, not the number 42.

You can't do arithmetic on text, so we need to "convert" it into a number.

### Text to Number

```rust,no_run
fn main() {
    println!("Please enter a number:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let num = input.trim().parse::<i32>().expect("not a number");

    println!("The number you entered is {}", num);
}
```

Running it:

```ignore
Please enter a number:
42
The number you entered is 42
```

### The Key Line Is This One

```rust,no_run
# fn main() {
#     let mut input = String::new();
#     std::io::stdin().read_line(&mut input).expect("failed to read input");
    let num = input.trim().parse::<i32>().expect("not a number");
# }
```

Breaking it down:

1. `input.trim()` → Strip whitespace and newlines from both ends.
2. `.parse::<i32>()` → **Parse** the text into an integer (`i32` is one of the integer types).
3. `.expect("not a number")` → If the conversion fails (say, the user typed "abc"), print this error message and end the program.

### A Complete Interactive Example

```rust,no_run
fn main() {
    println!("Please enter a number:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let num = input.trim().parse::<i32>().expect("not a number");

    println!("{} times 2 is {}", num, num * 2);
}
```

```ignore
Please enter a number:
7
7 times 2 is 14
```

Now you can read numbers and compute with them!

## Recap

- What the user types in is text; use `.parse::<i32>()` to turn it into an integer before doing arithmetic.
- `.expect("error message")` prints the message and ends the program if the conversion fails.
- The full pipeline: `input.trim().parse::<i32>().expect("not a number")`.
