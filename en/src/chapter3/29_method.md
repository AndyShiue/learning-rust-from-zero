# Methods

## Goal of This Episode

Learn to define methods with `self`, so functions can be called on a value with `.`.

## Concept

Last episode we learned associated functions, called with `::` and tied to the "type." But sometimes we want to operate on a value that **already exists** — say, "compute this `Point`'s `x + y`."

That's a **method** — the first slot in the parameter list is `self`, standing for "the value this method was called on":

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn sum(self) -> i32 {
        self.x + self.y
    }
}
#
# fn main() {}
```

Call it with `.` rather than `::`:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# impl Point {
#     fn new(x: i32, y: i32) -> Point {
#         Point { x, y }
#     }
#
#     fn sum(self) -> i32 {
#         self.x + self.y
#     }
# }
# fn main() {
    let p = Point::new(3, 7);
    let s = p.sum(); // Calling the method with .
# }
```

Note: when calling `p.sum()`, **you don't pass `self` manually**. The `p` before the `.` automatically becomes the method's `self`. So although the definition says `fn sum(self)`, the call is just `p.sum()`, not `p.sum(p)`.

### Methods Can Take Other Parameters

Besides `self`, a method can take one or more other parameters — just like an ordinary function:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
impl Point {
    fn add(self, other: Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}
#
# fn main() {}
```

When calling, `self` comes automatically from the value before the `.`; you only pass the remaining parameters:

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# impl Point {
#     fn new(x: i32, y: i32) -> Point {
#         Point { x, y }
#     }
#
#     fn add(self, other: Point) -> Point {
#         Point {
#             x: self.x + other.x,
#             y: self.y + other.y,
#         }
#     }
# }
#
# fn main() {
    let p1 = Point::new(1, 2);
    let p2 = Point::new(3, 4);
    let p3 = p1.add(p2); // p1 is self, p2 is other
# }
```

### The Difference between Associated Functions and Methods:

- Associated function: no `self`, called with `::` → `Point::new(3, 7)`.
- Method: first parameter is `self`, called with `.` → `p.sum()`.

## Example Code

```rust,editable
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    // Associated function (no self)
    fn new(x: i32, y: i32) -> Point {
        Point { x, y }
    }

    // Method (first parameter is self)
    fn sum(self) -> i32 {
        self.x + self.y
    }

    // Methods can take parameters beyond self
    fn add(self, other: Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }

    // Another method
    fn is_origin(self) -> bool {
        self.x == 0 && self.y == 0
    }
}

enum Direction {
    Up,
    Down,
    Left,
    Right,
}

impl Direction {
    // enums can have methods too
    fn is_horizontal(self) -> bool {
        match self {
            Direction::Left => true,
            Direction::Right => true,
            Direction::Up => false,
            Direction::Down => false,
        }
    }
}

fn main() {
    let p = Point::new(3, 7); // :: calls the associated function
    let s = p.sum();          // . calls the method
    println!("3 + 7 = {}", s);

    // A method with an extra parameter
    let a = Point::new(1, 2);
    let b = Point::new(10, 20);
    let c = a.add(b); // a is self, b is other
    println!("After adding: ({}, {})", c.x, c.y);

    let origin = Point::new(0, 0);
    println!("Is it the origin? {}", origin.is_origin());

    // An enum's method
    let dir = Direction::Left;
    let horizontal = dir.is_horizontal();
    println!("Is it horizontal? {}", horizontal);
}
```

## Recap

- A method's first parameter is `self`, standing for the value itself.
- Methods are called with `.`: `p.sum()` — the value before the `.` automatically becomes `self`; no manual passing.
- Methods can take parameters beyond `self`: `fn add(self, other: Point) -> Point`; when calling, the parentheses hold only the non-`self` arguments.
- Both `struct`s and `enum`s can have methods.
