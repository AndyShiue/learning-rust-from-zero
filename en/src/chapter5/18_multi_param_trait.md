# Multi-parameter `trait`s

## Goal of This Episode

Learn to define `trait`s with extra type parameters, so one type can implement the same `trait` for different target types.

## Concept

Our `trait`s so far have been fairly simple — `Describe`, `Clone`, `Display`, no extra type parameters. But sometimes the behavior you want to define relates to **another type**.

Take "conversion": an `i32` can turn into an `f64`, or into a `String`. Same type, different targets, different logic.

### `trait`s with Extra Type Parameters

```rust,noplayground
trait Convert<T> {
    fn convert(self) -> T;
}
#
# fn main() {}
```

`Convert<T>` means: "can be converted into type `T`." One type can implement `Convert<f64>`, `Convert<String>`, and other versions.

### Implementing a Multi-parameter `trait`

```rust,noplayground
# trait Convert<T> {
#     fn convert(self) -> T;
# }
#
impl Convert<(i32,)> for i32 {
    fn convert(self) -> (i32,) {
        (self,)
    }
}
#
# fn main() {}
```

Here `i32` implements `Convert<(i32,)>` — turning itself into a single-element tuple.

The same type can implement it multiple times, as long as the type parameters differ:

```rust,noplayground
# trait Convert<T> {
#     fn convert(self) -> T;
# }
#
impl Convert<String> for i32 {
    fn convert(self) -> String {
        // Using the ToString trait (i32 already has it)
        self.to_string()
    }
}
#
# fn main() {}
```

### The Difference from `trait`s without Extra Parameters

- `Clone` (no extra parameters): a type can implement `Clone` only once.
- `Convert<T>` (with a parameter): a type can implement several versions — `Convert<String>`, `Convert<(i32,)>`, and so on.

## Example Code

```rust,editable
// Defining a trait with a type parameter
trait Convert<T> {
    fn convert(self) -> T;
}

// i32 into a single-element tuple
impl Convert<(i32,)> for i32 {
    fn convert(self) -> (i32,) {
        (self,)
    }
}

// i32 into String
impl Convert<String> for i32 {
    fn convert(self) -> String {
        self.to_string()
    }
}

// bool into i32
impl Convert<i32> for bool {
    fn convert(self) -> i32 {
        if self {
            1
        } else {
            0
        }
    }
}

fn main() {
    // i32 -> (i32,)
    let x: i32 = 42;
    let tuple: (i32,) = x.convert();
    println!("{:?}", tuple);

    // i32 -> String
    let y: i32 = 100;
    let s: String = y.convert();
    println!("{}", s);

    // bool -> i32
    let b = true;
    let n: i32 = b.convert();
    println!("{}", n);
}
```

## Recap

- A `trait` can take extra type parameters: `trait Convert<T> { ... }`.
- One type can implement the same `trait` for different `T`s (e.g. `Convert<String>` and `Convert<(i32,)>`).
- Unlike `trait`s without extra parameters, which a type can implement only once.
- Multi-parameter `trait`s give a unified home to "behavior involving another type."
