# Installing Rust

## Goal of This Episode

Get Rust installed on your computer and make sure it works.

## Main Text

Hello! Welcome to this Rust tutorial series!

This is episode one, and we won't write any code yet — we'll just get the tools set up. If you want to cook, you need a pot first, right?

### Installing rustup

Rust has an official installation tool called **rustup**, which installs everything you need in one go.

Open your browser and head to this URL:

```ignore
https://rustup.rs
```

- **Windows users**: Download `rustup-init.exe`, double-click to run it, and just keep pressing enter to accept the defaults.
- **Mac / Linux users**: Open a terminal and paste in this command:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

It will ask whether you want to use the default settings — just press enter.

### Confirming the Installation Succeeded

Once it's done, open a **new** terminal (this matters — the old one may not pick up the changes yet), and type:

```bash
rustc --version
```

If you see something like this:

```ignore
rustc 1.XX.X (xxxxxxx 20XX-XX-XX)
```

Congratulations! Rust is installed!

`rustc` is the Rust compiler. Its job is to turn the code you write into something the computer can run. As for what a compiler is, we'll get to that little by little later — for now, all you need to know is "it's installed, and it works."

## Recap

- Install Rust with **rustup**, which sets up all the tools you need in one go.
- After installing, open a new terminal and confirm the installation with `rustc --version`.
- `rustc` is the Rust compiler, which turns your code into something the computer can run.
