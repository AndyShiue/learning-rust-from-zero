# std::env / std::process

## 本集目標
學會讀取命令列參數、環境變數，以及控制程式結束。

## 概念說明

### 命令列參數

程式執行的時候可以帶參數，例如 `cargo run -- hello world`。用 `std::env::args()` 拿到：

```rust
use std::env;

fn main() {
    for arg in env::args() {
        println!("{}", arg);
    }
}
```

第一個是程式本身的路徑，後面才是你傳的參數。通常會 `collect` 成 Vec 來用：

```rust
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("請提供參數");
        return;
    }
    println!("你輸入的是：{}", args[1]);
}
```

### 環境變數

環境變數是作業系統提供的一組 key-value 設定，程式可以讀取它們來取得系統資訊。如果你不熟悉環境變數，請自行搜尋相關資料。

```rust
use std::env;

fn main() {
    match env::var("HOME") {
        Ok(val) => println!("HOME = {}", val),
        Err(_) => println!("HOME 沒有設定"),
    }
}
```

`env::var` 回傳 `Result<String, VarError>`。環境變數不存在就會回傳 `Err`。

### process::exit

```rust,should_panic
use std::process;

fn main() {
    process::exit(1); // 立刻結束程式，回傳錯誤碼 1
}
```

回傳 0 通常代表成功，非 0 代表失敗。進階語言功能那章學過 `process::exit` 的回傳型別是 `!`（never type）。

### eprintln!

```rust
# fn main() {
    eprintln!("這是錯誤訊息");
    println!("這是正常輸出");
# }
```

`println!` 輸出到 **stdout**（標準輸出），`eprintln!` 輸出到 **stderr**（標準錯誤）。兩者在終端機上看起來一樣，但可以分開導向不同的地方。錯誤訊息應該用 `eprintln!`。

## 範例程式碼

```rust,should_panic
use std::env;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("用法：{} <名字>", args[0]);
        process::exit(1);
    }

    let name = &args[1];
    println!("你好，{}！", name);

    // 印出一些環境變數
    if let Ok(home) = env::var("HOME") {
        println!("你的 HOME 目錄：{}", home);
    }

    if let Ok(path) = env::var("PATH") {
        println!("PATH 的前 50 個字元：{}", &path[..path.len().min(50)]);
    }
}
```

## 重點整理
- `env::args()` 回傳命令列參數的迭代器，第一個是程式路徑
- `env::var("NAME")` 回傳 `Result`
- `process::exit(code)` 立刻結束程式，回傳型別是 `!`
- `eprintln!` 輸出到 stderr，錯誤訊息應該用它
