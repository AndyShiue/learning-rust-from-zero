# `std::path`

## Goal of This Episode

Learn to handle cross-platform paths with `Path` and `PathBuf`.

## Concept

### Motivation

Programs constantly deal with files — reading config files, writing logs, handling user-supplied paths. We'll learn to read and write files soon, but before that, we need a way to express "where the file is."

Path formats differ across operating systems — Windows uses `\`, while Linux / macOS use `/`. If you glue paths together from raw strings, cross-platform code can break. `std::path` handles those differences for you.

### `Path` and `PathBuf`

The same relationship as `str` and `String`:

- `Path` corresponds to `str` — a DST you can't hold directly; usually used as `&Path`.
- `PathBuf` corresponds to `String` — the owned, modifiable version.

```rust,editable
use std::path::{Path, PathBuf};

fn main() {
    let p = Path::new("/home/user/file.txt");

    let mut buf = PathBuf::from("/home/user");
    buf.push("documents");
    buf.push("file.txt");
    println!("{}", buf.display()); // /home/user/documents/file.txt
}
```

`push` automatically inserts the correct path separator.

### Common Methods

```rust,editable
use std::path::Path;

fn main() {
    let p = Path::new("/home/user/notes.txt");

    println!("{:?}", p.parent());    // Some("/home/user")
    println!("{:?}", p.file_name()); // Some("notes.txt")
    println!("{:?}", p.extension()); // Some("txt")
    println!("{:?}", p.file_stem()); // Some("notes")
    println!("{}", p.exists());      // does the path exist
    println!("{}", p.is_file());     // is it a file
    println!("{}", p.is_dir());      // is it a directory
}
```

`file_name`, `extension`, and `file_stem` return `Option<&OsStr>`, not `Option<&str>` — because on some operating systems a file name isn't necessarily valid UTF-8. Most of the time you can convert to `&str` with `.to_str().unwrap()`.

### `join`

`join` is like `push`, but instead of modifying the original `Path` or `PathBuf`, it returns a new `PathBuf`:

```rust,editable
use std::path::Path;

fn main() {
    let dir = Path::new("/home/user");
    let file = dir.join("documents").join("file.txt");
    println!("{}", file.display()); // /home/user/documents/file.txt
}
```

### Converting To and From Strings

```rust,noplayground
use std::path::{Path, PathBuf};

fn main() {
    // &str → &Path
    let p = Path::new("hello.txt");

    // &str → PathBuf
    let buf = PathBuf::from("/some/path");

    // PathBuf → String (possibly lossy; non-UTF-8 characters get replaced)
    let s: String = buf.to_string_lossy().into_owned();
}
```

## Example Code

```rust,editable
use std::path::{Path, PathBuf};

fn show_info(path: &Path) {
    println!("path: {}", path.display());

    if let Some(parent) = path.parent() {
        println!("  parent: {}", parent.display());
    }
    if let Some(name) = path.file_name() {
        println!("  file name: {:?}", name);
    }
    if let Some(ext) = path.extension() {
        println!("  extension: {:?}", ext);
    }
    println!("  exists: {}", path.exists());
}

fn main() {
    show_info(Path::new("/home/user/notes.txt"));

    // building a path with PathBuf
    let mut config_path = PathBuf::from("/home/user");
    config_path.push(".config");
    config_path.push("app");
    config_path.push("settings.toml");
    show_info(&config_path);

    // join leaves the original Path unchanged
    let base = Path::new("/var/log");
    let log_file = base.join("app.log");
    show_info(&log_file);
}
```

## Recap

- `Path` is a DST (corresponding to `str`); `PathBuf` is the owned version (corresponding to `String`).
- `push` / `join` insert the correct path separator automatically.
- `parent`, `file_name`, `extension`, `file_stem` take paths apart.
- `exists`, `is_file`, `is_dir` check a path's status.
