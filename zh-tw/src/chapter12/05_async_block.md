# `async` block：當場做出一個 Future

## 本集目標

學會用 `async { ... }` 在函數裡當場做出一個 future，並分清楚它和 `async fn` 的差別。

## 概念說明

### 除了 `async fn`，還有 `async` 區塊

到目前為止，我們的 future 都是從 `async fn` 來的——呼叫一個非同步函數，拿到一個 future。但其實還有另一種更隨手的做法：在程式中間直接寫一個 `async { ... }` 區塊。

```rust,ignore
#[tokio::main]
async fn main() {
    let fut = async {
        println!("我是一個 async 區塊");
        42
    };

    // 跟前面一樣，這時候 fut 只是個 future，裡面那行還沒印出來
    let value = fut.await; // 推進它，才會印出來、才會拿到 42
    println!("拿到：{}", value);
}
```

`async { ... }` 整塊就是一個運算式，它的值是一個 **future**。這個 future 被 `.await` 的時候，才會執行區塊裡的內容、算出最後的值。和第 3 集的結論完全一致：建出來什麼都還沒發生，`.await` 才真的跑。

你可以把第 3 章學過的 block 運算式（`{ ... }` 本身是運算式）拿來類比：普通的 `{ ... }` 當場算出一個值，`async { ... }` 當場做出一個**還沒算的 future**。

### 和 `async fn` 差在哪

兩者都會產生 future，差別在「可不可以重複使用」：

- `async fn` 是一個**工廠**。它定義了一份藍圖，你每呼叫一次，就生出一個**新的** future。可以呼叫很多次，生很多個。
- `async { ... }` 是**當場做出來的那一個**匿名 future。它就是一個值，做出來就是那一個，不是藍圖。

```rust,ignore
async fn make() -> i32 { 1 } // 工廠：可以一直呼叫，每次生一個新 future

#[tokio::main]
async fn main() {
    let f1 = make(); // 第一個 future
    let f2 = make(); // 又一個全新的 future

    let block = async { 1 }; // 當場做出的那一個 future，就這麼一個
}
```

一個粗略但好記的對應：`async fn` 之於 `async block`，有點像「具名函數」之於「閉包」。函數可以到處呼叫，閉包是你當場做出來的那一個東西。

### 為什麼非得有 `async { }` 這個語法？用 Result 對照就懂了

承上一集「兩個世界」的對照。你可能會想：既然 `async block` 就像閉包，那是不是根本不需要特別的語法，直接用閉包就好？在 **Result 世界**，這個想法完全成立——你想當場寫一小段「中間可以用 `?`、最後給出一個 `Result`」的計算，根本不用任何新語法，一個**立刻呼叫的閉包**就辦到了：

```rust,ignore
let result: Result<i32, std::num::ParseIntError> = (|| {
    let a: i32 = "10".parse()?; // 中間可以寫問號
    let b: i32 = "20".parse()?;
    Ok(a + b)
})(); // 後面這個 () 是「定義完馬上呼叫」
```

閉包本身就是一個函數，`?` 在裡面就是「從這個閉包提早 return」，所以這個閉包整個算出來就是一個 `Result`；後面加 `()` 當場呼叫它，`result` 就拿到結果了。在 Result 世界，「一個能用 `?` 的當場區塊」＝「一個立刻呼叫的閉包」，不需要任何新語法。

那 **Future 世界**能不能照搬，寫成 `(|| { ... .await ... })()`？**不行。** 原因就是上一集說的：`.await` 的規矩太重——它要求整段程式被**改寫成一台能暫停、能恢復的狀態機**（第 15 集）。而一個普通閉包，編譯出來就是一個普通函數：呼叫它、它一路跑到完、回傳，**沒有「暫停」這回事**。普通閉包語法根本表達不了那種改寫。

所以 Rust 才給了 async 一個**專屬的區塊語法** `async { ... }`：它等於對編譯器說「請把這一塊改寫成一個 future（狀態機）」。同樣是「當場做一個包起來的計算」，Result 世界用現成的閉包就夠，Future 世界卻非得有自己的語法不可——差別正是 `.await` 背後那層沉重的改寫。

### 什麼時候用 async block

最常見的情境是：你需要一個 future 來傳給別人（例如丟給某個會幫你同時跑很多 future 的工具），但又懶得為它特地定義一個 `async fn`。這時候就地寫一個 `async { ... }` 最方便。本章後面講 `join!`、`spawn` 的時候會大量用到。

它也常和 `move` 一起出現——`async move { ... }`，意思和第 6 章的 `move` 閉包一樣：把用到的外部變數**搬進**這個 future 裡，而不是用借的。當這個 future 之後可能跑得比現在的函數還久時（例如丟給別的執行緒），就需要 `move` 把資料的所有權帶著走。

```rust,ignore
#[tokio::main]
async fn main() {
    let name = String::from("Rust");

    let greeting = async move {
        // name 被搬進這個 future 裡
        format!("你好，{}！", name)
    };

    println!("{}", greeting.await);
}
```

## 範例程式碼

```rust,ignore
#[tokio::main]
async fn main() {
    let numbers = vec![1, 2, 3];

    // 當場做一個 future，把整個 vec 搬進去處理
    let sum_future = async move {
        let mut total = 0;
        for n in numbers {
            total += n;
        }
        total
    };

    // 做出來的當下什麼都還沒算
    println!("future 已建立，但還沒計算");

    let total = sum_future.await; // 現在才真的跑迴圈
    println!("總和是 {}", total);
}
```

## 重點整理

- `async { ... }` 是一個運算式，它的值是一個 **future**；被 `.await` 時才執行
- `async fn` 像**工廠**：每次呼叫生一個新 future；`async block` 是**當場做出的那一個**匿名 future
- 類比：`async fn` ↔ 具名函數，`async block` ↔ 閉包
- 對照 Result 世界：那邊「能用 `?` 的當場區塊」用一個立刻呼叫的閉包 `(|| { ...? ; Ok(..) })()` 就行；async 因為 `.await` 要把程式改寫成狀態機，普通閉包表達不了，才需要專屬的 `async { }` 語法
- 需要一個 future 又懶得定義函數時，就地寫 `async { ... }` 最方便
- `async move { ... }` 會把用到的外部變數搬進 future 裡（和第 6 章 `move` 閉包同理）
