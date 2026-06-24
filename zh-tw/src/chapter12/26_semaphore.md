# `Semaphore` 與 backpressure

## 本集目標

用 semaphore 限制「同時進行的數量」,並理解 backpressure(背壓)這個概念。

## 概念說明

### 一個常見的需求:限制同時數量

假設你要下載 1000 個檔案。你當然不想一個一個下載(太慢),但也不該 1000 個同時下載——這會塞爆網路、開太多連線、可能被對方封鎖。你想要的是「**最多同時下載 10 個**,有空位才放下一個進來」。

控制「同時最多幾個」的工具,就是 **semaphore(號誌)**。

### semaphore = 一疊有限的通行證

把 semaphore 想成櫃台上一疊**通行證(permit)**,數量固定,比方說 10 張。規則是:

- 想開始工作,先去拿一張通行證(`acquire`)。拿得到就開始;沒了(10 張都被拿走)就**在那裡等**,直到有人還回來。
- 工作做完,把通行證**還回去**,讓下一個等待的人能拿。

因為通行證總共就 10 張,所以**同時最多就只有 10 個工作在進行**。這就達成了「限制並行數量」。

```rust,ignore
use std::sync::Arc;
use tokio::sync::Semaphore;

#[tokio::main]
async fn main() {
    // 一疊 10 張通行證
    let semaphore = Arc::new(Semaphore::new(10));

    let mut handles = Vec::new();
    for i in 0..1000 {
        let sem = semaphore.clone();
        handles.push(tokio::spawn(async move {
            // 拿一張通行證;拿不到就在這裡 .await 等
            let _permit = sem.acquire().await.unwrap();

            download(i).await; // 做事——此刻最多只有 10 個 task 同時跑到這裡

            // _permit 在這裡離開 scope、自動還回去,下一個等待者就能拿到
        }));
    }

    for h in handles { h.await.unwrap(); }
}
# async fn download(_i: i32) {}
```

### RAII:通行證自己會還

注意我們**沒有**手動寫「還通行證」的程式碼。`acquire()` 回傳的 `_permit`,是一個會在離開 scope 時**自動把通行證還回去**的東西——就是第 5 章的 `Drop`、以及第 8 章 `MutexGuard` 那套 RAII 模式。permit 還活著,代表你還佔著一個名額;它一被 drop,名額就釋出。所以只要讓 permit 在「你做事的那段範圍」內活著就好,剩下的它自己管。

(小提醒:正因為 permit 一 drop 名額就放開,別不小心讓它太早被丟掉——例如寫成 `let _ = sem.acquire().await;`,`_` 會讓 permit **當場就 drop**,等於沒限制到。要用具名的 `let _permit = ...` 把它留住。)

### backpressure:當下游跟不上,讓上游慢下來

semaphore 背後是一個更通用的概念,叫 **backpressure(背壓)**。

想像一條生產線:上游一直生產工作,下游負責處理。如果上游生產得比下游處理得快,工作就會越積越多——記憶體被未處理的工作塞爆,系統垮掉。backpressure 的意思是:**當下游忙不過來時,要有一個機制讓上游「慢下來、先等一等」**,而不是無限制地塞。

semaphore 就是一種 backpressure:通行證有限,拿不到的人得等,於是「正在進行的量」被自然地壓在容量之內。很多東西本質上都是這個模式:

- **有容量上限的 channel**(下一集的 bounded channel):佇列滿了,送的人就得等。
- **connection pool(連線池)**:連線數有限,要用得先借、用完還。
- **worker pool**:固定數量的 worker,工作多了就排隊。

它們都可以用同一句話理解:**容量有限,滿了就等空位。** 認得這個模式,你就能在很多看似不同的工具裡看到同一個影子。

## 範例程式碼

```rust,ignore
use std::sync::Arc;
use tokio::sync::Semaphore;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let semaphore = Arc::new(Semaphore::new(2)); // 同時最多 2 個
    let mut handles = Vec::new();

    for i in 1..=6 {
        let sem = semaphore.clone();
        handles.push(tokio::spawn(async move {
            let _permit = sem.acquire().await.unwrap();
            println!("任務 {} 開始", i);
            sleep(Duration::from_secs(1)).await; // 假裝在做事
            println!("任務 {} 結束", i);
        }));
    }

    for h in handles { h.await.unwrap(); }
}
```

跑起來你會看到任務一次只開始兩個,前面的結束、釋出通行證後,後面的才接著開始——同時進行數被牢牢壓在 2。

## 重點整理

- `Semaphore` 控制「同時最多幾個」:`acquire().await` 拿一張通行證(拿不到就等),做完釋出
- 通行證(permit)用 **RAII** 管理:離開 scope 自動還回去——和 `MutexGuard` 同一套;別用 `let _ =` 讓它當場 drop
- 背後的通用概念是 **backpressure**:下游忙不過來時,讓上游等一等,避免工作無限堆積撐爆系統
- 同模式的還有:bounded channel(下一集)、連線池、worker pool——都是「容量有限,滿了就等空位」
