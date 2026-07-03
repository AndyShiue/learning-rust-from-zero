# `loop` + `break`

## Goal of This Episode

Create an infinite loop with `loop`, then use `break` to jump out at the right moment.

## Main Text

Up to now, our programs run once and end. But what if something needs to be done repeatedly? Like a countdown: 5, 4, 3, 2, 1, liftoff!

That calls for a **loop**.

### `loop` — the Infinite Loop

`loop` just keeps running and running, forever:

```rust,no_run
fn main() {
    loop {
        println!("I can't stooooop");
    }
}
```

If you actually run this program, it will print and print and print... You'll have to force-stop it with `Ctrl + C`.

So we need an "exit."

### `break` — Jumping Out of the Loop

```rust,editable
fn main() {
    let mut count = 5;
    loop {
        if count == 0 {
            println!("Liftoff!");
            break;
        }
        println!("{}", count);
        count -= 1;
    }
}
```

### How Does It Work?

1. `count` starts at 5.
2. Enter the `loop`. First check: is `count == 0`? No, so print 5, then `count -= 1` makes count 4.
3. Back to the top of the `loop`. Is `count == 0`? No, print 4, count becomes 3.
4. ...and so on...
5. When `count` reaches 0, `if count == 0` holds: print "Liftoff!", then `break` out of the loop.
6. The program ends.

## Recap

- `loop` repeats the code inside the curly braces forever.
- `break` jumps out of the loop so the program can continue on.
- A `loop` without a `break` is an infinite loop — remember to have an exit.
