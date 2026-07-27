# `join!`

## 本集目標

學會用 `join!` 在同一個 `Task` 裡同時等待多個 `Future`，並理解它為什麼是巨集。

## 正文

### 在同一個 `Task` 裡並行

第 9 集我們手寫過 `JoinAll`，把多個 `Future` 一起推進。Tokio 提供現成的 `join!`，做的是同一件事：

```rust,editable
extern crate tokio;

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
    println!("a = {}, b = {}", a, b);
}
```

`join!` 會等**所有** branch 都完成才往下走，把每個 branch 的結果包成一個 tuple 還給你。上面兩個 `fetch` 各要等一秒，但因為是並行，總共只花約一秒，不是兩秒。

### `spawn` 和 `join!` 的差別

`spawn` 和 `join!` 兩者都能並行，但作法不同：

- `tokio::spawn` 把每個工作變成**獨立的 `Task`** 交給 runtime，可能被分到不同的 `Thread` 上跑，所以要 `Send + 'static`。
- `join!` 是在**同一個 `Task`** 裡輪流 `poll` 那幾個 branch，它們**不會**變成獨立 `Task`。

正因為各個 branch 都保存在目前這個 `Task` 裡，並由 `join!` 等到全部完成，它們不會脫離目前作用域成為獨立的 `Task`。因此，`join!` 適合「**固定數量**、需要在目前作用域內一併完成」的並行 I/O——例如同時呼叫三個 API、同時讀兩個檔案。

### `join!` 的並行不是 CPU 平行

這裡要澄清一個重要的限制。`join!` 的各個 branch 是在**同一個 `Task`** 上**輪流被 `poll`** 的，這代表它的並行是「交錯切換」那種，**不可能是** CPU 平行。

後果很實際：如果某個 branch 長時間不 `.await`（在裡面做比較耗時的計算，或呼叫同步阻塞函數），它就會霸佔住執行緒——而且因為大家在同一個 `Task` 上輪流，**連同一個 `join!` 裡其他 branch 都得不到 `poll`**。並行的假象當場破功。

這正是上一集「不要 block 住執行緒」那條鐵律在 `join!` 上的具體案例。如果某個 branch 真的要幹大事，記得用 `spawn_blocking`，別讓它卡在 `join!` 裡。

### 為什麼 `join!` 是巨集

你大概會注意到 `join!` 也是一個巨集，不是函數。這次又為什麼非得是巨集？

因為它要吃任意數量、各自不同型別的 `Future`，再回傳一個形狀剛好對應的 tuple。`join!(a, b)`、`join!(a, b, c, d)` 都行，而且每個 branch 的 `Future` 型別可以完全不一樣；回傳值也會跟著變成 `(A::Output, B::Output)` 或 `(A::Output, B::Output, C::Output, D::Output)`。

一般 Rust 函數的參數數量是固定的。我們可以分別為兩個、三個或四個 `Future` 撰寫泛型函數，讓每個函數回傳元素型別與這些 `Future` 輸出相符的 tuple；但單一函數無法涵蓋所有可能的參數數量。巨集則能在**編譯時期**根據每次呼叫，產生 tuple 形狀完全吻合的程式碼。

對照第 9 集的 `JoinAll` 就更清楚了：`JoinAll` 處理的是「**同回傳型別、動態數量**」——數量要到執行時期才定，至於裡面具體是哪一種 `Future`，我們用 `dyn Future<Output = ()>` 把它抹掉了，只要求輸出一律是 `()`。`join!` 反過來，是「**異回傳型別、固定數量**」——數量和每個 `Future` 的輸出型別在你寫程式碼時就定死了，所以能用巨集在編譯時期攤開成一個剛好對應的 tuple。

## 重點整理

- `join!` 在**同一個 `Task`** 裡同時等多個 `Future`，等全部完成後把結果包成 tuple 回傳。
- 和 `spawn` 不同：`join!` 的 branch 不變成獨立 `Task`，適合固定數量、需要在目前作用域內一併完成的並行 I/O。
- `join!` 的並行不是 CPU 平行：branch 在同一個 `Task` 上輪流 `poll`，某個 branch 卡住會害其他 branch 都得不到 `poll`。
- `join!` 是巨集，因為每次呼叫都可以傳入不同數量、型別各異的 `Future`，並產生形狀對應的輸出 tuple；一般函數則必須為每種參數數量各寫一個版本。
- 對照我們自己寫的 `JoinAll`（同回傳型別、動態數量），`join!` 是異回傳型別、固定數量。
