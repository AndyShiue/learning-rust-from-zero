# `oneshot`、`watch` 與 `broadcast`

## 本集目標

認識另外三種 channel,學會用「訊息的拓樸」來選對工具。

## 概念說明

### 不是只有 mpsc 一種 channel

上一集的 `mpsc` 適合「一串工作排隊處理」。但訊息傳遞還有別的形狀,tokio 針對不同形狀提供了不同的 channel。選哪一個,先問三個問題:

1. 有**幾個發送端**、**幾個接收端**?
2. 要傳的是「一連串訊息」,還是「就一個值」?
3. 接收端要看到**每一則**訊息,還是只關心**最新狀態**?

### `oneshot`:只送一次,回傳一個結果

`oneshot` 就是字面意思——**一個發送端、一個接收端,只傳一個值,傳完就結束**。最典型的用途是「我請另一個 task 幫我算個東西,算完把結果送回來給我」。

```rust,ignore
use tokio::sync::oneshot;

#[tokio::main]
async fn main() {
    let (tx, rx) = oneshot::channel::<i32>();

    tokio::spawn(async move {
        // 做一些計算 ...
        tx.send(42).unwrap(); // 送出唯一的那個結果(注意:不用 .await)
    });

    let result = rx.await.unwrap(); // 等那一個結果
    println!("拿到 {}", result);
}
```

注意 `rx` 本身就是個 future,直接 `rx.await` 就好。`oneshot` 常被當作各種「請求—回應」的回傳管道:你發一個請求出去,順便附上一個 `oneshot` 的 `tx`,對方做完用它把答案送回來。

### `watch`:只關心「最新狀態」

`watch` 適合「**有一個會變動的狀態,大家只關心它現在是什麼**」。它有一個發送端、多個接收端。發送端每次 `send` 會**覆蓋**掉舊值,接收端讀到的永遠是**最新**的那個——中間錯過的舊值不重要。

```rust,ignore
use tokio::sync::watch;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = watch::channel("啟動中");

    tokio::spawn(async move {
        tx.send("執行中").unwrap();
        tx.send("關閉中").unwrap(); // 接收端可能只看到最新的「關閉中」
    });

    // changed() 等到值有變動,再用 borrow() 看目前的值
    while rx.changed().await.is_ok() {
        println!("目前狀態：{}", *rx.borrow());
    }
}
```

`watch` 最經典的用途是 **shutdown flag(關機旗標)**:主程式把狀態設成「該關機了」,所有在背景跑的 task 都 watch 著這個旗標,一變動就知道該收尾。因為大家只需要知道「現在要不要關機」,不需要每一次變動的歷史,正好是 `watch` 的形狀。

### `broadcast`:每個接收端都要看到每一則

`broadcast` 適合「**一則訊息要讓所有接收端都收到**」——多個發送端、多個接收端,而且和 `watch` 不同,它**保留每一則**訊息發給每一個接收端(只要接收端跟得上)。

```rust,ignore
use tokio::sync::broadcast;

#[tokio::main]
async fn main() {
    let (tx, mut rx1) = broadcast::channel::<&str>(16);
    let mut rx2 = tx.subscribe(); // 再要一個接收端

    tx.send("大家好").unwrap();

    // 兩個接收端都會各自收到「大家好」
    println!("rx1: {}", rx1.recv().await.unwrap());
    println!("rx2: {}", rx2.recv().await.unwrap());
}
```

典型用途是「事件廣播」:聊天室裡一個人發言,所有人都要收到;或一個事件要通知好幾個獨立的處理者。

### 對照表

把四種 channel 放一起,用「訊息拓樸」來記最清楚:

```text
channel      發送  接收   特性
─────────    ───   ───   ──────────────────────────────
mpsc         多    一     一串工作排隊;有容量會 backpressure
oneshot      一    一     只送一個值,請求—回應的回傳管道
watch        一    多     只保留最新狀態;適合 shutdown flag
broadcast    多    多     每則訊息發給每個接收端;事件廣播
```

選 channel 時別硬背,回到那三個問題:**幾個 sender、幾個 receiver、要每一則還是只要最新。** 形狀對上了,工具就選對了。

## 範例程式碼

用 `watch` 當 shutdown flag,通知多個 worker 一起收工:

```rust,ignore
use tokio::sync::watch;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let (shutdown_tx, shutdown_rx) = watch::channel(false); // false = 還不用關

    // 開三個 worker,都盯著同一個關機旗標
    let mut handles = Vec::new();
    for id in 1..=3 {
        let mut rx = shutdown_rx.clone();
        handles.push(tokio::spawn(async move {
            loop {
                if *rx.borrow() { // 旗標變 true 就收工
                    println!("worker {} 收工", id);
                    break;
                }
                // ... 做一點工作 ...
                let _ = rx.changed(); // 簡化:實務上會配 select!
                sleep(Duration::from_millis(100)).await;
            }
        }));
    }

    sleep(Duration::from_secs(1)).await;
    shutdown_tx.send(true).unwrap(); // 一聲令下,大家一起收工

    for h in handles { h.await.unwrap(); }
}
```

## 重點整理

- 選 channel 先問三件事:**幾個發送端、幾個接收端、要每一則還是只要最新狀態**
- `oneshot`:一對一、只送一個值;請求—回應的回傳管道(`rx` 本身就是 future)
- `watch`:一對多、只保留**最新**狀態;經典用途是 shutdown flag
- `broadcast`:多對多、**每則**訊息發給**每個**接收端;事件廣播
- 加上上一集的 `mpsc`(多對一、工作佇列),四種形狀涵蓋了大部分 task 間溝通的需求
