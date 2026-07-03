# Destructuring in `for` Loops

## Goal of This Episode

Learn to destructure tuples or `struct`s directly in the variable position of a `for` loop.

## Concept

We've already seen `let` destructure tuples and `struct`s. It turns out the variable position of a `for` loop can too — just write the same destructuring syntax right there.

Iterating over an array of tuples:

```rust,editable
fn main() {
    let pairs = [(1, "one"), (2, "two"), (3, "three")];

    for (num, name) in pairs {
        println!("{} = {}", num, name);
    }
}
```

`(num, name)` is the pattern. Each element of the array is a tuple, and the loop splits it into `num` and `name`.

Iterating over `struct`s works the same way:

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let points = [
        Point { x: 0, y: 0 },
        Point { x: 1, y: 2 },
        Point { x: 3, y: 4 },
    ];

    for Point { x, y } in points {
        println!("({}, {})", x, y);
    }
}
```

Think of it as `let` destructuring combined with a `for` loop: each time the loop takes out an element, it splits it apart with `let`-destructuring syntax.

## Example Code

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    // Iterate over a tuple array, destructuring
    let scores = [("Alice", 85), ("Bob", 92), ("Carol", 78)];
    for (name, score) in scores {
        println!("{}: {}", name, score);
    }

    // Iterate over a struct array, destructuring
    let points = [
        Point { x: 0, y: 0 },
        Point { x: 3, y: 4 },
        Point { x: -1, y: 2 },
    ];
    for Point { x, y } in points {
        println!("({}, {})", x, y);
    }

    // Use .. to ignore unwanted fields
    let more_points = [
        Point { x: 1, y: 10 },
        Point { x: 2, y: 20 },
    ];
    for Point { x, .. } in more_points {
        println!("x = {}", x);
    }
}
```

## Recap

- The variable position of a `for` loop accepts destructuring patterns directly.
- Iterating over an array of tuples: `for (a, b) in pairs`.
- Iterating over an array of `struct`s: `for Point { x, y } in points`.
