# `macro_rules!`

## Goal of This Episode

Learn to define your own declarative macros with `macro_rules!`.

## Concept

### Macros vs Functions

We've been using macros since Chapter 1 — `println!`, `vec!`, `format!`, `assert_eq!`. The exclamation mark `!` in the call is what distinguishes a macro from a function.

The most fundamental difference between macros and functions: macros **expand into code at compile time**. The macro call you write gets replaced during compilation by its expanded code, and the compiler then compiles that expanded result. Macros can produce arbitrary code — new functions, `struct`s, even other macro calls. They can also accept things that aren't values as arguments — type names, patterns, and so on.

But macros are also harder to write, harder to read, and give worse error messages. If a function will do, don't use a macro.

### Basic Syntax

```rust,editable
macro_rules! say_hello {
    () => {
        println!("Hello!");
    };
}

fn main() {
    say_hello!(); // prints Hello!
}
```

The structure is `(pattern) => { expansion }` — match on the left, expand on the right.

### With Parameters

Capture parameters with `$name:kind`:

```rust,editable
macro_rules! say {
    ($msg:expr) => {
        println!("{}", $msg);
    };
}

fn main() {
    say!("hi");
    say!(1 + 2);
}
```

Common kinds:
- `expr`: an expression
- `ty`: a type
- `ident`: an identifier (like a variable name)
- `tt`: a token tree (the most flexible)

There are other kinds too; look them up if you ever need them.

### Multiple Arms

```rust,editable
macro_rules! log {
    ($val:expr) => {
        println!("value: {}", $val);
    };
    ($name:expr, $val:expr) => {
        println!("{} = {}", $name, $val);
    };
}

fn main() {
    log!(42);           // value: 42
    log!("score", 100); // score = 100
}
```

### Repetition

The `$( ... ),*` syntax matches repeated items. Broken down:

- `$( ... )` holds the pattern to repeat.
- `,` is the separator — each repetition is separated by a comma. The separator doesn't have to be a comma; you can use `;` or other symbols, or omit it.
- `*` means zero or more. You can also use `+` for one or more.

```rust,noplayground
macro_rules! make_vec {
    ($($element:expr),*) => {
        {
            let mut v = Vec::new();
            $( v.push($element); )*
            v
        }
    };
}

fn main() {
    let v = make_vec![1, 2, 3];
}
```

Expansion also uses `$( ... )*` — `$( v.push($element); )*` expands once per captured element, becoming:

```rust,ignore
v.push(1);
v.push(2);
v.push(3);
```

### Three Kinds of Brackets

Macros can be called with three kinds of brackets, with identical effect:
- `macro!(...)` — parentheses, like a function call.
- `macro![...]` — square brackets, like an array (`vec![1,2,3]` uses these).
- `macro!{...}` — curly braces, like a code block.

The difference is purely convention.

### Macro Scope

A macro defined with `macro_rules!` can only be used after its definition (unlike functions — functions aren't restricted by definition order).

To make a macro usable by other `crate`s, add `#[macro_export]` in front. When referring to items from the defining `crate` inside the macro, use the `$crate` path — that way the path resolves correctly no matter what name the user's `crate` gives yours:

```rust,noplayground
// in the my_lib crate

pub fn _log_impl(msg: &str) {
    println!("[LOG] {}", msg);
}

#[macro_export]
macro_rules! log_msg {
    ($msg:expr) => {
        $crate::_log_impl($msg);
    };
}
#
# fn main() {}
```

A `crate` that depends on `my_lib` can call the macro as `my_lib::log_msg!("hello")`, or import it with `use my_lib::log_msg;` and then write `log_msg!("hello")`. `$crate` automatically resolves to the `crate` where the macro was defined.

## Example Code

```rust,editable
macro_rules! max {
    ($a:expr, $b:expr) => {{
        let a = $a;
        let b = $b;
        if a > b { a } else { b }
    }};
}

macro_rules! print_all {
    ($($item:expr),*) => {
        $(
            println!("{}", $item);
        )*
    };
}

// stringify! is a built-in macro that turns whatever you pass in into a string verbatim
// stringify!(hello) becomes "hello"
macro_rules! create_fn {
    ($name:ident) => {
        fn $name() {
            println!("called the function {}", stringify!($name));
        }
    };
}

create_fn!(hello);
create_fn!(world);

fn main() {
    println!("max(3, 7) = {}", max!(3, 7));

    print_all!["a", "b", "c"];

    hello();
    world();
}
```

## Recap

- If a function will do, don't use a macro.
- `macro_rules!` defines declarative macros: `(pattern) => { expansion }`.
- Receive parameters with `$name:expr` etc.; common kinds: `expr`, `ty`, `ident`, `tt`.
- `$(...),*` matches repeated items; `$( ... )*` in the expansion repeats per item.
- The three bracket styles `()` / `[]` / `{}` behave identically.
- Macros are usable only after their definition (unlike functions).
- `#[macro_export]` makes a macro usable from other `crate`s.
