# `Drop`

## Goal of This Episode

Learn to discard a value early with `drop(value)`, understand how Rust automatically `drop`s the contents a value owns, and use the `Drop` `trait` to perform an extra action before the contained values are `drop`ped.

## Concept

### Discarding a Value Early with `drop(value)`

Rust normally `drop`s a value automatically when it leaves scope. If you do not want to wait until the scope ends, call `drop(value)` to `drop` it early:

```rust,editable
fn main() {
    let message = String::from("hello");
    println!("{}", message);

    drop(message);
    println!("message has been dropped");

    // println!("{}", message); // Compile error! message's value was moved
}
```

`drop` is an ordinary function provided by the prelude, so it needs no additional `use`. It takes ownership of the value passed to it, which means you cannot use the original value after `drop(message)`.

More precisely, it is the **value** bound to `message` that is `drop`ped, not the variable name itself. The variable's original scope has not become shorter; its value has been moved into `drop` and then discarded.

### Contained Values Are `drop`ped Automatically

When a value is `drop`ped, Rust continues by `drop`ping the fields or elements that the value owns:

```rust,editable
struct Message {
    title: String,
    body: String,
}

fn main() {
    let message = Message {
        title: String::from("Greeting"),
        body: String::from("Hello!"),
    };

    drop(message);
}
```

We only need to `drop` `message`; Rust automatically `drop`s its `title` and `body` too. The same mechanism applies to values owned by tuples, `enum`s, arrays, `Vec`s, and other types. You do not need to clean them up one by one yourself.

### Using `Drop` to Act Before `drop`ping

Sometimes we want to do something before Rust automatically `drop`s the contained values, such as closing a connection, returning a resource, or printing a log message. We can implement the `Drop` `trait` for the type:

```rust,noplayground
# struct Resource {
#     name: String,
# }
#
impl Drop for Resource {
    fn drop(&mut self) {
        println!("Releasing resource: {}", self.name);
    }
}
#
# fn main() {}
```

When a `Resource` is `drop`ped, Rust runs `Drop`'s `.drop()` method first and then automatically `drop`s its fields. This method adds an action to the `drop` process; it does not replace Rust's automatic handling of the contained values.

Although `Drop`'s `.drop()` method and the `drop(value)` function are both named `drop`, they are used differently:

- `drop(value)` is an ordinary function that you can call to `drop` a value early.
- `Drop`'s `.drop()` method is run automatically by Rust when a value is `drop`ped. You cannot call it manually as `value.drop()`.

Why can't you call `value.drop()` manually? Because this method only receives `&mut self`; it does not take ownership of the value. If a manual call were allowed, the value would still exist afterward. When the value was actually `drop`ped later, Rust would run the same method again, potentially releasing the same resource twice. Rust therefore rejects this syntax.

`drop(value)` is different: it takes ownership of the value, so the original value cannot be used afterward. This lets Rust complete the entire `drop` process early without leaving behind a value that must be `drop`ped again later.

## Example Code

```rust,editable
struct Resource {
    name: String,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("Releasing resource: {}", self.name);
    }
}

struct Worker {
    name: String,
    resource: Resource,
}

impl Drop for Worker {
    fn drop(&mut self) {
        println!(
            "Stopping worker: {} (releasing {} next)",
            self.name,
            self.resource.name,
        );
    }
}

fn main() {
    let worker = Worker {
        name: String::from("downloader"),
        resource: Resource {
            name: String::from("network connection"),
        },
    };

    println!("Worker is running");
    drop(worker);
    println!("Worker was dropped early");

    {
        let temporary = Resource {
            name: String::from("temporary file"),
        };
        println!("Using temporary resource: {}", temporary.name);
    } // temporary is dropped automatically here
}
```

## Types That Implement `Drop` Cannot Be Partially Moved

If a type implements `Drop`, you cannot move a value out of one of its fields:

```rust,compile_fail
struct Resource {
    name: String,
    id: i32,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("Releasing {} (ID {})", self.name, self.id);
    }
}

fn main() {
    let resource = Resource {
        name: String::from("database connection"),
        id: 1,
    };

    let name = resource.name; // Compile error! A partial move is not allowed
}
```

`Drop`'s `.drop()` method receives a complete `&mut self`, so it might access any field. If `name` could be moved out first, `resource` would no longer be complete when this method later ran. Rust therefore rejects this operation.

If a field is itself a `struct`, moving a value out of one of its deeper fields would also leave the outer value incomplete, so that is rejected as well.

The restriction applies to **moving** a value out of a field. You can still:

- Move the entire `resource`.
- Borrow a field, such as `&resource.name`.
- Copy a field that implements `Copy`, such as `resource.id`.

## Recap

- Rust automatically `drop`s a value when it leaves scope.
- `drop(value)` takes ownership of a value and lets you `drop` it before the scope ends.
- When an outer value is `drop`ped, the contained values it owns are `drop`ped automatically too.
- `Drop`'s `.drop()` method lets you perform an extra action before contained values are `drop`ped. Rust runs it automatically, so you cannot call it directly.
- A type that implements `Drop` cannot be partially moved, but you can still move the whole value, borrow its fields, or copy fields that implement `Copy`.
