# The Stack and the Heap

## Goal of This Episode

Understand the difference between the stack and the heap, and unveil what Episode 1's keychain analogy really meant.

## Concept

### Two Common Places in Memory

While a program runs, its data lives in memory. For now, let's look at two common places where data can be stored: the stack and the heap.

**The stack**:

- When a function is called, the stack is commonly used to store local variables whose sizes are known at compile time.
- The types we've learned so far — integers, floats, booleans, `char`s, fixed-length arrays, tuples, and `struct`s containing only these kinds of data — are commonly stored directly on the stack when used as local variables.
- Data whose size is known at compile time is not necessarily small; what matters is that the compiler already knows how much space it needs.
- When the function ends, the stack space used by that call is reclaimed together.

**The heap**:

- A program can request additional heap space as needed while it runs.
- Data is often stored separately on the heap when its amount is known only at runtime or may grow while the program runs. For example, if a program needs to store every number a user enters, it may not know beforehand how many there will be.
- The program remembers how to find the data stored there later.
- Rust's ownership system determines when that space can be returned.

### The Keychain Analogy, Unveiled!

Remember Episode 1's keychain analogy? Time to reveal what it really meant:

- **The key** = the information that lets the program find the safe later.
- **The safe** = data stored separately on the heap.
- **The charms on the keychain** = data carried directly on the keychain.

So when we said "a move is handing over the keychain":

- The key and the charms are handed to the new owner together.
- The safe itself stays where it is; it doesn't need to be moved or recreated.

### Why Are Integers `Copy`?

Integers (`i32` and so on) are like the charms on the keychain. Copying an integer is a simple, mechanical operation, so integers implement `Copy`.

Some types are also responsible for managing data stored separately on the heap, so they can't be copied automatically in the same way. Assigning such a value moves it; creating a clone requires an explicit `.clone()`. The next few episodes will show concrete examples.

## Example Code

```rust,editable
#[derive(Debug, Copy, Clone)]
struct StackData {
    x: i32,
    y: i32,
    active: bool,
}

fn main() {
    // These local variables have sizes known at compile time, so they can be stored directly on the stack
    let a = 42;    // i32, 4 bytes
    let b = 3.14;  // f64, 8 bytes
    let c = true;  // bool, 1 byte
    let ch = '🦀'; // char, 4 bytes
    println!("Integer: {}, float: {}, boolean: {}, character: {}", a, b, c, ch);

    // The struct stores all its fields directly, so it can be stored on the stack too
    let data = StackData { x: 10, y: 20, active: true };
    let data2 = data; // Copy! data stays usable
    println!("data = {:?}", data);
    println!("data2 = {:?}", data2);

    // A fixed-length array can be stored directly on the stack too
    let arr = [1, 2, 3, 4, 5];
    println!("Array: {:?}", arr);

    // A tuple can be stored directly on the stack too
    let t = (42, true, 'A');
    println!("tuple: {:?}", t);
}
```

## Recap

- **Stack**: local variables whose sizes are known at compile time — such as integers, fixed-length arrays, tuples, and `struct`s made from these kinds of data — are commonly stored directly here; the space used by a function call is reclaimed when the function ends.
- **Heap**: commonly stores data whose amount is known only at runtime or may grow; the program remembers how to find the data stored there.
- Keychain analogy unveiled: key = the information used to find the data, safe = separately stored heap data, charms = directly carried data.
- Integers implement `Copy` because copying them is a simple, mechanical operation.
- Types that manage separately stored heap data move on assignment; creating a clone requires an explicit `.clone()`.
