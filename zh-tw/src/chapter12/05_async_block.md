# `async` block

## 本集目標

學會用 `async { ... }` 在函數裡當場做出一個 `Future`，並理解它和 `async fn` 的關係。

## 概念說明

### 當場做一個 `Future`

除了 `async fn`，Rust 還讓你用 `async { ... }` 在程式中間**當場**建立一個 `Future`：

```rust,no_run
# extern crate tokio;
#[tokio::main]
async fn main() {
    // 這個 async block 本身就是一個 Future
    let fut = async {
        println!("我在一個 async block 裡");
        42
    };

    // 和 async fn 一樣，要 .await 才會真的跑
    let value = fut.await;
    println!("拿到 {value}");
}
```

注意：和 `async fn` 完全一樣，光是寫出 `async { ... }` 不會執行裡面的程式，你只是做出一個惰性的 `Future`，要 `.await` 才會動。

### `async fn` 和 `async` block 的關係

這兩者的關係，其實就是你在第 6 章看過的**具名函數 ↔ 閉包**：

- `async fn` 是一個**具名的 `Future` 工廠**——你定義一次，之後可以重複呼叫，每次呼叫產生一個新的 `Future`。
- `async` block 是**當場建立的一個匿名 `Future`**——就在這裡、這一個，沒有名字。

就像普通函數和閉包一樣：一個是先定義好、到處呼叫的具名工具，一個是在需要的地方臨時寫出來的匿名版本。

### 在 `Result` 世界，這件事不需要新語法

這裡有個很有意思的對照。在 `Result` 世界，如果你想要「當場來一段可以用 `?` 的區塊」，其實**不需要任何新語法**——一個立刻呼叫的閉包就辦到了：

```rust,editable
fn main() {
    // 定義一個閉包，然後馬上用 () 呼叫它
    let result: Result<i32, std::num::ParseIntError> = (|| {
        let x = "3".parse::<i32>()?;
        let y = "4".parse::<i32>()?;
        Ok(x + y)
    })();

    println!("{result:?}");
}
```

這裡的 `(|| { ... })()` 是「定義一個閉包並立刻呼叫」。閉包的函數體可以用 `?`，因為它回傳 `Result`。`Result` 世界靠現成的閉包就能表達「當場一段」，不必發明新東西。

### 為什麼 `Future` 世界不能照搬

你可能會想：那 `Future` 世界是不是也照抄就好？把 `.await` 塞進一個立刻呼叫的閉包裡？

```rust,compile_fail
# extern crate tokio;
async fn get_number() -> i32 {
    42
}

#[tokio::main]
async fn main() {
    let value = (|| {
        get_number().await // 編譯錯誤：普通閉包裡不能 .await
    })();
}
```

不行。原因回到上一集講的：`.await` 需要把整段程式**改寫成狀態機**，才能做到「暫停以允許並行」。但一個普通閉包只會被編譯成一個普通函數，裡面**沒有**「暫停、之後再恢復」這回事——它表達不了那種改寫。所以 `Result` 世界那招在這裡行不通。

這正是 `async` block 存在的理由。當你寫 `async { ... }`，等於是明確地叫編譯器：「把這一塊改寫成一個 `Future`」。有了這個專屬語法，裡面才能合法地用 `.await`：

```rust,no_run
# extern crate tokio;
async fn get_number() -> i32 {
    42
}

#[tokio::main]
async fn main() {
    let value = async {
        get_number().await // 這次可以了，因為這是 async block
    }.await;
    println!("{value}");
}
```

到這裡，前五集把「`async` 是什麼」從使用者的角度講完了。下一集開始，我們要捲起袖子，自己動手把 `Future` 的內部機制拆開來看。

## 重點整理

- `async { ... }` 在函數中間當場建立一個匿名的 `Future`，一樣要 `.await` 才會跑。
- `async fn` ↔ `async` block 的關係，就像具名函數 ↔ 閉包：一個是可重複呼叫的工廠，一個是當場的匿名版本。
- `Result` 世界用「立刻呼叫的閉包」就能表達「當場一段」，不需新語法。
- `Future` 世界不能照搬，因為 `.await` 要改寫成狀態機，普通閉包做不到——所以才需要 `async` block 這個專屬語法。
