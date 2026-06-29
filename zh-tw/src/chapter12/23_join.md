# `join!`

## 本集目標

學會用 `join!` 在同一個 `Task` 裡同時等待多個 `Future`，並理解它為什麼是巨集。

## 正文

### 在同一個 `Task` 裡並行

第 9 集我們手寫過 `JoinAll`，把多個 `Future` 一起推進。Tokio 提供現成的 `join!`，做的是同一件事：

```rust,no_run
# extern crate tokio;
#
use tokio::time::{sleep, Duration};

async fn fetch_a() -> i32 {
    sleep(Duration::from_secs(1)).await;
    1
}

async fn fetch_b() -> &'static str {
    sleep(Duration::from_secs(1)).await;
    "hello"
}

#[tokio::main]
async fn main() {
    // 兩個 Future 同時等，總共約一秒，回傳一個 tuple
    let (a, b) = tokio::join!(fetch_a(), fetch_b());
    println!("a = {a}, b = {b}");
}
```

`join!` 會等**所有** branch 都完成才往下走，把每個 branch 的結果包成一個 tuple 還給你。上面兩個 `fetch` 各要等一秒，但因為是並行，總共只花約一秒，不是兩秒。

### `join!` 和 `spawn` 的差別

兩者都能並行，但路線不同：

- `tokio::spawn` 把每個工作變成**獨立的 `Task`** 交給 runtime，可能被分到不同的 `Thread` 上跑，所以要 `Send + 'static`。
- `join!` 是在**同一個 `Task`** 裡輪流 `poll` 那幾個 branch，它們**不會**變成獨立 `Task`，也不會被搬到別條 thread。

正因為 branch 的生命週期就綁在目前這個函數裡（不會被丟出去獨立存在），`join!` 適合「**固定數量**、生命週期就在當下」的並行 I/O——例如同時呼叫三個 API、同時讀兩個檔案。

### `join!` 的並行不是 CPU 平行

這裡要澄清一個重要的限制。`join!` 的各個 branch 是在**同一個 `Task`** 上**輪流被 `poll`** 的，這代表它的並行是「交錯切換」那種，**不是** CPU 平行。

後果很實際：如果某個 branch 長時間不 `.await`（在裡面做比較重的計算，或呼叫同步阻塞函式），它就會霸佔住執行緒——而且因為大家在同一個 `Task` 上輪流，**連同一個 `join!` 裡其他 branch 都得不到 `poll`**。並行的假象當場破功。

這正是上一集「不要 block 住執行緒」那條鐵律，在 `join!` 上的具體案例。如果某個 branch 真的要幹大事，記得用 `spawn_blocking` 或乾脆直接 `spawn`，別讓它卡在 `join!` 裡。

### 為什麼 `join!` 是巨集

你大概注意到 `join!` 也是一個巨集，不是函式。這次又為什麼非得是巨集？

因為它要吃任意數量、各自不同型別的 `Future`，再回傳一個形狀剛好對應的 tuple。`join!(a, b)`、`join!(a, b, c, d)` 都行，而且每個 branch 的 `Future` 型別可以完全不一樣；回傳值也會跟著變成 `(A::Output, B::Output)` 或 `(A::Output, B::Output, C::Output, D::Output)`。

Rust 的函式做不到這些：函式不能接收任意個參數，更不可能讓回傳的 tuple 型別還隨之改變。只有巨集能在**編譯期**，按你實際丟進去的 `Future` 即時生成對應的程式碼。

對照第 9 集的 `JoinAll` 就更清楚了：`JoinAll` 處理的是「**同型別、動態數量**」——一個 `Vec<F>`，裡面全是同一種 `Future`，數量執行時才定。`join!` 反過來，是「**異型別、固定數量**」——數量和型別在你寫程式碼時就定死了，所以能用巨集在編譯期攤開成一個剛好對應的 tuple。

## 重點整理

- `join!` 在**同一個 `Task`** 裡同時等多個 `Future`，等全部完成後把結果包成 tuple 回傳
- 和 `spawn` 不同：`join!` 的 branch 不變成獨立 `Task`、不跨 `Thread`，適合固定數量、生命週期就在當下的並行 I/O
- `join!` 的並行不是 CPU 平行：branch 在同一個 `Task` 上輪流 `poll`，某個 branch 卡住會害其他 branch 都得不到 `poll`
- `join!` 是巨集，因為它要吃「任意數量＋各自不同型別」的 `Future` 並回傳形狀對應的 tuple，這是函式做不到的
- 對照我們自己寫的 `JoinAll`（同型別、動態數量），`join!` 是異型別、固定數量
