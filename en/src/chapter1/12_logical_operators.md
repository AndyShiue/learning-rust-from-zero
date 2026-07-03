# Logical Operators

## Goal of This Episode

Learn to combine multiple conditions with `&&` (and), `||` (or), and `!` (not).

## Main Text

Over the last few episodes we learned `if`, but our conditions were all simple — just one at a time. In real life, you often need to consider several conditions at once, such as "at least 18 years old **and** a student." That's where logical operators come in.

### `&&` — AND

**Both** conditions must hold for the result to be `true`:

```rust,editable
fn main() {
    let age = 24;
    let is_student = true;

    if age >= 18 && is_student {
        println!("An adult student");
    }
}
```

Since 24 >= 18 is `true` and `is_student` is also `true`, both hold, so the whole thing is `true`.

If you change `age` to 15, then 15 >= 18 is `false`, and no matter whether `is_student` is `true` or not, the whole thing is `false`, so nothing is printed.

### `||` — OR

As long as **either** condition holds, the result is `true`:

```rust,editable
fn main() {
    let is_weekend = false;
    let is_holiday = true;

    if is_weekend || is_holiday {
        println!("No work today!");
    }
}
```

Although `is_weekend` is `false`, `is_holiday` is `true` — one `true` is all it takes.

### `!` — NOT

Turns `true` into `false` and `false` into `true`:

```rust,editable
fn main() {
    let raining = false;

    if !raining {
        println!("Let's go out for a walk!");
    }
}
```

`raining` is `false`; with `!` in front it becomes `true`, so the condition holds.

You can read it as: "If it's **not** raining, go out for a walk."

## Recap

- `&&` (and): `true` only when both sides are `true`.
- `||` (or): `true` as long as either side is `true`.
- `!` (not): turns `true` into `false` and `false` into `true`.
- Combine multiple conditions with logical operators to write more precise checks.
