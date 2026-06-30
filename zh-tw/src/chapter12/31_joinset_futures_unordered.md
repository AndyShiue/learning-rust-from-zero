# `JoinSet` 與 `FuturesUnordered`

## 本集目標

學會處理「大量、動態產生、誰先好先處理」的並行工作，並分清楚 `JoinSet` 和 `FuturesUnordered` 的取捨。

## 正文

### `join!` 的不足

`join!` 很好用，但它有兩個限制：數量**固定**（你寫程式時就得列出所有 branch），而且它要等**全部**完成。

可是很多時候你的工作是「**大量、動態產生、而且誰先好就先處理誰**」——例如爬一千個網址、批次打很多 API。這種需求 `join!` 應付不來，得換工具。有兩條路，差別在於「要不要變成獨立 `Task`」。

### 路線一：`JoinSet`（spawn 的動態版）

`tokio::task::JoinSet` 可以想成「**`spawn` 的動態版**」。你往裡面 `spawn` 任意多個工作，每一個都是**獨立的 `Task`**，所以可以被分到不同 `Thread` 上**真平行**地跑（也因此和 `spawn` 一樣需要 `Send + 'static`）。然後用 `join_next().await` 把完成的結果一個一個收回來——**誰先完成就先拿到誰**：

```rust,editable
# extern crate tokio;
#
use tokio::task::JoinSet;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let mut set = JoinSet::new();

    // 動態 spawn 五個工作，故意讓延遲長短不同
    for i in 0..5 {
        set.spawn(async move {
            sleep(Duration::from_millis(100 * (5 - i))).await;
            i
        });
    }

    // 誰先做完就先收到誰（不是按 spawn 的順序）
    while let Some(result) = set.join_next().await {
        let value = result.expect("task panic 或被 abort");
        println!("完成：{}", value);
    }
}
```

`join_next()` 回傳 `Option<Result<T, JoinError>>`：

- `None`：已經沒有 `Task` 了，收完了。
- `Some(Ok(value))`：一個 `Task` 順利完成。
- `Some(Err(...))`：那個 `Task` panic 或被 abort（所以要處理這個 `Result`）。

`JoinSet` 還支援 `abort_all()` 把所有工作一次喊停，而且 `JoinSet` 被 `drop` 時會**自動 abort** 裡面所有還沒完成的 `Task`——這在做 graceful shutdown 時很方便（下一集會用到）。

### 路線二：`FuturesUnordered`（join! 的動態版）

`futures::stream::FuturesUnordered` 則是「**`join!` 的動態版**」。它在**同一個 `Task` 內**輪流推進一堆 `Future`，**不**把它們變成獨立 `Task`、**不**跨 `Thread`。代價和好處都從這裡來：

- 因為不跨 `Thread`，所以**不需要 `Send + 'static`**——它可以放借用了區域變數的 `Future`（`JoinSet` 因為要 `spawn` 就做不到）。
- 但因為大家在同一個 `Task` 上輪流，**一個 branch 卡住會拖累其他**（又是「不要 block 住執行緒」那條鐵律）。

`FuturesUnordered` 本身其實就是一個 `Stream`（上一集學的）——它只是「把內部那堆 `Future` 輪流 `poll`」，自己不 `spawn`、不碰排程。所以它**不依賴特定 runtime**，這是它相對於 `JoinSet` 的一大優點（`JoinSet` 的 `spawn` 就綁死 Tokio runtime）。用 `Stream` 的方式走訪它：

```rust,editable
extern crate tokio;
extern crate futures;

use futures::stream::FuturesUnordered;
use futures::StreamExt;

#[tokio::main]
async fn main() {
    let mut futures = FuturesUnordered::new();

    // 動態塞進一堆 Future（不會變成獨立 Task）
    for i in 0..5 {
        futures.push(async move { i * 2 });
    }

    // 它是個 Stream，誰先完成就先冒出來
    while let Some(value) = futures.next().await {
        println!("完成：{}", value);
    }
}
```

### 怎麼選

兩者都是「誰先完成就先產生結果」，都很適合爬蟲、批次請求這類工作。差別在：

- 要**真平行、各工作互不影響**（一個卡住不拖累別人）→ 用 **`JoinSet`**（每個是獨立 `Task`，但要 `Send + 'static`、綁 Tokio）。
- 想**就地借用區域變數、工作輕量、不想依賴特定 runtime** → 用 **`FuturesUnordered`**（同一個 `Task` 內多工，不需 `Send`，但一個卡住會拖累其他）。

下一集，我們把目前學的這些工具——`select!`、channel、`JoinSet`——兜成一個完整的 graceful shutdown 流程。

## 重點整理

- 處理「大量、動態、誰先好先處理」的工作，`join!` 不夠用，改用 `JoinSet` 或 `FuturesUnordered`
- **`JoinSet`**（`spawn` 的動態版）：每個工作是獨立 `Task`、可真平行、需 `Send + 'static`、綁 Tokio；`join_next()` 回 `Option<Result<T, JoinError>>`，支援 `abort_all()` 與 `drop` 時自動 abort
- **`FuturesUnordered`**（`join!` 的動態版）：同一個 `Task` 內多工、不跨 `Thread`、不需 `Send`（可借用區域變數），但一個 branch 卡住會拖累其他；本身是個不綁 runtime 的 `Stream`
- 要真平行互不影響用 `JoinSet`；要就地借用、工作輕量、不綁 runtime 用 `FuturesUnordered`
