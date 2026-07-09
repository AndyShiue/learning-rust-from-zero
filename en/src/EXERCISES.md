# Fixed Practice-Problem Bank

This document is a practice-problem spec for AIs. When the reader wants exercises, the AI must read this document first, then decide how to respond based on the reader's current progress.

Distinguish between two kinds of problems:

1. **Fixed-bank problems**: the problems written out later in this document.
2. **Improvised problems**: when the reader insists on practicing but there is no suitable fixed problem for their progress, a small problem the AI writes on the spot, following the rules.

This bank is not a "source of inspiration" — it is a "source of boundaries." The AI must not read this document and then add its own string of more advanced, more complete, or more conventional-Rust-course problems; even improvised problems must be small, conservative, and constrained by the reader's progress.

## Problem-Assignment Principles

1. First confirm which chapter and episode the reader is currently on.
2. Look for problems within the reader's progress in this document, and check each entry's status.
3. Only entries whose status is `available` may be assigned directly as fixed-bank problems; pick 1 problem at a time.
4. When the status is `no problems`, briefly explain the entry's reason, then suggest the nearest earlier available problem or ask the reader to keep reading.
5. If there is no suitable fixed problem but the reader still insists on practicing, you may assign 1 improvised problem; you must state clearly that it is not a fixed-bank problem.

## Default Strategy by Chapter

- Chapters 1 and 2 have fixed practice problems by default. If the reader insists on practicing an episode that has no fixed problem, you may improvise 1 problem, but say first:

> This episode has no fixed problems in the bank. Below is a practice problem I improvised for your current progress.

- Improvised problems for Chapters 1–2 must be conservative, small, and complete; don't design big integrative problems.
- Chapter 3 and later have no fixed practice problems. Much of that material leans toward data modeling, syntactic expression, code organization, or convention round-ups; forcing fixed problems there easily turns into retyping examples or terminology quizzes.
- If the reader is on Chapter 3 or later and actively asks for problems, you may improvise 1 problem, but say first:

> There's no fixed problem bank past Chapter 3. Below is an improvised challenge; it may use content taught later, and you shouldn't feel you must solve it entirely on your own.

- Improvised problems past Chapter 3 may lean a little toward challenge problems, but still avoid piling on too many untaught tools at once.

## Rules for Using the Fixed Bank

1. Show the reader only the "Problems" part; don't hand over the "Grading criteria," "Hint directions," or "Reference answer" up front.
2. After the reader answers, first use the "Grading criteria" to judge whether they hit the problem's goal.
3. When the reader is stuck, give the "Hint directions" one layer at a time; don't spread the whole answer out at once.
4. Only give the "Reference answer" when the reader asks for it, or has tried and is still stuck.
5. The fixed bank focuses on programming problems; don't pad it with setup checks or terminology quizzes.

## Problem Entry Format

``````md
### Chapter X, Episode Y: Title

Status: no problems / available

Reason for no problems:
- If the status is `no problems`, briefly explain why; other statuses may omit this section.

Practice goals:
- ...

Problems:
1. ...
2. ...
3. ...

Grading criteria:
- ...

Hint directions:
1. ...
2. ...
3. ...

Reference answer:
```rust
// If the problem needs code, it goes here.
```
``````

## Chapter 1

### Chapter 1, Episode 1: Installing Rust

Status: no problems

Reason for no problems:
- This episode's goal is installing the tools and confirming that `rustc --version` runs; it's environment setup, not suited to a programming problem.
- The AI may help confirm the installation succeeded, or handle issues like the terminal not finding the command, but shouldn't force a practice problem.

### Chapter 1, Episode 2: Your First Program

Status: no problems

Reason for no problems:
- This episode is mainly about using `cargo new` to create a project for the first time, opening `src/main.rs`, and running the example with `cargo run` — project operations and following along with the book's first program.
- Forcing a problem here easily turns into a setup check or terminology quiz; suggest the reader first make sure the program runs, then read on to the next episode suited to practice.

### Chapter 1, Episode 3: Variables and Output

Status: available

Practice goals:
- Confirm the reader can create a variable with `let`.
- Confirm the reader can use `{}` to put a variable into `println!` output.
- Confirm the reader knows `let` can declare first and assign later, but the variable must have a value before it's used.

Problems:
1. Create a variable called `name` whose value is your name, then have the program print `Hello, <your name>!`.

Grading criteria:
- The variable must be declared with `let`.
- This episode practices a single `{}`; don't ask the reader to use multiple placeholders — multiple `{}` gets handled in Chapter 1, Episode 5.
- The text must be wrapped in double quotes.
- If the reader declares first and assigns later, that's fine as long as the assignment happens before the `println!`.

Hint directions:
1. `let name = "Alice";` creates a text variable.
2. In `println!("Hello, {}!", name);`, the `{}` gets replaced by `name`'s value.

Reference answer:

```rust
fn main() {
    let name = "Alice";
    println!("Hello, {}!", name);
}
```

### Chapter 1, Episode 4: Comments

Status: available

Practice goals:
- Confirm the reader knows whatever follows `//` doesn't get executed.
- Confirm the reader can use a comment to temporarily switch off a line of code.

Problems:
1. The program below currently prints two lines. Use `//` to comment out one of them, so the program prints only `Hello, Rust!`.

Starting code:

```rust
fn main() {
    println!("Hello, world!");
    println!("Hello, Rust!");
}
```

Grading criteria:
- The reader should use `//` to comment out `println!("Hello, world!");`.
- Deleting the line isn't required.
- No need for `/* */`; this problem practices single-line comments only.

Hint directions:
1. Whatever follows `//` is ignored by the computer.
2. This problem should leave the `Hello, Rust!` line running normally.

Reference answer:

```rust
fn main() {
    // println!("Hello, world!");
    println!("Hello, Rust!");
}
```

### Chapter 1, Episode 5: Arithmetic Operators

Status: available

Practice goals:
- Confirm the reader can use `/` for integer division.
- Confirm the reader can use `%` to get the remainder.
- Confirm the reader can line up several `{}` with the values after them, in order.

Problems:
1. Create two variables `total = 17` and `group = 5`, and print the following two lines:

```text
17 / 5 = 3
17 % 5 = 2
```

Grading criteria:
- The two variables `total` and `group` must be used; don't just hard-code the numbers into the string.
- The first line must use `total / group`.
- The second line must use `total % group`.
- The number of `{}` in `println!` must match the number of values after it.
- If the reader asks why `17 / 5` is `3`, answer with "integer division simply drops the fractional part."

Hint directions:
1. You can start with `let total = 17;` and `let group = 5;`.
2. `println!("{} / {} = {}", total, group, total / group);`.
3. `%` computes what's left over after the division.

Reference answer:

```rust
fn main() {
    let total = 17;
    let group = 5;

    println!("{} / {} = {}", total, group, total / group);
    println!("{} % {} = {}", total, group, total % group);
}
```

### Chapter 1, Episode 6: Operator Precedence

Status: no problems

Reason for no problems:
- This episode's point is understanding "multiplication and division before addition and subtraction" and using parentheses to change the order; a problem here would easily be just retyping the text's examples.
- The concept shows up naturally in later arithmetic problems; there's no need to force a standalone problem in this episode.

### Chapter 1, Episode 7: Comparison Operators

Status: no problems

Reason for no problems:
- This episode mainly introduces `==`, `!=`, `<`, `>`, `<=`, `>=`, and the fact that comparisons produce `true` / `false`.
- A standalone problem is either too easy or turns into a symbol quiz; comparison operators get natural practice inside programming problems from Episode 8's `if` onward.

### Chapter 1, Episode 8: `if`

Status: available

Practice goals:
- Confirm the reader can write a basic `if`.
- Confirm the reader knows the code in the braces runs only when the condition is `true`.
- Confirm the reader doesn't wrap the `if` condition in parentheses.

Problems:
1. Create a variable `score = 85`. If `score >= 60`, print `Pass`.

Expected output:

```text
Pass
```

Grading criteria:
- Must use `if score >= 60 { ... }`.
- `println!("Pass");` must go inside the `if` braces.
- Don't write `else`; `else` is taught in the next episode.
- Rust's `if` condition needs no parentheses; if the reader adds them, you can suggest removing them to match the book's style.

Hint directions:
1. First create the variable: `let score = 85;`.
2. The condition can be written as `score >= 60`.
3. What should happen when the condition holds goes inside `{}`.

Reference answer:

```rust
fn main() {
    let score = 85;

    if score >= 60 {
        println!("Pass");
    }
}
```

### Chapter 1, Episode 9: Scope

Status: available

Practice goals:
- Confirm the reader knows `{}` creates a scope.
- Confirm the reader knows a variable created inside a scope can't be used once you leave the `{}`.
- Confirm the reader can put a variable in the right place so the program compiles.

Problems:
1. The program below errors because `message` can't be used outside the braces. Move only the line `let message = "Hello";` so the program prints `Hello`.

Starting code:

```rust
fn main() {
    {
        let message = "Hello";
    }

    println!("{}", message);
}
```

Grading criteria:
- `let message = "Hello";` should move to the outer level — somewhere the `println!` can see it.
- Don't just move the `println!` into the inner block; that runs, but it doesn't practice "making the variable visible outside."
- The empty braces may stay or go.
- Don't explain ownership or lifetimes; this is only about scope.
- After the fix, the program must run with `cargo run`.

Hint directions:
1. A variable created inside `{}` becomes invisible once you leave that pair of `{}`.
2. For the `println!` to see `message`, `message` must sit at the same level as the `println!`, or further out.

Reference answer:

```rust
fn main() {
    let message = "Hello";

    println!("{}", message);
}
```

### Chapter 1, Episode 10: `else`

Status: available

Practice goals:
- Confirm the reader can write `if ... else ...`.
- Confirm the reader knows the `if` side runs when the condition holds and the `else` side when it doesn't.
- Confirm the reader knows `if...else...` takes exactly one of the two paths.

Problems:
1. Create a variable `temperature = 18`. If `temperature >= 25`, print `Hot`; otherwise print `Cool`.

Expected output:

```text
Cool
```

Grading criteria:
- Must use `if temperature >= 25 { ... } else { ... }`.
- With `temperature = 18`, the `else` side should run.
- Don't write two separate `if`s; this problem practices the either-or shape.
- Rust's `if` condition needs no parentheses.

Hint directions:
1. First create the variable: `let temperature = 18;`.
2. The condition is `temperature >= 25`.
3. What should happen when the condition fails goes inside `else`.

Reference answer:

```rust
fn main() {
    let temperature = 18;

    if temperature >= 25 {
        println!("Hot");
    } else {
        println!("Cool");
    }
}
```

### Chapter 1, Episode 11: `else if`

Status: available

Practice goals:
- Confirm the reader can use `else if` to handle three or more cases.
- Confirm the reader knows Rust checks the conditions from top to bottom.
- Confirm the reader knows that once one condition holds, the later branches don't run.

Problems:
1. Create a variable `temperature = 32` and print a result by the following rules:
   - `temperature >= 35`: print `Very hot`.
   - `temperature >= 25`: print `Warm`.
   - anything else: print `Chilly`.

Expected output:

```text
Warm
```

Grading criteria:
- Must use `if ... else if ... else`.
- With `temperature = 32`, the first condition `temperature >= 35` fails and the second condition `temperature >= 25` holds, so it prints `Warm`.
- The condition order can't be flipped; if `temperature >= 25` comes first, everything 35 and up gets captured there too.
- Don't write three separate `if`s.

Hint directions:
1. Check the strictest condition first: `temperature >= 35`.
2. The second stage is `else if temperature >= 25`.
3. Finish with `else` to handle everything remaining.

Reference answer:

```rust
fn main() {
    let temperature = 32;

    if temperature >= 35 {
        println!("Very hot");
    } else if temperature >= 25 {
        println!("Warm");
    } else {
        println!("Chilly");
    }
}
```

### Chapter 1, Episode 12: Logical Operators

Status: available

Practice goals:
- Confirm the reader can combine two conditions with `&&`.
- Confirm the reader knows `&&` requires both sides to hold.
- Confirm the reader can use `||` and parentheses to express more complex condition grouping.

Problems:
1. Create two variables: `age = 20`, `has_ticket = true`. If `age >= 18` and `has_ticket` is `true`, print `Admitted`; otherwise print `Not admitted`.
2. Create three variables: `age = 16`, `with_parent = true`, `has_ticket = true`. The rule: you may enter if you have a ticket, and are either at least 18 or accompanied by a parent. Print `Admitted` or `Not admitted`.

Expected output:

```text
Admitted
Admitted
```

Grading criteria:
- Problem 1 must use `age >= 18 && has_ticket`.
- No need to write `has_ticket == true`; `has_ticket` on its own is enough.
- Problem 2 should use `has_ticket && (age >= 18 || with_parent)`.
- Problem 2's parentheses matter, because the rule is "has a ticket" and "is 18+ or accompanied by a parent."
- Don't write `has_ticket && age >= 18 || with_parent` — that makes `with_parent` look like it can bypass the ticket requirement.
- If the reader asks about operator order, first remind them that "when unsure, add parentheses to make the condition clearer"; no need to unfold too many details.

Hint directions:
1. "And" maps to `&&`.
2. "Or" maps to `||`.
3. In problem 2, you can write "18+ or accompanied by a parent" as `(age >= 18 || with_parent)` first, then join it to `has_ticket` with `&&`.

Reference answer:

```rust
fn main() {
    let age = 20;
    let has_ticket = true;

    if age >= 18 && has_ticket {
        println!("Admitted");
    } else {
        println!("Not admitted");
    }

    let age = 16;
    let with_parent = true;
    let has_ticket = true;

    if has_ticket && (age >= 18 || with_parent) {
        println!("Admitted");
    } else {
        println!("Not admitted");
    }
}
```

### Chapter 1, Episode 13: `let mut`

Status: available

Practice goals:
- Confirm the reader knows Rust variables are immutable by default.
- Confirm the reader can declare a mutable variable with `let mut`.
- Confirm the reader knows updating a variable doesn't take another `let`.

Problems:
1. The program below wants to change `coins` from `3` to `5`, but it currently fails to compile. Fix it so the program prints `5` at the end.

Starting code:

```rust
fn main() {
    let coins = 3;
    coins = 5;
    println!("{}", coins);
}
```

Grading criteria:
- The declaration should become `let mut coins = 3;`.
- The update should stay `coins = 5;`, not `let coins = 5;`.
- Don't introduce shadowing here; shadowing isn't covered until Chapter 2, Episode 2.
- After the fix, the program should print `5`.

Hint directions:
1. Rust variables can't be changed by default.
2. To change one later, add `mut` at the declaration.
3. The updating line doesn't need another `let`.

Reference answer:

```rust
fn main() {
    let mut coins = 3;
    coins = 5;
    println!("{}", coins);
}
```

### Chapter 1, Episode 14: Compound Assignment Operators

Status: available

Practice goals:
- Confirm the reader knows `x += 5` is the same as `x = x + 5`.
- Confirm the reader can update a mutable variable with compound assignment operators.
- Confirm the reader knows the variable must be `let mut` to use compound assignment.

Problems:
1. A teacher is adjusting a student's score: it starts at `60`, first gains `10` bonus points, then gets multiplied by `2`. The program below works; change the two lines that update `score` to use compound assignment operators, keeping the final output `140`.

Starting code:

```rust
fn main() {
    let mut score = 60;

    score = score + 10;
    score = score * 2;

    println!("{}", score);
}
```

Expected output:

```text
140
```

Grading criteria:
- The updates should become `score += 10;` and `score *= 2;`.
- `score` must keep its `let mut`.
- Don't just write the result directly as `let score = 140;` or `score = 140;`.
- The final output must still be `140`.

Hint directions:
1. `score = score + 10;` can become `score += 10;`.
2. Multiplication has a corresponding shorthand too.
3. Since `score` keeps changing, the declaration keeps its `mut`.

Reference answer:

```rust
fn main() {
    let mut score = 60;

    score += 10;
    score *= 2;

    println!("{}", score);
}
```

### Chapter 1, Episode 15: `stdin`

Status: available

Practice goals:
- Confirm the reader can copy the fixed stdin boilerplate.
- Confirm the reader uses `input.trim()` when printing what the user typed.
- Confirm the reader doesn't need to understand the details of `String::new()`, `&mut`, `.expect()` here.

Problems:
1. Write a program that asks the user for their favorite food, then prints `You like <food>!`.

Sample run:

```text
Please enter your favorite food:
ramen
You like ramen!
```

Grading criteria:
- The book's three-line stdin boilerplate can be used as-is.
- The output must use `input.trim()`, so the trailing newline doesn't get printed too.
- Don't ask the reader to explain `String::new()`, `&mut`, `.expect()`.
- Don't switch this to reading numbers; converting text to numbers comes next episode.

Hint directions:
1. Copy the book's three-line input-reading boilerplate first.
2. Change the prompt to `Please enter your favorite food:`.
3. Finish with `println!("You like {}!", input.trim());`.

Reference answer:

```rust
fn main() {
    println!("Please enter your favorite food:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    println!("You like {}!", input.trim());
}
```

### Chapter 1, Episode 16: `parse`

Status: available

Practice goals:
- Confirm the reader can convert the user's text input into an `i32`.
- Confirm the reader can use the converted number in arithmetic.
- Confirm the reader keeps using `.expect("not a number")`, not error handling that hasn't been taught yet.

Problems:
1. Write a program that asks the user for a number, then prints that number plus `10`.

Sample run:

```text
Please enter a number:
32
32 plus 10 is 42
```

Grading criteria:
- Must use `input.trim().parse::<i32>().expect("not a number")`.
- The addition must use the converted number variable; don't handle the input as text.
- Don't use `.unwrap()` or `?`.
- Don't unfold turbofish, generics, or `Result`; for now, treat `.parse::<i32>()` as fixed boilerplate, the way the book does.

Hint directions:
1. Copy the fixed stdin input-reading boilerplate first.
2. Convert the text to a number with `let num = input.trim().parse::<i32>().expect("not a number");`.
3. `num + 10` is the result after adding 10.

Reference answer:

```rust
fn main() {
    println!("Please enter a number:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let num = input.trim().parse::<i32>().expect("not a number");

    println!("{} plus 10 is {}", num, num + 10);
}
```

### Chapter 1, Episode 17: Practice Problems

Status: available

Practice goals:
- Confirm the reader can combine `stdin`, `parse`, `if`, `else if`, and `else`.
- Confirm the reader can add a new condition branch to the existing score-grading program.
- Confirm the reader knows the order of `else if` branches affects the result.

Problems:
1. Starting from the book's "enter a score → print the grade" program, add a D grade: scores from `60` to `69` print `Your grade is D`. All other rules stay the same.

Sample run:

```text
Please enter your score:
65
Your grade is D
```

Grading criteria:
- The stdin and parse boilerplate must be kept.
- `else if score >= 60` must be inserted after `score >= 70` and before the final `else`.
- The condition order can't get scrambled; putting `score >= 60` too early would wrongly classify scores of 70, 80, 90 and up as D.
- Don't ask the reader to handle scores above 100 or below 0; that can wait for later, or for the reader's own initiative.

Hint directions:
1. First find the C branch in the book's program: `else if score >= 70`.
2. D goes after C and before F.
3. The final `else` still handles everything below 60.

Reference answer:

```rust
fn main() {
    println!("Please enter your score:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let score = input.trim().parse::<i32>().expect("not a number");

    if score >= 90 {
        println!("Your grade is A");
    } else if score >= 80 {
        println!("Your grade is B");
    } else if score >= 70 {
        println!("Your grade is C");
    } else if score >= 60 {
        println!("Your grade is D");
    } else {
        println!("Your grade is F");
    }
}
```

### Chapter 1, Episode 18: `loop` + `break`

Status: available

Practice goals:
- Confirm the reader can use `loop` to keep asking for input.
- Confirm the reader can use `break` to leave the loop when a condition holds.
- Confirm the reader can combine `stdin`, `parse`, `if`, and `loop`.

Problems:
1. Write a program that repeatedly asks the user for a number. If the number is greater than `0`, print `Got a positive number!` and end the program; if the number is less than or equal to `0`, print `Try again` and keep asking.

Sample run:

```text
Please enter a positive number:
-3
Try again
Please enter a positive number:
0
Try again
Please enter a positive number:
5
Got a positive number!
```

Grading criteria:
- `loop` must wrap the whole prompt–read–parse–check flow.
- Each iteration must create a fresh `input`; don't reuse the previous round's.
- Must use `.parse::<i32>().expect("not a number")`.
- When `num > 0`, print `Got a positive number!` and `break`.
- When `num <= 0`, print `Try again`, without `break`ing.
- Don't switch to `while` or `for`; those are taught later.

Hint directions:
1. Start by writing `loop { ... }`.
2. Put the stdin and parse boilerplate inside the `loop`.
3. Use `if num > 0 { ... } else { ... }` to decide whether to `break`.

Reference answer:

```rust
fn main() {
    loop {
        println!("Please enter a positive number:");

        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("failed to read input");

        let num = input.trim().parse::<i32>().expect("not a number");

        if num > 0 {
            println!("Got a positive number!");
            break;
        } else {
            println!("Try again");
        }
    }
}
```

### Chapter 1, Episode 19: `while`

Status: available

Practice goals:
- Confirm the reader can use `while` to repeat while a condition holds.
- Confirm the reader can update a variable inside the loop so the loop eventually stops.
- Confirm the reader can combine two rounds of `stdin`, `parse`, `let mut`, and `while`.

Problems:
1. Write a "savings goal" program using `while`. Ask the user first for a target amount `goal`, then for the amount they've saved so far, `money`. Each round, the program saves another `30` for them and prints the current total. As long as `money` is still less than `goal`, keep saving; once the goal is reached, print `Goal reached!`.

Sample run:

```text
Please enter the target amount:
100
Please enter the current amount:
40
Saved so far: 70
Saved so far: 100
Goal reached!
```

Grading criteria:
- Two inputs must be read: one for `goal`, one for `money`.
- `goal` may stay immutable; `money` must be `let mut`, since the loop changes it.
- Both inputs must use `.parse::<i32>().expect("not a number")`.
- Must use `while money < goal`.
- Inside the loop, first `money += 30;`, then print the current amount.
- After the loop ends, print `Goal reached!`.
- Don't switch to `loop` or `for`; this problem practices `while`.

Hint directions:
1. Read `goal` with the fixed stdin boilerplate first.
2. Then write a second copy of the stdin boilerplate to read `money`.
3. Since `money` grows inside the loop, write `let mut money = ...`.
4. The condition can be written as `while money < goal`.

Reference answer:

```rust
fn main() {
    println!("Please enter the target amount:");

    let mut goal_input = String::new();
    std::io::stdin().read_line(&mut goal_input).expect("failed to read input");

    let goal = goal_input.trim().parse::<i32>().expect("not a number");

    println!("Please enter the current amount:");

    let mut money_input = String::new();
    std::io::stdin().read_line(&mut money_input).expect("failed to read input");

    let mut money = money_input.trim().parse::<i32>().expect("not a number");

    while money < goal {
        money += 30;
        println!("Saved so far: {}", money);
    }

    println!("Goal reached!");
}
```

### Chapter 1, Episode 20: `for` + Ranges

Status: available

Practice goals:
- Confirm the reader can use `for` with a range to repeat.
- Confirm the reader knows `a..b` excludes `b` while `a..=b` includes it.
- Confirm the reader knows the `for` variable needs no `let` of its own.
- Confirm the reader can combine `for`, `%`, `if` / `else if` / `else`, and `&&`.

Problems:
1. Using `for`, ask the user for the last seat number `last`, then print from `1` to `last`, one line per seat, each in the format `Seat No. <n>`.
2. Write a FizzBuzz program using `for`. Ask the user for a positive integer `n`, and print from `1` to `n`: if a number is a multiple of both `3` and `5`, print `FizzBuzz`; if it's only a multiple of `3`, print `Fizz`; if it's only a multiple of `5`, print `Buzz`; print every other number as-is.

Sample runs:

```text
Please enter the last seat number:
4
Seat No. 1
Seat No. 2
Seat No. 3
Seat No. 4
```

```text
Please enter a positive integer:
15
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

Grading criteria:
- Must use the stdin boilerplate and `.parse::<i32>().expect("not a number")`.
- Problem 1 must use `for seat in 1..=last`, because the last seat is included.
- Problem 1 must not use `1..last` — that would skip the final seat.
- Problem 2 must use `for i in 1..=n`, printing from 1 to n.
- Problem 2 must check `i % 3 == 0 && i % 5 == 0` first, and only then 3 or 5 on their own; in the reverse order, `FizzBuzz` never prints.
- Problem 2 shouldn't switch to `i % 15 == 0`; this problem practices combining two conditions with `&&`.
- No `let seat` needed; `for seat in ...` takes care of it.
- Don't switch to `while`; this problem practices `for` + ranges.

Hint directions:
1. Read the user's input and convert it to `last`.
2. Since the last number is included, the range needs `..=`.
3. `println!("Seat No. {}", seat);` prints each seat number.
4. FizzBuzz must handle "a multiple of both 3 and 5" first.
5. Use `%` for remainders, e.g. `i % 3 == 0`.

Reference answer:

```rust
fn main() {
    println!("Please enter the last seat number:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let last = input.trim().parse::<i32>().expect("not a number");

    for seat in 1..=last {
        println!("Seat No. {}", seat);
    }
}
```

```rust
fn main() {
    println!("Please enter a positive integer:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let n = input.trim().parse::<i32>().expect("not a number");

    for i in 1..=n {
        if i % 3 == 0 && i % 5 == 0 {
            println!("FizzBuzz");
        } else if i % 3 == 0 {
            println!("Fizz");
        } else if i % 5 == 0 {
            println!("Buzz");
        } else {
            println!("{}", i);
        }
    }
}
```

### Chapter 1, Episode 21: Nested Loops

Status: available

Practice goals:
- Confirm the reader knows one outer-loop pass runs the inner loop in full.
- Confirm the reader can use `print!` and `println!()` to produce two-dimensional output.
- Confirm the reader knows `break` exits only the innermost loop, while `break 'outer` exits the labeled outer loop.

Problems:
1. Ask the user for a height `height` and a width `width`, then print a block of stars.
2. Ask the user for a number of levels `levels`, then print a left-aligned star pyramid.
3. Ask the user for a target number `target`. Use nested `for` loops over `1..=9` and `1..=9` to find the first pair with `a * b >= target`. When found, print `a = <a>, b = <b>` and use a loop label to jump out of both loops at once.

Sample runs:

```text
Please enter the height:
3
Please enter the width:
5
*****
*****
*****
```

```text
Please enter the number of levels:
4
*
**
***
****
```

```text
Please enter the target number:
20
a = 3, b = 7
```

Grading criteria:
- All three problems must use the stdin boilerplate and `.parse::<i32>().expect("not a number")`.
- Problem 1 needs two `for` loops: the outer one controls the height, the inner one the width.
- In problems 1 and 2, the inner loop should use `print!("*");`, and each outer pass should end with `println!();` for the newline.
- Problem 2's inner range must depend on the outer variable, e.g. `1..=row`.
- Problem 3 must use a loop label, e.g. `'outer: for a in 1..=9 { ... }`.
- Problem 3 must `break 'outer;` once the first pair is found, not just `break` the inner loop.
- Problems 1 and 2 may produce "unused variable" warnings; that's normal. Don't silence them with underscore variables — those come in Chapter 2, Episode 3.
- Don't use arrays, `Vec`, functions, or recursion.

Hint directions:
1. Think of nested loops as "the outer loop picks the row, the inner loop prints that row."
2. `print!` doesn't add a newline; `println!()` can do the line break.
3. Problem 2's inner endpoint can use the outer loop's variable.
4. To jump straight out of the outer loop from inside, put a label on the outer loop.

Reference answer:

```rust
fn main() {
    println!("Please enter the height:");

    let mut height_input = String::new();
    std::io::stdin().read_line(&mut height_input).expect("failed to read input");

    let height = height_input.trim().parse::<i32>().expect("not a number");

    println!("Please enter the width:");

    let mut width_input = String::new();
    std::io::stdin().read_line(&mut width_input).expect("failed to read input");

    let width = width_input.trim().parse::<i32>().expect("not a number");

    for row in 1..=height {
        for col in 1..=width {
            print!("*");
        }
        println!();
    }
}
```

```rust
fn main() {
    println!("Please enter the number of levels:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let levels = input.trim().parse::<i32>().expect("not a number");

    for row in 1..=levels {
        for col in 1..=row {
            print!("*");
        }
        println!();
    }
}
```

```rust
fn main() {
    println!("Please enter the target number:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let target = input.trim().parse::<i32>().expect("not a number");

    'outer: for a in 1..=9 {
        for b in 1..=9 {
            if a * b >= target {
                println!("a = {}, b = {}", a, b);
                break 'outer;
            }
        }
    }
}
```

### Chapter 1, Episode 22: `continue`

Status: available

Practice goals:
- Confirm the reader knows `continue` skips this round, rather than ending the whole loop.
- Confirm the reader can use `continue 'outer` in nested loops to jump to the outer loop's next round.
- Confirm the reader can combine `stdin`, `parse`, `for`, `%`, nested loops, and loop labels.

Problems:
1. Ask the user for a positive integer `n`, and print every prime between `2` and `n`. Use `continue 'outer`: when a candidate turns out to be divisible by some other number, jump straight to the next candidate. The goal here is practicing `continue 'outer`, not chasing the fastest primality algorithm.

Sample run:

```text
Please enter the upper limit:
20
2
3
5
7
11
13
17
19
```

Grading criteria:
- Must use the stdin boilerplate and `.parse::<i32>().expect("not a number")`.
- The outer loop can be written as `'outer: for num in 2..=n`.
- The inner loop can be written as `for divisor in 2..num`, checking whether anything divides `num`.
- If `num % divisor == 0`, `num` isn't prime — use `continue 'outer;`.
- Only when the inner loop runs to completion without skipping do you print `num`.
- Don't use arrays, `Vec`, functions, or recursion.
- Don't reduce this to checking a single number; the problem lists all primes in a range.
- Don't demand optimizations from the reader (checking only up to the square root, skipping evens, and so on); those aren't the point of this problem.

Hint directions:
1. The outer loop checks each `num` one by one.
2. The inner loop looks for a `divisor` that divides `num`.
3. As soon as some `divisor` divides it, `num` isn't prime — `continue 'outer` to move on to the next `num`.
4. Only if the inner loop never triggers `continue 'outer` does the program reach `println!("{}", num);`.

Reference answer:

```rust
fn main() {
    println!("Please enter the upper limit:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let n = input.trim().parse::<i32>().expect("not a number");

    'outer: for num in 2..=n {
        for divisor in 2..num {
            if num % divisor == 0 {
                continue 'outer;
            }
        }

        println!("{}", num);
    }
}
```

### Chapter 1, Episode 23: Types (the Basics)

Status: no problems

Reason for no problems:
- This episode mainly introduces `i32`, `f64`, `bool`, type inference, and manual type annotations.
- A problem here would easily be retyping the examples; these types keep getting natural use in the programming problems that follow.

### Chapter 1, Episode 24: Types (Numbers in Detail)

Status: no problems

Reason for no problems:
- This episode supplements numeric types, default types, literal suffixes, floating-point precision, and similar background.
- A problem here easily becomes type-name memorization or a table quiz; there's no need to make the reader deliberately drill every numeric type right now.

### Chapter 1, Episode 25: `char`

Status: no problems

Reason for no problems:
- This episode mainly introduces `char`, the difference between single and double quotes, and Unicode characters.
- A standalone problem has little practice value; the next episode, "Escape Characters," is better suited to output problems involving quotes and special characters.

### Chapter 1, Episode 26: Escape Characters

Status: available

Practice goals:
- Confirm the reader can use `\n` and `\t` to control output formatting.
- Confirm the reader can print a double quote `"` inside a string.
- Confirm the reader can print a backslash `\` inside a string.

Problems:
1. Write a program that uses only one `println!` to print two lines of text:

```text
First line
Second line
```

2. Write a program that prints the following sentence, double quotes included:

```text
He said: "Rust is fun!"
```

3. Write a program that prints this path:

```text
C:\Users\Ferris\code
```

Grading criteria:
- Problem 1 must use `\n`; don't write two `println!`s.
- Problem 2 must use `\"` inside the string to print the double quotes.
- Problem 3 must use `\\` to print the backslashes.
- Don't ask the reader to use raw strings; those aren't introduced until Appendix I.
- If the reader wraps a string in single quotes, remind them Rust strings use double quotes.

Hint directions:
1. `\n` means a line break.
2. To print `"` inside a string, write `\"`.
3. To print `\` inside a string, write `\\`.

Reference answer:

```rust
fn main() {
    println!("First line\nSecond line");
}
```

```rust
fn main() {
    println!("He said: \"Rust is fun!\"");
}
```

```rust
fn main() {
    println!("C:\\Users\\Ferris\\code");
}
```

### Chapter 1, Episode 27: `if` as an Expression

Status: available

Practice goals:
- Confirm the reader knows `if` can return a value directly.
- Confirm the reader knows the `if` and `else` sides must have the same type.
- Confirm the reader leaves off the semicolon where a value is being returned.
- Confirm the reader can combine `stdin`, `parse`, and the `if` expression.

Problems:
1. Write a ticket-pricing program. Ask the user for their age `age`; if the age is under `18`, the ticket price is `50`, otherwise it's `100`. Use an `if` expression to set `ticket_price` directly, then print the price.

Sample run:

```text
Please enter your age:
12
The ticket price is 50 dollars
```

Grading criteria:
- Must use the stdin boilerplate and `.parse::<i32>().expect("not a number")`.
- It should read `let ticket_price = if age < 18 { 50 } else { 100 };`.
- No `let mut ticket_price` needed.
- No semicolons after the `50` and `100`.
- Both the `if` and `else` sides must return integers.
- Don't turn this into ordinary `if...else...` assignment; this problem practices the `if` expression.

Hint directions:
1. Read the user's input and convert it to `age`.
2. The whole of `if age < 18 { 50 } else { 100 }` can sit on the right of `let ticket_price =`.
3. The `50` and `100` inside the braces are return values — no semicolons.

Reference answer:

```rust
fn main() {
    println!("Please enter your age:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let age = input.trim().parse::<i32>().expect("not a number");

    let ticket_price = if age < 18 { 50 } else { 100 };

    println!("The ticket price is {} dollars", ticket_price);
}
```

## Chapter 2

### Chapter 2, Episode 1: `const`

Status: available

Practice goals:
- Confirm the reader can declare a constant with `const`.
- Confirm the reader knows `const` must have a type annotation.
- Confirm the reader knows the naming convention for constants is all-caps with underscores.
- Confirm the reader knows `const` can sit outside `fn main()`.

Problems:
1. Write a pass/fail program. Outside `fn main()`, declare the constant `PASS_SCORE: i32 = 60`. The program asks the user for a score; if the score is at least `PASS_SCORE`, print `Pass`, otherwise print `Fail`.

Sample run:

```text
Please enter a score:
72
Pass
```

Grading criteria:
- `PASS_SCORE` should be declared with `const`, not `let`.
- `const PASS_SCORE: i32 = 60;` should sit outside `fn main()`.
- `const` must have a type; `const PASS_SCORE = 60;` won't compile.
- The constant's name must be all-caps with underscores.
- Don't write `const mut`; constants can't take `mut`.
- The check must use `score >= PASS_SCORE`; don't hard-code `60` into the `if`.

Hint directions:
1. The constant can go above `fn main()`.
2. The `const` format is `const NAME: Type = value;`.
3. After reading the score, check `score >= PASS_SCORE`.

Reference answer:

```rust
const PASS_SCORE: i32 = 60;

fn main() {
    println!("Please enter a score:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let score = input.trim().parse::<i32>().expect("not a number");

    if score >= PASS_SCORE {
        println!("Pass");
    } else {
        println!("Fail");
    }
}
```

### Chapter 2, Episode 2: Shadowing

Status: no problems

Reason for no problems:
- Important as this episode is, problems here easily become retyping the text's examples, or artificially staged concept quizzes.
- Shadowing fits naturally into later integrated problems; there's no need to force one in this episode.

### Chapter 2, Episode 3: Underscore Variables

Status: available

Practice goals:
- Confirm the reader knows `_` can be used when the loop variable isn't needed.
- Confirm the reader can use `for _ in 0..n` to simply repeat a fixed number of times.
- Confirm the reader knows `_` is not a variable to be used later.

Problems:
1. Write a simple password-check program. The correct password is `"rust"`. Give the user at most 3 attempts: on a correct guess, print `Login successful` and end the loop; on a wrong guess, print `Wrong password`. Use `for _ in 0..3`, since this problem doesn't need to know which attempt it's on.

Sample run:

```text
Please enter the password:
abc
Wrong password
Please enter the password:
rust
Login successful
```

Grading criteria:
- Must use `for _ in 0..3`.
- Don't write `for i in 0..3` and then never use `i`.
- Each round must read fresh input.
- `input.trim() == "rust"` can check whether the password is correct.
- On success, `break` out of the loop.
- Don't require an extra message after three failures; the point here is `_` and fixed-count loops.

Hint directions:
1. `for _ in 0..3` means "repeat three times, without needing to know which round it is."
2. Each iteration can read a line with the fixed stdin boilerplate.
3. If `input.trim() == "rust"`, print the success message and `break`.

Reference answer:

```rust
fn main() {
    for _ in 0..3 {
        println!("Please enter the password:");

        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("failed to read input");

        if input.trim() == "rust" {
            println!("Login successful");
            break;
        } else {
            println!("Wrong password");
        }
    }
}
```

### Chapter 2, Episode 4: Tuples

Status: no problems

Reason for no problems:
- This episode covers basic tuple creation, element access, and single-element tuple syntax; standalone problems are either too easy or just retype the text's examples.
- Tuples get natural practice later in function return values, destructuring, and integrated problems; there's no need to force one in this episode.

### Chapter 2, Episode 5: `{:?}` and the `Debug` Format

Status: no problems

Reason for no problems:
- This episode mainly introduces output-format tools: `{:?}`, `{:#?}`, `dbg!`.
- A standalone problem would just ask the reader to swap `{}` for `{:?}` — little practice value.
- The `Debug` format gets heavy natural use later with structs, enums, and derive; putting it in problems will mean more then.

### Chapter 2, Episode 6: Simple Functions

Status: available

Practice goals:
- Confirm the reader can define a function with `fn name() { ... }`.
- Confirm the reader can call their own function from `main`.
- Confirm the reader knows a function can be called multiple times.
- Confirm the reader names functions in snake_case.

Problems:
1. Write a program that defines a function `print_menu()` which prints a three-line menu. Then call `print_menu()` twice in `main`.

Expected output:

```text
Today's Menu
1. Ramen
2. Curry rice
Today's Menu
1. Ramen
2. Curry rice
```

Grading criteria:
- Must define `fn print_menu() { ... }`.
- Must call `print_menu();` twice in `main`.
- Don't use function parameters; those are taught next episode.
- The function name must be snake_case, not `printMenu`.
- The function may sit above or below `main`; both are fine.

Hint directions:
1. First write `fn print_menu() { ... }` with the three `println!`s inside.
2. Write `print_menu();` twice in `main`.
3. A call needs `()` and a semicolon after the function name.

Reference answer:

```rust
fn print_menu() {
    println!("Today's Menu");
    println!("1. Ramen");
    println!("2. Curry rice");
}

fn main() {
    print_menu();
    print_menu();
}
```

### Chapter 2, Episode 7: Function Parameters

Status: available

Practice goals:
- Confirm the reader can define a function with parameters.
- Confirm the reader knows function parameters must have type annotations.
- Confirm the reader can call the function with the corresponding values.
- Confirm the reader knows this episode has no return values yet, so the function prints its result directly.

Problems:
1. Write a program that defines a function `print_total(price: i32, count: i32)` which prints the total `price * count`. In `main`, ask the user for the unit price and the quantity, convert them to numbers, then call `print_total(price, count)`.

Sample run:

```text
Please enter the unit price:
30
Please enter the quantity:
4
The total is 120 dollars
```

Grading criteria:
- Must define `fn print_total(price: i32, count: i32)`.
- Both parameters `price` and `count` must have type annotations.
- `print_total` should `println!` directly; don't write a return value — those come next episode.
- `main` must read two inputs, converting them into `price` and `count`.
- The call must be `print_total(price, count);`.
- Don't put all the logic in `main`; this problem practices function parameters.

Hint directions:
1. The parameter format is `name: Type`.
2. You can read `price` and `count` in `main` first.
3. Then pass both values to `print_total(price, count);`.

Reference answer:

```rust
fn print_total(price: i32, count: i32) {
    println!("The total is {} dollars", price * count);
}

fn main() {
    println!("Please enter the unit price:");

    let mut price_input = String::new();
    std::io::stdin().read_line(&mut price_input).expect("failed to read input");

    let price = price_input.trim().parse::<i32>().expect("not a number");

    println!("Please enter the quantity:");

    let mut count_input = String::new();
    std::io::stdin().read_line(&mut count_input).expect("failed to read input");

    let count = count_input.trim().parse::<i32>().expect("not a number");

    print_total(price, count);
}
```

### Chapter 2, Episode 8: Function Return Values

Status: available

Practice goals:
- Confirm the reader can declare a return type with `-> Type`.
- Confirm the reader knows the last line without a semicolon is the return value.
- Confirm the reader can receive a function's return value in `main`.
- Confirm the reader can return multiple values with a tuple.

Problems:
1. Write a function `calculate_total(price: i32, count: i32) -> i32` that returns the total `price * count`. In `main`, ask the user for the unit price and quantity, call the function, and print the total.
2. Write a function `buy_ticket(money: i32, price: i32) -> (i32, i32)` that returns "how many tickets you can buy" and "how much money is left." In `main`, ask the user for the money on hand and the ticket price, then print the result.

Sample runs:

```text
Please enter the unit price:
30
Please enter the quantity:
4
The total is 120 dollars
```

```text
Please enter how much money you have:
230
Please enter the ticket price:
70
You can buy 3 tickets, with 20 dollars left
```

Grading criteria:
- Problem 1's function must return an `i32`; don't `println!` inside the function.
- Problem 1's last line should be `price * count`, with no semicolon.
- Problem 2's return type should be `(i32, i32)`.
- Problem 2 can compute the two values with `money / price` and `money % price`.
- Problem 2 must return a tuple, e.g. `(count, change)`.
- After calling the tuple-returning function, use `.0` and `.1` to take out the results.
- Don't use `return`; early `return` is taught next episode — this episode practices last-line returns.

Hint directions:
1. The return type goes after the parameters: `fn name(...) -> i32`.
2. Don't put a semicolon on the function's last line.
3. To return two values, pack them into a tuple.

Reference answer:

```rust
fn calculate_total(price: i32, count: i32) -> i32 {
    price * count
}

fn main() {
    println!("Please enter the unit price:");

    let mut price_input = String::new();
    std::io::stdin().read_line(&mut price_input).expect("failed to read input");
    let price = price_input.trim().parse::<i32>().expect("not a number");

    println!("Please enter the quantity:");

    let mut count_input = String::new();
    std::io::stdin().read_line(&mut count_input).expect("failed to read input");
    let count = count_input.trim().parse::<i32>().expect("not a number");

    let total = calculate_total(price, count);

    println!("The total is {} dollars", total);
}
```

```rust
fn buy_ticket(money: i32, price: i32) -> (i32, i32) {
    let count = money / price;
    let change = money % price;

    (count, change)
}

fn main() {
    println!("Please enter how much money you have:");

    let mut money_input = String::new();
    std::io::stdin().read_line(&mut money_input).expect("failed to read input");
    let money = money_input.trim().parse::<i32>().expect("not a number");

    println!("Please enter the ticket price:");

    let mut price_input = String::new();
    std::io::stdin().read_line(&mut price_input).expect("failed to read input");
    let price = price_input.trim().parse::<i32>().expect("not a number");

    let result = buy_ticket(money, price);

    println!("You can buy {} tickets, with {} dollars left", result.0, result.1);
}
```

### Chapter 2, Episode 9: Early `return`

Status: available

Practice goals:
- Confirm the reader can use `return value;` to leave a function early.
- Confirm the reader knows `return` takes a semicolon.
- Confirm the reader knows the ordinary last line still uses the semicolon-free natural return.
- Confirm the reader understands what a guard clause is for.

Problems:
1. Write a function `discount_price(price: i32, is_member: bool) -> i32`. If `price <= 0`, the price is invalid — `return 0;` right away. If the price is valid, members get 20% off and non-members pay full price. In `main`, ask the user for a price, call the function with a variable `is_member = true`, and print the discounted price.

Sample run:

```text
Please enter the price:
100
The discounted price is 80 dollars
```

Grading criteria:
- The function must first check `price <= 0` and leave early with `return 0;`.
- `return 0;` needs its semicolon.
- For valid prices, don't `return` all over the place; the end can use the natural return `if is_member { price * 8 / 10 } else { price }`.
- The return type must be `-> i32`.
- No floating-point discounts; integer arithmetic is fine for now.
- Don't introduce `Result` or `Option`; those aren't taught until Chapter 5.

Hint directions:
1. Write the guard clause first: `if price <= 0 { return 0; }`.
2. Then handle the member and non-member prices.
3. An `if` expression can serve directly as the function's last line.

Reference answer:

```rust
fn discount_price(price: i32, is_member: bool) -> i32 {
    if price <= 0 {
        return 0;
    }

    if is_member {
        price * 8 / 10
    } else {
        price
    }
}

fn main() {
    println!("Please enter the price:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let price = input.trim().parse::<i32>().expect("not a number");

    let is_member = true;
    let final_price = discount_price(price, is_member);

    println!("The discounted price is {} dollars", final_price);
}
```

### Chapter 2, Episode 10: Recursion

Status: available

Practice goals:
- Confirm the reader knows a recursive function needs a stopping condition.
- Confirm the reader knows every recursive call must move the problem toward the stopping condition.
- Confirm the reader can keep the "compute a result" and "print the process" flavors of recursion separate.
- Confirm the reader can put "read the input" in `main` and "compute and return the result" in the function.

Problems:
1. Write a function `is_power_of_two(n: i32) -> bool` that checks whether `n` is a power of two. This function only computes and returns the result; don't read stdin or print inside it. Be sure to reject negative numbers and 0: neither is a power of two. In `main`, read an integer, call the function, and print `It's a power of two` or `It's not a power of two`. Use recursion, not loops.
2. Write a function `print_collatz(n: i32)` that prints the Collatz sequence for the input. The rules: if `n` is 1, print 1 and stop; if `n` is even, the next number is `n / 2`; if `n` is odd, the next number is `3 * n + 1`. In `main`, read a positive integer and call the function, printing all the way down to 1 using recursion, not loops.

Sample runs:

```text
Please enter a number:
16
It's a power of two
```

```text
Please enter the starting number:
6
6
3
10
5
16
8
4
2
1
```

Grading criteria:
- `is_power_of_two` must rely only on its parameter `n` to compute and return a `bool`; no stdin reads or printing inside the function.
- `is_power_of_two` must at least handle the cases `n == 1`, `n <= 0`, odd, and even; negatives and 0 should both return `false`.
- `print_collatz` should print the current `n` first, then decide whether to call itself again.
- `print_collatz`'s stopping condition should be `n == 1`.
- Neither problem may use `loop`, `while`, `for`, arrays, or `Vec`.
- This episode practices recursion, not the mathematical fine points of the Collatz conjecture; you may assume the input is a positive integer.

Hint directions:
1. `is_power_of_two(1)` should return `true`.
2. Numbers at or below 0 aren't powers of two.
3. If `n` is odd and isn't 1, it can't be a power of two.
4. If `n` is even, the problem shrinks to checking `n / 2`.
5. The Collatz function can `println!("{}", n);` first, then use `if` to decide which number the next call gets.

Reference answer:

```rust
fn is_power_of_two(n: i32) -> bool {
    if n == 1 {
        true
    } else if n <= 0 {
        false
    } else if n % 2 != 0 {
        false
    } else {
        is_power_of_two(n / 2)
    }
}

fn main() {
    println!("Please enter a number:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let n = input.trim().parse::<i32>().expect("not a number");

    if is_power_of_two(n) {
        println!("It's a power of two");
    } else {
        println!("It's not a power of two");
    }
}
```

```rust
fn print_collatz(n: i32) {
    println!("{}", n);

    if n == 1 {
        return;
    }

    if n % 2 == 0 {
        print_collatz(n / 2);
    } else {
        print_collatz(3 * n + 1);
    }
}

fn main() {
    println!("Please enter the starting number:");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("failed to read input");

    let n = input.trim().parse::<i32>().expect("not a number");

    print_collatz(n);
}
```

### Chapter 2, Episode 11: Array Basics

Status: available

Practice goals:
- Confirm the reader can create a fixed-length array.
- Confirm the reader knows array elements must all have the same type.
- Confirm the reader can print a whole array with `{:?}`.
- Confirm the reader can access array elements by index, and knows indices start at 0.
- Avoid jumping ahead to the next episode's array iteration.

Problems:
1. Write a program that reads three days' temperatures and stores them in an array `temperatures`. Then print the whole array, day 1's temperature, day 3's temperature, and how many degrees days 1 and 3 differ by. The difference can't be negative; use `if` yourself to work out the absolute value. Use indexing for access.

Sample run:

```text
Please enter day 1's temperature:
25
Please enter day 2's temperature:
27
Please enter day 3's temperature:
22
Temperatures for the three days: [25, 27, 22]
Day 1 temperature: 25
Day 3 temperature: 22
Days 1 and 3 differ by 3 degrees
```

Grading criteria:
- The three temperatures must go into an array, e.g. `let temperatures = [day1, day2, day3];`.
- The whole array must be printed with `{:?}`, not `{}`.
- Day 1 must be `temperatures[0]`, day 3 `temperatures[2]`.
- The difference can't be negative; use `if` to determine which is bigger before subtracting.
- Don't call a ready-made absolute-value function; this practices the `if` and operators learned so far.
- Don't use `for x in temperatures`; array iteration is taught next episode.
- Don't have the reader input an index and access with it; that pulls in `usize` conversions and blurs the focus.

Hint directions:
1. Read `day1`, `day2`, `day3` separately first.
2. Then put the three variables into an array: `[day1, day2, day3]`.
3. Print the whole array with `{:?}`.
4. The array's first element has index 0.

Reference answer:

```rust
fn main() {
    println!("Please enter day 1's temperature:");

    let mut day1_input = String::new();
    std::io::stdin().read_line(&mut day1_input).expect("failed to read input");
    let day1 = day1_input.trim().parse::<i32>().expect("not a number");

    println!("Please enter day 2's temperature:");

    let mut day2_input = String::new();
    std::io::stdin().read_line(&mut day2_input).expect("failed to read input");
    let day2 = day2_input.trim().parse::<i32>().expect("not a number");

    println!("Please enter day 3's temperature:");

    let mut day3_input = String::new();
    std::io::stdin().read_line(&mut day3_input).expect("failed to read input");
    let day3 = day3_input.trim().parse::<i32>().expect("not a number");

    let temperatures = [day1, day2, day3];

    println!("Temperatures for the three days: {:?}", temperatures);
    println!("Day 1 temperature: {}", temperatures[0]);
    println!("Day 3 temperature: {}", temperatures[2]);
    let difference = if temperatures[2] >= temperatures[0] {
        temperatures[2] - temperatures[0]
    } else {
        temperatures[0] - temperatures[2]
    };

    println!("Days 1 and 3 differ by {} degrees", difference);
}
```

### Chapter 2, Episode 12: Iterating over Arrays

Status: available

Practice goals:
- Confirm the reader can iterate over an array with `for x in arr`.
- Confirm the reader can process each element while iterating.
- Confirm the reader can use a mutable variable as an accumulator.
- Confirm the reader can tell "filling the array by index" apart from "iterating over the elements directly."

Problems:
1. Write a program that first creates a mutable array `expenses` holding five `0`s. Then use `for i in 0..5` to read 5 expenses for the day, storing each into `expenses[i]`. Once input is done, iterate with `for expense in expenses`, printing each expense. If an expense is 100 or more, additionally print `That one's on the high side`. Finally, print the total.

Sample run:

```text
Please enter expense No. 1:
80
Please enter expense No. 2:
120
Please enter expense No. 3:
45
Please enter expense No. 4:
200
Please enter expense No. 5:
60
Expense: 80 dollars
Expense: 120 dollars
That one's on the high side
Expense: 45 dollars
Expense: 200 dollars
That one's on the high side
Expense: 60 dollars
Total expenses: 505 dollars
```

Grading criteria:
- A mutable array must be created first, e.g. `let mut expenses = [0; 5];`.
- Input can be read with `for i in 0..5`, storing each expense into `expenses[i]`.
- The processing pass must use `for expense in expenses` to iterate over the array.
- An accumulator like `let mut total = 0;` must be set up.
- Each pass must add `expense` into `total`.
- The high-expense check can be `if expense >= 100`.
- Don't compute the total with index iteration, e.g. `for i in 0..5 { total += expenses[i]; }`; this episode's star is `for expense in expenses`.
- Don't use `len()`, slices, or `Vec`.

Hint directions:
1. Start with `let mut expenses = [0; 5];`.
2. Read input with `for i in 0..5`; the prompt can print `i + 1`.
3. Store each number into `expenses[i]`.
4. Prepare `let mut total = 0;` before the iteration pass.
5. Inside `for expense in expenses`, print the expense, check whether it's 100 or more, and add it to the total.

Reference answer:

```rust
fn main() {
    let mut expenses = [0; 5];

    for i in 0..5 {
        println!("Please enter expense No. {}:", i + 1);

        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("failed to read input");

        let expense = input.trim().parse::<i32>().expect("not a number");
        expenses[i] = expense;
    }

    let mut total = 0;

    for expense in expenses {
        println!("Expense: {} dollars", expense);

        if expense >= 100 {
            println!("That one's on the high side");
        }

        total += expense;
    }

    println!("Total expenses: {} dollars", total);
}
```

### Chapter 2, Episode 13: Slices: `&[T]`

Status: no problems

Reason for no problems:
- This episode is about slice syntax, range bounds, taking the `&` on faith for now, and slices not copying data.
- Problems here easily become the text's examples with a different array and range — little practice value.
- Asking the reader to input ranges themselves drags in index types, out-of-bounds handling, and borrowing details, pulling the focus away.
- Slices are better practiced together in the next episode, "Slices as Parameters."

### Chapter 2, Episode 14: Slices as Parameters

Status: available

Practice goals:
- Confirm the reader can write a function parameter as `&[i32]`.
- Confirm the reader knows a call can pass a slice of the whole array, e.g. `&steps`.
- Confirm the reader knows a call can also pass part of the array, e.g. `&steps[..5]` and `&steps[5..]`.
- Confirm the reader can iterate over the slice inside the function, totaling with an accumulator.
- Confirm the reader understands one function can handle data of different lengths.

Problems:
1. Write a function `total_steps(steps: &[i32]) -> i32` that returns the sum of all the step counts in the slice. In `main`, have the user enter 7 days of step counts, stored in an array `steps`. The goal is 8000 steps per day, so the whole-week threshold is `7 * 8000`, the weekday threshold `5 * 8000`, and the weekend threshold `2 * 8000`. Use `total_steps(&steps)`, `total_steps(&steps[..5])`, and `total_steps(&steps[5..])` to compute the totals for the whole week, the weekdays, and the weekend, printing each total along with whether the goal was met.

Sample run:

```text
Please enter the step count for day 1:
9000
Please enter the step count for day 2:
7500
Please enter the step count for day 3:
8200
Please enter the step count for day 4:
6000
Please enter the step count for day 5:
10000
Please enter the step count for day 6:
3000
Please enter the step count for day 7:
12000
Whole week total: 55700 steps, goal not met
Weekday total: 40700 steps, goal met
Weekend total: 15000 steps, goal not met
```

Grading criteria:
- The parameter must be written as `steps: &[i32]`, not as a fixed-length array `[i32; 7]`.
- `total_steps` must iterate over the slice with `for step in steps`, accumulating with `total += step` — the same spelling as this episode's `sum` in the text.
- The goal checks must live in `main`, comparing the totals the function returns (plain `i32`s).
- Do **not** move the goal check into the function as `step >= 8000`: the `step` you get from `for step in steps` is a reference to the element, and comparing it to a number directly is a compile error; the `*` that would fix it isn't taught until Chapter 4. If the reader writes this and gets stuck, steer them toward moving the check back into `main` and comparing totals instead.
- The whole-week call must pass `&steps`; the weekday call `&steps[..5]` (days 1 through 5); the weekend call `&steps[5..]` (days 6 and 7).
- The thresholds may be written as `7 * 8000`, `5 * 8000`, `2 * 8000`, or directly as `56000`, `40000`, `16000`; the multiplication spelling shows the intent better.
- The goal verdict may be printed with an ordinary `if ... else ...`, or by picking the text first with the `if` expression from Chapter 1, Episode 27; both are fine.
- Don't write separate functions for the week, weekdays, and weekend; the point is that one slice-parameter function accepts data of different lengths.
- Don't use `Vec`, `.len()`, or Iterator methods.

Hint directions:
1. Start with `fn total_steps(steps: &[i32]) -> i32`, preparing `let mut total = 0;` inside.
2. Iterate over each day's steps with `for step in steps`, adding each into the total with `total += step` — just like this episode's `sum` in the text.
3. In `main`, a mutable array `[0; 7]` plus `for i in 0..7` can read the 7 days of steps.
4. The whole-week threshold is `7 * 8000`, so `if week_total >= 7 * 8000` can make the call; the weekdays and the weekend work the same way.

Reference answer:

```rust
fn total_steps(steps: &[i32]) -> i32 {
    let mut total = 0;

    for step in steps {
        total += step;
    }

    total
}

fn main() {
    let mut steps = [0; 7];

    for i in 0..7 {
        println!("Please enter the step count for day {}:", i + 1);

        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("failed to read input");

        let step = input.trim().parse::<i32>().expect("not a number");
        steps[i] = step;
    }

    let week_total = total_steps(&steps);
    let weekday_total = total_steps(&steps[..5]);
    let weekend_total = total_steps(&steps[5..]);

    let week_verdict = if week_total >= 7 * 8000 { "goal met" } else { "goal not met" };
    println!("Whole week total: {} steps, {}", week_total, week_verdict);

    let weekday_verdict = if weekday_total >= 5 * 8000 { "goal met" } else { "goal not met" };
    println!("Weekday total: {} steps, {}", weekday_total, weekday_verdict);

    let weekend_verdict = if weekend_total >= 2 * 8000 { "goal met" } else { "goal not met" };
    println!("Weekend total: {} steps, {}", weekend_total, weekend_verdict);
}
```

### Chapter 2, Episode 15: String Slices: `&str`

Status: available

Practice goals:
- Confirm the reader knows a string literal can be used as a `&str`.
- Confirm the reader can write a function parameter as `&str`.
- Confirm the reader can pass slices of an English string into a function.
- Confirm the reader knows not to slice non-ASCII strings casually.

Problems:
1. Write a function `print_ticket(name: &str, from: &str, to: &str)` that prints the passenger's name, departure station, and arrival station. In `main`, declare `let route = "TPE-TNN";`, take the departure station `TPE` with `&route[0..3]`, and the arrival station `TNN` with `&route[4..7]`. Finally, print ticket information for both `"Andy"` and `"小明"`.

Expected output:

```text
Passenger: Andy
From: TPE
To: TNN
Passenger: 小明
From: TPE
To: TNN
```

Grading criteria:
- The parameters must be written as `name: &str`, `from: &str`, `to: &str`.
- `route` can be written as `let route = "TPE-TNN";`.
- The departure station must use `&route[0..3]`, the arrival station `&route[4..7]`.
- `route` is all English letters and symbols, so byte-index slicing is safe here.
- Both `"Andy"` and `"小明"` can be passed directly to `name: &str`.
- Don't slice `"小明"` — Chinese characters aren't 1 byte each, and slicing at the wrong position panics.
- Don't introduce `String`; this episode practices `&str`.

Hint directions:
1. Start with `fn print_ticket(name: &str, from: &str, to: &str)`.
2. Use three `println!`s inside the function for the passenger, departure, and arrival.
3. In `main`, slice `from` and `to` out of `route`.
4. A call can look like `print_ticket("Andy", from, to);`.

Reference answer:

```rust
fn print_ticket(name: &str, from: &str, to: &str) {
    println!("Passenger: {}", name);
    println!("From: {}", from);
    println!("To: {}", to);
}

fn main() {
    let route = "TPE-TNN";
    let from = &route[0..3];
    let to = &route[4..7];

    print_ticket("Andy", from, to);
    print_ticket("小明", from, to);
}
```
