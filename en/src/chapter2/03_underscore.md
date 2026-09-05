# Underscore Variables

## Goal of This Episode

Use variable names starting with an underscore `_` to tell the compiler "I know this is unused — stop nagging me."

## Main Text

Rust's compiler is very considerate (sometimes a bit annoying). If you declare a variable but never use it, it gives you a warning:

```rust,editable
fn main() {
    let x = 5;
    // x is never used
}
```

The program still runs, but that yellow warning is unpleasant to look at. How do we get rid of it?

### Method 1: Add an Underscore Prefix

Put an underscore `_` in front of the variable name:

```rust,editable
fn main() {
    let _x = 5;
    // _x is never used, but the compiler no longer warns
}
```

Now the compiler understands: "Oh, you're leaving it unused on purpose. Fine."

Note that `_x` is still a normal variable — you can still use it if you want:

```rust,editable
fn main() {
    let _x = 5;
    println!("{}", _x);  // Still usable
}
```

### Method 2: A Lone Underscore `_`

If you don't even want to bother naming it, just use a single underscore:

```rust,editable
fn main() {
    let _ = 42;
}
```

This means "I don't care about this value at all." It has no name, so you can't use it afterward either.

### The Difference between `_x` and `_`

- `_x`: has a name; the value is kept and can be used later.
- `_`: does not give the value a name; you cannot use `_` to access it later.

In most situations either one works.

### Underscores Work in `for` Loops Too

Last chapter we learned `for i in 0..5`, where the loop variable `i` takes the values 0, 1, 2, 3, 4 in turn. But what if you just want to do something five times and don't care which iteration you're on? That's when `_` comes in:

```rust,editable
fn main() {
    for _ in 0..5 {
        println!("Five times!");
    }
}
```

`for _ in 0..5` means "run five times, but I don't need to know which round it currently is."

### A Practical Use: Guess the Number

Here's a slightly more complete example — challenge the player to guess a number within five tries:

```rust,no_run
fn main() {
    let secret = 67;
    let mut success = false;

    println!("Guess a number from 1~100:");

    for _ in 0..5 {
        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("failed to read input");
        let guess = input.trim().parse::<i32>().expect("not a number");

        if guess == secret {
            success = true;
            break;
        }

        println!("Not it......");
    }

    if success {
        println!("Congratulations, you guessed it within five tries!");
    } else {
        println!("Five tries and no luck......");
    }
}
```

If you guess right:

```ignore
Guess a number from 1~100:
50
Not it......
70
Not it......
67
Congratulations, you guessed it within five tries!
```

If all five guesses miss:

```ignore
Guess a number from 1~100:
50
Not it......
75
Not it......
60
Not it......
80
Not it......
90
Not it......
Five tries and no luck......
```

Here `for _ in 0..5` means "at most five guesses." We don't need to know which attempt we're on — we just need the loop to run five times. On a correct guess, we set `success` to `true` and `break` out of the loop.

## Recap

- Rust's compiler warns you about unused variables.
- Prefixing the name with `_` (like `_x`) silences the warning.
- A lone `_` means "I don't care about this value at all."
- `_x` can still be used; `_` cannot.
- When you don't need the loop variable, `for _ in 0..5` simply repeats five times.
