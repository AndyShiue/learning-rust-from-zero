# `let` chains

## 本集目標

認識 `let` chains——在 `if` 和 `while` 的條件裡用 `&&` 串接多個 `let` 和布林條件。

> 本集是**第 3 章**的補充。

## 概念說明

### 問題：巢狀的 `if let`

第 3 章學了 `if let`。但如果你需要連續做多次模式匹配，就會變成巢狀的 `if let`：

```rust,editable
enum Wrapper {
    Value(i32),
    Empty,
}

fn get_a() -> Wrapper { Wrapper::Value(10) }
fn get_b(x: i32) -> Wrapper { Wrapper::Value(x + 1) }

fn main() {
    if let Wrapper::Value(a) = get_a() {
        if a > 0 {
            if let Wrapper::Value(b) = get_b(a) {
                println!("a = {}, b = {}", a, b);
            }
        }
    }
}
```

每多一個條件就多一層縮排，程式碼越來越深。

### `let` chains 攤平

你可以用 `&&` 把多個 `let` 和布林條件串在同一個 `if` 裡：

```rust,editable
enum Wrapper {
    Value(i32),
    Empty,
}

fn get_a() -> Wrapper { Wrapper::Value(10) }
fn get_b(x: i32) -> Wrapper { Wrapper::Value(x + 1) }

fn main() {
    if let Wrapper::Value(a) = get_a()
        && a > 0
        && let Wrapper::Value(b) = get_b(a)
    {
        println!("a = {}, b = {}", a, b);
    }
}
```

每個用 `&&` 串起來的條件從左到右依序檢查。前面的 `let` 綁定的變數在後面的條件裡可以使用（像上面的 `a`）。只要任何一個條件不成立，後面的就不會執行——跟 `&&` 的短路行為一樣。

### `while` 裡也能用

```rust,ignore
while let Some(item) = next_item()
    && item.value > 0
{
    // ...
}
```

## 範例程式碼

```rust,editable
enum Command {
    Run { speed: i32 },
    Stop,
}

fn get_command() -> Command {
    Command::Run { speed: 5 }
}

fn get_boost() -> Command {
    Command::Run { speed: 3 }
}

fn main() {
    // 巢狀寫法
    if let Command::Run { speed: s } = get_command() {
        if s > 0 {
            if let Command::Run { speed: boost } = get_boost() {
                println!("巢狀：速度 {} + 加速 {} = {}", s, boost, s + boost);
            }
        }
    }

    // let chains 寫法——同樣的邏輯，更扁平
    if let Command::Run { speed: s } = get_command()
        && s > 0
        && let Command::Run { speed: boost } = get_boost()
    {
        println!("扁平：速度 {} + 加速 {} = {}", s, boost, s + boost);
    }
}
```

## 重點整理

- `let` chains 讓你在 `if` 和 `while` 裡用 `&&` 串接多個 `let` 和布林條件
- 取代巢狀的 `if let`，讓程式碼更扁平
- 前面綁定的變數後面可以使用
- 跟 `&&` 的短路行為一致：前面不成立就不繼續
