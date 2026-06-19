# `FuturesUnordered`：大量動態的 Future

## 本集目標

學會處理「**很多個、而且數量會變動**」的 future——`join!` 不適合的場景。

## 概念說明

### `join!` 的極限

第 22 集的 `join!` 很好用,但它有兩個前提:future 的數量是**固定**的(你在寫程式時就要把每個分支列出來),而且通常數量不多。

可是真實的工作常常是這樣:「我有一個清單,裡面有 500 個網址,我要全部抓下來,最多同時抓 50 個。」這裡 future 是**動態產生**的(跑的時候才知道有幾個)、而且**數量很多**。你沒辦法寫 `join!(抓第1個, 抓第2個, ..., 抓第500個)`——數量不固定,根本列不出來。

這種「一大堆、動態的 future」就交給 **`FuturesUnordered`**。

### 一個「誰先好就先吐誰」的容器

`FuturesUnordered`(來自 `futures` crate)是一個**裝 future 的容器**。你把一堆 future 丟進去,它會同時推進裡面所有的 future,而它本身是一個 stream(第 29 集)——你用 `next().await` 拿結果,**哪個 future 先完成,就先吐出哪個的結果**(unordered = 不保證順序,以完成先後為準)。

```rust,ignore
use futures::stream::FuturesUnordered;
use futures::StreamExt;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let mut tasks = FuturesUnordered::new();

    // 動態地把一堆 future 丟進去
    for i in [3, 1, 2] {
        tasks.push(async move {
            sleep(Duration::from_secs(i)).await;
            format!("等了 {} 秒的任務", i)
        });
    }

    // 誰先完成就先拿到誰(所以這裡的輸出順序是 1 秒、2 秒、3 秒)
    while let Some(result) = tasks.next().await {
        println!("{}", result);
    }
}
```

把它想成一個「**完成佇列**」:你塞一堆事情進去,它幫你同時跑,誰先好就先把誰的結果遞給你——很適合「我要儘快處理每個完成的結果,不在乎順序」的批次工作。

### 和 `join!`、`spawn` 怎麼分工

這三個都能「同時做很多事」,但定位不同,放一起對照最清楚:

```text
工具                適合的情況
─────────────       ──────────────────────────────────────────
join! / try_join!   固定、少量、可能不同型別的 future,等全部完成
FuturesUnordered    大量、動態產生的 future,誰先好先處理,在同一個 task 內並行
tokio::spawn        要把工作丟到 runtime 變成獨立 task(可跨執行緒),需 Send + 'static
```

注意 `FuturesUnordered` 和 `spawn` 的關鍵差別:`FuturesUnordered` 裡的 future 是在**目前這一個 task** 裡被並行推進的(沒變成獨立 task、不跨執行緒,所以不需要 `Send + 'static`);`spawn` 則是真的把每個工作交給排程器變成獨立 task。爬蟲、批次 API 請求這類「一個函式內要併發很多事、還想限制併發數」的工作,`FuturesUnordered` 通常最順手。

### 搭配 backpressure 限制併發數

回到那個「500 個網址、最多同時 50 個」的需求。`FuturesUnordered` 加上一點控制就能做到:維持容器裡大約 50 個 future,每當有一個完成(`next().await` 吐出一個),就再 `push` 一個新的進去,讓「同時在跑的數量」穩定在 50。`futures` 還提供更高階的 `for_each_concurrent`,一行就能表達「對這個 stream 的每個 item 併發處理,但最多同時 N 個」,本質上就是這個模式的包裝。

```rust,ignore
use futures::StreamExt;

#[tokio::main]
async fn main() {
    let urls = vec!["a", "b", "c", "d", "e"];

    // 對每個 url 併發處理,但最多同時 2 個
    futures::stream::iter(urls)
        .for_each_concurrent(2, |url| async move {
            fetch(url).await;
        })
        .await;
}
# async fn fetch(_url: &str) {}
```

`for_each_concurrent` 的那個 `2` 就是併發上限——和第 25 集 semaphore 限制同時數量是同一個 backpressure 精神,只是換了個更順手的寫法。

## 範例程式碼

上面「動態 push、誰先好先處理」的範例就是 `FuturesUnordered` 的核心用法。再強調一次它和 `join!` 的差別:`join!` 要你把每個 future 寫死在巨集裡,`FuturesUnordered` 讓你在迴圈裡動態 `push`、邊跑邊收結果——這才扛得住「數量跑起來才知道」的批次工作。

## 重點整理

- `join!` 適合**固定、少量**的 future;**大量、動態產生**的 future 用 `FuturesUnordered`
- `FuturesUnordered`(`futures` crate)是裝 future 的容器,本身是個 stream,**誰先完成就先 `next().await` 吐出誰**
- 它在**同一個 task** 內並行推進(不跨執行緒、不需 `Send + 'static`),和 `spawn` 變獨立 task 不同
- 適合爬蟲、批次請求等「一個函式內併發很多事」的工作;配合「完成一個補一個」可限制併發數
- `for_each_concurrent(N, ...)` 是更高階的包裝,一行表達「併發處理但最多同時 N 個」——延續第 25 集的 backpressure 精神
