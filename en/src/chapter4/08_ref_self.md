# `self` vs `&self` vs `&mut self`

## Goal of This Episode

Learn to choose between `self`, `&self`, and `&mut self` in methods, and how to pick `T` / `&T` / `&mut T` for function parameters.

## Concept

### Recap: Chapter 3's `self`

In Chapter 3 we learned `impl` and methods, where every method took `self` by value:

```rust,noplayground
# struct Cat;
#
impl Cat {
    fn meow(self) {
        println!("Meow~");
    }
}
#
# fn main() {}
```

But taking `self` by value **consumes** the value — after the call, the original variable can't be used anymore (it was moved).

Now that we know borrowing, we can be smarter!

### The Three Kinds of `self`

| Form | Meaning | Effect |
|---|---|---|
| `self` | Takes ownership | After the call, the original variable is unusable (move) |
| `&self` | Read-only borrow of itself | The original stays usable afterward, but the borrow can't modify |
| `&mut self` | Mutable borrow of itself | The original stays usable afterward, and the borrow can modify |

### How to Choose?

- **Just reading data** → use `&self` (the most common!)
- **Modifying your own fields** → use `&mut self`.
- **Transferring ownership (original unusable after the call)** → use `self`.

Most methods use `&self`, because you usually just want to "look at this thing's state" without consuming it.

### A Real Example: `Clone`

A great example is the `Clone` `trait`. Its simplified definition looks like this:

```rust,editable
trait Clone {
    fn clone(&self) -> Self;
}

fn main() {}
```

`clone` takes `&self` — merely borrowing itself, not consuming — then returns a new `Self` (capital `Self`, taught in Chapter 3's last episode: the type implementing this `trait`). This explains why you can call `.clone()` on the same variable over and over — `clone` only borrows, never moving the original value.

If clone's signature were `fn clone(self) -> Self`, every `clone` would consume the original — defeating the whole point of `clone`.

### Function Parameters Follow the Same Logic

It's not just methods' `self` — ordinary function parameters follow the same logic:

| Parameter type | Meaning |
|---|---|
| `p: Point` | Takes ownership (move) |
| `p: &Point` | Read-only borrow |
| `p: &mut Point` | Mutable borrow |

Same selection principle:

- Read only → `&T`.
- Modify → `&mut T`.
- Consume → `T`.

## Example Code

```rust,editable
#[derive(Debug)]
struct Counter {
    id: i32,
    count: i32,
}

impl Counter {
    // Associated function: create a new Counter
    fn new(id: i32) -> Self {
        Counter { id, count: 0 }
    }

    // &self: read-only
    fn get_count(&self) -> i32 {
        self.count
    }

    // &self: read-only, printing info
    fn display(&self) {
        println!("Counter {}: current count = {}", self.id, self.count);
    }

    // &mut self: mutable borrow, modifying count
    fn increment(&mut self) {
        self.count += 1;
    }

    // self: takes ownership, returning the final result
    fn finish(self) -> i32 {
        println!("Counter {} finished! Final count = {}", self.id, self.count);
        self.count
    }
}

// Ordinary functions follow the same logic
fn print_counter(c: &Counter) {
    println!("(Function version) Counter {}: {}", c.id, c.count);
}

fn reset_counter(c: &mut Counter) {
    c.count = 0;
}

fn main() {
    let mut c = Counter::new(1);

    // &self: read-only
    c.display();
    println!("Currently: {}", c.get_count());

    // &mut self: modifying
    c.increment();
    c.increment();
    c.increment();
    c.display();

    // &T and &mut T with ordinary functions
    print_counter(&c);
    reset_counter(&mut c);
    c.display();
    c.increment();
    c.increment();

    // self: taking ownership
    let final_count = c.finish();
    println!("Returned final count: {}", final_count);
    // finish took c's ownership; uncommenting the line below is a compile error:
    // c.display();
}
```

## No Manual `&` or `&mut` at the Call Site

You may have noticed — when calling, we just write `c.display()` and `c.increment()`, not `(&c).display()` or `(&mut c).increment()`. Rust automatically adds the `&` or `&mut` based on the method's `self` parameter. You could write `(&c).display()` or `(&mut c).increment()`, but there's no need.

## Recap

- `&self`: read-only borrow — the most common; the value stays usable after the call.
- `&mut self`: mutable borrow — can modify fields; the value stays usable after the call.
- `self`: consumes ownership — the variable is unusable after the call.
- Selection principle: **read → `&self`, modify → `&mut self`, consume → `self`**.
- `Clone`'s method is defined as `fn clone(&self) -> Self` — borrowing itself to produce a new replica, so `clone` never consumes the original.
- Ordinary function parameters likewise: **read → `&T`, modify → `&mut T`, consume → `T`**.
- Call methods simply as `c.method()`.
