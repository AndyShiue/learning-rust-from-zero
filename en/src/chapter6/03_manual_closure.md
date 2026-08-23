# Implementing Closures by Hand

## Goal of This Episode

We'll manually model closures as `struct`s + methods, so you can understand what the compiler does behind the scenes. You'll see one `struct`-based example for each of the three closure kinds, and why calling a closure is really calling a method.

## Concept

### A Closure = an Anonymous `struct` + a Method

Last episode we saw closures capture outside variables. But how do they "remember" them?

The answer is direct — the compiler does two things for you:

1. **Creates an anonymous `struct`**, storing the captured variables as fields.
2. **`impl`s a method on that `struct`**, whose body is what you wrote after the `||`.

In other words, the closure body you write (the code inside `{ ... }`) is that method's implementation.

Today we'll do the compiler's job by hand, simulating each of the three closure kinds.

### Calling a Closure = Calling a Method

When you write `f()` to call a closure, the compiler actually turns it into a method call on the `struct`:

- **`FnOnce`**: `f()` → `f.call_once()` — takes `self`, consuming the whole `struct`.
- **`FnMut`**: `f()` → `f.call_mut()` — takes `&mut self`, a mutable reference to the `struct`.
- **`Fn`**: `f()` → `f.call()` — takes `&self`, a shared reference to the `struct`.

See it? These are the three `self` parameter forms from Chapter 4: `self`, `&mut self`, `&self`. The three closure kinds are, at bottom, the three ways a method can receive `self`.

Last episode introduced `FnOnce` (consumes captured values, one call only) and `FnMut` (modifies captured values, repeatable calls). **`Fn` didn't appear last episode** — it's the third kind: calling it neither consumes the closure nor requires a mutable reference to it, so it can be called any number of times.

Next we'll simulate all three by hand with `struct`s. Note: **the three examples below use different field types**. These are the field types used in these examples, not fixed requirements of the three closure kinds.

### An `FnOnce` Example: The `struct` Stores Owned Values, the Method Takes `self`

Suppose we have this closure:

```rust,editable
fn main () {
    let name = String::from("Alice");
    let greet = || {
        let s = name; // The closure body moves name away
        println!("Hello, {}!", s);
    };
    greet();
    // greet(); // Compile error! name was moved; no second call
}
```

The compiler generates something like:

```rust,noplayground
struct GreetOnce {
    name: String, // Owns name
}

// Creating the closure = stuffing the captures into the struct
// let greet = GreetOnce { name };

impl GreetOnce {
    // Calling the closure = calling the struct's method
    fn call_once(self) {
        let s = self.name; // Move name out of the struct
        println!("Hello, {}!", s);
    }
}
#
# fn main() {}
```

Since the method takes `self`, the whole `struct` is consumed on the call — hence one call only. That's `FnOnce`.

### An `FnMut` Example: The `struct` Stores Mutable References, the Method Takes `&mut self`

Suppose the closure modifies a captured variable:

```rust,editable
fn main() {
    let mut name = String::from("Alice");
    let mut greet = || {
        name.push_str("!");
        println!("Hello, {}", name);
    };
    greet();
    greet(); // Repeated calls are fine
}
```

The compiler's product:

```rust,noplayground
struct GreetMut<'a> {
    name: &'a mut String, // A mutable reference to name
}

// let mut greet = GreetMut { name: &mut name };

impl<'a> GreetMut<'a> {
    fn call_mut(&mut self) {
        self.name.push_str("!");
        println!("Hello, {}", self.name);
    }
}
#
# fn main() {}
```

**Why does the `struct` store `&mut` while the method also takes `&mut self`?** Because a closure may capture several variables. If a closure modifies `a`, `b`, and `c`, the `struct` has three fields:

```rust,noplayground
struct SomeClosure<'a> {
    a: &'a mut i32,
    b: &'a mut String,
    c: &'a mut Vec<i32>,
}
#
# fn main() {}
```

The method takes `&mut self` rather than `self` because `self` would consume it in one call — making it `FnOnce`. `FnMut` needs repeated calls, so it can only take a mutable reference to the `struct`.

### An `Fn` Example: The `struct` Stores Shared References, the Method Takes `&self`

If the closure only reads captured variables, never modifying:

```rust,editable
fn main() {
    let name = String::from("Alice");
    let greet = || {
        println!("Hello, {}!", name);
    };
    greet();
    greet(); // Repeated calls, no problem at all
}
```

The compiler's product:

```rust,noplayground
struct GreetRef<'a> {
    name: &'a String, // A shared reference to name
}

// let greet = GreetRef { name: &name };

impl<'a> GreetRef<'a> {
    fn call(&self) {
        println!("Hello, {}!", self.name);
    }
}
#
# fn main() {}
```

Since the method takes `&self`, the `struct` is neither consumed nor modified — callable any number of times. That's `Fn`.

### The Comparison Table

| `self` kind | Corresponding kind | What the fields hold in this example | What it can do |
|----------|----------|-----------------|---------|
| `self` | `FnOnce` | Owned values (like `String`) | Consumes captures; one call only |
| `&mut self` | `FnMut` | Mutable references (like `&mut String`) | Modifies captures; repeatable calls |
| `&self` | `Fn` | Shared references (like `&String`) | Reads only; repeatable calls |

### Wrapping Up: What Is a Closure, Really?

Stringing it all together:

1. The compiler builds an anonymous `struct` for you, storing the captures inside.
2. The closure body you write is the implementation of a method on that `struct`.
3. When you write `f()`, the compiler — depending on the closure's kind — calls the `struct`'s `.call_once()` / `.call_mut()` / `.call()`.

Every time you write a closure, the compiler is backstage doing "build a `struct` → `impl` a method → call the method."

Having grasped that "the closure body is just a method's content," here's a bonus thought: what happens if you write `return` inside a closure? Since the closure body really is some method's implementation, `return` exits that method — i.e. **it exits only the innermost closure**, never the enclosing function. Much like `break`'s default effect — `break` also exits only the innermost loop, not every nested loop at once.

## Example Code

The complete code below collects the three examples above. Each `struct` simulates one closure kind with the field types and `self` parameter form used in that example:

```rust,editable
// === Simulating FnOnce ===
// The struct owns the value; the method takes self
struct GreetOnce {
    name: String,
}

impl GreetOnce {
    fn call_once(self) {
        // The closure body: move name away
        let s = self.name;
        println!("[FnOnce] Hello, {}!", s);
        // self has been consumed; no more use
    }
}

// === Simulating FnMut ===
// The struct stores a mutable reference; the method takes &mut self
struct GreetMut<'a> {
    name: &'a mut String,
}

impl<'a> GreetMut<'a> {
    fn call_mut(&mut self) {
        // The closure body: modify the captured variable
        self.name.push_str("!");
        println!("[FnMut] Hello, {}", self.name);
    }
}

// === Simulating Fn ===
// The struct stores a shared reference; the method takes &self
struct GreetRef<'a> {
    name: &'a String,
}

impl<'a> GreetRef<'a> {
    fn call(&self) {
        // The closure body: read only, no modification
        println!("[Fn] Hello, {}!", self.name);
    }
}

fn main() {
    // --- FnOnce: consumed after one call ---
    let name1 = String::from("Alice");
    let greet_once = GreetOnce { name: name1 };
    greet_once.call_once();
    // greet_once.call_once(); // Compile error! The struct has been consumed

    // --- FnMut: repeatable calls, modifying each time ---
    let mut name2 = String::from("Bob");
    {
        let mut greet_mut = GreetMut { name: &mut name2 };
        greet_mut.call_mut(); // Bob!
        greet_mut.call_mut(); // Bob!!
        greet_mut.call_mut(); // Bob!!!
    } // greet_mut leaves scope; its mutable reference is no longer in use
    println!("name2 is now: {}", name2);

    // --- Fn: read-only; call as many times as you like ---
    let name3 = String::from("Charlie");
    let greet_ref = GreetRef { name: &name3 };
    greet_ref.call();
    greet_ref.call();
    greet_ref.call();
}
```

## Recap

- Behind a closure is an anonymous `struct`; the captured variables become its fields.
- **The three closure kinds differ in how the method receives `self`**: `self` (`FnOnce`), `&mut self` (`FnMut`), `&self` (`Fn`).
- The closure body is the implementation of the `struct`'s method.
- `f()` gets compiled into a method call: `f.call_once()` / `f.call_mut()` / `f.call()`.
- `Fn`: calling it only requires a shared reference to the closure value, so it can be called repeatedly.
- Since a closure body is just a method's content, a `return` inside a closure exits only the innermost closure, not the enclosing function — like `break` exiting only the innermost loop by default.
- Next episode: how the compiler **automatically decides** whether a closure counts as `FnOnce`, `FnMut`, or `Fn`.
