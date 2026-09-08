# graceful shutdown

## 本集目標

把前面學的工具兜成一個完整的 graceful shutdown（優雅關閉）流程。

## 正文

### 什麼是 graceful shutdown

伺服器要關閉時，最粗暴的做法是直接砍掉——但這樣進行到一半的工作就斷在那裡，可能留下壞掉的資料、沒回應完的請求。**graceful shutdown** 是更有禮貌的關法：收到停止要求時不硬切，而是「**通知大家收工 → 等手邊的工作做完；逾時則要求取消剩餘工作**」。

把它拆成三個要素：

1. **訊號來源**：怎麼知道「該關了」。
2. **廣播 shutdown**：怎麼把「要收工了」告訴所有 worker。
3. **等待 drain**：怎麼等所有 worker 收尾完畢。

我們用前面學過的工具，一個一個對上。

### 三要素組起來

- **訊號來源**用 `tokio::signal::ctrl_c()`——它是個 `Future`，`.await` 它會等到使用者按下 Ctrl-C（實務上還會再加上監聽 SIGTERM）。
- **廣播 shutdown** 用第 26 集的 `watch` 當一個 shutdown flag：一對多、而且晚訂閱的 worker 也讀得到當前狀態。
- **等待 drain** 用第 31 集的 `JoinSet`，`join_next()` 一直收到全空為止。

每個 worker 內部用 `select!`，**同時**等「下一份工作」和「shutdown 訊號」。如果先等到工作，就離開 `select!` 處理它；如果先等到 shutdown，就不再拿新工作：

```rust,no_run
# extern crate tokio;
#
use std::time::Duration;
use tokio::sync::watch;
use tokio::task::JoinSet;
use tokio::time::{sleep, timeout};

async fn wait_next_job(id: u32, next_job: &mut u32) -> u32 {
    // 這裡用 sleep 假裝「等待下一份工作送進來」。
    // 這個等待可以被 shutdown 取消；真正處理工作會放在 select! 外面。
    sleep(Duration::from_millis(500)).await;
    let job = *next_job;
    *next_job += 1;
    println!("worker {} 拿到工作 {}", id, job);
    job
}

async fn process_job(id: u32, job: u32) {
    // 這裡才是假裝「真正處理工作」。
    // 它刻意放在 select! 外面，所以 shutdown 不會直接把它取消在半路。
    sleep(Duration::from_millis(300)).await;
    println!("worker {} 處理完工作 {}", id, job);
}

async fn worker(id: u32, mut shutdown: watch::Receiver<bool>) {
    let mut next_job = 0;

    loop {
        let job = tokio::select! {
            // 等下一份工作：這件事可以被 shutdown 取消
            job = wait_next_job(id, &mut next_job) => job,
            // 收工訊號
            _ = shutdown.changed() => {
                println!("worker {} 收到收工訊號，退出", id);
                break;
            }
        };

        // 在 select! 外面處理，避免被 shutdown 直接 drop 在半路
        process_job(id, job).await;
    }
}

async fn drain_workers(workers: &mut JoinSet<()>) {
    while let Some(result) = workers.join_next().await {
        if let Err(error) = result {
            eprintln!("worker 非正常結束：{}", error);
        }
    }
}

#[tokio::main]
async fn main() {
    // 廣播 shutdown 用的 watch flag
    let (shutdown_tx, shutdown_rx) = watch::channel(false);

    // 用 JoinSet 管理所有 worker
    let mut workers = JoinSet::new();
    for id in 0..3 {
        workers.spawn(worker(id, shutdown_rx.clone()));
    }

    // 1. 等訊號
    tokio::signal::ctrl_c().await.expect("監聽 Ctrl-C 失敗");
    println!("收到 Ctrl-C，開始 graceful shutdown");

    // 2. 廣播收工
    shutdown_tx.send(true).expect("沒有 worker 在聽");

    // 3. 等所有 worker drain，但給 5 秒期限
    match timeout(Duration::from_secs(5), drain_workers(&mut workers)).await {
        Ok(()) => println!("所有 worker 均已結束"),
        Err(_) => {
            println!("等待收尾逾時，要求取消剩下的 worker");
            workers.abort_all();
        }
    }
}
```

這裡的 `timeout(Duration::from_secs(5), future)` 是替等待這個 `future` 設定五秒期限。

它自己也是一個 `Future`。等待完成時，`.await` 會得到 `Ok(裡面的輸出)`；等待逾時則得到 `Err(_)`。在這個例子裡，裡面的 `future` 是：

```rust,ignore
drain_workers(&mut workers)
```

也就是「逐一檢查 worker 的結束結果，直到 `JoinSet` 空掉」。`drain_workers` 會印出收到的 `JoinError`，再繼續等其他 worker，因此 `Ok(())` 只代表等待已完成，不代表每個 worker 都正常結束。逾時後則呼叫 `abort_all()`，要求取消剩餘 `Task`。

### cancellation safety 的設計重點

這裡有個呼應第 27、28 集的關鍵設計：要**刻意安排 `select!` 的位置**。在上面的 worker 裡，`select!` 等的是「下一份工作」和「shutdown」；一旦真的拿到工作，就離開 `select!`，再呼叫 `process_job`。因此 shutdown 勝出時，被 `drop`（取消）的是「等下一份工作」這種可以重來的等待，而不是已經開始處理的工作。

如果反過來，把真正的處理流程直接放進會輸給 shutdown 的 branch，像 `read_exact` 這類不可安全取消的操作就可能被砍在半路，資料也跟著掉了。這就是前面強調過的 cancellation safety 在 shutdown 上的具體應用。

### 設定等待收尾的期限

這五秒是讓 worker 自行完成手邊工作的等待期限。逾時後，我們要求取消剩餘 `Task`；進入取消階段後，即使 `process_job` 放在 `select!` 外面，處理中的工作仍可能被中斷。

這不是整個程式保證退出的時間上限。Tokio 需要 `Task` 配合讓出執行權，才能處理排程與取消；一直不讓出的迴圈或阻塞呼叫，不能靠 `timeout` 或 `abort_all()` 立即中斷。已開始執行的 `spawn_blocking` 工作也不能靠 `abort_all()` 停止。`abort_all()` 返回只代表提出取消要求。

### 更匹配的工具：`CancellationToken`

用 `watch` 當 shutdown flag 可行，但有點像「借」一個狀態廣播工具來當開關。`tokio-util` 提供了一個從頭就為「取消」設計的工具——`CancellationToken`，語意更貼切。`tokio-util` 不在 Tokio 本體裡，使用前要加上依賴：

```toml
[dependencies]
tokio-util = "0.7"
```

（和第 30 集的 `tokio-stream` 一樣，`crate` 名稱裡的 `-` 在程式碼中會變成 `_`：`use tokio_util::...`。）

把上面的 `watch` 換成它：

```rust,no_run
# extern crate tokio;
# extern crate tokio_util;
#
use std::time::Duration;
use tokio::task::JoinSet;
use tokio::time::{sleep, timeout};
use tokio_util::sync::CancellationToken;

async fn wait_next_job(id: u32, next_job: &mut u32) -> u32 {
    sleep(Duration::from_millis(500)).await;
    let job = *next_job;
    *next_job += 1;
    println!("worker {} 拿到工作 {}", id, job);
    job
}

async fn process_job(id: u32, job: u32) {
    sleep(Duration::from_millis(300)).await;
    println!("worker {} 處理完工作 {}", id, job);
}

async fn worker(id: u32, token: CancellationToken) {
    let mut next_job = 0;

    loop {
        let job = tokio::select! {
            job = wait_next_job(id, &mut next_job) => job,
            _ = token.cancelled() => { // 直接等「被取消」
                println!("worker {} 收到取消，退出", id);
                break;
            }
        };

        process_job(id, job).await;
    }
}

async fn drain_workers(workers: &mut JoinSet<()>) {
    while let Some(result) = workers.join_next().await {
        if let Err(error) = result {
            eprintln!("worker 非正常結束：{}", error);
        }
    }
}

#[tokio::main]
async fn main() {
    let token = CancellationToken::new();

    let mut workers = JoinSet::new();
    for id in 0..3 {
        workers.spawn(worker(id, token.clone())); // 每個 worker 拿一份 clone
    }

    tokio::signal::ctrl_c().await.expect("監聽 Ctrl-C 失敗");
    token.cancel(); // 一聲令下，全部取消

    match timeout(Duration::from_secs(5), drain_workers(&mut workers)).await {
        Ok(()) => println!("所有 worker 均已結束"),
        Err(_) => {
            println!("等待收尾逾時，要求取消剩下的 worker");
            workers.abort_all();
        }
    }
}
```

`token.cancelled()` 是一個等「被取消」的 `Future`，`token.cancel()` 一呼叫，所有持有 `clone` 的 worker 都會醒來。它讀起來就是「取消」的意思，比借 `watch` 當開關更貼合需求。

## 重點整理

- graceful shutdown：通知收工，等待手邊工作完成；逾時則要求取消剩餘工作。
- 三要素：訊號來源（`tokio::signal::ctrl_c()`）、廣播 shutdown（`watch` flag）、等待 drain（用 `join_next()` 逐一檢查結果，直到 `JoinSet` 空掉）。
- `select!` 適合用來同時等「下一份工作」與「shutdown」；若真正的工作不能安全取消，就先用 `select!` 拿到工作，再離開 `select!` 處理，避免 shutdown 把處理中的工作 `drop` 在半路（cancellation safety）。
- 用 `timeout` 設定自行收尾的期限，逾時後用 `abort_all()` 要求取消。
- 更匹配的工具是 `tokio_util` 的 `CancellationToken`：`token.cancel()` 一聲令下，所有 `token.cancelled()` 都醒來，語意比借 `watch` 更貼切。
