# Recursion

## Goal of This Episode

Have a function call itself to solve a problem — a technique called "recursion."

## Main Text

Have you ever wondered: can a function call itself from inside itself?

The answer is **yes**, and the technique is called **recursion**. It sounds mystical, but the concept is actually simple.

### The Classic Example: Factorial

"The factorial of 5" is written `5!`, meaning `5 × 4 × 3 × 2 × 1 = 120`.

Thinking recursively:
- `5! = 5 × 4!`
- `4! = 4 × 3!`
- `3! = 3 × 2!`
- `2! = 2 × 1!`
- `1! = 1` (stop here)

See it? Each step is "myself times the factorial one size smaller than me," stopping once we reach 1.

```rust,editable
fn factorial(n: u32) -> u32 {
    if n <= 1 {
        1
    } else {
        n * factorial(n - 1)
    }
}

fn main() {
    println!("5! = {}", factorial(5));
    println!("3! = {}", factorial(3));
    println!("1! = {}", factorial(1));
}
```

### The Two Keys to Recursion

Every recursive function needs two things:

**1. The base case**: when to stop

```rust,ignore
if n <= 1 {
    1 // Stop! No more calling myself
}
```

**2. The recursive case**: how to shrink the problem

```rust,ignore
n * factorial(n - 1) // Shrink the problem: n becomes n - 1
```

If you forget the base case, the function calls itself endlessly and the program eventually blows up.

### Tracing the Execution

Let's trace how `factorial(5)` executes:

```ignore
factorial(5)
= 5 * factorial(4)
= 5 * (4 * factorial(3))
= 5 * (4 * (3 * factorial(2)))
= 5 * (4 * (3 * (2 * factorial(1))))
= 5 * (4 * (3 * (2 * 1)))
= 5 * (4 * (3 * 2))
= 5 * (4 * 6)
= 5 * 24
= 120
```

Like Russian nesting dolls: unfold layer by layer, hit the bottom, then fold back up layer by layer.

### Another Example: Countdown

```rust,editable
fn countdown(n: u32) {
    if n == 0 {
        println!("Liftoff! 🚀");
        return;
    }
    println!("{}...", n);
    countdown(n - 1);
}

fn main() {
    countdown(5);
}
```

### Recursion vs Loops

All the examples above could be written with loops. So when to use recursion, and when loops?

- **Simple repetition** → loops are more intuitive.
- **The problem itself has a recursive structure** → recursion is more natural.

For now, just knowing how to write recursion is enough — the right scenarios will come along later.

## Recap

- Recursion is a function calling itself.
- There must be a **base case** (stopping condition), or you get an infinite loop.
- Each call must make the problem **smaller**, moving toward the base case.
