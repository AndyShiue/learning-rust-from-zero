# `mod`

## Goal of This Episode

Learn to organize code into a layered structure with `mod`.

## Concept

As programs grow longer, cramming everything into one `main.rs` becomes hard to maintain. We need to group related functions, `struct`s, and `enum`s — and in Rust, that grouping mechanism is the **module (`mod`)**.

### Defining a `mod` in the Same File

The simplest usage: create a block right in the file with the `mod` keyword.

```rust,noplayground
mod math {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }

    pub fn multiply(a: i32, b: i32) -> i32 {
        a * b
    }
}
#
# fn main() {}
```

Call a `mod`'s functions with the `::` path syntax:

```rust,noplayground
# mod math {
#     pub fn add(a: i32, b: i32) -> i32 {
#         a + b
#     }
#
#     pub fn multiply(a: i32, b: i32) -> i32 {
#         a * b
#     }
# }
#
# fn main() {
    let result = math::add(3, 5);
# }
```

Note that `pub` — things inside a `mod` are **private by default**. Without `pub`, the outside can't see or use them. The full rules for `pub` come in Episode 4; for now, remember: want outside access, add `pub`.

### Nested `mod`s

`mod`s can nest, layer within layer:

```rust,noplayground
mod math {
    pub mod basic {
        pub fn add(a: i32, b: i32) -> i32 {
            a + b
        }
    }

    pub mod advanced {
        pub fn power(base: i32, exp: u32) -> i32 {
            let mut result = 1;
            for _ in 0..exp {
                result *= base;
            }
            result
        }
    }
}
#
# fn main() {}
```

Calls then use the full path:

```rust,noplayground
# mod math {
#     pub mod basic {
#         pub fn add(a: i32, b: i32) -> i32 {
#             a + b
#         }
#     }
#
#     pub mod advanced {
#         pub fn power(base: i32, exp: u32) -> i32 {
#             let mut result = 1;
#             for _ in 0..exp {
#                 result *= base;
#             }
#             result
#         }
#     }
# }
#
# fn main() {
    let sum = math::basic::add(2, 3);
    let p = math::advanced::power(2, 10);
# }
```

It's like a filesystem's folder structure — `math` holds two sub-`mod`s, `basic` and `advanced`.

## Example Code

```rust,editable
mod geometry {
    pub struct Rectangle {
        pub width: f64,
        pub height: f64,
    }

    impl Rectangle {
        pub fn new(width: f64, height: f64) -> Rectangle {
            Rectangle { width, height }
        }

        pub fn area(&self) -> f64 {
            self.width * self.height
        }
    }

    pub mod utils {
        pub fn describe_shape(name: &str, area: f64) {
            println!("The area of the {} is {}", name, area);
        }
    }
}

fn main() {
    let rect = geometry::Rectangle::new(10.0, 5.0);
    let area = rect.area();
    geometry::utils::describe_shape("rectangle", area);
}
```

## Recap

- `mod name { ... }` creates a `mod` in the same file.
- Things inside a `mod` are called with the `mod_name::item` path syntax.
- `mod`s can nest, making paths ever longer: `a::b::c::func()`.
- Everything inside a `mod` is **private by default**; external use requires `pub`.
- `mod` is Rust's basic unit of code organization — like folders organizing files.
