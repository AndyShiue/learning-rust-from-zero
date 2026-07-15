# `Vec` and Ownership

## Goal of This Episode

Understand `Vec`'s ownership behavior, and its symmetry with `String` / `&str`.

## Concept

### `Vec` and `String` Are a Pair

In recent episodes we learned the relationship between `String` and `&str`:

| Owned version | Borrowed version |
|---|---|
| `String` | `&str` |

`Vec` has exactly the same correspondence:

| Owned version | Borrowed version |
|---|---|
| `Vec` | `&[T]` (a slice) |

A `String` owns a piece of text; an `&str` borrows a piece of text. A `Vec` owns a set of elements; an `&[T]` borrows a set of elements. **Perfectly symmetric concepts.**

### `Vec` Moves

A `Vec`'s data lives mainly on the heap, so it's not `Copy`. Assignment and passing into functions both move:

```rust,noplayground
# fn main() {
    let v1 = vec![1, 2, 3];
    let v2 = v1; // Move! v1 can't be used anymore
# }
```

Exactly like `String`.

### Use Slices `&[T]` for Function Parameters

Same advice as with `String` / `&str` — if a function only needs to read the contents of a `Vec` of `i32`, use a slice `&[i32]`:

```rust,editable
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn main() {
    let v = vec![1, 2, 3, 4, 5];
    let total = sum(&v); // &Vec of i32 auto-converts to &[i32]
    println!("Total: {}", total);
    println!("v is still here: {:?}", v);
}
```

Just as `&String` auto-converts to `&str`, an `&Vec` of `i32` auto-converts to `&[i32]`.

### `for` Loops and Ownership

This point matters a lot: when a `for` loop iterates a `Vec`, you choose between move and borrow:

**`for x in v` — move!**

```rust,editable
fn main() {
    let v = vec![1, 2, 3];
    for x in v {
        println!("{}", x);
    }
    // v was moved away; it can't be used anymore!
}
```

`for x in v` consumes the whole `Vec`. After the loop, `v` no longer exists.

**`for x in &v` — borrow!**

```rust,editable
fn main() {
    let v = vec![1, 2, 3];
    for x in &v {
        println!("{}", x); // x has type &i32
    }
    println!("v is still here: {:?}", v); // OK!
}
```

`for x in &v` merely borrows; `v` isn't consumed.

One detail matters here: `x` is not an `i32`; it is a reference, with type `&i32`. Because the loop iterates over the borrowed `&v`, each element it receives is borrowed too, rather than moved out of the `Vec`. Similarly, the earlier function parameter `nums: &[i32]` is already a borrowed slice, so the `x` in `for x in nums` is also an `&i32`.

Most of the time you should use `for x in &v`, unless you're certain you won't need the `Vec` again.

## Example Code

```rust,editable
// Slice parameters: &Vec of i32 auto-converts to &[i32]
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn print_all(nums: &[i32]) {
    let mut first = true;
    for x in nums {
        if first {
            first = false;
        } else {
            print!(", ");
        }
        print!("{}", x);
    }
    println!();
}

fn main() {
    // Vec moves
    let v1 = vec![10, 20, 30];
    let v2 = v1.clone(); // clone keeps v1
    println!("v1 = {:?}", v1);
    println!("v2 = {:?}", v2);

    // Functions with slice parameters (borrowing)
    let scores = vec![85, 92, 78, 95, 88];
    println!("Total = {}", sum(&scores));
    print_all(&scores);
    println!("scores is still here: {:?}", scores);

    // Slice operations
    let slice = &scores[1..4]; // Borrowing a part
    println!("The middle three: {:?}", slice);
    println!("Total of the middle three = {}", sum(slice));

    // for x in &v: borrowing iteration
    println!("Listing one by one (borrowed):");
    for s in &scores {
        println!("  {}", s);
    }
    println!("scores is still here: {:?}", scores);

    // for x in v: moving iteration (gone after use)
    let temp = vec![1, 2, 3];
    println!("Consuming iteration:");
    for x in temp {
        println!("  {}", x);
    }
    // temp has been moved; the line below would be a compile error:
    // println!("{:?}", temp);

    // The symmetry, summarized
    // String  ↔ &str     (own ↔ borrow, text)
    // Vec     ↔ &[T]     (own ↔ borrow, a set of values)
    println!("--- The symmetry ---");
    let s = String::from("hello");
    let s_ref: &str = &s; // &String → &str
    println!("String: {}, &str: {}", s, s_ref);

    let v = vec![1, 2, 3];
    let v_ref: &[i32] = &v; // & of i32 → &[i32]
    println!("Vec: {:?}, slice: {:?}", v, v_ref);
}
```

## How Do You Write the Type of "a `Vec` of `i32`"?

Throughout this episode we kept saying "a `Vec` of `i32`" — but you may have noticed the code never once spelled that type out. Variable types were all inferred by Rust, and function parameters only used the slice `&[i32]`. What if you someday need to write it by hand (say, as a parameter or return type)? And what exactly can that `T` in `&[T]` from the table above be? Both questions have the same answer — and the next chapter spends a great deal of time on it.

## Recap

- **`Vec` and `String` have perfectly symmetric ownership behavior**: both keep their data mainly on the heap, both move, both can `clone`.
- `String` ↔ `&str` mirrors `Vec` ↔ `&[T]` (own ↔ borrow).
- `&Vec` auto-converts to `&[T]` (just like `&String` to `&str`).
- Prefer slice parameters `&[T]` over `&Vec`.
- `for x in v`: **move** — consumes the whole `Vec`.
- `for x in &v`: **borrow** — the `Vec` survives; in this example, `x` is a reference with type `&i32`.
- Mostly use `for x in &v`, unless you're sure you're done with the `Vec`.
- We never wrote out the type of "a `Vec` of `i32`" by hand — how to write it, and what the `T` in `&[T]` is, gets revealed next chapter.

Congratulations on finishing Chapter 4! 🎉 In this chapter you learned Rust's most central concepts — ownership, moves, `clone`, `Copy`, borrowing — plus `String` and `Vec`, the two most commonly used non-`Copy` types. These concepts are Rust's biggest departure from other languages, and the key to how Rust guarantees memory safety without sacrificing performance. Next chapter, we move into generics, `trait` bounds, and lifetimes — letting your code handle arbitrary types while staying type-safe!
