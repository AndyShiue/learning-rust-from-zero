# `PhantomData` / `PhantomPinned`

## Goal of This Episode

Understand how a marker type tells the compiler about a type designer's promise without storing any actual data, and tell apart the different jobs of `PhantomData` and `PhantomPinned`.

> This episode supplements **Chapter 5's generics**, this appendix's variance episode, and `Pin` from the **async chapter**.

## Concept

Some standard library types carry no useful runtime data of their own; they exist purely to influence type checking. Such types are commonly called **marker types**.

This episode's two protagonists have similar names, and both affect whether the enclosing type automatically implements certain `auto trait`s, but they express different things:

- `PhantomData<T>`: says "this type logically uses `T`," so `T`'s properties may affect the enclosing type.
- `PhantomPinned`: a marker whose sole purpose is to stop the enclosing type from automatically implementing `Unpin`.

### The Problem: A Generic Parameter That Never Appears in a Field

Suppose we want to tag database IDs differently, making `Id<User>` and `Id<Article>` distinct types at compile time so user IDs and article IDs never get mixed up:

```rust,compile_fail
struct Id<T> {
    value: u64,
}
#
# fn main() {}
```

We only want `T` to serve as a type tag; there's no need to actually store a `User` or an `Article`. But Rust doesn't allow declaring a generic parameter that goes entirely unused in the fields, so the code above won't compile. The compiler can't tell whether this is a deliberate tag or an accidental omission of `T`.

This is where `PhantomData<T>` comes in, stating explicitly "I really do want this type to be related to `T`":

```rust,editable
use std::marker::PhantomData;

struct User;
struct Article;

struct Id<T> {
    value: u64,
    _kind: PhantomData<T>,
}

fn show_user(id: Id<User>) {
    println!("User ID: {}", id.value);
}

fn main() {
    let user_id = Id::<User> {
        value: 7,
        _kind: PhantomData,
    };
    show_user(user_id);

    let _article_id = Id::<Article> {
        value: 7,
        _kind: PhantomData,
    };
    // show_user(_article_id); // Id<Article> is not Id<User>
}
```

`PhantomData<T>` doesn't actually put a `T` inside, so `Id<T>`'s runtime content is still just a `u64`. But in the type system's eyes, `Id<User>` and `Id<Article>` are already different types.

### "Logically Uses" Is About More Than Silencing an Error

`PhantomData<T>` tells the compiler: when analyzing this enclosing type, please treat it as related to `T`. That affects:

- **Variance**: `PhantomData<&'a T>`, for instance, carries the relationship between `'a` and `T`.
- **`auto trait`s**: whether `T` is `Send`, `Sync`, and so on may affect the enclosing type.

Different spellings express different relationships:

```rust,ignore
PhantomData<T>     // As if it logically owns a T
PhantomData<&'a T> // As if it logically borrows an &'a T
PhantomData<fn(T)> // T sits in function input position
```

These distinctions matter a great deal in low-level libraries. In ordinary applications the most common case is the first `Id<T>` example: using a type tag to keep identical underlying data from being mixed up.

### `PhantomPinned`: Blocking the Automatic `Unpin` Implementation

As the async chapter taught, `Unpin` is an `auto trait` just like `Send` and `Sync`. As long as every field is `Unpin`, the enclosing `struct` normally implements `Unpin` automatically too.

But when designing an address-sensitive type, we may need to tell the compiler explicitly: "even if every other field can move, this type must not be moved once pinned." On stable Rust, if all of a custom type's fields implement `Unpin`, we can't opt out of `Unpin` with a single direct declaration; we have to include a field that doesn't implement `Unpin`. The `Future`s produced by `async fn` and `async` blocks usually don't implement `Unpin`, but their concrete types are anonymous, so no type name can be written into a field. `PhantomPinned` is exactly the named zero-sized marker the standard library provides for this.

Putting `PhantomPinned` in a field stops the enclosing type from automatically implementing `Unpin`:

```rust,compile_fail
use std::marker::PhantomPinned;

struct AddressSensitive {
    name: String,
    _pin: PhantomPinned,
}

fn assert_unpin<T: Unpin>(_: T) {}

fn main() {
    let value = AddressSensitive {
        name: String::from("don't assume I can be moved"),
        _pin: PhantomPinned,
    };

    assert_unpin(value);
}
```

The gist of the error is that `PhantomPinned` doesn't implement `Unpin`, so `AddressSensitive`, which contains it, doesn't implement `Unpin` automatically either.

But adding `PhantomPinned` **is not the same as having pinned the value**. It only changes whether the type automatically implements `Unpin`; actually creating a `Pin<&mut T>` or a `Pin<Box<T>>` still requires `pin!`, `Box::pin`, or the like.

### Moving Is Still Allowed at Construction Time

`PhantomPinned` doesn't make a value completely immovable from birth. The rule from the async chapter still holds: **moving is fine before pinning; the address only has to stay put afterward.**

```rust,editable
use std::marker::PhantomPinned;
use std::pin::Pin;

struct AddressSensitive {
    name: String,
    _pin: PhantomPinned,
}

fn show(value: Pin<&AddressSensitive>) {
    println!("{} is at {:p}", value.name, &*value);
}

fn main() {
    let value = AddressSensitive {
        name: String::from("fixed position"),
        _pin: PhantomPinned,
    };

    // Until now value is still an ordinary value and can move into Box::pin.
    let pinned = Box::pin(value);
    show(pinned.as_ref());
}
```

`Box::pin` moves the value into its final position on the heap and creates a `Pin<Box<T>>`. The `Pin<Box<T>>` pointer itself can be moved afterward, but no safe API can move the `AddressSensitive` inside out of its address.

### A Practical Case: Keeping an Executor on the Thread That Created It

The executor built from Episode 11 of the async chapter onward records the current `Thread` with `thread::current()` inside `Executor::new()`. Later, `Task::wake` calls `.unpark()` through that `Thread` handle, while an executor with no work parks the `Thread` currently running it via `thread::park()`.

Hidden here is a constraint the type system doesn't spot on its own: the `Executor` has to stay on the `Thread` that created it. Here's a simplified version:

```rust,no_run
use std::thread::{self, Thread};

struct Task {
    executor_thread: Thread,
}

impl Task {
    fn wake(self) {
        self.executor_thread.unpark();
    }
}

struct Executor {
    executor_thread: Thread,
}

impl Executor {
    fn new() -> Self {
        Self {
            executor_thread: thread::current(),
        }
    }

    fn run_once(&self) {
        let task = Task {
            executor_thread: self.executor_thread.clone(),
        };

        thread::spawn(move || task.wake())
            .join()
            .expect("the thread failed");
        thread::park();
    }
}

fn main() {
    let executor = Executor::new(); // Remembers the main thread

    // Executor's fields are all Send, so this compiles — and may hang forever.
    thread::spawn(move || executor.run_once())
        .join()
        .expect("the thread failed");
}
```

A `Thread` handle can be sent across threads, but moving the handle doesn't change which thread it points at. After the example above moves `executor` to a new `Thread`:

1. `task.wake()` calls `.unpark()` on the **main thread**, the one that created the executor.
2. `run_once()`, meanwhile, calls `thread::park()` on the **new `Thread`**.

So `.unpark()` isn't ineffective — it delivers the wake token to the wrong `Thread`. The new `Thread` actually running the executor never receives a token and may block indefinitely.

This executor can only stay on the `Thread` that created it, and other `Thread`s shouldn't be able to call `.run()` on it through a shared reference either. So we can add a zero-sized marker that blocks the automatic `Send` and `Sync` implementations:

```rust,compile_fail
use std::marker::PhantomData;
use std::rc::Rc;
use std::thread::{self, Thread};

struct Executor {
    executor_thread: Thread,
    _not_send_sync: PhantomData<Rc<()>>,
}

impl Executor {
    fn new() -> Self {
        Self {
            executor_thread: thread::current(),
            _not_send_sync: PhantomData,
        }
    }

    fn run(&self) {
        thread::park();
    }
}

fn main() {
    let executor = Executor::new();

    // Compile error: Executor can no longer be sent across threads.
    thread::spawn(move || executor.run());
}
```

`Rc<()>` is neither `Send` nor `Sync`, and `PhantomData<Rc<()>>` makes the `auto trait` analysis treat `Executor` as logically containing an `Rc<()>`. So `Executor` is likewise neither `Send` nor `Sync`: not being `Send` keeps it from being moved to another `Thread`, and not being `Sync` keeps other `Thread`s from calling `.run()` through an `&Executor`. What the `move` example above demonstrates directly is that the executor is now non-`Send`; an attempt to share an `&Executor` across `Thread`s would be rejected for being non-`Sync`. This field never actually allocates or stores an `Rc`; the correct usage is to create and run the executor on the same `Thread`, while wakers can still call `.unpark()` on that executor's `Thread` from other `Thread`s.

## Example Code

```rust,editable
use std::marker::{PhantomData, PhantomPinned};
use std::pin::Pin;

struct Meters;
struct Seconds;

struct Measurement<Unit> {
    value: f64,
    _unit: PhantomData<Unit>,
}

struct AddressSensitive {
    name: String,
    _pin: PhantomPinned,
}

fn print_record(record: Pin<&AddressSensitive>) {
    println!("Record: {}, address: {:p}", record.name, &*record);
}

fn main() {
    let distance = Measurement::<Meters> {
        value: 12.5,
        _unit: PhantomData,
    };
    let time = Measurement::<Seconds> {
        value: 3.0,
        _unit: PhantomData,
    };

    println!("Distance: {}, time: {}", distance.value, time.value);

    let record = AddressSensitive {
        name: String::from("distance measurement"),
        _pin: PhantomPinned,
    };
    let pinned = Box::pin(record);
    print_record(pinned.as_ref());
}
```

## Recap

- A marker type can affect type checking without storing any runtime data.
- `PhantomData<T>` says the enclosing type logically uses, owns, or borrows some `T`.
- `PhantomData<T>` affects variance and `auto trait`s.
- `PhantomPinned` blocks the enclosing type's automatic `Unpin` implementation.
- `PhantomPinned` doesn't pin a value by itself; you still create the `Pin` through `pin!`, `Box::pin`, and the like.
- `PhantomPinned` doesn't forbid moves before pinning; the real address guarantee begins once the value is pinned.
- A type that must stay on the `Thread` that created it can use `PhantomData<Rc<()>>` to block the automatic `Send` and `Sync` implementations, keeping it from being moved to another `Thread` or used across `Thread`s through a shared reference.
