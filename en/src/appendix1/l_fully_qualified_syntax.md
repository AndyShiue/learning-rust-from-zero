# Fully Qualified Syntax

## Goal of This Episode

Learn the three levels of method-call syntax, and how to disambiguate when `trait` method names collide.

> This episode supplements **Chapter 5**.

## Concept

In Rust, calling a method actually has three notations, from simple to complete:

### The First: Method Syntax

```rust,noplayground
# trait Animal {
#     fn speak(&self);
# }
#
# struct Dog;
#
# impl Animal for Dog {
#     fn speak(&self) {
#         println!("Woof!");
#     }
# }
#
# fn main() {
#     let dog = Dog;
    dog.speak();
# }
```

The most common form. The compiler finds the matching method automatically.

### The Second: Naming the `trait` or Type

```rust,noplayground
# trait Animal {
#     fn speak(&self);
# }
#
# struct Dog;
#
# impl Animal for Dog {
#     fn speak(&self) {
#         println!("Woof!");
#     }
# }
#
# fn main() {
#     let dog = Dog;
    Animal::speak(&dog);
# }
```

Explicitly telling the compiler "I'm calling the `speak` on the `Animal` `trait`." The `&dog` is what would have been `&self`.

### The Third: Fully Qualified Syntax

```rust,noplayground
# trait Animal {
#     fn speak(&self);
# }
#
# struct Dog;
#
# impl Animal for Dog {
#     fn speak(&self) {
#         println!("Woof!");
#     }
# }
#
# fn main() {
#     let dog = Dog;
    <Dog as Animal>::speak(&dog);
# }
```

The most explicit form: "On the `Animal` `trait` as implemented by `Dog`, call the `speak` method, passing `&dog`."

### When Is It Needed?

Mostly the first form suffices. But when **several `trait`s define same-named methods**, the compiler can't tell which you mean, and more explicit syntax is required:

```rust,noplayground
trait Animal {
    fn name(&self) -> &str;
}

trait Robot {
    fn name(&self) -> &str;
}
#
# fn main() {}
```

If some type implements both `Animal` and `Robot`, calling `.name()` errors. That's when the second or third form disambiguates.

### Associated Functions Need It More Often

For **associated functions** without a `self` parameter, there's no receiver for the compiler to infer from, so fully qualified syntax is needed more often:

```rust,noplayground
# trait TraitA {
#     fn create() -> i32;
# }
#
# trait TraitB {
#     fn create() -> i32;
# }
#
# struct MyType;
#
# impl TraitA for MyType {
#     fn create() -> i32 {
#         0
#     }
# }
#
# impl TraitB for MyType {
#     fn create() -> i32 {
#         1
#     }
# }
#
# fn main() {
    // When several traits have the create() associated function
    let x = <MyType as TraitA>::create();
# }
```

### Accessing Associated Types

Fully qualified syntax also reaches a type's **associated type** on a particular `trait`:

```rust,noplayground
// The IntoIterator trait has an associated type named Item
// Fully qualified syntax retrieves its concrete type:
type MyItem = <Vec<i32> as IntoIterator>::Item; // i32
#
# fn main() {}
```

Some places allow plain `Type::TypeName`, but under ambiguity or failed inference, fully qualified syntax makes the type explicit.

## Example Code

```rust,editable
trait Animal {
    fn speak(&self);
    fn category() -> &'static str;
}

trait Robot {
    fn speak(&self);
    fn category() -> &'static str;
}

struct CyberDog {
    name: String,
}

impl Animal for CyberDog {
    fn speak(&self) {
        println!("{} goes woof! (animal)", self.name);
    }

    fn category() -> &'static str {
        "mammal"
    }
}

impl Robot for CyberDog {
    fn speak(&self) {
        println!("{} goes beep! (robot)", self.name);
    }

    fn category() -> &'static str {
        "artificial intelligence"
    }
}

// CyberDog has a speak of its own too
impl CyberDog {
    fn speak(&self) {
        println!("{} goes woof-beep! (itself)", self.name);
    }
}

fn main() {
    let dog = CyberDog {
        name: String::from("Snowy"),
    };

    // Level one: method syntax — the type's own method wins
    dog.speak(); // "Snowy goes woof-beep! (itself)"

    // Level two: naming the trait
    Animal::speak(&dog); // "Snowy goes woof! (animal)"
    Robot::speak(&dog);  // "Snowy goes beep! (robot)"

    // Level three: fully qualified syntax
    <CyberDog as Animal>::speak(&dog); // "Snowy goes woof! (animal)"
    <CyberDog as Robot>::speak(&dog);  // "Snowy goes beep! (robot)"

    // Associated functions (no self) — fully qualified syntax needed all the more
    // Animal::category(); // Compile error! The compiler doesn't know whose implementation
    let animal_cat = <CyberDog as Animal>::category();
    let robot_cat = <CyberDog as Robot>::category();
    println!("Animal category: {}", animal_cat);
    println!("Robot category: {}", robot_cat);

    // Accessing an associated type
    // Vec<i32> implements IntoIterator, whose Item is i32
    // Fully qualified syntax retrieves the associated type:
    let _: <Vec<i32> as IntoIterator>::Item = 42; // The type is i32
    println!("Vec<i32>'s IntoIterator::Item is i32");
}
```

## Recap

- Method calls have three levels: `object.method()` → `Trait::method(&object)` → `<Type as Trait>::method(&object)`.
- Use the simplest; escalate only on conflict.
- With same-named methods across `trait`s, name whose version you're calling.
- Associated functions (no `self`) need fully qualified syntax more often.
- The fully-qualified format: `<Type as Trait>::function(args)`.
- It also reaches associated types: `<Type as Trait>::TypeName`.
