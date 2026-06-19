# `mpsc` channel：async 的工作佇列

## 本集目標

用 tokio 的 async `mpsc` channel 在 task 之間傳工作,並理解 bounded channel 怎麼帶來 backpressure。

## 概念說明

### 又見 channel,這次是 async 版

第 8 章用過 `std::sync::mpsc`——多個生產者、單一消費者的 channel,讓執行緒之間傳訊息。tokio 提供 async 版的 `mpsc`,概念一樣,差別在:當你 `send` 而佇列滿了、或 `recv` 而還沒有訊息時,它是 `.await`(讓出執行緒)而不是卡住整條執行緒。

```rust,ignore
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    // 建立一個容量為 32 的 channel:tx 送、rx 收
    let (tx, mut rx) = mpsc::channel::<i32>(32);

    // 生產者:spawn 一個 task 一直送
    tokio::spawn(async move {
        for i in 0..5 {
            tx.send(i).await.unwrap(); // 送一個工作進去
        }
        // tx 在這裡 drop——之後 rx 會知道沒人再送了
    });

    // 消費者:一直收,直到所有 tx 都關閉
    while let Some(value) = rx.recv().await {
        println!("收到 {}", value);
    }
    println!("沒人再送了,結束");
}
```

### 它是 async task 之間最常見的工作佇列

這個模式——一個(或多個)task 一直把工作 `send` 進來,另一個 task 用 `while let Some(x) = rx.recv().await` 一個一個拿出來處理——是 async 程式裡最常見的結構之一,常被叫做 **worker loop(工作迴圈)**。生產者只管把工作丟進 channel,消費者只管從 channel 拿出來做,兩邊解耦,各自的節奏互不干擾。

`mpsc` 是 **multi-producer, single-consumer** 的縮寫:可以有**很多**個發送端(把 `tx` 用 `.clone()` 複製給多個 task,大家一起送),但只有**一個**接收端。

### `recv` 怎麼知道該停

消費者的 `while let` 什麼時候結束?當**所有** `tx`(含所有 clone)都被 drop 之後,`rx.recv().await` 會回傳 `None`,迴圈自然結束。這是判斷「工作送完了、可以收工」的標準方式——不需要額外傳一個「結束」訊號,把發送端關掉就是訊號。

### bounded channel:容量帶來 backpressure

建立 channel 時那個 `32`,是它的**容量**。這種有容量上限的叫 **bounded channel**,它正好接續上一集的 backpressure:

當 channel 裡已經積了 32 個還沒被處理的工作,生產者再 `send` 時,`send().await` 就會**等**——等到消費者拿走一些、騰出空間,才送得進去。換句話說,**消費者跟不上時,生產者會被自動拖慢**,工作不會無限堆積撐爆記憶體。這就是為什麼 `send` 是個要 `.await` 的操作:它可能需要等空位。

(tokio 也有 `unbounded_channel`,沒有容量上限、`send` 不用 `.await` 也不會等。但少了 backpressure,生產者暴衝時可能把記憶體吃光,要謹慎使用。一般優先用 bounded。)

### 搭配 `select!`:同時等工作和關機訊號

實務上消費者常常不只等工作,還要能回應「該關機了」。把第 23 集的 `select!` 配上來就很自然:

```rust,ignore
use tokio::sync::mpsc;

async fn worker(mut rx: mpsc::Receiver<i32>, mut shutdown: mpsc::Receiver<()>) {
    loop {
        tokio::select! {
            Some(job) = rx.recv() => {
                println!("處理工作 {}", job);
            }
            _ = shutdown.recv() => {
                println!("收到關機訊號,收工");
                break;
            }
        }
    }
}
```

消費者一邊等新工作、一邊等關機訊號,哪個先來處理哪個——這是 async 服務裡非常典型的骨架。

## 範例程式碼

多個生產者(`tx.clone()`)、單一消費者:

```rust,ignore
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel::<String>(16);

    // 開三個生產者,各自送幾則訊息
    for id in 1..=3 {
        let tx = tx.clone(); // 每個 task 一份發送端
        tokio::spawn(async move {
            for n in 1..=2 {
                tx.send(format!("生產者 {} 的第 {} 則", id, n)).await.unwrap();
            }
        });
    }
    drop(tx); // 丟掉最初那個 tx,否則 rx 會一直以為還有人要送

    // 單一消費者收到所有訊息,直到全部 tx 關閉
    while let Some(msg) = rx.recv().await {
        println!("{}", msg);
    }
}
```

注意那個 `drop(tx)`:三個 task 各自 clone 了一份 tx,但**最初的 tx** 還在 `main` 手上;如果不 drop 它,即使三個 task 都送完關閉了,`main` 手上這個 tx 還活著,`rx.recv()` 就會一直等下去。

## 重點整理

- tokio 的 `mpsc` 是 async 版 channel:`send`／`recv` 在滿／空時 `.await` 讓出執行緒,不卡死
- 「生產者 `send`,消費者 `while let Some(x) = rx.recv().await` 處理」是最常見的 **worker loop**
- `mpsc` = 多生產者(`tx.clone()`)、單消費者;**所有 `tx` 都 drop 後 `recv` 回 `None`**,用來判斷收工
- **bounded channel** 的容量帶來 **backpressure**:佇列滿時 `send().await` 會等,消費者跟不上就自動拖慢生產者
- 消費者常用 `select!` 同時等「新工作」和「關機訊號」
