# `select!`

## 本集目標

學會用 `select!` 等待多個 branch，直到其中一個完成且輸出符合 pattern，並理解它和取消（cancellation）的密切關係。

## 正文

### 等「誰先到」

`join!` 等的是「**全部**都完成」。`select!` 可說是它的一種相反：它同時等多個 branch，只要其中一個完成，而且輸出符合左邊的 pattern，就執行那個 branch 對應的 handler，然後整個 `select!` 就結束——**其他還沒完成的 branch 會被 `drop` 掉**。

### 基本語法

`select!` 的每個 branch 大致長這樣：

```rust,ignore
tokio::select! {
    pattern = future => {
        // future 完成後，輸出會被 pattern 接住
    }
    _ = other_future => {
        // 不關心 other_future 的輸出
    }
}
```

等號前的 `pattern` 用來接住等號後那個 `Future` 的輸出；如果 pattern 裡綁定了變數，那個變數會被帶進右邊的大括號裡使用。等號後寫的是要等待的 `Future` 而已，這裡**不要**自己加 `.await`。`select!` 會負責同時 `poll` 這些 `Future`，等其中一個完成且輸出符合 pattern。

如果你不需要某個 `Future` 的輸出，就像一般 `match` pattern 一樣用 `_` 忽略它：

```rust,ignore
tokio::select! {
    value = compute() => {
        println!("算出來了：{}", value);
    }
    _ = shutdown.recv() => {
        println!("收到 shutdown 訊號");
    }
}
```

如果輸出本身是 `Option<T>` 或 `Result<T, E>`，最直覺的寫法是先把整個值接住，再在 handler 裡自己 `match`：

```rust,ignore
tokio::select! {
    message = receiver.recv() => {
        match message {
            Some(message) => println!("收到訊息：{}", message),
            None => println!("channel 關閉"),
        }
    }
    _ = shutdown.recv() => {
        println!("準備關閉");
    }
}
```

`select!` 本身也可以有回傳值，回傳的是勝出 branch 大括號裡最後一個表達式。這點跟 `match` 很像：每個 branch 都要回傳同一種型別。

```rust,ignore
let status = tokio::select! {
    value = compute() => {
        println!("算出來了：{}", value);
        "done"
    }
    _ = shutdown.recv() => {
        println!("收到 shutdown 訊號");
        "shutdown"
    }
};

println!("狀態：{}", status);
```

`select!` 最經典的用途是 **timeout**：把「真正的工作」和「一個計時器」一起 `select!`，看誰先到。

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

輸掉的 branch 不會執行自己的大括號，這本來就是 `select!` 的正常行為，問題不在這裡。真正要小心的是：那個輸掉的 `Future` 在被丟掉以前，可能已經造成一部分外部效果，例如從 socket 讀走一些 bytes，或把一部分資料寫出去。

所以風險不是「handler 沒跑」，而是「`Future` 被取消時，已經做了一半的事沒有被完整收尾」。如果這個操作需要跨多步累積進度，就應該把進度放在 `select!` 外面，branch 裡只等待一次可以安全取消的小步驟。本章後面我們會示範如何遵守這樣的設計原則。

### 幾個實用補充

`select!` 還有幾個常用功能：

**branch precondition**：在 branch 後面加 `, if 條件`。這個條件可以使用進入 `select!` 前就已經存在的變數，例如下面的 `accepting_jobs`；但不能使用左邊 pattern 才會綁定的變數。`job` 要等 `jobs.recv()` 完成且 `Some(job)` 匹配成功後，才能在 handler 裡使用。

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

處理一次 `select!` 時，相關步驟依序是：

1. 先求值所有 branch 的 `if` precondition；條件為假的 branch 會在這次 `select!` 中被停用。
2. 求值所有等號右邊的 `async` 表達式，包括已停用 branch 的表達式。條件為假時，表達式仍會被求值以建立 `Future`，但產生的 `Future` 不會被 `poll`。這裡的「求值」是建立 `Future`，不是執行其中的 `async` 工作；不過，建立 `Future` 前的參數運算等一般表達式仍會執行。
3. `poll` 其餘 branch 的 `Future`。
4. 某個 `Future` 完成後，嘗試用它的輸出匹配左邊的 pattern。匹配成功就執行 handler 並結束 `select!`；匹配失敗則停用這個 branch，繼續等待其他 branch。因此最先完成的 branch 不一定會勝出；勝出的是完成且 pattern 匹配成功的 branch。
5. 所有 branch 都被停用時，執行 `else`；如果沒有 `else`，`select!` 會 panic。

**`else` branch**：例如 `Some(job) = jobs.recv()` 遇到 channel 關閉、`.recv()` 回 `None` 時，`Some(job)` 會匹配失敗，這個 branch 便會被停用。如果其他 branch 也全部被停用，就會執行 `else`。

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

**公平性與 `biased;`**：`select!` 預設是**隨機**挑選同時就緒的 branch（避免某個 branch 永遠被優先，餓死其他人）。如果你希望改成「由上到下依序檢查」，在開頭加一行 `biased;`。

```rust,ignore
tokio::select! {
    biased; // 改成由上到下依序檢查，而非隨機
    _ = high_priority() => { /* ... */ }
    _ = low_priority()  => { /* ... */ }
}
```

## 重點整理

- `select!` 同時等多個 branch，第一個完成且輸出符合 pattern 的 branch 會執行對應 handler，其他 branch 被 `drop`（取消）。
- 基本語法是 `pattern = future => { ... }`；`=>` 左邊不用寫 `.await`，不需要輸出時用 `_ = future`；`select!` 本身也能回傳勝出 branch 的值。
- 所以 `select!` 是程式裡**最常製造取消**的地方；適合 timeout、多 channel 接收、等 shutdown 訊號。
- 在 `loop` 裡用 `select!` 要注意 cancellation safety：別把 `read_exact` 這類不可安全取消的 `Future` 放進會被 `drop` 的 branch。
- 補充功能：branch `if`（precondition）、pattern 不匹配時停用該 branch、`else`（所有 branch 都被停用時）、`biased;` 把預設的隨機改成依序。
