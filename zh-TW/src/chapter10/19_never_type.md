# never type `!`

## 本集目標

認識 `!` 型別——代表永遠不會產生值。

## 概念說明

### 永不回傳的函數

大部分函數執行完會回傳一個值。但有些函數**永遠不會回傳**：

```rust,noplayground
fn forever() -> ! {
    loop {
        // 永遠跑下去
    }
}
#
# fn main() {}
```

`-> !` 表示這個函數不可能回傳。

### 哪些東西的型別是 !

- `panic!("...")` — 讓目前的執行緒發生 panic，而不是正常回傳。
- `std::process::exit(0)` — 程式結束。
- `loop {}`（沒有 break）— 永遠跑下去。
- `return` 表達式本身
- `break` 表達式本身
- `continue` 表達式本身

### `!` 可以被強制轉換成任何型別

這是 `!` 最實用的特性。因為一個永遠不會產生值的表達式，放在任何需要值的地方都不會矛盾——反正它不會真的產生值。

這就是為什麼下面的程式碼能通過編譯：

```rust,noplayground
# fn main() {
#     let option = Some(1);
    let x: i32 = match option {
        Some(v) => v,
        None => panic!("不該是 None"),
    };
# }
```

`match` 的每個分支必須回傳同一個型別。`Some(v) => v` 回傳 `i32`，`None => panic!(...)` 回傳 `!`。因為 `!` 可以轉成任何型別，所以被當成 `i32`，`match` 的型別一致。

`return`、`break` 和 `continue` 也一樣：

```rust,ignore
# fn main() {
    let x: i32 = match option {
        Some(v) => v,
        None => return, // return 的型別是 !
    };
# }
```

```rust,ignore
# fn main() {
    for item in list {
        let value: i32 = match item.parse::<i32>() {
            Ok(n) => n,
            Err(_) => continue, // continue 的型別是 !
        };
        println!("{}", value);
    }
# }
```

### `!` 也能寫在其他型別的位置

`!` 和其他型別一樣，可以寫在任何需要型別的地方。最簡單的例子是變數的型別：

```rust,should_panic
fn main() {
    let _never: ! = panic!("這個變數永遠拿不到值");
}
```

`=` 右邊必須是型別為 `!` 的表達式，例如 `panic!(...)`。所以這個變數永遠不會真的拿到值——程式在這一行就 panic 了。

`!` 也能放進其他型別裡。例如 `Result<i32, !>` 是一個一定成功、不可能是 `Err` 的 `Result`：

```rust,editable
fn always_ok() -> Result<i32, !> {
    Ok(42)
}

fn main() {
    let Ok(value) = always_ok();
    println!("{}", value);
}
```

第 3 章說過，`let` 只接受不會比對失敗的 pattern。`Ok(value)` 在這裡不會失敗：要變成 `Err`，就得在裡面放一個型別是 `!` 的值，而這種值不存在。

這種型別通常出現在 `trait` 規定要回傳 `Result`、某個實作卻不可能失敗的時候。

### `Result<i32, !>` 不會自動變成 `Result<i32, ()>`

`!` 可以被強制轉換成任何型別，但這不代表 `Result<i32, !>` 可以轉成 `Result<i32, ()>`：

```rust,compile_fail
fn always_ok() -> Result<i32, !> {
    Ok(42)
}

fn main() {
    let result: Result<i32, ()> = always_ok(); // 編譯錯誤！
}
```

前面的強制轉換，針對的是型別本身就是 `!` 的表達式：它永遠不會產生值，放在哪裡都不矛盾。`Result<i32, !>` 不一樣，`always_ok()` 真的會產生一個值 `Ok(42)`，只是型別裡寫著 `!`。`Result<i32, !>` 和 `Result<i32, ()>` 是兩個不同的型別，兩者之間沒有自動轉換。

需要 `Result<i32, ()>` 的時候，就先用 `let Ok(value)` 把值取出來，再自己包成 `Ok(value)`。

## 範例程式碼

```rust,editable
trait Source {
    type Error;
    fn read(&self) -> Result<String, Self::Error>;
}

// 使用者可能什麼都沒輸入，所以讀取可能失敗
struct Input {
    text: String,
}

impl Source for Input {
    type Error = String;

    fn read(&self) -> Result<String, String> {
        if self.text.is_empty() {
            Err(String::from("沒有輸入"))
        } else {
            Ok(self.text.clone())
        }
    }
}

// 資料早就存在記憶體裡，讀取不可能失敗，所以錯誤型別是 !
struct Memory {
    text: String,
}

impl Source for Memory {
    type Error = !;

    fn read(&self) -> Result<String, !> {
        Ok(self.text.clone())
    }
}

fn exit_with_error(msg: &str) -> ! {
    println!("錯誤：{}", msg);
    std::process::exit(1);
}

fn read_or_exit(input: &Input) -> String {
    match input.read() {
        Ok(text) => text,
        Err(e) => exit_with_error(&e), // ! 被當成 String
    }
}

fn print_result(result: Result<String, String>) {
    match result {
        Ok(text) => println!("讀到：{}", text),
        Err(e) => println!("讀取失敗：{}", e),
    }
}

fn main() {
    let input = Input { text: String::from("哈囉") };
    println!("輸入：{}", read_or_exit(&input));

    let memory = Memory { text: String::from("你好") };

    // 錯誤型別是 !，不可能是 Err，直接用 let 取出值
    let Ok(saved) = memory.read();

    print_result(input.read());

    // 編譯錯誤：Result<String, !> 不是 Result<String, String>
    // print_result(memory.read());
    print_result(Ok(saved)); // 取出值之後，自己重新包成 Ok

    // let empty = Input { text: String::new() };
    // read_or_exit(&empty); // 這會呼叫 exit_with_error，程式直接結束
}
```

## 重點整理

- `!` 是 never type，代表永遠不會產生值。
- `-> !` 的函數永遠不會回傳。
- `panic!`、`process::exit`、`return`、`break`、`continue` 的型別都是 `!`。
- `!` 可以被強制轉換成任何型別——`match` 裡一條路線回傳值一條路線 panic 就是靠這個。
- `!` 可以寫在任何需要型別的地方，例如變數的型別或 `Result<i32, !>`。
- `Result<i32, !>` 不可能是 `Err`，可以直接用 `let Ok(value) = ...` 取出值。
- `Result<i32, !>` 不會自動轉成 `Result<i32, ()>`。

恭喜你完成了進階語言功能這一章！🎉 這一章涵蓋了 Rust 的進階語言功能——從 `dyn Trait`、編譯時期運算、型別轉換、attribute、巨集系統，到 `unsafe`、`static`、FFI、`union` 和 never type。這些功能大部分在日常開發中不會天天用到，但知道它們的存在，需要的時候就能派上用場。下一章我們將看看標準庫裡的更多實用工具。
