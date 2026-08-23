# `'a: 'b`

## Goal of This Episode

Understand what `'a: 'b` actually solves: when a generic API juggles long-lived data and short-lived operations at once, how to tell the compiler explicitly which lifetime has to live longer.

> This episode supplements **Chapter 5's lifetimes**.

## Main Text

Chapter 5 showed this kind of bound:

```rust,ignore
T: 'a
```

It says every reference inside `T` must outlive `'a`. Both sides of the bound can be lifetimes too:

```rust,ignore
'a: 'b
```

This reads "`'a` **outlives** `'b`," meaning `'a` lasts at least as long as `'b`.

The real purpose of this notation isn't to work out which of two local variables goes out of scope first — it's to **hand generic code a guarantee it can use**. If `'a` and `'b` are two unrelated lifetime parameters, a function or type can't assume on its own which is longer; only once `'a: 'b` is added can the code safely take data tied to `'a` and place it somewhere that only needs to last for `'b`.

### A Practical Problem: A Long-lived Setting as a Short-lived Fallback

Suppose a service has long-lived configuration but also lets each request name a language temporarily:

```rust,noplayground
struct Config {
    default_language: String,
}
#
# fn main() {}
```

We want `language_for_request` to return the request's language when there is one, and otherwise borrow the default from the config:

```rust,compile_fail
struct Config {
    default_language: String,
}

fn language_for_request<'config, 'request>(
    config: &'config Config,
    requested: Option<&'request str>,
) -> &'request str {
    match requested {
        Some(language) => language,
        None => &config.default_language,
    }
}
#
# fn main() {}
```

This doesn't compile. The `Some` branch returns an `&'request str`, but the `None` branch returns an `&'config str` borrowed from `config`. The signature declares two lifetimes and says nothing about how their lengths relate.

As far as the compiler knows, the caller might hand over a very short-lived `config` while demanding the function return an `&'request str` that lives longer. So it can't simply treat an `&'config str` as an `&'request str`.

This is exactly what `'config: 'request` is for:

```rust,editable
struct Config {
    default_language: String,
}

fn language_for_request<'config, 'request>(
    config: &'config Config,
    requested: Option<&'request str>,
) -> &'request str
where
    'config: 'request,
{
    match requested {
        Some(language) => language,
        None => &config.default_language,
    }
}

fn main() {
    let config = Config {
        default_language: String::from("zh-TW"),
    };

    {
        let request_language = String::from("en");
        let selected = language_for_request(&config, Some(&request_language));
        println!("Specified by the request: {selected}");
    }

    {
        let selected = language_for_request(&config, None);
        println!("Using the default: {selected}");
    }
}
```

`'config: 'request` guarantees the configuration data stays valid throughout `'request`. The `None` branch can therefore **shorten** its `&'config str` into an `&'request str`, letting both branches return the same type.

That is the most direct practical use of lifetime-outlives-lifetime:

- The input data comes from two lifetimes playing different roles.
- The API picks one of them as the lifetime of the return value or of the result of an operation.
- If the other piece of data may also become a source for that result, it must be guaranteed to outlive that lifetime.

### Which APIs Have This Relationship?

Don't bother memorizing a pile of API names yet. This relationship usually just describes the following situation:

> There is a longer-lived piece of data; we borrow it temporarily to produce a result or a tool that will only be used for a short while.

The `Config` above is exactly that:

- `config.default_language` lives longer.
- `language_for_request` only needs to return an `&str` valid for the duration of this request.
- Hence the configuration's lifetime must outlive the request's lifetime.

The `DebugStruct` coming up is the same thing:

- The `Formatter` and the output target it writes to live longer.
- `DebugStruct` only borrows the `Formatter` temporarily, to help assemble this one piece of output.
- Hence the lifetime of the data inside the `Formatter` must cover the lifetime of the reference `DebugStruct` holds.

In ordinary code the compiler can often infer this relationship on its own, so you won't see `'long: 'short` scattered everywhere. It shows up mostly in library type signatures. For now, just remember: **when you temporarily borrow long-lived data, that data can't expire before the reference you obtained from it.**

### A Real Case: `DebugStruct<'a, 'b>`

The standard library's `DebugStruct`, which helps implement `Debug`, is defined roughly like this:

```rust,ignore
pub struct DebugStruct<'a, 'b: 'a> {
    fmt: &'a mut Formatter<'b>,
    // Other fields omitted
}
```

`'b: 'a` is the same as writing the `where` clause below:

```rust,ignore
pub struct DebugStruct<'a, 'b>
where
    'b: 'a,
{
    fmt: &'a mut Formatter<'b>,
}
```

The two lifetimes here each have a clear role:

- `'a` is the period during which `DebugStruct` temporarily borrows the `Formatter`.
- `'b` is the lifetime of the output target inside the `Formatter`.

During `'a`, `DebugStruct` writes to that output target through `Formatter<'b>`, so the target mustn't expire while the builder still exists. `'b: 'a` is precisely that requirement: the data borrowed inside the `Formatter` must outlive the reference held by the outer builder.

Users normally never have to write these two lifetimes themselves:

```rust,editable
use std::fmt;

struct Account {
    id: u64,
    token: String,
}

impl fmt::Debug for Account {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("Account")
            .field("id", &self.id)
            .field("token", &"<hidden>")
            .finish()
    }
}

fn main() {
    let account = Account {
        id: 7,
        token: String::from("secret-token"),
    };

    println!("{account:?}");
}
```

This code really does use `DebugStruct`, but `Formatter::debug_struct` has already baked the correct lifetime relationship into the API — the caller only has to satisfy it. You typically encounter or write `'b: 'a` directly only when reading standard library documentation, building a generic wrapper around this sort of builder, or designing your own type containing several layers of references.

### What's the Benefit of Separating the Two Lifetimes?

Why doesn't `DebugStruct` just use a single lifetime? We can write a simplified pair to compare.

Let `FormatterLike` stand in for `Formatter`. It borrows the `String` that actually holds the output text:

```rust,ignore
struct FormatterLike<'buffer> {
    output: &'buffer mut String,
}
```

If the builder used only one `'a`, the outer reference to `FormatterLike` and the inner reference to the `String` would be forced onto the same lifetime:

```rust,compile_fail
struct FormatterLike<'buffer> {
    output: &'buffer mut String,
}

struct BadBuilder<'a> {
    formatter: &'a mut FormatterLike<'a>,
}

impl BadBuilder<'_> {
    fn field(&mut self, text: &str) {
        self.formatter.output.push_str(text);
    }
}

fn write_two_parts<'buffer>(formatter: &mut FormatterLike<'buffer>) {
    let mut first = BadBuilder { formatter };
    first.field("first part");

    formatter.output.push(' ');

    let mut second = BadBuilder { formatter };
    second.field("second part");
}
#
# fn main() {}
```

The `String` inside `FormatterLike<'buffer>` may be borrowed for a long time, but `BadBuilder` really only needs to borrow `formatter` briefly. Writing both as `'a` forces the compiler to tie the outer mutable reference and the inner data to the same length, so `formatter` remains unusable even after the first builder is done.

Splitting them into two lifetimes describes the requirement precisely:

```rust,editable
struct FormatterLike<'buffer> {
    output: &'buffer mut String,
}

struct Builder<'borrow, 'buffer: 'borrow> {
    formatter: &'borrow mut FormatterLike<'buffer>,
}

impl Builder<'_, '_> {
    fn field(&mut self, text: &str) {
        self.formatter.output.push_str(text);
    }
}

fn write_two_parts<'buffer>(formatter: &mut FormatterLike<'buffer>) {
    let mut first = Builder { formatter };
    first.field("first part");

    formatter.output.push(' ');

    let mut second = Builder { formatter };
    second.field("second part");
}

fn main() {
    let mut output = String::new();
    let mut formatter = FormatterLike {
        output: &mut output,
    };
    write_two_parts(&mut formatter);

    println!("{output}");
}
```

Here `'buffer` is how long the inner `String` is borrowed, while `'borrow` is how long one particular builder temporarily borrows the `FormatterLike`. `'buffer: 'borrow` only demands that the inner output outlive this short-lived reference; it doesn't extend the short-lived reference in return.

The variables and scopes are identical in both versions — the only difference is the builder's lifetime design. In the correct version, once `first` is used for the last time the compiler can end the `formatter` reference it holds; after that you can write to `formatter` directly and build a second `Builder`. Using two lifetimes in `DebugStruct<'a, 'b: 'a>` buys exactly this flexibility: **the underlying output can live a long time, while each formatting builder borrows the `Formatter` only briefly, when it needs to.**

### It Doesn't Work in Reverse

An outlives bound only lets you use a longer guarantee as a shorter one; it can't make short-lived data live longer out of thin air:

```rust,compile_fail
fn extend<'short, 'long>(short: &'short str, _long: &'long str) -> &'long str
where
    'long: 'short,
{
    short
}
#
# fn main() {}
```

`'long: 'short` says `'long` is longer than `'short`, yet the function wants to return a reference guaranteed only to live for `'short` as an `&'long str`. The bound provides no such guarantee, so this doesn't compile.

## Recap

- Two lifetime parameters don't necessarily have any fixed length relationship; generic code can only use the guarantees the signature provides.
- `'long: 'short` provides the guarantee "`'long` lasts at least as long as `'short`."
- With that guarantee, an `&'long T` can be shortened to an `&'short T` and used as the return value of, or an internal reference in, a short-lived operation.
- A long-lived setting acting as the fallback for a short-lived request is a direct application of this bound.
- Ordinary call sites mostly rely on inference; you meet `'a: 'b` head-on mainly when designing or reading generic APIs that keep several lifetime roles apart.
- An outlives bound can only prove an existing relationship — it can't extend anything's lifetime.
