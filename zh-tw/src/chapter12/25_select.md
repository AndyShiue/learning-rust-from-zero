# `select!`

## 本集目標

學會用 `select!` 等待「多個 branch 中第一個完成的」，並理解它和取消（cancellation）的密切關係。

## 正文

### 等「誰先到」

`join!` 等的是「**全部**都完成」。`select!` 可說是它的一種相反：它同時等多個 branch，只要**第一個**完成，就執行那個 branch 對應的 handler，然後整個 `select!` 就結束——**其他還沒完成的 branch 會被 `drop` 掉**。

最經典的用途是 **timeout**：把「真正的工作」和「一個計時器」一起 `select!`，看誰先到。

```rust,editable
extern crate tokio;

use tokio::time::{sleep, Duration};

async fn do_work() {
    sleep(Duration::from_secs(5)).await; // 假設工作要五秒
    println!("工作完成");
}

#[tokio::main]
async fn main() {
    tokio::select! {
        _ = do_work() => {
            println!("工作順利做完了");
        }
        _ = sleep(Duration::from_secs(1)) => {
            println!("逾時！工作太久了，不等了");
        }
    }
}
```

這裡計時器一秒就到，比五秒的工作快，所以 `select!` 走計時器那個 branch、印出「逾時」，然後**把 `do_work()` 那個 `Future` `drop` 掉**——工作就此被取消。

`select!` 很適合這些情境：

- **timeout**（上面的例子）。
- **同時接收多個 channel**：哪個 channel 先有訊息就處理哪個。
- **等待 shutdown signal**：一邊做正常工作，一邊聽「該收工了」的訊號，誰先到就反應誰。

### 在迴圈裡用 `select!` 要小心 cancellation safety

剛剛提到了 `drop`：這正是上一集講的 **cancellation**：`drop` 一個 `Future` 就是取消它。而 `select!` 天生就會在某個 branch 勝出時，把其他 branch 全部 `drop`。理解這一點，後面用 `select!` 才不會踩雷。   

`select!` 常常被放在 `loop` 裡反覆使用（例如一個伺服器迴圈：每輪 `select!` 等「新工作」或「shutdown 訊號」）。這種寫法要特別小心上一集的 **cancellation safety**。

回想上一集：`read_exact` 這類「跨多次推進、累積中間狀態」的操作**不是 cancellation safe**，中途被取消時，可能已經消費了一部分資料，但整個「讀滿 buffer」的動作沒有完成。而 `select!` 每一輪都可能因為**別的** branch 先完成，而把這一個 branch 的 `Future` `drop` 掉（取消）。如果你把 `read_exact` 放進 `select!` 的某個 branch，又在 `loop` 裡反覆跑，那它就很可能在讀到一半時被取消，留下不好接續的半成品。

所以原則是：**別把非 cancellation safe 的 `Future` 放進「會被 `drop` 的 `select!` branch」**。如果非用不可，要嘛改用 cancellation safe 的替代寫法，要嘛把累積狀態保存在 branch 外面、讓它能跨輪存活。第 32 集講 graceful shutdown 時，會再看到同一個設計原則：`select!` 可以拿來等 shutdown，但要安排好，別讓它把處理到一半的工作砍掉。

### 幾個實用補充

`select!` 還有幾個常用功能：

**branch precondition**：在 branch 後面加 `,if 條件`。條件為假時，這個 branch 直接略過，不會參與本輪競爭。

```rust,ignore
tokio::select! {
    Some(job) = jobs.recv(), if accepting_jobs => {
        handle(job).await;
    }
    _ = shutdown.recv() => {
        accepting_jobs = false;
    }
}
```

**`else` 分支**：當所有 branch 都因為 precondition 被略過，沒有任何 branch 能跑時，執行 `else`。

```rust,ignore
tokio::select! {
    Some(job) = jobs.recv(), if accepting_jobs => {
        handle(job).await;
    }
    Some(msg) = messages.recv(), if accepting_messages => {
        handle_message(msg).await;
    }
    else => {
        break; // 這一輪沒有任何 branch 能跑
    }
}
```

**公平性與 `biased;`**：`select!` 預設是**隨機**挑選同時就緒的 branch（避免某個 branch 永遠被優先、餓死其他人）。如果你希望改成「由上到下依序檢查」，在開頭加一行 `biased;`。

```rust,ignore
tokio::select! {
    biased; // 改成由上到下依序檢查，而非隨機
    _ = high_priority() => { /* ... */ }
    _ = low_priority()  => { /* ... */ }
}
```

## 重點整理

- `select!` 同時等多個 branch，**第一個**完成就執行對應 handler，其他 branch 被 `drop`（取消）
- 所以 `select!` 是程式裡**最常製造取消**的地方；適合 timeout、多 channel 接收、等 shutdown 訊號
- 在 `loop` 裡用 `select!` 要注意 cancellation safety：別把 `read_exact` 這類不可安全取消的 `Future` 放進會被 `drop` 的 branch
- 補充功能：branch `if`（precondition）、`else`（所有 branch 都被略過時）、`biased;` 把預設的隨機改成依序
