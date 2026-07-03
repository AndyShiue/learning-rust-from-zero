# `Box<T>`

## Goal of This Episode

Learn to put data on the heap with `Box<T>`, and understand why it's necessary for recursive types.

## Concept

Remember Chapter 4's safe analogy? A key hangs on the keychain, the key opens a safe, and the safe holds the real goods.

`Box<T>` is that safe — it puts the data on the heap, leaving a key (a pointer) on the stack.

### Why Do We Need `Box`?

Most of the time, Rust putting data straight on the stack is fine. But two situations call for `Box`:

**1. The data is too big**

If a `struct` has many fields and takes lots of space, the stack may not be a great place for it (stack space is limited). `Box` moves it to the heap, leaving just a pointer on the stack.

**2. Recursive types**

The more important reason. Suppose you want to define a linked list:

```rust,compile_fail
enum List {
    Node(i32, List), // Compile error!
    Empty,
}
#
# fn main() {}
```

Rust needs to know every type's size at compile time. But here's the problem: to know `List`'s size, you need to know how big `Node` is. `Node` holds an `i32` and a `List` — so you need `List`'s size. But `List` contains another `List`...

Expanding it: `List`'s size = `i32` + `List`'s size = `i32` + `i32` + `List`'s size = ... it never terminates. The compiler flat-out errors: "recursive type has infinite size."

The fix is `Box`:

```rust,noplayground
enum List {
    Node(i32, Box<List>),
    Empty,
}
#
# fn main() {}
```

`Box<List>` has a fixed size (a pointer's size), and the problem is solved.

### Using a `Box`

```rust,editable
fn main() {
    let x = Box::new(42);
    println!("{}", x); // Usable directly; Rust fetches the inner value automatically
}
```

`Box::new(value)` moves the value onto the heap. The `Box` owns its contents and releases them automatically at scope exit (since `Box` implements `Drop`).

## Example Code

```rust,editable
// A recursive type via Box: a linked list
enum List {
    Node(i32, Box<List>),
    Empty,
}

// Printing the list
fn print_list(list: &List) {
    match list {
        List::Node(value, next) => {
            print!("{} -> ", value);
            print_list(next);
        }
        List::Empty => {
            println!("end");
        }
    }
}

fn main() {
    // Basic Box usage
    let x = Box::new(42);
    println!("The value in the Box: {}", x);

    // Building a linked list step by step: 3 -> 2 -> 1 -> end
    // Starting from the tail
    let list = List::Empty;                   // end
    let list = List::Node(1, Box::new(list)); // 1 -> end
    let list = List::Node(2, Box::new(list)); // 2 -> 1 -> end
    let list = List::Node(3, Box::new(list)); // 3 -> 2 -> 1 -> end

    print_list(&list);

    // A Box is the sole owner — the key isn't Copy, so let b = a is a move
    let a = Box::new(String::from("hello"));
    let b = a; // The key passes from a to b, leaving a empty
    // println!("{}", a); // Compile error! a has been moved
    println!("{}", b);
}
```

## Recap

- `Box<T>` puts data on the heap, leaving only a pointer on the stack (the "key" from the safe analogy).
- Its most important use: **recursive types** (like linked lists) need `Box` to break the infinite-size problem.
- `Box::new(value)` creates the `Box`; it's released automatically at scope exit.
- A `Box` is the sole owner; its move semantics match every other non-`Copy` type.
