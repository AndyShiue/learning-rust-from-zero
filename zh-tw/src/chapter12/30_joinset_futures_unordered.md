# `JoinSet` 與 `FuturesUnordered`

## 本集目標

處理「**很多個、數量會變動、誰先好就先處理**」的並行工作——`join!` 不適合的場景。介紹兩個工具：`JoinSet`（spawn 版）與 `FuturesUnordered`（同一 task 內多工版），並講清楚什麼時候用哪個。

## 概念說明

### `join!` 的極限

第 22 集的 `join!` 很好用,但它有兩個前提:future 的數量是**固定**的(你寫程式時就要把每個分支列出來),而且通常數量不多。

可是真實工作常常是:「我有一個清單,裡面 500 個網址,要全部抓下來,最多同時抓 50 個。」這裡 future 是**動態產生**的(跑的時候才知道有幾個)、而且**數量很多**。你沒辦法寫 `join!(抓第1個, …, 抓第500個)`——數量不固定,根本列不出來。

### 兩條路,對應 `join!` 與 `spawn` 兩個世界

回想第 21、22 集那個分法:「在**同一個 task** 裡多工」是 `join!` 的世界;「交給 runtime 變成**獨立 task**」是 `spawn` 的世界。處理「大量動態」的工作,剛好也分這兩條路:

```text
join!  的動態版  →  FuturesUnordered（同一 task 內多工）
spawn  的動態版  →  JoinSet（一堆獨立 spawn 的 task）
```

兩個用起來很像(都是「丟一堆進去、誰先好就先收誰」),但底層是不同世界。先各看一個。

### `JoinSet`：一堆 spawn 出去的 task，統一管理

`tokio::task::JoinSet` 把每個工作 `spawn` 成**獨立 task**(所以可跨 worker thread、真正平行),再幫你統一收集:`join_next().await` 哪個先完成就先吐出哪個的結果。

```rust,ignore
use tokio::task::JoinSet;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let mut set = JoinSet::new();

    // 動態地 spawn 一堆 task
    for i in [3, 1, 2] {
        set.spawn(async move {
            sleep(Duration::from_secs(i)).await;
            format!("等了 {} 秒的任務", i)
        });
    }

    // 誰先完成就先拿到誰（1、2、3 秒）
    while let Some(res) = set.join_next().await {
        match res {
            Ok(s) => println!("{}", s),
            Err(e) => println!("有 task 出事：{}", e), // panic 或被 abort
        }
    }
}
```

幾個重點:

- `set.spawn(fut)` 把工作變成**獨立 task**——可能落在不同 worker thread 上跑,所以是**真平行**;也因此 future 要 `Send + 'static`(和第 21 集 `tokio::spawn` 一樣)。
- `join_next()` 回的是 `Option<Result<T, JoinError>>`:某個 task **panic** 或被 **abort** 時,你會在這裡收到 `Err(JoinError)`(`e.is_panic()` 可判斷),不會讓 panic 默默吞掉。
- `set.abort_all()` 一次取消所有 task;而且 **`JoinSet` 被 drop 時,裡面所有 task 都會被 abort**——很適合「函式結束就把這批背景工作收乾淨」。

### `FuturesUnordered`：在同一個 task 內多工

`FuturesUnordered`(來自 `futures` crate)是一個**裝 future 的容器**。你把一堆 future 丟進去,它在**目前這一個 task** 裡同時推進它們;它本身是一個 stream(第 29 集),用 `next().await` 拿結果,**哪個先完成就先吐出哪個**。

```rust,ignore
use futures::stream::FuturesUnordered;
use futures::StreamExt;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let mut tasks = FuturesUnordered::new();

    for i in [3, 1, 2] {
        tasks.push(async move {
            sleep(Duration::from_secs(i)).await;
            format!("等了 {} 秒的任務", i)
        });
    }

    // 誰先完成就先拿到誰（1、2、3 秒）
    while let Some(result) = tasks.next().await {
        println!("{}", result);
    }
}
```

和 `JoinSet` 寫起來幾乎一樣,但底層差很多:`FuturesUnordered` 的 future **沒有變成獨立 task**,而是全部在目前這顆 task 裡輪流被 poll。所以:**不需要 `Send + 'static`**(可以放心借用周圍的區域變數)、回傳的就是 future 的值本身(沒有 `JoinError`,因為沒有獨立 task 可 panic/abort);但相對地,它們**不會跨 thread 平行**,而且某個 future 若長時間不 `.await`(重計算、blocking),會卡住同容器裡的其他 future(整顆 task 都被它佔住)。

### 怎麼選

```text
                  FuturesUnordered                JoinSet
跑在哪           目前這一個 task 裡多工          一堆獨立 spawn 的 task
平行             否（單 thread 上輪流）          是（可跨 worker thread）
Send + 'static   不需要（可借用區域變數）        需要（因為 spawn）
取結果            future 的值本身                Result<T, JoinError>
panic            一個 branch panic 會炸整顆 task  變成 join_next 的 Err
整批取消          丟掉容器即停                    abort_all() / drop 時自動 abort
出身             futures crate                  tokio
對應第 22 集     join! 的動態版                  spawn 的動態版
```

口訣:**想要真平行、或工作之間互不影響 → `JoinSet`;想就地借用區域變數、不想 spawn、工作很輕 → `FuturesUnordered`。**

### 限制併發數（backpressure）

回到那個「500 個網址、最多同時 50 個」的需求。兩種容器都能做到:**維持容器裡大約 50 個工作,每當完成一個(`next`/`join_next` 吐出一個),就再加一個進去**,讓「同時在跑的數量」穩定在 50。

`futures` 還提供更高階的 `for_each_concurrent`,一行就表達「對這個 stream 的每個 item 併發處理,但最多同時 N 個」,本質就是這個模式的包裝:

```rust,ignore
use futures::StreamExt;

#[tokio::main]
async fn main() {
    let urls = vec!["a", "b", "c", "d", "e"];

    // 對每個 url 併發處理，但最多同時 2 個
    futures::stream::iter(urls)
        .for_each_concurrent(2, |url| async move {
            fetch(url).await;
        })
        .await;
}
# async fn fetch(_url: &str) {}
```

那個 `2` 就是併發上限——和第 25 集 semaphore 限制同時數量是同一個 backpressure 精神,只是換了更順手的寫法。

## 範例程式碼

上面 `JoinSet` 與 `FuturesUnordered` 兩段「動態加入、誰先好先處理」的程式,就是它們的核心用法。對照一次:`join!` 要你把每個 future 寫死在巨集裡;這兩個讓你在迴圈裡**動態加入、邊跑邊收結果**,才扛得住「數量跑起來才知道」的批次工作。差別只在你要不要「真平行 + 獨立 task」(`JoinSet`)還是「同一 task 內輕量多工」(`FuturesUnordered`)。

## 重點整理

- `join!` 適合**固定、少量**的 future;**大量、動態產生**的用 `JoinSet` 或 `FuturesUnordered`
- 兩者對應第 22 集的兩個世界:**`FuturesUnordered` = `join!` 的動態版**(同一 task 多工)、**`JoinSet` = `spawn` 的動態版**(獨立 task)
- `JoinSet`(tokio):每個工作是獨立 task,**可跨 thread 平行**,要 `Send + 'static`;`join_next()` 回 `Result<T, JoinError>`,panic/abort 會收到 `Err`;`abort_all()` 或 drop 可整批取消
- `FuturesUnordered`(futures crate):在**同一 task** 內多工,**不跨 thread、不需 `Send + 'static`**(可借用區域變數),但一個 branch 卡住會拖累其他
- 兩者都能「完成一個補一個」限制併發數;`for_each_concurrent(N, …)` 是更高階的包裝,延續第 25 集 backpressure 精神
