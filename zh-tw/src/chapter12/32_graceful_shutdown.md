# graceful shutdown

## 本集目標

把前面學的工具兜成一個完整的**優雅關閉**：當程式被要求停止時,不要硬生生切斷正在進行的工作,而是**通知大家「該收工了」→ 等手上的事做完（或在期限內做完）→ 再乾淨退出**。這一集幾乎沒有新 API,主要是 `select!`（第 25 集）、`watch`（第 28 集）與 `JoinSet`（第 31 集）的組合練習。

## 概念說明

### 為什麼需要優雅關閉

一個長期執行的程式——web server、背景 worker、訊息處理器——遲早會被要求停止：使用者按 Ctrl-C、容器平台送來 SIGTERM、部署時要換新版本。如果這時直接讓 process 結束,**正在處理到一半的工作會被硬切斷**：連線突然斷掉、檔案寫到一半、資料庫交易沒 commit、訊息收了卻沒處理完。

優雅關閉就是「**有禮貌地收尾**」：停止接受新工作 → 讓進行中的工作跑完 → 釋放資源 → 退出。注意它和第 24 集的「取消」剛好是一體兩面——取消是「中途喊停、丟掉」,優雅關閉則是「儘量**別**中途喊停,給它時間做完」。

### 拆成三個要素

要做到優雅關閉,需要回答三個問題,剛好對上三樣工具：

```text
1. 怎麼知道該關了？      → shutdown 訊號來源（tokio::signal::ctrl_c()）
2. 怎麼告訴所有 task？    → 廣播一個 shutdown 訊號（watch，第 28 集）
3. 怎麼等大家真的做完？  → 等待 drain（JoinSet，第 31 集）
```

### 要素一：接收 shutdown 訊號

`tokio::signal::ctrl_c()` 回傳一個 future,**等到使用者按下 Ctrl-C 才完成**：

```rust,ignore
tokio::signal::ctrl_c().await.unwrap();
println!("收到 Ctrl-C，開始關閉");
```

（實務上的伺服器除了 Ctrl-C（SIGINT）,通常還要處理容器平台送的 **SIGTERM**——用 `tokio::signal::unix::signal(SignalKind::terminate())`,常見作法是用 `select!` 同時等這兩種訊號,任一來就開始關閉。）

### 要素二：把 shutdown 廣播給每個 task —— 用 `watch`

收到訊號之後,要怎麼讓**所有**正在跑的 task 都知道「該收工了」？這正是第 28 集 `watch` 的拿手好戲：它帶一個「最新值」、是一對多廣播、而且晚訂閱的人一進來就讀得到當前狀態。我們用一個 `watch::channel(false)` 當 **shutdown flag**：`false` = 繼續跑,`true` = 該關了。

每個 worker 用 `select!`（第 25 集）**同時等兩件事**：自己的工作、以及「shutdown 變 true」。哪個先來就處理哪個：

```rust,ignore
loop {
    tokio::select! {
        _ = shutdown.changed() => {
            break; // 收到關閉訊號，跳出迴圈去收尾
        }
        job = next_job() => {
            handle(job).await; // 平常的工作
        }
    }
}
```

> **這裡藏著一個 cancellation safety 的設計重點（呼應第 24、25 集）。** `select!` 在 shutdown 分支贏的時候,會把另一條 branch 的 future `drop` 掉＝取消它。所以你要確保「被取消的那條 branch」是**可以安全取消的**——上面把「拿下一份工作（`next_job()`）」放在會被取消的 branch,而真正處理工作（`handle(job).await`）是拿到工作後才在 branch **裡面**完整跑完,不會被 shutdown 從中間砍斷。換句話說:**讓 shutdown 只會打斷「等待下一份工作」,不會打斷「正在處理的那一份」**。這就是「進行中的工作能跑完」的關鍵。

### 要素三：等所有 task 做完（drain）

廣播完 shutdown,`main` 不能馬上 `return`——那樣 runtime 一收,還沒退出的 task 就被丟掉了。我們要**等所有 worker 真的收工**。把 worker 都收進一個 `JoinSet`（第 31 集）,關閉時用 `join_next()` 一路等到它空掉就行：

```rust,ignore
while set.join_next().await.is_some() {} // 等到 JoinSet 全空
```

### 給優雅一個期限：`timeout`

「等大家做完」聽起來很美,但萬一某個 task 卡住、永遠做不完呢？優雅關閉**不能無限期等**。實務上的標準作法是**給一個期限**：最多等 N 秒,逾時就不再客氣、強制中止剩下的。用 `tokio::time::timeout` 包住 drain,逾時就 `abort_all()`（或直接 `drop` 掉 `JoinSet`——第 31 集講過,它一被 drop 就 abort 裡面所有 task）：

```rust,ignore
match timeout(Duration::from_secs(5), drain).await {
    Ok(()) => println!("所有 worker 都乾淨退出了"),
    Err(_) => { set.abort_all(); } // 逾時：強制中止
}
```

這就是真實世界的「graceful shutdown with a deadline」：**先禮貌地等,等不到就動手**。

## 範例程式碼

把三個要素組起來：三個 worker 各自跑著工作,`main` 等 Ctrl-C,收到後廣播關閉、再等它們收工（最多 5 秒）。

```rust,ignore
use std::time::Duration;
use tokio::sync::watch;
use tokio::task::JoinSet;
use tokio::time::{sleep, timeout};

async fn worker(id: u32, mut shutdown: watch::Receiver<bool>) {
    loop {
        tokio::select! {
            // shutdown flag 變了：跳出去收尾
            _ = shutdown.changed() => {
                println!("worker {id}：收到關閉，準備收工");
                break;
            }
            // 平常的工作（用 sleep 代表處理一份請求）
            _ = sleep(Duration::from_millis(500)) => {
                println!("worker {id}：處理完一份工作");
            }
        }
    }
    // 收尾：flush、關連線、commit……（這裡只印個訊息）
    println!("worker {id}：已乾淨退出");
}

#[tokio::main]
async fn main() {
    // false = 繼續跑，true = 該關了
    let (shutdown_tx, shutdown_rx) = watch::channel(false);

    let mut set = JoinSet::new();
    for id in 0..3 {
        set.spawn(worker(id, shutdown_rx.clone()));
    }
    drop(shutdown_rx); // main 自己不需要 receiver

    // 等 Ctrl-C
    tokio::signal::ctrl_c().await.unwrap();
    println!("收到 Ctrl-C，開始 graceful shutdown");

    // 1) 廣播關閉
    shutdown_tx.send(true).unwrap();

    // 2) 等所有 worker 收工，但最多等 5 秒
    let drain = async { while set.join_next().await.is_some() {} };
    match timeout(Duration::from_secs(5), drain).await {
        Ok(()) => println!("所有 worker 都乾淨退出了"),
        Err(_) => {
            println!("逾時！還有 worker 沒收工，強制中止");
            set.abort_all(); // 等同 drop(set)：JoinSet 一 drop 就 abort 剩下的
        }
    }
}
```

跑起來會持續印出 worker 處理工作的訊息;按下 Ctrl-C 後,三個 worker 各自印「收到關閉 → 已乾淨退出」,`main` 確認全部收工才結束。

### 更道地的做法：`CancellationToken`

上面用 `watch` 當 shutdown flag,是為了複習已學的工具。但實務上**廣播 shutdown 這件事有個更道地的專用工具**:`tokio-util` 的 **`CancellationToken`**。

`watch` 本來是用來「廣播一個會變的值」的,我們只是借它的 `bool` 當開關;而 `CancellationToken` 從頭就是為「取消／關閉」設計的——它**沒有值**,只有「還沒取消」和「已取消」兩個狀態,而且取消是**單向、不可逆、idempotent**(取消很多次跟取消一次一樣)。用起來就是:複製一份給每個 task,任何一處呼叫 `cancel()`,所有持有它的人都會在 `cancelled().await` 那裡醒來。

把前面的 worker 換成 `CancellationToken`,`select!` 的那條 branch 讀起來更直白:

```rust,ignore
use tokio_util::sync::CancellationToken;

async fn worker(id: u32, token: CancellationToken) {
    loop {
        tokio::select! {
            // 被取消了：跳出去收尾
            _ = token.cancelled() => {
                println!("worker {id}：收到關閉，準備收工");
                break;
            }
            _ = sleep(Duration::from_millis(500)) => {
                println!("worker {id}：處理完一份工作");
            }
        }
    }
    println!("worker {id}：已乾淨退出");
}

#[tokio::main]
async fn main() {
    let token = CancellationToken::new();

    let mut set = JoinSet::new();
    for id in 0..3 {
        set.spawn(worker(id, token.clone())); // 複製一份給每個 worker
    }

    tokio::signal::ctrl_c().await.unwrap();
    token.cancel(); // 一句話通知全體收工

    let drain = async { while set.join_next().await.is_some() {} };
    let _ = timeout(Duration::from_secs(5), drain).await;
    // 逾時的話 set 在這裡 drop 掉，JoinSet 自動 abort 剩下的（第 31 集）
}
```

比起 `watch`,它省掉了「初始值 `false`、要記得 `send(true)`、用 `changed()` 判斷」這些跟「取消」無關的細節,意圖更純粹。而且 `CancellationToken` 還能**組成父子階層**:`token.child_token()` 生出來的子 token,父一取消就連帶取消,但取消子不會反過來影響父——很適合「關閉整個服務 → 連帶關閉它底下每個子系統」這種樹狀結構。另外它也提供 `run_until_cancelled(future)`,一行表達「跑這個 future,但 token 一取消就放棄」。

至於**等待 drain** 那一半,`tokio-util` 也有對應的 **`TaskTracker`**:它把「追蹤一堆 task、等它們全部結束」包好,取代你手動維護 `JoinSet` 的 drain 迴圈。`CancellationToken`(廣播取消)＋ `TaskTracker`(等全部結束)兩個搭起來,就是 tokio 生態系裡最常見的優雅關閉骨架。

原理和這集從零做的一模一樣——`select!` ＋ 廣播訊號 ＋ 等待 drain——只是不必自己接線。知道底層在做什麼,你看到 `CancellationToken` / `TaskTracker` 就懂了。

## 重點整理

- **優雅關閉**＝收到停止要求時,不硬切進行中的工作,而是「通知收工 → 等做完（或到期限）→ 乾淨退出」;它是第 24 集「取消」的反面——儘量**不**中途喊停
- 三要素:**訊號來源**（`tokio::signal::ctrl_c()`,實務再加 SIGTERM）、**廣播 shutdown**（`watch` flag,第 28 集）、**等待 drain**（`JoinSet`,第 31 集）
- 每個 task 用 `select!`（第 25 集）同時等「自己的工作」與「shutdown 訊號」;設計時要讓 shutdown 只打斷「等下一份工作」、不打斷「正在處理的那一份」（cancellation safety,呼應第 24、25 集）
- 優雅關閉**要給期限**:用 `tokio::time::timeout` 包住 drain,逾時就 `abort_all()` / `drop` 掉 `JoinSet` 強制收掉剩下的——「先禮貌地等,等不到就動手」
- 實務上**廣播 shutdown 更道地的工具是 `tokio-util` 的 `CancellationToken`**:複製給每個 task、任一處 `cancel()` 全體在 `cancelled().await` 醒來,取消單向不可逆、還能父子階層;比借 `watch` 當開關更純粹。等 drain 那半則有 `TaskTracker`。兩者底層仍是 `select!` ＋ 廣播 ＋ 等待 drain
