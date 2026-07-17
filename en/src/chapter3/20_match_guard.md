# `match` Guards

## Goal of This Episode

Learn to add extra conditional checks (guards) to `match` arms.

## Concept

Patterns are good at checking the shape of data, fixed values, and ranges. However, a pattern does not evaluate comparisons between fields such as `from == to`, and a variable created with `let` cannot be used as the bound of a range pattern. A `match` guard handles these extra computations.

A **`match` guard** adds an `if condition` after a pattern:

```text
pattern if condition => ...
```

For example, a sensor reading carries a room number and a measured value. A pattern can first destructure those fields, and a guard can then check whether the measurement has crossed a warning level:

```rust,editable
enum Reading {
    Temperature { room: i32, celsius: i32 },
    Humidity { room: i32, percent: i32 },
    Offline { room: i32 },
}

fn main() {
    let reading = Reading::Temperature {
        room: 3,
        celsius: 34,
    };
    let heat_warning = 30;

    match reading {
        Reading::Temperature { room, celsius } if celsius >= heat_warning => {
            println!("Room {} is too hot: {} degrees", room, celsius);
        }
        Reading::Temperature { room, celsius } => {
            println!("Room {} has a normal temperature: {} degrees", room, celsius);
        }
        Reading::Humidity { room, percent } if percent > 70 => {
            println!("Room {} is too humid: {}%", room, percent);
        }
        Reading::Humidity { room, percent } => {
            println!("Room {} has normal humidity: {}%", room, percent);
        }
        Reading::Offline { room } => {
            println!("The sensor in room {} is offline", room);
        }
    }
}
```

The first arm happens in two steps:

1. `Reading::Temperature { room, celsius }` first confirms that the value is a `Temperature` reading and binds its two fields to `room` and `celsius`.
2. `if celsius >= heat_warning` then uses the newly bound `celsius` in an extra check.

After the pattern matches, `room` and `celsius` are available in both the guard and the code on the right. A guard can also use variables that existed before the pattern, such as `heat_warning` above.

## A Failed Guard Tries the Next Arm

A matching pattern does not necessarily mean that its arm runs. If the guard is `false`, Rust continues trying the later arms.

For the temperature example:

- A `Temperature` with `celsius >= heat_warning` runs the first arm.
- If it is a `Temperature` below the warning level, the first guard fails and the second `Temperature` arm handles it.
- If it is not a `Temperature` at all, neither of those two patterns matches, so Rust continues looking for another variant.

An arm with a guard therefore usually goes before the more general arm that handles its remaining cases.

A guard can compare not only one field with a limit, but also multiple fields bound by the same pattern:

In the example below, the first guard compares `from` with `to`, while the second compares `amount` with the outer `daily_limit`. Conditions involving calculations between fields or values chosen at runtime are where guards are more appropriate than plain patterns.

## Example Code

```rust,editable
enum Request {
    Transfer {
        from: i32,
        to: i32,
        amount: i32,
    },
    CheckBalance {
        account: i32,
    },
}

fn main() {
    let request = Request::Transfer {
        from: 1001,
        to: 2002,
        amount: 1500,
    };
    let daily_limit = 1000;

    match request {
        Request::Transfer { from, to, amount } if from == to => {
            println!(
                "Account {} does not need to transfer {} to itself",
                from, amount
            );
        }
        Request::Transfer { from, to, amount } if amount > daily_limit => {
            println!(
                "Transfer {} from account {} to account {}: extra confirmation required",
                amount, from, to
            );
        }
        Request::Transfer { from, to, amount } => {
            println!(
                "Transfer {} from account {} to account {}",
                amount, from, to
            );
        }
        Request::CheckBalance { account } => {
            println!("Check the balance of account {}", account);
        }
    }
}
```

## Guards and Exhaustiveness

Suppose we write two arms for `Temperature`:

- One guard is `celsius >= heat_warning`.
- The other guard is `celsius < heat_warning`.

We can see that every temperature must satisfy one of those conditions, so the two arms logically cover every possibility. However, Rust's exhaustiveness check may not be able to infer from the logical relationship between the guards that every temperature has been handled. Even with both arms present, the compiler may still consider `Temperature` not fully covered.

To make the coverage clear to the compiler as well, keep a **pattern without a guard**. That is why the second `Temperature` arm in the earlier example has no guard: the first arm handles temperatures at or above the warning level, and the second catches every remaining temperature. The `Humidity` and `Transfer` arms follow the same arrangement.

## Recap

- A `match` guard has the syntax `pattern if condition => ...`.
- Rust first matches the pattern and creates its bindings, then checks the guard.
- A guard can use variables bound by the same pattern as well as variables that already exist outside it.
- If the pattern matches but the guard is `false`, Rust continues trying the later arms.
- Even when several guards logically cover every possibility, the compiler may still need an arm without a guard to confirm that the `match` is exhaustive.
- Guards are especially useful for comparisons between fields, calculations, and comparisons with runtime limits.
