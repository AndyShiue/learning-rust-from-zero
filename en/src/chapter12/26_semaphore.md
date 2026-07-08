# `Semaphore` and backpressure

## Goal of This Episode

Learn to cap "how many things happen at once" with a `Semaphore`, and understand the idea of backpressure.

## Main Text

### Capping Simultaneity

Some things you don't want happening "all together without limit." For instance: don't download too many files at once (or your bandwidth chokes), the number of simultaneously open files has a ceiling, and requests to some API must be throttled (or they'll block you).

`tokio::sync::Semaphore` manages exactly this. Its core is a fixed number of **permits**: you set how many exist in total; whoever wants to work must first take one, returning it when done. When permits run out, latecomers wait until someone returns one.

```rust,editable
extern crate tokio;

use std::sync::Arc;
use tokio::sync::Semaphore;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    // only 3 permits total, so at most 3 tasks can work at once
    let semaphore = Arc::new(Semaphore::new(3));

    let mut handles = vec![];
    for i in 0..10 {
        let semaphore = Arc::clone(&semaphore);
        handles.push(tokio::spawn(async move {
            // take a permit, .awaiting if none is available
            let _permit = semaphore.acquire().await.expect("the semaphore was closed");
            println!("task {} got a permit, starting work", i);
            sleep(Duration::from_millis(100)).await;
            // _permit leaves scope here, automatically returning the slot
        }));
    }

    for h in handles {
        h.await.expect("a task failed");
    }
}
```

We spawned 10 tasks, but with only 3 permits, at most 3 are working at any moment; the rest queue up dutifully waiting for a permit.

### Permits Return Themselves via `Drop`

Notice that after taking the permit above, we **never manually returned it** — how did it come back on its own?

Because the permit implements `Drop`. When `_permit` leaves scope, its `Drop` implementation automatically gives the slot back to the `Semaphore`. So as long as the permit leaves scope at the "right moment to finish," the return happens automatically — impossible to forget. That's also why we bound it to a variable with `let _permit = ...` — to keep it **alive until the work ends** before being `drop`ped. Writing `let _ = ...` would `drop` it immediately, returning the permit at once — no cap enforced at all.

### backpressure

`Semaphore` leads into a more general idea: **backpressure**.

Picture an assembly line: upstream keeps sending items in; downstream processes them slowly. If upstream sends faster than downstream can process, items pile up — a blown-out memory is only a matter of time. Backpressure means: **when downstream can't keep up, there must be a way to make upstream "slow down and wait,"** instead of stuffing without limit.

A `Semaphore` can build that backpressure: permits represent "capacity," and once capacity is full, would-be entrants are held at `acquire().await`, naturally slowing down.

Next episode's **bounded channel** works on the same principle — limited capacity, and when it's full, `send().await` waits, forcing upstream to ease off. So you can understand all the backpressure tools through one lens: "**finite capacity — when full, you wait**."

## Recap

- `tokio::sync::Semaphore` expresses capacity as a fixed number of **permits**, capping "how many at once": simultaneous downloads, open files, `Task`s inside some section, etc.
- `acquire().await` takes a permit, waiting if none is free; permits implement `Drop` and return their slot automatically on leaving scope.
- Use `let _permit = ...` so the permit lives until the work finishes; don't write `let _ = ...` (instant `drop`).
- **backpressure**: make upstream wait when downstream can't keep up, avoiding unbounded pileups; understand `Semaphore` (and next episode's bounded channel) as "finite capacity, wait when full."
