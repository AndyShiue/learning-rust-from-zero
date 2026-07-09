# Practice Problems

## Goal of This Episode

Combine what we've learned so far into a small "enter a score → get a grade" program.

## Main Text

Congratulations on making it this far! Today we're going to string together everything we've learned into a genuinely useful little program.

### The Goal

Let the user enter a score, and have the program determine the letter grade and print it.

### The Complete Code

```rust,no_run
fn main() {
    println!("Please enter your score:");

    // Read user input
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    // Convert the text into a number
    let score = input.trim().parse::<i32>().expect("not a number");

    // Determine the grade
    if score >= 90 {
        println!("Your grade is A");
    } else if score >= 80 {
        println!("Your grade is B");
    } else if score >= 70 {
        println!("Your grade is C");
    } else {
        println!("Your grade is F");
    }
}
```

### Give It a Run

```ignore
Please enter your score:
85
Your grade is B
```

```ignore
Please enter your score:
92
Your grade is A
```

```ignore
Please enter your score:
45
Your grade is F
```

### A Look Back at the Techniques We Used

1. `println!` → printing a prompt message (Episode 2)
2. `let mut` + `String::new()` → getting ready to receive input (Episode 15)
3. `stdin().read_line(&mut input)` → reading keyboard input (Episode 15)
4. `.trim().parse::<i32>()` → converting text to a number (Episode 16)
5. `if` / `else if` / `else` → conditional logic (Episodes 8, 10, 11)

See that? By combining various features, you can build an interactive little program. That's the charm of programming — piece small bits of knowledge together and you can make something useful.

### Challenges

If you'd like more practice, try these:

- Add a D grade (scores 60 ~ 69).
- If the score is above 100 or below 0, print "Invalid score".

## Recap

- Combining the `stdin`, `parse`, `if`, and `else if` we learned earlier gives you an interactive program.
- The charm of programming: piecing small bits of knowledge together makes something useful.
- Beyond learning new syntax, practicing how to combine things matters a lot too.
