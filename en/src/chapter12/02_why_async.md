# Why `async` Is Needed

## Goal of This Episode

Understand what kinds of programs `async` suits, and clearly separate two often-confused words: "concurrency" and "parallelism."

## Main Text

### Why `async` Exists

Last episode's server had one defining characteristic: it spends most of its time **waiting**. Waiting for someone to connect, for data to arrive, for a response to be written out. The time actually spent computing on the CPU is pitifully small.

Programs that "mostly wait" are in fact everywhere:

- Web servers: waiting for clients to send requests, for the database to answer.
- Crawlers: firing off a pile of network requests, then waiting for replies.
- Database queries: sending the query, waiting for results.
- Chat rooms: waiting for each user to type a message.
- All sorts of background jobs: waiting on timers, files, other programs.

The bottleneck in these programs isn't "the CPU can't compute fast enough" — it's "too much time spent waiting." `async` was born for this situation: it lets your program, while waiting on one thing, put its precious `Thread`s to work advancing other jobs.

### Why Not Just Open Lots of `Thread`s

You might think: didn't earlier chapters teach multithreading? To handle ten thousand connections at once, just open ten thousand `Thread`s?

The problem is cost. Operating system `Thread`s (OS `Thread`s) are **memory-hungry** — for each one, the OS has to set aside stack space, often several MB. Ten thousand `Thread`s could eat several GB of memory, before even counting the OS's overhead of switching among that many `Thread`s. For a program that "mostly waits," opening ten thousand `Thread`s and letting nearly all of them sleep is extravagant indeed.

`async` takes a different approach: it can use **just a few** `Thread`s to advance **thousands upon thousands** of waiting jobs in turn. Each job no longer corresponds to a heavyweight OS `Thread`, but to something lightweight (we'll gradually see its true face later). That's how `async` supports huge numbers of connections.

### Concurrency vs Parallelism

Time to nail down two easily confused words, because they're key to understanding `async`.

**Concurrency**: *handling* many things at once, by way of "interleaved switching." Picture one barista covering several tables alone: he takes table A's order, and while the coffee machine is brewing, goes to take table B's order, then returns to finish up with table A. At any single instant he's really doing only one thing, but because he knows to switch to something else during the "waiting" gaps, it looks like he's serving many tables at once. One person — one `Thread` — is enough for concurrency.

**Parallelism**: at the same instant, many things truly *executing* together. This needs multiple CPU cores — like a coffee shop with several baristas, each covering their own table, genuinely working at the same time.

These are **two independent dimensions**, freely combinable:

- Single-threaded `async`: concurrency, no parallelism (one barista serving tables in turn).
- Pure computation thrown onto multiple cores: parallelism (several baristas), no need for `async`'s concurrency.
- A multithreaded runtime (Tokio's default): both (several baristas, each of whom also switches tables during the gaps).

### What `async` Provides Is Concurrency

Here comes the key conclusion: **`async` itself provides concurrency** — it lets a few `Thread`s advance a large pile of waiting jobs, interleaved. Whether you also get **parallelism** is decided by how many `Thread`s the runtime uses to run those jobs.

So remember: `async` **does not make your CPU computations faster**. If your program is grinding through a resource-hungry math computation, `async` can't help — that's a problem only parallelism (spreading over multicore processors) can solve. `async` solves a different problem — **making sure waiting time isn't wasted**, switching to other work during the gaps.

Starting next episode, we take "what exactly is `async`" apart, layer by layer.

## Recap

- `async` suits programs that "spend most of their time waiting on I/O": servers, crawlers, databases, chat rooms, background jobs.
- OS `Thread`s are memory-hungry; "one `Thread` per connection" can't sustain huge connection counts — `async` advances masses of work on just a few `Thread`s.
- **Concurrency** is interleaved switching, *handling* many things at once — one `Thread` suffices (the barista analogy); **parallelism** is multiple cores truly *executing* at the same instant.
- `async` provides concurrency; parallelism depends on how many `Thread`s the runtime uses.
- `async` doesn't speed up computation; it just lets waiting time be spent on other work.
