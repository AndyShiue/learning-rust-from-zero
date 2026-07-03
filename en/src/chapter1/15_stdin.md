# `stdin`

## Goal of This Episode

Make the program read the user's keyboard input — copy the code as-is for now; you don't need to fully understand every line.

## Main Text

So far, the values in our programs have all been hard-coded. But what if we want the user to type things in themselves? For example, letting the user enter their name so the program can greet them?

### First, Copy This Code As-Is

```rust,noplayground
fn main() {
    println!("Please enter your name:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("Failed to read input");

    println!("Hello, {}!", input.trim());
}
```

What it looks like when run:

```ignore
Please enter your name:
Andy
Hello, Andy!
```

### What Is This Doing?

I know this looks a bit intimidating, but don't worry — for now, treat it as a **black box**. All you need to know is that it reads user input.

Roughly speaking:

1. `let mut input = String::new();` → Create an empty text variable, ready to receive input.
2. `std::io::stdin().read_line(&mut input).expect("Failed to read input");` → Read one line of text from the keyboard and store it in `input`.
3. `input.trim()` → Strip off the extra whitespace and the newline character.

As for what `String::new()`, `&mut`, and `.expect()` mean — we'll get to those gradually. For now, just copy them as-is.

### Why No Explanation Yet?

Because explaining this code requires several concepts we haven't learned yet. Rather than force-feeding you a pile of incomprehensible explanations, it's better to learn to use it first — understanding will come naturally later.

It's like learning to ride a bike as a kid: you didn't need to study mechanics and gyroscopic effects first — you just got on and rode.

### The Important Bit

Whenever you need to read user input, grab these three lines:

```rust,noplayground
# fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("Failed to read input");
    let name = input.trim(); // Strip the trailing newline
# }
```

## Recap

- The three-line boilerplate for reading user input: `String::new()` → `stdin().read_line()` → `.trim()`.
- Treat it as a black box and copy it for now; the underlying concepts will come gradually later.
- `.trim()` strips the newline character off the end of the input.
