# `while let`

## 本集目標

學會用 `while let` 在迴圈中持續做模式匹配，直到模式不再符合為止。

## 概念說明

上一集學了 `if let`——「如果符合模式就執行一次」。`while let` 則是「只要符合模式就一直執行」，是 `if let` 的迴圈版本。

語法：

```rust,ignore
while let 模式 = 值 {
    // 迴圈本體
}
```

每次迴圈開始前，Rust 會檢查「值是否符合模式」。符合就繼續跑，不符合就停下來。

為了示範 `while let`，我們用一個自訂 `enum` 來模擬「可能有值、可能結束」的情況：

```rust,noplayground
enum Step {
    Value(i32),
    Done,
}
#
# fn main() {}
```

## 範例程式碼

```rust,editable
enum Step {
    Value(i32),
    Done,
}

fn get_step(index: i32) -> Step {
    if index < 5 {
        Step::Value(index * 10)
    } else {
        Step::Done
    }
}

fn main() {
    let mut i = 0;

    // while let：只要 get_step 回傳 Value，就繼續
    while let Step::Value(v) = get_step(i) {
        println!("第 {} 步，值 = {}", i, v);
        i += 1;
    }
    println!("結束了！總共跑了 {} 步", i);

    println!();

    // 另一個例子：倒數計時
    let mut count = 5;

    // 利用自訂 enum 模擬倒數
    while let Countdown::Tick(n) = get_countdown(count) {
        println!("倒數 {}...", n);
        count -= 1;
    }
    println!("發射！🚀");
}

enum Countdown {
    Tick(i32),
    Launch,
}

fn get_countdown(n: i32) -> Countdown {
    if n > 0 {
        Countdown::Tick(n)
    } else {
        Countdown::Launch
    }
}
```

## 重點整理

- `while let 模式 = 值 { ... }` 是 `if let` 的迴圈版本
- 只要值符合模式，就持續執行迴圈
- 值不符合模式時，迴圈自動結束
