# `Rc` Cycles and `Weak`

## Goal of This Episode

Understand how `Rc` reference cycles leak memory, and learn to break cycles with `Weak`.

> This episode supplements **Chapter 5**.

## Concept

Remember `Rc<T>` from Chapter 5? It manages memory through reference counting — each extra `Rc` pointing at the same data adds one to the count; each fewer subtracts one; hitting zero releases the memory.

Sounds perfect, but it has one fatal weakness: the **reference cycle**.

### What's a Reference Cycle?

Picture two nodes A and B: A holds an `Rc` to B, and B holds an `Rc` to A. When the outside no longer holds either:

1. A's external `Rc` gets `drop`ped → A's count decrements, but B still points at A → the count isn't zero → A isn't released.
2. B's external `Rc` gets `drop`ped → B's count decrements, but A still points at B → the count isn't zero → B isn't released.

Result: A and B are **never released** — a memory leak. A ring invisible from outside, holding itself up — that's the essence of the cycle problem.

What makes a leak awkward is that it has no visible symptom: nothing panics, nothing fails to compile, that memory simply never comes back. So let's make it visible with `Drop` — give the node a destructor that prints, and a message that never appears means a value that was never released:

```rust,editable
use std::rc::Rc;
use std::cell::RefCell;

struct Node {
    name: &'static str,
    other: Option<Rc<RefCell<Node>>>,
}

impl Drop for Node {
    fn drop(&mut self) {
        println!("{} released", self.name);
    }
}

fn main() {
    {
        let a = Rc::new(RefCell::new(Node { name: "A", other: None }));
        let b = Rc::new(RefCell::new(Node { name: "B", other: None }));

        a.borrow_mut().other = Some(b.clone());
        b.borrow_mut().other = Some(a.clone());

        println!("before leaving the scope, A's strong count = {}", Rc::strong_count(&a));
    }

    println!("the scope has been left");
}
```

The output is only two lines:

```text
before leaving the scope, A's strong count = 2
the scope has been left
```

That `strong count = 2` is exactly the "B still points at A" from above, and neither "released" message shows up — the variables `a` and `b` are gone, yet the nodes they pointed at are still holding each other up. Comment out the `b.borrow_mut().other = ...` line and run it again: the ring is broken, and both messages appear.

### What Is `Weak`

`Weak<T>` is a "weak reference" — it points at the same data but **doesn't increase the strong count**.

```rust,noplayground
# use std::rc::{Rc, Weak};
#
# fn main() {
    let strong = Rc::new(42);
    let weak: Weak<i32> = Rc::downgrade(&strong);
# }
```

`Rc::downgrade` demotes an `Rc` to a `Weak`. Internally, `Rc` keeps **two** counters: the strong count and the weak count. `.clone()` bumps the strong count; `Rc::downgrade()` bumps only the weak count. `Rc` decides "release or not" solely on the strong count — hitting zero releases, whatever the weak count says.

Since data a `Weak` points at may already be gone, direct access isn't allowed. You must `.upgrade()` first:

```rust,editable
use std::rc::{Rc, Weak};

fn main() {
    let strong = Rc::new(42);
    let weak: Weak<i32> = Rc::downgrade(&strong);

    match weak.upgrade() {
        Some(rc) => println!("Still here: {}", rc),
        None => println!("Already released"),
    }
}
```

`upgrade` returns `Option<Rc<T>>` — an `Rc` if the data survives, `None` if it's been released.

### Breaking Cycles with `Weak`

Back to the example. The crux: the graph formed by strong counts contains a ring. Flip one direction to `Weak`, and the strong-count graph has no ring — `Weak` contributes nothing to strong counts.

A concrete illustration: suppose we're building a **doubly linked list** — each node points to both its predecessor and successor, so walking head-to-tail or tail-to-head is easy. With `Rc` in both directions, adjacent nodes form cycles.

The fix: `next` (forward) uses `Rc`; `prev` (backward) uses `Weak`:

```rust,noplayground
use std::rc::{Rc, Weak};
use std::cell::RefCell;

struct Node<T> {
    value: T,
    next: Option<Rc<RefCell<Node<T>>>>,
    prev: Option<Weak<RefCell<Node<T>>>>,
}
#
# fn main() {}
```

Why does this avoid cycles? Look at the strong-count graph:

```text
outside ──Rc──→ A ──Rc──→ B ──Rc──→ C
                 ←·Weak·←   ←·Weak·←
```

The `Weak` edges don't count toward strong counts. The strong-count graph has only the left-to-right arrows — a chain, no ring.

The outside releases A → A's strong count hits zero → A is `drop`ped → A's `next` gets `drop`ped along with it → B's strong count hits zero → B is `drop`ped → ... a chain reaction all the way down. No node gets propped up by a `prev`, because `prev` is `Weak` and contributes no strong count.

### Do `Rc`s from `upgrade` Cause Problems?

You might wonder: "If I `upgrade` a `Weak`, get an `Rc`, and hold onto it, isn't that one more strong count?"

Correct — an `upgrade`d `Rc` does add one to the strong count. But that `Rc` is an **independent variable** — its strong-count contribution is charged to "the variable holding that `Rc`," not to the original `Weak` field. The `Weak` field's contribution to the strong count is forever 0.

The cycle question was settled — or not — the moment the data structure was built; how you `upgrade` afterward is entirely beside the point.

## Example Code

```rust,editable
use std::rc::{Rc, Weak};
use std::cell::RefCell;

struct Node<T> {
    value: T,
    next: Option<Rc<RefCell<Node<T>>>>,
    prev: Option<Weak<RefCell<Node<T>>>>,
}

impl<T> Node<T> {
    fn new(value: T) -> Rc<RefCell<Node<T>>> {
        Rc::new(RefCell::new(Node { value, next: None, prev: None }))
    }
}

/// Attach b after a
fn link<T>(a: &Rc<RefCell<Node<T>>>, b: &Rc<RefCell<Node<T>>>) {
    a.borrow_mut().next = Some(b.clone());
    b.borrow_mut().prev = Some(Rc::downgrade(a));
}

fn main() {
    let a = Node::new(1);
    let b = Node::new(2);
    let c = Node::new(3);

    link(&a, &b);
    link(&b, &c);

    // Walking forward (via Rc)
    print!("Walking forward: ");
    let mut current = Some(a.clone());
    while let Some(node) = current {
        print!("{} ", node.borrow().value);
        // next is Option<Rc<...>>; as_ref gives Option<&Rc<...>>, then map clones a new Rc
        current = node.borrow().next.as_ref().map(|rc| rc.clone());
    }
    println!();

    // Walking backward (via Weak; upgrade needed)
    print!("Walking backward: ");
    let mut current = Some(c.clone());
    while let Some(node) = current {
        print!("{} ", node.borrow().value);
        current = node.borrow().prev.as_ref().and_then(|w| w.upgrade());
    }
    println!();

    // Checking the counts
    // Strong counts are charged to the node pointed at:
    // a.next points at b → b's strong +1; b.next points at c → c's strong +1
    // Weak counts are charged to the node pointed at too:
    // b.prev points at a → a's weak +1; c.prev points at b → b's weak +1
    // a: strong=1 (variable a), weak=1 (b.prev)
    // b: strong=2 (variable b + a.next), weak=1 (c.prev)
    // c: strong=2 (variable c + b.next), weak=0 (no node's prev points at c)
    println!("a strong={}, weak={}", Rc::strong_count(&a), Rc::weak_count(&a));
    println!("b strong={}, weak={}", Rc::strong_count(&b), Rc::weak_count(&b));
    println!("c strong={}, weak={}", Rc::strong_count(&c), Rc::weak_count(&c));
}
```

## Recap

- `Rc` reference cycles leak memory — the strong count can never hit zero.
- `Weak` doesn't raise the strong count, so it never blocks a release.
- `Rc::downgrade(&rc)` creates a `Weak<T>`; `weak.upgrade()` returns `Option<Rc<T>>`.
- Breaking cycles with `Weak`: keep the strong-count graph ring-free.
- The doubly-linked-list recipe: `next` uses `Rc` (owning the successor); `prev` uses `Weak` (observing the predecessor).
- A `Weak` field's contribution to the strong count is forever 0; `upgrade`d `Rc`s are independent variables.
- `Rc::strong_count()` and `Rc::weak_count()` inspect the current counts.
