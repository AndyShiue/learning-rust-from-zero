# Type Aliases

## Goal of This Episode

Learn to create type aliases with `type`, making complex generic types easier to read.

## Concept

Now that we know generics, types will get increasingly complex. For example, a three-dimensional data structure:

```rust,ignore
Vec<Vec<Vec<i32>>>
```

Writing the full type every time is tiring, and hard to read. Rust offers the `type` keyword for creating **type aliases**:

```rust,noplayground
type Grid3D = Vec<Vec<Vec<i32>>>;
#
# fn main() {}
```

From then on, `Grid3D` and `Vec<Vec<Vec<i32>>>` are the same type — just under a different name. It doesn't create a new type; it's purely shorthand.

### A Simple Alias

```rust,noplayground
type Name = String;
#
# fn main() {}
```

`Name` and `String` are fully equivalent, usable interchangeably.

### Type Aliases with Parameters

Type aliases can take generic parameters too:

```rust,noplayground
type Pair<T> = (T, T);
#
# fn main() {}
```

Now `Pair<i32>` equals `(i32, i32)`, and `Pair<String>` equals `(String, String)`.

### Note

A type alias is only shorthand, not a new type. `Name` and `String` are freely interchangeable — the compiler treats them as one and the same type.

## Example Code

```rust,editable
// A simple type alias
type Name = String;

// Simplifying a complex nested type
type Grid3D = Vec<Vec<Vec<i32>>>;

// An alias with a generic parameter
type Pair<T> = (T, T);

fn main() {
    // Name IS String
    let greeting: Name = String::from("Hello");
    println!("{}", greeting);

    // A 3D Vec is much tidier with an alias
    let mut grid: Grid3D = vec![vec![vec![0; 3]; 3]; 3];
    grid[1][1][1] = 42;
    println!("grid[1][1][1] = {}", grid[1][1][1]);

    // Pair<i32> IS (i32, i32)
    let point: Pair<i32> = (3, 7);
    println!("{:?}", point);

    let coords: Pair<f64> = (1.5, 3.7);
    println!("{:?}", coords);
}
```

## Recap

- `type Name = ExistingType;` creates a type alias — shorthand only, not a new type.
- Type aliases can take generic parameters: `type Pair<T> = (T, T);`.
- Common use: simplifying complex nested types (like `Vec<Vec<Vec<i32>>>`).
- An alias is fully equivalent to the original type, usable interchangeably.
