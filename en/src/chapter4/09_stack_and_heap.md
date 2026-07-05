# The Stack and the Heap

## Goal of This Episode

Understand the difference between the stack and the heap, and unveil what Episode 1's keychain analogy really meant.

## Concept

### The Two Regions of Memory

While a program runs, its data lives in memory. Memory has two main regions:

**The stack**:

- Fast.
- Sizes are determined at compile time.
- Function-local variables, integers, floats, booleans, and `char`s live here.
- When a function ends, these variables are cleaned up automatically.

**The heap**:

- Slower, but more flexible.
- Sizes can be decided while the program runs (e.g. a piece of text — you don't know how much the user will type).
- Requires manual management (in other languages), or automatic management via the ownership system (in Rust).

### The Keychain Analogy, Unveiled!

Remember Episode 1's keychain analogy? Time to reveal what it really meant:

- **The charms on the keychain** = data on the stack (small and fixed, traveling with the keychain).
- **The safe** = data on the heap (large and flexible, stored elsewhere).
- **The key** = a pointer, recording where in memory the safe sits.

So when we said "a move is handing over the keychain":

- If the keychain carries only charms (stack data), handing it over is cheap — you can even duplicate it outright (that's `Copy`!)
- If the keychain carries a key (a pointer), what's handed over is the pointer; the safe (heap data) is never copied.

### Why Are Integers `Copy`?

Now it should click: integers (`i32` etc.) are like the little charms on the keychain — entirely on the stack, tiny, zero-cost to copy. So Rust makes them `Copy` automatically.

Types like `String` (coming soon) keep their data on the heap. Replicating that freely would mean replicating everything in the safe — expensive. So Rust uses moves, and full replication requires an explicit `.clone()`.

## Example Code

```rust,editable
#[derive(Debug, Copy, Clone)]
struct StackData {
    x: i32,
    y: i32,
    active: bool,
}

fn main() {
    // All of these live on the stack
    let a = 42;    // i32, 4 bytes, stack
    let b = 3.14;  // f64, 8 bytes, stack
    let c = true;  // bool, 1 byte, stack
    let ch = '🦀'; // char, 4 bytes, stack
    println!("Integer: {}, float: {}, boolean: {}, character: {}", a, b, c, ch);

    // The struct holds nothing but stack data, so the whole struct is on the stack too
    let data = StackData { x: 10, y: 20, active: true };
    let data2 = data; // Copy! data stays usable
    println!("data = {:?}", data);
    println!("data2 = {:?}", data2);

    // Arrays live on the stack too (fixed size)
    let arr = [1, 2, 3, 4, 5];
    println!("Array: {:?}", arr);

    // Tuples as well
    let t = (42, true, 'A');
    println!("tuple: {:?}", t);

    // Later we'll learn String and Vec, whose data lives on the heap
    // That's when moves and borrowing really show their importance!
}
```

## Recap

- **Stack**: fast, fixed sizes. Integers, floats, booleans, `char`s, and small `struct`s live here.
- **Heap**: flexible, variable sizes. Large or dynamically sized data goes here.
- Keychain analogy unveiled: charms = stack data, safe = heap data, key = pointer.
- Integers are `Copy` because they live entirely on the stack — copying costs practically nothing.
- Heap data moves by default (only the key is transferred); for types like `String`, `clone` ensures safety by basically replicating the safe's entire contents.
