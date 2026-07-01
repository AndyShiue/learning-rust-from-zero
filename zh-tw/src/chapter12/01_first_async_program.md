# 第一個 `async` 程式

## 本集目標

直接用 Tokio 寫一個會回應瀏覽器的小小伺服器，先對 `async` 程式長什麼樣子有個印象。

## 正文

歡迎來到非同步的世界！這一章我們會花很多力氣，慢慢把非同步（`async`）的原理一層一層挖開。不過第一集先不講原理，我們直接寫一個能跑的程式，讓你對 `async` 的程式碼長相先有個感覺。讀到這裡的你已經學過很多東西了，相信光看程式碼，大概就猜得出它在做什麼。

先從「非同步」這三個字的字面意思開始。**同步**是「大家照同一個步調走」：一件事沒做完，下一件事就先等著。**非同步**則是「不一定要照同一個步調等」：某件事正在等結果時，程式可以先去推進別的事。放到伺服器裡，就是等待某個瀏覽器連進來、或等待某個回應送出去時，不必讓其他連線都卡在原地。

### Rust 的 `async` 需要一個 runtime

和很多其他程式語言不一樣，Rust 標準庫本身**沒有**內建非同步的執行引擎（我們之後會叫它 runtime）。標準庫只定義了非同步的「規格」，至於要怎麼真的把這些非同步的工作跑起來，是交給第三方套件決定的。這聽起來有點奇怪，但這個設計讓 Rust 的 `async` 可以用在從大型伺服器到小型嵌入式裝置等各種場合。

目前最多人用的 runtime 叫做 **Tokio**。這一章後半，我們會深入了解 Tokio 的功能。要使用它，先在 `Cargo.toml` 加上依賴：

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

或是用指令：

```bash
cargo add tokio --features full
```

等一下的程式會在 `main` 裡直接寫 `.await`。這裡先記一個語法規則：**`.await` 只能出現在 `async` 的環境裡**。普通的 `fn main()` 裡不能直接 `.await`，所以我們會把它寫成 `async fn main()`。

不過，`async fn main()` 不能像普通的 `fn main()` 那樣自己直接當程式入口。`#[tokio::main]` 這個 attribute 就是 Tokio 提供的幫手：它會替我們準備 runtime，讓這個 `async fn main()` 可以真的被執行。

### 一個會數數的伺服器

下面這個程式會在你的電腦上開一個小伺服器，每當有人連進來，就回一句「這是第 N 個 request」。所有連線共用同一個計數器，所以你重新整理瀏覽器時，數字會一直往上加：

```rust,no_run
# extern crate tokio;
#
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};
use tokio::io::AsyncWriteExt;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() {
    // 所有連線共用的計數器
    let counter = Arc::new(AtomicU64::new(0));

    // 監聽本機的 8080 連接埠
    let listener = TcpListener::bind("127.0.0.1:8080").await.expect("無法監聽連接埠");
    println!("伺服器啟動了，請用瀏覽器打開 http://127.0.0.1:8080");

    loop {
        // 等待下一個連線進來
        let (mut socket, _) = listener.accept().await.expect("接受連線失敗");

        // 把計數器的所有權分一份給待會的背景工作
        let counter = Arc::clone(&counter);

        // 把這個連線丟到背景處理，主迴圈馬上回去等下一個連線
        tokio::spawn(async move {
            let n = counter.fetch_add(1, Ordering::SeqCst) + 1;
            let body = format!("這是第 {} 個 request\n", n);
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}",
                body.len(),
                body,
            );
            socket.write_all(response.as_bytes()).await.expect("回應失敗");
        });
    }
}
```

在你的電腦上把它跑起來之後，打開瀏覽器連到 `http://127.0.0.1:8080`，重新整理幾次，你會看到數字一直增加。

### `.await` 是什麼意思

程式裡出現了好幾個 `.await`，這是 `async` 程式最核心的東西。你可以先這樣理解它：

> `.await` 的意思是「這件事可能要等一下才會好；在等的這段時間，請試著找別的事做。」

以 `listener.accept().await` 為例：接受新連線要等到真的有人連進來，這中間可能是幾毫秒，也可能是好幾秒。`.await` 標出這個「可能需要等」的位置；等的期間，這個 `async` 工作可以先被暫停，把執行機會讓出去。

### 它真的能同時處理很多連線

注意我們用了 `tokio::spawn`，把「處理單一連線」這件事丟到背景。主迴圈只負責接收新連線；每接到一個，就生出一個背景工作去寫回應，自己立刻回去等下一個連線。

所以就算某個連線正在 `socket.write_all(response.as_bytes()).await`，主迴圈也不必等它寫完。其他連線可以繼續被接受、繼續被處理。這種把很多件事拆開、交錯推進的能力，正是 `async` 的賣點。

這一集先讓你看到 `async` 程式的長相和效果。下一集我們再把動機講清楚：它適合什麼場景、為什麼不直接開很多 `Thread`，以及「並行」和「平行」到底差在哪裡。

## 重點整理

- Rust 標準庫只定義 `async` 的規格，真正執行要靠第三方的 **runtime**，最常用的是 **Tokio**
- `.await` 只能寫在 `async` 的環境裡；`#[tokio::main]` 讓 `main` 可以寫成 `async fn`，並幫你把 runtime 準備好，把它驅動起來
- `.await` 的意思是「等這件事好，期間可以去做別的事」，而不是傻傻卡住
- 搭配 `tokio::spawn` 把工作丟到背景，`async` 程式可以同時推進很多連線
