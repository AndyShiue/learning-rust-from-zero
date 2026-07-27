# `@` 綁定

## 本集目標

學會用 `@` 在比對模式的同時，把符合的值綁定到一個變數上。

## 概念說明

前面學過 range pattern：`0..=100` 可以比對 0 到 100 之間的值。現在假設一個 `Command` 的 `SetVolume` variant 攜帶了音量，我們想檢查音量是否在範圍內，並在分支裡印出實際的音量：

```rust,editable
enum Command {
    SetVolume(i32),
    SetBrightness(i32),
    Quit,
}

fn main() {
    let command = Command::SetVolume(72);

    match command {
        Command::SetVolume(level @ 0..=100) => {
            println!("把音量設為 {}", level);
        }
        Command::SetVolume(level) => {
            println!("音量 {} 超出範圍", level);
        }
        Command::SetBrightness(level) => {
            println!("把亮度設為 {}", level);
        }
        Command::Quit => println!("結束程式"),
    }
}
```

`Command::SetVolume(level @ 0..=100)` 裡，右邊的 `0..=100` 負責比對範圍，左邊的 `level` 則綁定實際音量。當值是 `Command::SetVolume(72)` 時，這個 pattern 會匹配成功，而分支裡的 `level` 就是 `72`。

這就是 `@` 的語法：

```text
變數名 @ pattern
```

左邊建立綁定，右邊負責比對。比對成功後，就能在分支裡使用左邊的變數。

`@` 不只能搭配 range，也能搭配 `|` 等其他 pattern：

下方範例的第一個分支先用 `('a' | 'e' | 'i' | 'o' | 'u')` 比對小寫母音，再把匹配到的字元綁定成 `key`。當 `@` 右邊用了 `|` 時，這一組 pattern 要用括號包起來。

`MouseClick` 的分支則示範在 `struct` variant 的欄位裡使用 `@`。`0..=10` 比對 `x` 欄位的範圍，`horizontal` 綁定匹配到的實際座標。

## 範例程式碼

```rust,editable
enum Event {
    KeyPress(char),
    MouseClick { x: i32, y: i32 },
    Quit,
}

fn main() {
    let event = Event::MouseClick { x: 6, y: 30 };

    match event {
        Event::KeyPress(key @ ('a' | 'e' | 'i' | 'o' | 'u')) => {
            println!("按下小寫母音 '{}'", key);
        }
        Event::KeyPress(key @ 'a'..='z') => {
            println!("按下其他小寫字母 '{}'", key);
        }
        Event::KeyPress(key) => {
            println!("按下其他按鍵 '{}'", key);
        }
        Event::MouseClick {
            x: horizontal @ 0..=10,
            y,
        } => {
            println!("在左側區域點擊：({}, {})", horizontal, y);
        }
        Event::MouseClick { x, y } => {
            println!("在其他區域點擊：({}, {})", x, y);
        }
        Event::Quit => println!("結束"),
    }
}
```

## 重點整理

- `變數名 @ pattern` 會用右邊的 pattern 比對；成功後，實際值會綁定到左邊的變數。
- `Command::SetVolume(level @ 0..=100)` 同時限制音量範圍並取得實際音量。
- `@` 可以用在 `enum` variant、`struct` 欄位等巢狀資料中。
- `@` 可以搭配 range、`|` 等 pattern；搭配 `|` 時要寫成 `value @ (pattern1 | pattern2)`。
