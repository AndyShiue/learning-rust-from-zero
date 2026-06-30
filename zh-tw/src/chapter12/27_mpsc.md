# `mpsc`

## 本集目標

學會用 `async` 版的 `mpsc` channel 在 `Task` 之間傳遞工作，並理解 bounded channel 的 backpressure。

## 正文

### `Task` 之間的工作佇列

第 9 章我們用過 `std::sync::mpsc` 讓 `Thread` 之間傳訊息。`async` 世界有對應的 `tokio::sync::mpsc`，是 `Task` 之間最常見的「工作佇列」：一邊（生產者）把工作 `send` 進去，另一邊（消費者）`recv` 出來處理。一樣是 **multi-producer single-consumer**——可以有很多發送端，但只有一個接收端。

```rust,editable
extern crate tokio;

use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    // 建立一個容量 32 的 bounded channel
    let (tx, mut rx) = mpsc::channel::<i32>(32);

    // 生產者：spawn 出去送 5 個工作
    tokio::spawn(async move {
        for i in 0..5 {
            tx.send(i).await.expect("接收端已關閉");
            println!("送出 {}", i);
        }
        // tx 在這裡 drop，接收端的 recv 之後會收到 None
    });

    // 消費者：一直收到 channel 關閉
    while let Some(value) = rx.recv().await {
        println!("收到 {}", value);
    }
    println!("channel 關閉了，結束");
}
```

`rx.recv().await` 回傳 `Option`：有訊息就是 `Some(value)`，所有發送端都 `drop` 之後就回 `None`，於是 `while let` 自然結束。

### bounded channel 與 backpressure

注意我們建立 channel 時給了一個容量 `32`——這是 **bounded（有容量上限的）** channel。容量上限正是上一集 backpressure 的延伸。

當 channel 裡累積的訊息**塞滿** 32 個（代表消費者來不及處理），生產者的 `tx.send(value).await` 就會**等待**，直到消費者收走一些、騰出空位才繼續。這就是 backpressure：消費者忙不過來時，自動讓生產者慢下來，而不是讓訊息無限堆積把記憶體塞爆。

這也解釋了為什麼 `send` 要 `.await`——因為它**可能要等**（等空位）。對照第 9 章同步版的 `send` 不用等（那是無上限的），這裡的 `.await` 正是 backpressure 的體現。Tokio 也有 `unbounded_channel`，它的 `send` 不用 `.await`，但就沒有 backpressure，要小心用。

## 重點整理

- `tokio::sync::mpsc` 是 `async` `Task` 之間最常見的工作佇列：多發送端、單接收端
- `rx.recv().await` 回傳 `Option`，所有發送端 `drop` 後回 `None`，可用 `while let Some(x) = rx.recv().await` 走訪
- **bounded channel** 有容量上限，塞滿時 `send().await` 會等待——這就是 backpressure，逼生產者配合消費者的速度
- `send` 要 `.await` 正是因為它可能要等空位；`unbounded_channel` 不用等但沒有 backpressure
