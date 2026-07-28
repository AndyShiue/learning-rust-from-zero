# Operator Overloading

## Goal of This Episode

Learn to implement operators like `+` and `-` for your own types.

## Concept

### Operators Are `trait` Methods

In Rust, `a + b` is really shorthand for `a.add(b)` — `+` corresponds to the `std::ops::Add` `trait`. Implement `Add` for your type and you can use `+`.

### The Definition of the `Add` `trait`

```rust,noplayground
trait Add<Rhs = Self> {
    type Output;
    fn add(self, rhs: Rhs) -> Self::Output;
}
#
# fn main() {}
```

Three things to note:

- `Rhs = Self`: the default parameter from last episode — the right-hand side of the addition defaults to the same type as the left.
- `type Output`: the associated type from Chapter 5 — the result of an addition isn't necessarily the same type as the inputs.
- `self`, not `&self`: `add` consumes the left-hand value (types that are `Copy` are unaffected).

### Implementing `Add` for `Point`

```rust,noplayground
use std::ops::Add;

#[derive(Debug)]
struct Point { x: i32, y: i32 }

impl Add for Point {
    type Output = Point;
    fn add(self, rhs: Point) -> Point {
        Point {
            x: self.x + rhs.x,
            y: self.y + rhs.y,
        }
    }
}
#
# fn main() {}
```

### Common Operators

Commonly used `trait`s in `std::ops`:

| Operator | `trait` | Method |
|--------|---------|------|
| `+` | `Add` | `add(self, rhs)` |
| `-` | `Sub` | `sub(self, rhs)` |
| `*` | `Mul` | `mul(self, rhs)` |
| `/` | `Div` | `div(self, rhs)` |
| `%` | `Rem` | `rem(self, rhs)` |
| `-x` | `Neg` | `neg(self)` |
| `!x` | `Not` | `not(self)` |
| `&` | `BitAnd` | `bitand(self, rhs)` |
| `\|` | `BitOr` | `bitor(self, rhs)` |
| `^` | `BitXor` | `bitxor(self, rhs)` |
| `<<` | `Shl` | `shl(self, rhs)` |
| `>>` | `Shr` | `shr(self, rhs)` |
| `+=` | `AddAssign` | `add_assign(&mut self, rhs)` |
| `&=` | `BitAndAssign` | `bitand_assign(&mut self, rhs)` |
| `[]` | `Index` | `index(&self, idx)` |
| `[]` mutable | `IndexMut` | `index_mut(&mut self, idx)` |

The bitwise operators (`&`, `|`, `^`, `<<`, `>>`, `!`) come up a lot in systems programming — flags, masks, bit fields, and so on. If you're not yet familiar with bitwise operations, it's worth looking them up on your own.

Every binary operator listed above has a corresponding assign version (e.g. `&=` corresponds to `BitAndAssign`, `<<=` to `ShlAssign`), used just like the `+=` or `-=` you learned earlier.

### `AddAssign` vs `Add`

`a += b` and `a = a + b` aren't necessarily implemented the same way in Rust:

- `Add::add(self, rhs)` consumes `a` and produces a new value.
- `AddAssign::add_assign(&mut self, rhs)` modifies `a` in place.

For an `i32` the difference barely matters, but for a non-`Copy` type (like `String`), `s1 += &s2` only needs a mutable borrow of `s1`, while `s1 = s1 + &s2` has to give up ownership of `s1` and assign the result back. They ask for different things from you, and for some types the efficiency differs too, which is why they're separate `trait`s.

`Add` and `AddAssign` are completely independent — implementing `Add` doesn't automatically make `+=` work, nor vice versa. Without the implementation, it's a compile error.

### `Index` / `IndexMut`

`Vec` supports `v[i]` precisely because it implements `Index`:

```rust,noplayground
use std::ops::Index;

struct MyVec(Vec<i32>);

impl Index<usize> for MyVec {
    type Output = i32;
    fn index(&self, idx: usize) -> &i32 {
        &self.0[idx]
    }
}
#
# fn main() {}
```

### Adding Different Types

Override the default `Rhs`:

```rust,noplayground
use std::ops::Add;

struct Meters(f64);
struct Centimeters(f64);

impl Add<Centimeters> for Meters {
    type Output = Meters;
    fn add(self, rhs: Centimeters) -> Meters {
        Meters(self.0 + rhs.0 / 100.0)
    }
}
#
# fn main() {}
```

## Example Code

```rust,editable
use std::ops::{Add, Neg};

#[derive(Debug, Clone, Copy)]
struct Vec2 { x: f64, y: f64 }

impl Add for Vec2 {
    type Output = Vec2;
    fn add(self, rhs: Vec2) -> Vec2 {
        Vec2 { x: self.x + rhs.x, y: self.y + rhs.y }
    }
}

impl Neg for Vec2 {
    type Output = Vec2;
    fn neg(self) -> Vec2 {
        Vec2 { x: -self.x, y: -self.y }
    }
}

fn main() {
    let a = Vec2 { x: 1.0, y: 2.0 };
    let b = Vec2 { x: 3.0, y: 4.0 };
    let c = a + b;
    println!("a + b = {:?}", c);
    println!("-a = {:?}", -a);
}
```

## Recap

- `a + b` is shorthand for `Add::add(a, b)`; likewise for the other operators.
- `Add`'s signature uses a default parameter (`Rhs = Self`) and an associated type (`Output`).
- `AddAssign` (`+=`) modifies in place (`&mut self`); `Add` (`+`) produces a new value (`self`).
- `Index` / `IndexMut` let your type use the `[]` operator.
- Overriding `Rhs` enables operations between different types.
