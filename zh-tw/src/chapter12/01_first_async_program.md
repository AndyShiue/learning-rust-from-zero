# 第一個 `async` 程式

## 本集目標

直接動手寫一個會回應 HTTP 請求的小型 web server。語法細節先不深究——你已經寫了不少 Rust，這一集可以**靠經驗大致看懂 `async` 程式在做什麼**，把心智模型建立起來，後面幾集再把每個零件拆開講。

## 概念說明

### Rust 的 `async` 需要一個 runtime

Rust 語言本身只定義「`async` 的語法」和「`Future` 這個型別」（後面幾集會講），但**不內建執行它的引擎**。實際去跑 `async` 程式的那個引擎叫 **runtime**，要自己選一個。最常用的是 **Tokio**，這一集就用它。

頂層用 `#[tokio::main]` 把 `main` 標成 async，Tokio 會幫你把 runtime 架好、開始跑：

```rust,ignore
#[tokio::main]
async fn main() {
    // 這裡就是 async 世界，可以用 .await
}
```

### `.await` 是「等待時可以做別的事」

關鍵字就一個：**`.await`**。把它讀成「在這裡等一件事完成，而且**等的時候，這條執行緒可以挪去做別人的事**」。這正是 async 的賣點——等待網路、等待 I/O 的時候不會把執行緒卡死，而是讓別的工作見縫插針。

### 範例：一個會數 request 的 server

伺服器用一個**所有連線共用的計數器**，讓每個連進來的人看到「這是第 N 個 request」。每接到一條連線，就用 `tokio::spawn` 開一個**獨立的工作**去服務它——所以多個連線是**並行**處理的。

```rust,ignore
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use tokio::io::AsyncWriteExt;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    // 所有連線共用的計數器
    let counter = Arc::new(AtomicUsize::new(0));

    let listener = TcpListener::bind("127.0.0.1:8080").await.unwrap();
    println!("在 http://127.0.0.1:8080 等請求");

    loop {
        // 等下一條連線進來（等的時候執行緒不會被卡住）
        let (mut socket, _) = listener.accept().await.unwrap();
        let counter = counter.clone();

        // 每條連線各開一個獨立工作去服務，彼此並行
        tokio::spawn(async move {
            let n = counter.fetch_add(1, Ordering::SeqCst) + 1;
            let body = format!("這是第 {n} 個 request\n");
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}",
                body.len(),
                body
            );
            let _ = socket.write_all(response.as_bytes()).await;
        });
    }
}
```

`Cargo.toml` 需要：

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

跑起來後，用瀏覽器或 `curl http://127.0.0.1:8080` 連進去，會看到：

```text
這是第 1 個 request
這是第 2 個 request
...
```

開好幾個 `curl` 同時打，server 也接得住——這就是 async「同時處理很多連線」的本事。

### 先看出三件事就好

這一集不必看懂每個細節，先抓住這三點：

1. **`.await`**：黏在會「需要等」的動作後面（`accept().await`、`write_all().await`），意思是「在這等、但等的時候執行緒能去忙別的」。
2. **`#[tokio::main]`**：把 runtime 架起來、開始驅動整個 async 程式。
3. **`tokio::spawn`**：把一段 async 工作丟出去，讓它跟別人並行跑——所以一台 server 能同時服務很多連線。

接下來幾集，我們會把這些「黑盒子」一個一個打開：`async fn` 到底回傳什麼、`.await` 背後發生什麼事、runtime 又是怎麼把這些東西跑起來的。

## 重點整理

- Rust 只提供 `async` 語法與 `Future` 型別，**不內建 runtime**；要自己選一個來跑，最常用的是 **Tokio**
- `#[tokio::main]` 把 `main` 變成 async、並架好 runtime 開始驅動
- `.await` 黏在「需要等」的動作後面，意思是「在這等，但等待期間執行緒能挪去做別的事」
- `tokio::spawn` 把一段 async 工作交給 runtime 並行執行，所以一台 server 能同時處理很多連線
- 這一集先靠經驗看懂大概，後面幾集會把每個零件拆開細講
