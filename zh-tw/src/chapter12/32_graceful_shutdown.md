# graceful shutdown

## 本集目標

把前面學的工具兜成一個完整的 graceful shutdown（優雅關閉）流程。

## 正文

### 什麼是 graceful shutdown

伺服器要關閉時，最粗暴的做法是直接砍掉——但這樣進行到一半的工作就斷在那裡，可能留下壞掉的資料、沒回應完的請求。**graceful shutdown** 是更有禮貌的關法：收到停止要求時不硬切，而是「**通知大家收工 → 等手邊的工作做完（或到期限）→ 乾淨退出**」。

把它拆成三個要素：

1. **訊號來源**：怎麼知道「該關了」。
2. **廣播 shutdown**：怎麼把「要收工了」告訴所有 worker。
3. **等待 drain**：怎麼等所有 worker 收尾完畢。

我們用前面學過的工具，一個一個對上。

### 三要素組起來

- **訊號來源**用 `tokio::signal::ctrl_c()`——它是個 `Future`，`.await` 它會等到使用者按下 Ctrl-C（實務上還會再加上監聽 SIGTERM）。
- **廣播 shutdown**用第 28 集的 `watch` 當一個 shutdown flag：一對多、而且晚訂閱的 worker 也讀得到當前狀態。
- **等待 drain**用第 31 集的 `JoinSet`，`join_next()` 一直收到全空為止。

每個 worker 內部用 `select!`，**同時**等「自己的工作」和「shutdown 訊號」，哪個先到反應哪個：

```rust,no_run
# extern crate tokio;
#
use std::time::Duration;
use tokio::sync::watch;
use tokio::task::JoinSet;
use tokio::time::{sleep, timeout};

async fn worker(id: u32, mut shutdown: watch::Receiver<bool>) {
    loop {
        tokio::select! {
            // 自己的工作：這裡用 sleep 假裝「處理一份工作」
            _ = sleep(Duration::from_millis(500)) => {
                println!("worker {id} 處理了一份工作");
            }
            // 收工訊號
            _ = shutdown.changed() => {
                println!("worker {id} 收到收工訊號，退出");
                break;
            }
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
    tokio::signal::ctrl_c().await.expect("無法監聽 Ctrl-C");
    println!("收到 Ctrl-C，開始 graceful shutdown");

    // 2. 廣播收工
    shutdown_tx.send(true).expect("沒有 worker 在聽");

    // 3. 等所有 worker drain，但給 5 秒期限
    match timeout(Duration::from_secs(5), async {
        while workers.join_next().await.is_some() {}
    })
    .await
    {
        Ok(()) => println!("所有 worker 都乾淨退出了"),
        Err(_) => {
            println!("逾時！強制中止剩下的 worker");
            workers.abort_all();
        }
    }
}
```

這裡的 `timeout(Duration::from_secs(5), future)` 可以讀成：「最多等這個 `future` 五秒」。

它自己也是一個 `Future`。如果裡面的 `future` 在五秒內完成，`.await` 會得到 `Ok(裡面的輸出)`；如果五秒到了還沒完成，`.await` 會得到 `Err(_)`。在這個例子裡，裡面的 `future` 是：

```rust,ignore
async {
    while workers.join_next().await.is_some() {}
}
```

也就是「一直等 worker 結束，直到 `JoinSet` 空掉」。所以整段 `timeout` 的意思是：**最多等五秒讓所有 worker 自己收尾；五秒內都退完就印成功，超過五秒就進入 `Err(_)`，把剩下的 worker 強制 abort**。

### cancellation safety 的設計重點

這裡有個呼應第 24、25 集的關鍵設計。worker 的 `select!` 一邊是「自己的工作」、一邊是「shutdown」。當 shutdown 那個 branch 勝出時，「自己的工作」那個 branch 會被 `drop`（取消）。

所以你要**刻意設計 `select!` 的位置**：讓 shutdown 取消的是「**等下一份工作**」這種可以重來的等待，而不是「**已經開始處理的那一份**」。如果真正的處理流程不能安全取消，就先在 `select!` 裡等到工作，離開 `select!` 之後再處理它；不要把那段處理直接放進會輸給 shutdown 的 branch。否則像 `read_exact` 這類不可安全取消的操作，就可能被 shutdown 砍在半路，資料也跟著掉了。這就是前面強調過的 cancellation safety 在 shutdown 上的具體應用。

### 一定要給期限

graceful 不代表**無限期**等。萬一某個 worker 卡死了，你不能讓整個程式陪它一直耗下去。所以 drain 一定要**給期限**：上面用 `tokio::time::timeout` 把整個 drain 包起來，逾時就 `abort_all()`（或直接 `drop` 掉 `JoinSet`，它會自動 abort 剩下的 `Task`）強制收掉。

一句話總結這個原則：**先禮貌地等，等不到就動手**。

### 更匹配的工具：`CancellationToken`

用 `watch` 當 shutdown flag 可行，但有點像「借」一個狀態廣播工具來當開關。`tokio-util` 提供了一個從頭就為「取消」設計的工具——`CancellationToken`，語意更貼切。把上面的 `watch` 換成它：

```rust,no_run
# extern crate tokio;
# extern crate tokio_util;
#
use std::time::Duration;
use tokio::task::JoinSet;
use tokio::time::{sleep, timeout};
use tokio_util::sync::CancellationToken;

async fn worker(id: u32, token: CancellationToken) {
    loop {
        tokio::select! {
            _ = sleep(Duration::from_millis(500)) => {
                println!("worker {} 處理了一份工作", id);
            }
            _ = token.cancelled() => { // 直接等「被取消」
                println!("worker {} 收到取消，退出", id);
                break;
            }
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

    tokio::signal::ctrl_c().await.expect("無法監聽 Ctrl-C");
    token.cancel(); // 一聲令下，全部取消

    match timeout(Duration::from_secs(5), async {
        while workers.join_next().await.is_some() {}
    })
    .await
    {
        Ok(()) => println!("全部退出"),
        Err(_) => {
            println!("逾時！強制中止剩下的 worker");
            workers.abort_all();
        }
    }
}
```

`token.cancelled()` 是一個等「被取消」的 `Future`，`token.cancel()` 一呼叫，所有持有 clone 的 worker 都會醒來。它讀起來就是「取消」的意思，比借 `watch` 當開關更貼合需求（而且還支援父子 token 等進階用法）。

## 重點整理

- graceful shutdown：不硬切，而是「通知收工 → 等做完（或到期限）→ 乾淨退出」
- 三要素：訊號來源（`tokio::signal::ctrl_c()`）、廣播 shutdown（`watch` flag）、等待 drain（`JoinSet` 的 `join_next()` 到全空）
- `select!` 適合用來同時等「下一份工作」與「shutdown」；若真正的工作不能安全取消，就先用 `select!` 拿到工作，再離開 `select!` 處理，避免 shutdown 把處理中的工作 `drop` 在半路（cancellation safety）
- drain 一定要給期限：用 `tokio::time::timeout` 包住，逾時就 `abort_all()` 或 drop `JoinSet`——先禮貌地等，等不到就動手
- 更匹配的工具是 `tokio-util` 的 `CancellationToken`：`token.cancel()` 一聲令下，所有 `token.cancelled()` 都醒來，語意比借 `watch` 更貼切
