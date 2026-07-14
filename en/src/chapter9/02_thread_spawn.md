# `thread::spawn`

## Goal of This Episode

Learn to create `Thread`s, letting a program do several things at once.

## Concept

Until now, our programs have had a single flow of execution, doing one thing at a time. But sometimes you want a program doing several things **at once** — downloading a file while updating a progress bar, say. That's what **`Thread`s** are for.

### Creating a `Thread`

`std::thread::spawn` takes a closure and runs it on a new `Thread`:

```rust,editable
use std::thread;

fn main() {
    thread::spawn(|| {
        println!("I'm on another thread!");
    });
}
```

### No `join`, No Survival

Something important: when the `main` function ends, the whole program ends — whether or not other `Thread`s have finished.

```rust,editable
use std::thread;

fn main() {
    thread::spawn(|| {
        for i in 0..10 {
            println!("Child thread: {}", i);
        }
    });

    println!("main is done");
    // The child thread may have printed only part — or nothing at all
}
```

### `JoinHandle`

`thread::spawn` returns a `JoinHandle`. Calling `.join()` waits for that `Thread` to finish:

```rust,editable
use std::thread;

fn main() {
    let handle = thread::spawn(|| {
        for i in 0..5 {
            println!("Child thread: {}", i);
        }
    });

    handle.join().expect("thread panicked"); // Wait for the child thread
    println!("All done");
}
```

`.join()` isn't only waiting — it also retrieves the closure's return value. Whatever the closure returns, `.join().expect("thread panicked")` receives:

```rust,editable
use std::thread;

fn main() {
    let handle = thread::spawn(|| {
        let answer = 21 * 2;
        answer // The closure's return value
    });

    let result = handle.join().expect("thread panicked");
    println!("The result received from the other thread: {}", result); // 42
}
```

The simplest way to pass a computation result back from another `Thread`.

### `move` Closures

Using outside variables in the closure generally requires `move`:

```rust,compile_fail
use std::thread;

fn main() {
    let name = String::from("Rust");

    let handle = thread::spawn(move || {
        println!("Hello, {}!", name);
    });

    println!("{}", name); // Compile error! name was moved into the closure

    handle.join().expect("thread panicked");
}
```

Why is `move` needed? Because the new `Thread` may outlive the function that called `spawn`. If the closure merely borrowed `name`, and that function ended first, discarding `name`, the closure would be left holding a dangling reference. With `move`, `name`'s ownership travels into the closure, and however the original scope ends, the closure keeps its `name`.

### Interleaved Output

When several `Thread`s run at once, their output interleaves — differently on each run, perhaps:

```rust,editable
use std::thread;

fn main() {
    let h1 = thread::spawn(|| {
        for _ in 0..5 {
            println!("AAA");
        }
    });

    let h2 = thread::spawn(|| {
        for _ in 0..5 {
            println!("BBB");
        }
    });

    h1.join().expect("thread panicked");
    h2.join().expect("thread panicked");
}
```

Run it a few times and you'll see AAA and BBB in varying orders. That's the nature of multithreading — execution order is nondeterministic.

## Example Code

```rust,editable
use std::thread;

fn main() {
    let data = vec![1, 2, 3, 4, 5];

    let handle = thread::spawn(move || {
        let sum: i32 = data.iter().sum();
        println!("The sum the child thread computed: {}", sum);
        sum
    });

    // data has been moved; unusable here
    // println!("{:?}", data); // Compile error

    let result = handle.join().expect("thread panicked");
    println!("The main thread received the result: {}", result);
}
```

## Recap

- `thread::spawn(|| { ... })` creates a new `Thread`.
- All `Thread`s die when `main` ends; wait for a `Thread` with `.join()`.
- `.join()` also retrieves the closure's return value — the simplest way to pass results back.
- Closures using outside variables generally need `move`, since the new `Thread`'s lifespan is uncertain.
- Execution order across `Thread`s is nondeterministic; output may interleave.
