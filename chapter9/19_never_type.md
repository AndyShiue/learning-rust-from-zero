# 第九章第 19 集：never type `!`

## 本集目標
認識 `!` 型別——代表永遠不會產生值。

## 概念說明

### 永不回傳的函數

大部分函數執行完會回傳一個值。但有些函數**永遠不會回傳**：

```rust
fn forever() -> ! {
    loop {
        // 永遠跑下去
    }
}
```

`-> !` 表示這個函數不可能回傳。

### 哪些東西的型別是 !

- `panic!("...")` — 程式崩潰
- `std::process::exit(0)` — 程式結束
- `loop {}`（沒有 break）— 永遠跑下去
- `return` 表達式本身
- `break` 表達式本身
- `continue` 表達式本身

### ! 可以被強制轉換成任何型別

這是 `!` 最實用的特性。因為一個永遠不會產生值的表達式，放在任何需要值的地方都不會矛盾——反正它不會真的產生值。

你其實一直在用這個特性：

```rust
let x: i32 = match option {
    Some(v) => v,
    None => panic!("不該是 None"),
};
```

match 的每個分支必須回傳同一個型別。`Some(v) => v` 回傳 `i32`，`None => panic!(...)` 回傳 `!`。因為 `!` 可以轉成任何型別，所以被當成 `i32`，match 的型別一致。

`return` 和 `continue` 也一樣：

```rust
let x: i32 = match option {
    Some(v) => v,
    None => return, // return 的型別是 !
};
```

```rust
for item in list {
    let value: i32 = match item.parse::<i32>() {
        Ok(n) => n,
        Err(_) => continue, // continue 的型別是 !
    };
    println!("{}", value);
}
```

## 範例程式碼

```rust
fn exit_with_error(msg: &str) -> ! {
    eprintln!("錯誤：{}", msg);
    std::process::exit(1);
}

fn parse_or_exit(input: &str) -> i32 {
    match input.parse::<i32>() {
        Ok(n) => n,
        Err(_) => exit_with_error("請輸入有效的數字"), // ! 被當成 i32
    }
}

fn main() {
    let value = parse_or_exit("42");
    println!("解析成功：{}", value);

    // let bad = parse_or_exit("abc"); // 這會呼叫 exit_with_error，程式直接結束
}
```

## 重點整理
- `!` 是 never type，代表永遠不會產生值
- `-> !` 的函數永遠不會回傳
- `panic!`、`process::exit`、`return`、`break`、`continue` 的型別都是 `!`
- `!` 可以被強制轉換成任何型別——match 裡一條路線回傳值一條路線 panic 就是靠這個

恭喜你完成了第九章！🎉 這一章涵蓋了 Rust 的進階語言功能——從 dyn Trait、編譯期運算、型別轉換、attribute、巨集系統，到 unsafe、static、FFI、union 和 never type。這些功能大部分在日常開發中不會天天用到，但知道它們的存在，需要的時候就能派上用場。下一章我們將看看標準庫裡的更多實用工具。