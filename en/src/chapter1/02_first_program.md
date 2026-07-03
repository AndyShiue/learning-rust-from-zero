# Your First Program

## Goal of This Episode

Create a project with Cargo and run the very first Rust program of your life.

## Main Text

Last episode we got Rust installed, so today let's write our first program!

### Creating a Project with Cargo

Rust comes with a wonderfully handy tool called **Cargo**, Rust's project management tool. You can think of it as a butler that organizes your code, compiles it, and runs it — it takes care of everything.

Open a terminal and type:

```bash
cargo new hello
```

This creates a folder named `hello` for you, with a basic file structure already set up inside.

### Opening It in VS Code

Next, open the `hello` folder in VS Code (or your favorite editor). You'll see two important things:

1. **Cargo.toml** — This is the project's configuration file. It records things like your project's name and version. You don't need to worry about it right now; just know it exists.

2. **src/main.rs** — This is your code! Open it up and take a look:

```rust,editable
fn main() {
    println!("Hello, world!");
}
```

This is the first program Rust generated for you automatically. `fn main()` is the entry point of the program — every program starts running from here. `println!` is the command for printing things to the screen. Throughout Chapter 1, we'll only ever write code inside the curly braces that follow `fn main()`.

### What Is Compiling?

Before we run the program, let's cover an important concept.

The `.rs` files we write contain code meant for humans to read — computers can't actually understand it. So we need a translation step that turns the code we write into a file the computer can execute directly. This translation step is called **compiling**.

The tool responsible for this is called a **compiler**, and Rust's compiler is the `rustc` we installed last episode.

The good news is that you don't need to invoke `rustc` yourself: the `cargo run` command we're about to use will automatically compile and then run your program, all in one step.

### Let's Run It

Back in the terminal, first go into the `hello` folder:

```bash
cd hello
```

Then type:

```bash
cargo run
```

You should see this printed on the screen:

```ignore
Hello, world!
```

Fantastic! Your first Rust program is up and running!

### Change It and Run It Again

Now go back to your favorite text editor and change the text inside `println!` to:

```rust,editable
fn main() {
    println!("Hello, Rust!");
}
```

Save the file, then go back to the terminal and run `cargo run` again:

```ignore
Hello, Rust!
```

See that? Whatever you change it to, that's what it prints. That's what programming is all about — you tell the computer what to do, and it does exactly that.

## Recap

- **Cargo** is Rust's project management tool; use `cargo new` to create a new project.
- Inside a project, `Cargo.toml` is the configuration file and `src/main.rs` is the main code.
- **Compiling** means translating human-readable code into a file the computer can run.
- Use `cargo run` to compile and run in one step.
- `fn main()` is the program's entry point, and `println!` prints things to the screen.
