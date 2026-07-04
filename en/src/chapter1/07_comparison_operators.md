# Comparison Operators

## Goal of This Episode

Learn to use comparison operators to compare sizes and check equality.

## Main Text

So far we've been doing math, but there's another very important kind of operation in programming — **comparison**.

The result of a comparison isn't a number; it's `true` or `false`.

### `==` Equal To

```rust,editable
fn main() {
    println!("{}", 5 == 5);
}
```

Is 5 equal to 5? Yes, so it's `true`.

Careful here: it's **two equals signs** `==`, not one. A single equals sign `=` is for assigning values to variables (`let x = 5;`); two equals signs `==` are for comparing.

### `!=` Not Equal To

```rust,editable
fn main() {
    println!("{}", 5 != 3);
}
```

Is 5 not equal to 3? Correct.

### `<` Less Than

```rust,editable
fn main() {
    println!("{}", 3 < 5);
}
```

3 is less than 5.

### `>` Greater Than

```rust,editable
fn main() {
    println!("{}", 10 > 7);
}
```

10 is greater than 7.

### `<=` Less Than or Equal To

```rust,editable
fn main() {
    println!("{}", 5 <= 5);
}
```

Is 5 less than or equal to 5? Being equal counts too.

### `>=` Greater Than or Equal To

```rust,editable
fn main() {
    println!("{}", 8 >= 10);
}
```

Is 8 greater than or equal to 10? No.

### At a Glance

| Operator | Meaning | Example | Result |
|--------|------|------|------|
| `==` | equal to | `5 == 5` | `true` |
| `!=` | not equal to | `5 != 3` | `true` |
| `<` | less than | `3 < 5` | `true` |
| `>` | greater than | `10 > 7` | `true` |
| `<=` | less than or equal to | `5 <= 5` | `true` |
| `>=` | greater than or equal to | `8 >= 10` | `false` |

## Recap

- The six comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`.
- The result of a comparison is `true` or `false`.
- `==` (two equals signs) compares; `=` (one equals sign) assigns. Don't mix them up.
