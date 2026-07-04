# Testing `async` Programs

## Goal of This Episode

Learn to write `async` tests with `#[tokio::test]`, and use virtual time to make delay-related tests fast and reliable.

## Main Text

### `#[tokio::test]`

Chapter 7 taught testing with `#[test]` and `cargo test`. But `#[test]` marks an ordinary function, which can't `.await`. To test `async` code, Tokio provides `#[tokio::test]` — it automatically wraps your test function in a runtime, so you don't `block_on` yourself:

```rust,noplayground
# extern crate tokio;
#
async fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[tokio::test]
async fn test_add() {
    let result = add(2, 3).await;
    assert_eq!(result, 5);
}
#
# fn main() {}
```

That's all there is to it. `#[tokio::test]` equals "`#[test]` + automatic runtime setup + `async` allowed." Everything else matches Chapter 7: put tests in `#[cfg(test)] mod tests`, run them with `cargo test`, check results with macros like `assert_eq!`.

### What About Time-dependent Tests

`async` programs constantly involve time — timeouts, delays, scheduled retries. Tested literally, a "times out after 5 seconds" behavior means the test really waits 5 seconds — slow and annoying.

Tokio's answer is **virtual time**: time in the test is advanced **manually by you**, with no real waiting. Two key functions:

- `tokio::time::pause()`: "pause" time; from then on it doesn't flow by itself.
- `tokio::time::advance(duration)`: manually fast-forward time by a stretch.

```rust,noplayground
# extern crate tokio;
#
use tokio::time::{self, Duration};

#[tokio::test]
async fn test_with_virtual_time() {
    time::pause(); // pause time

    let start = time::Instant::now();

    // push virtual time forward 10 seconds — instant, no real waiting
    time::advance(Duration::from_secs(10)).await;

    assert_eq!(start.elapsed(), Duration::from_secs(10));
}
#
# fn main() {}
```

This test finishes **instantly**, even though logically "10 seconds passed." Time is virtual, and `advance` just jumps over it. If you want time paused from the very start, write `#[tokio::test(start_paused = true)]` and skip the manual `pause()` call.

With virtual time, any test involving timeouts, delays, or retry intervals becomes **deterministic (same result every run)** and fast — you fully control how time moves, no longer at the mercy of the real clock.

(Small reminder: the virtual-time tools `pause` / `advance` require Tokio's `test-util` feature — just add `"test-util"` to Tokio's features in `Cargo.toml`.)

## Recap

- `#[tokio::test]` wraps the test function in a runtime and allows `.await` — "`#[test]` + runtime + `async`"; everything else works like Chapter 7's `cargo test`.
- Don't use real time in time-dependent tests (slow and flaky); use Tokio's virtual time.
- `tokio::time::pause()` stops time, `tokio::time::advance(duration)` fast-forwards manually, making timeout/delay tests instant and deterministic.
- `#[tokio::test(start_paused = true)]` pauses time from the start; the virtual-time tools need Tokio's `test-util` feature.
