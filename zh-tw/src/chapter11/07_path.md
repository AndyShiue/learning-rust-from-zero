# `std::path`

## 本集目標

學會用 `Path` 和 `PathBuf` 處理跨平台路徑。

## 概念說明

### 動機

寫程式常常要跟檔案打交道——讀設定檔、寫 log、處理使用者指定的路徑。之後會學怎麼讀寫檔案，但在那之前，我們得先知道怎麼表示「檔案在哪裡」。

不同作業系統的路徑格式不一樣——Windows 用 `\`，Linux / macOS 用 `/`。如果你用字串硬拼路徑，跨平台就有可能出問題。`std::path` 幫你處理這些差異。

### `Path` 和 `PathBuf`

跟 `str` 和 `String` 的關係一樣：

- `Path` 對應 `str`——是 DST，不能直接持有，通常用 `&Path`
- `PathBuf` 對應 `String`——是具所有權的版本，可以修改

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

`push` 會自動加上正確的路徑分隔符號。

### 常用方法

```rust,editable
use std::path::Path;

fn main() {
    let p = Path::new("/home/user/notes.txt");

    println!("{:?}", p.parent());    // Some("/home/user")
    println!("{:?}", p.file_name()); // Some("notes.txt")
    println!("{:?}", p.extension()); // Some("txt")
    println!("{:?}", p.file_stem()); // Some("notes")
    println!("{}", p.exists());      // 檢查路徑是否存在
    println!("{}", p.is_file());     // 是不是檔案
    println!("{}", p.is_dir());      // 是不是目錄
}
```

`file_name`、`extension`、`file_stem` 回傳的是 `Option<&OsStr>`，不是 `Option<&str>`——因為檔案名稱在某些作業系統上不一定是合法的 UTF-8。大部分時候可以用 `.to_str().unwrap()` 轉成 `&str`。

### `join`

`join` 跟 `push` 類似，但不改變原本的 `Path` 或 `PathBuf`，而是回傳新的 `PathBuf`：

```rust,editable
use std::path::Path;

fn main() {
    let dir = Path::new("/home/user");
    let file = dir.join("documents").join("file.txt");
    println!("{}", file.display()); // /home/user/documents/file.txt
}
```

### 和字串的轉換

```rust,noplayground
use std::path::{Path, PathBuf};

fn main() {
    // &str → &Path
    let p = Path::new("hello.txt");

    // &str → PathBuf
    let buf = PathBuf::from("/some/path");

    // PathBuf → String（可能有損，非 UTF-8 字元會被替換）
    let s: String = buf.to_string_lossy().into_owned();
}
```

## 範例程式碼

```rust,editable
use std::path::{Path, PathBuf};

fn show_info(path: &Path) {
    println!("路徑：{}", path.display());

    if let Some(parent) = path.parent() {
        println!("  上層：{}", parent.display());
    }
    if let Some(name) = path.file_name() {
        println!("  檔名：{:?}", name);
    }
    if let Some(ext) = path.extension() {
        println!("  副檔名：{:?}", ext);
    }
    println!("  存在：{}", path.exists());
}

fn main() {
    show_info(Path::new("/home/user/notes.txt"));

    // 用 PathBuf 組合路徑
    let mut config_path = PathBuf::from("/home/user");
    config_path.push(".config");
    config_path.push("app");
    config_path.push("settings.toml");
    show_info(&config_path);

    // join 不改變原本的 Path
    let base = Path::new("/var/log");
    let log_file = base.join("app.log");
    show_info(&log_file);
}
```

## 重點整理

- `Path` 是 DST（對應 `str`），`PathBuf` 是擁有所有權的版本（對應 `String`）
- `push` / `join` 自動加上正確的路徑分隔符號
- `parent`、`file_name`、`extension`、`file_stem` 拆解路徑
- `exists`、`is_file`、`is_dir` 檢查路徑狀態