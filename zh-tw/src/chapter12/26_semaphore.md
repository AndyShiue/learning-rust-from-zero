# `Semaphore` 與 backpressure

## 本集目標

學會用 `Semaphore` 限制「同時進行的數量」，並理解 backpressure（反壓）這個觀念。

## 概念說明

### 限制同時進行的數量

有些事情你不希望「無限制地一起做」。例如：同時下載的檔案數別太多（不然頻寬爆掉）、同時開啟的檔案數有上限、同時打某個 API 的請求數要節制（不然對方會擋你）。

`tokio::sync::Semaphore` 就是管這個的。它的核心是一把固定數量的 **permit（許可證）**：你設定總共有幾張 permit，誰要做事就得先**拿一張**，做完**還回去**。permit 被拿光時，後來的人就得**等**，直到有人還回一張。

```rust,no_run
# extern crate tokio;
use std::sync::Arc;
use tokio::sync::Semaphore;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    // 總共只有 3 張 permit，所以最多 3 個 task 能同時工作
    let semaphore = Arc::new(Semaphore::new(3));

    let mut handles = vec![];
    for i in 0..10 {
        let semaphore = Arc::clone(&semaphore);
        handles.push(tokio::spawn(async move {
            // 拿一張 permit，拿不到就 .await 等著
            let _permit = semaphore.acquire().await.expect("semaphore 已關閉");
            println!("task {i} 拿到 permit，開始工作");
            sleep(Duration::from_millis(100)).await;
            // _permit 在這裡離開 scope，自動把名額還回去
        }));
    }

    for h in handles {
        h.await.expect("task 失敗");
    }
}
```

雖然我們 spawn 了 10 個 task，但因為只有 3 張 permit，任何時刻最多只有 3 個在工作，其餘的乖乖排隊等 permit。

### permit 靠 `Drop` 自動歸還

注意上面我們拿到 permit 後，**完全沒有手動把它還回去**——它怎麼自己回來的？

因為 permit（`acquire().await` 回傳的那個值）實作了 `Drop`（第 5 章學過）。當 `_permit` 離開 scope 被 drop 時，它的 `Drop` 就自動把名額還給 `Semaphore`。所以你只要讓 permit 在「該結束」的時候離開 scope，歸還就自動發生，不會忘記。這也是為什麼我們用 `let _permit = ...` 把它綁成一個變數——是為了讓它**活到工作結束**才被 drop；如果寫成 `let _ = ...`，它會立刻被 drop，permit 馬上就還回去了，等於沒限制到。

### backpressure（反壓）

`Semaphore` 帶出一個更一般的觀念：**backpressure**。

想像一條生產線：上游一直送東西進來，下游慢慢處理。如果上游送得比下游處理得快，東西就會越積越多——記憶體被塞爆只是時間問題。backpressure 的意思就是：**當下游忙不過來時，要有辦法讓上游「慢下來、等一等」**，而不是讓它無限制地塞。

`Semaphore` 正是一種 backpressure：permit 代表「容量」，容量滿了，想進來的人就被擋在 `acquire().await` 等待，自然就慢了下來。

下一集要講的 **bounded channel** 也是同一個道理——它的容量有限，滿了的時候 `send().await` 就會等待，逼上游放慢腳步。所以你可以用「**容量有限，滿了就等 permit**」這個角度，去理解各種帶 backpressure 的工具。

## 重點整理

- `tokio::sync::Semaphore` 用固定數量的 **permit** 表示容量，限制「同時進行的數量」：同時下載數、同時開檔數、同時進入某段流程的 `Task` 數等。
- `acquire().await` 拿一張 permit，拿不到就等；permit 實作 `Drop`，離開 scope 時自動把名額還回去。
- 用 `let _permit = ...` 讓 permit 活到工作結束才歸還；別寫成 `let _ = ...`（會馬上 drop）。
- **backpressure**：下游忙不過來時讓上游等一等，避免無限堆積；`Semaphore`（和下一集的 bounded channel）都可以用「容量有限、滿了就等」來理解。
