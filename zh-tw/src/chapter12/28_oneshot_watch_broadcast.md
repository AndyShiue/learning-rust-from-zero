# `oneshot`、`watch` 與 `broadcast`

## 本集目標

認識另外三種 channel，並學會用「發送端與接收端的數量」來判斷該用哪一個。

## 正文

上一集的 `mpsc` 是「多發送、單接收」。Tokio 還有三種 channel，各自適合不同的狀況。最基本的不同之處是**發送端**和**接收端**各有幾個，以及訊息怎麼流。

### `oneshot`：一個值，一次

`oneshot` 是「**一個發送端、一個接收端、只送一個值**」。最適合「背景算一個結果，算好送回來」這種一次性的回傳。

```rust,editable
extern crate tokio;

use tokio::sync::oneshot;

#[tokio::main]
async fn main() {
    let (tx, rx) = oneshot::channel::<i32>();

    tokio::spawn(async move {
        // 算好一個結果，送回去（send 只能用一次，而且不用 .await）
        tx.send(42).expect("接收端不見了");
    });

    // rx 本身就是一個 Future，.await 它就拿到那個值
    let result = rx.await.expect("發送端不見了");
    println!("拿到結果：{result}");
}
```

注意 `oneshot` 的接收端 `rx` 本身就是一個 `Future`，直接 `rx.await` 即可。其實第 12 集我們手寫的 `JoinHandle` 就很像一個 `oneshot`——背景算好一個值、透過共享狀態送回給等待者。

### `watch`：只關心「最新狀態」

`watch` 是「**一個發送端、多個接收端，但接收端只看得到最新的值**」。它不是排隊收每一則訊息，而是像一個「公告欄」：發送端隨時更新上面的內容，接收端只關心「現在公告欄上寫什麼」。中間錯過的舊值不會補給你。

這最適合用來廣播如「目前設定是什麼」的狀態。

```rust,editable
extern crate tokio;

use tokio::sync::watch;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = watch::channel("啟動中");

    tokio::spawn(async move {
        tx.send("執行中").expect("沒有接收端");
        tx.send("完成").expect("沒有接收端");
    });

    // changed().await 等到值有更新，borrow() 讀目前最新的值
    while rx.changed().await.is_ok() {
        println!("最新狀態：{}", *rx.borrow());
    }
}
```

### `broadcast`：每個接收端都要看到每則訊息

`broadcast` 是「**多發送、多接收，而且每個接收端都會收到每一則訊息**」。和 `watch` 不同，它不是只給最新值，而是每則都送到每個接收端手上。適合「一則事件要通知所有訂閱者」的場景。

```rust,editable
extern crate tokio;

use tokio::sync::broadcast;

#[tokio::main]
async fn main() {
    let (tx, mut rx1) = broadcast::channel::<i32>(16);
    let mut rx2 = tx.subscribe(); // 多開一個接收端

    tx.send(1).expect("沒有接收端");
    tx.send(2).expect("沒有接收端");

    // rx1 和 rx2 都會收到 1 和 2
    println!("rx1 收到：{}", rx1.recv().await.unwrap());
    println!("rx1 收到：{}", rx1.recv().await.unwrap());
    println!("rx2 收到：{}", rx2.recv().await.unwrap());
    println!("rx2 收到：{}", rx2.recv().await.unwrap());
}
```

## 重點整理

- 用「發送端 / 接收端數量 + 訊息怎麼流」來選 channel
- `oneshot`：單送單收、一個值一次，接收端本身是 `Future`（`rx.await`），適合回傳結果
- `watch`：單送多收、只看得到最新值，適合廣播目前狀態；用 `changed().await` + `borrow()`
- `broadcast`：多送多收、每個接收端都收到每一則，適合把事件通知所有訂閱者
- 對照上一集的 `mpsc`（多送單收、收每一則、工作佇列）
