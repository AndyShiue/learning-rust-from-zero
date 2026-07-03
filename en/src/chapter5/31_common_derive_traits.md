# Common `derive` `trait`s

## Goal of This Episode

Learn the uses of, and differences between, the common `derive` `trait`s: `PartialEq`, `Eq`, `PartialOrd`, `Ord`, `Default`, and friends.

## Concept

Chapter 4 covered `Debug`, `Clone`, and `Copy`. Rust's standard library has other `derive`-able `trait`s — today we meet the most common ones.

### `PartialEq` and `Eq`

`PartialEq` lets your type be compared with `==` and `!=`.

```rust,noplayground
#[derive(PartialEq)]
struct Point { x: i32, y: i32 }
#
# fn main() {}
```

`Eq` is a supertrait relationship on top of `PartialEq` (last episode's topic); it guarantees **reflexivity** — every value equals itself.

"Wait, what value doesn't equal itself?" — `f64::NAN`! In the floating-point standard, `NAN != NAN`. That's why `f64` has only `PartialEq`, not `Eq`.

If your type contains no floats, you can usually `derive` both `PartialEq` and `Eq`.

### `PartialOrd` and `Ord`

`PartialOrd` lets your type be compared with `<`, `>`, `<=`, `>=`.

`Ord` is a total ordering — guaranteeing any two values can be ranked. Because of `NAN`, `f64` has only `PartialOrd`, not `Ord`.

`NAN` compared with anything returns `false` — including itself:

```rust,editable
fn main() {
    let nan = f64::NAN;
    println!("{}", nan < 1.0);  // false
    println!("{}", nan > 1.0);  // false
    println!("{}", nan == nan); // false
    println!("{}", nan <= nan); // false
}
```

That's why `f64` can't have `Ord` — there's no way to place `NAN` in a sorted order, since every comparison with it is `false`; no position makes sense for it.

### The Full Relationship among the Four `trait`s

First their definitions (simplified):

```rust,ignore
pub trait PartialEq { ... }
pub trait Eq: PartialEq { }
pub trait PartialOrd: PartialEq { ... }
pub trait Ord: PartialOrd + Eq { ... }
```

Organized as an inheritance picture:

- `Eq: PartialEq` — total equality presupposes partial equality.
- `PartialOrd: PartialEq` — comparing sizes presupposes comparing equality (since `<=` subsumes `==`).
- `Ord: PartialOrd + Eq` — total ordering presupposes partial ordering **and** total equality.

Why does `PartialOrd` require `PartialEq`? Because "comparing sizes" implicitly involves "judging equality" — if `a <= b` and `b <= a`, then `a == b`.

Why does `Ord` require `Eq`? Because a total ordering must compare any two values, equal ones included. And `Ord` guarantees every value a definite position, so values like `NAN` that "aren't equal to themselves" aren't allowed.

That's why `f64` can only walk one side (`PartialEq` + `PartialOrd`) and never reach the other (`Eq` + `Ord`).

### `Default`

The `Default` `trait` provides a "default value." Numbers default to `0`, `bool` to `false`, `String` to the empty string, `Vec` to an empty `Vec`.

If every field of a struct has `Default`, you can `derive` it:

```rust,noplayground
#[derive(Debug, Default)]
struct Config {
    width: i32,
    height: i32,
    title: String,
}

fn main() {
    let config = Config::default();
    // Config { width: 0, height: 0, title: "" }
}
```

## Example Code

```rust,editable
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Clone, Default)]
struct Student {
    grade: i32,
    name: String,
}

fn main() {
    let alice = Student { grade: 90, name: String::from("Alice") };
    let bob = Student { grade: 85, name: String::from("Bob") };
    let alice2 = Student { grade: 90, name: String::from("Alice") };

    // PartialEq: == and !=
    println!("alice == alice2: {}", alice == alice2);
    println!("alice == bob: {}", alice == bob);
    println!("alice != bob: {}", alice != bob);

    // PartialOrd: < > <= >=
    // The derived Ord compares fields in declaration order (grade first, then name)
    println!("alice > bob: {}", alice > bob);
    println!("bob < alice: {}", bob < alice);

    // Sorting requires Ord
    let mut students = vec![
        Student { grade: 70, name: String::from("Charlie") },
        Student { grade: 90, name: String::from("Alice") },
        Student { grade: 85, name: String::from("Bob") },
    ];

    students.sort();
    for s in &students {
        println!("{}: {}", s.name, s.grade);
    }

    // f64's special case: NAN
    let nan = f64::NAN;
    println!("NAN == NAN: {}", nan == nan); // false!
    println!("NAN < 1.0: {}", nan < 1.0);   // false!
    println!("NAN > 1.0: {}", nan > 1.0);   // false!

    // f64 has no Ord, so .sort() won't work
    // let mut floats = vec![1.0, 2.0, f64::NAN];
    // floats.sort(); // Compile error! f64 doesn't implement Ord

    // Default
    let default_student = Student::default();
    println!("Default student: {:?}", default_student);
    // Student { grade: 0, name: "" }
}
```

## Recap

- `PartialEq`: `==`, `!=` comparisons; `Eq`: guarantees reflexivity (`NAN` being the exception).
- `PartialOrd`: `<`, `>`, `<=`, `>=` comparisons; `Ord`: guarantees a total ordering.
- Because of `NAN`, `f64` has only the `Partial` versions, never the total ones.
- The derived `Ord` compares fields one by one in declaration order.
- `Default`: provides default values (numbers `0`, `bool` `false`, `String` empty).
