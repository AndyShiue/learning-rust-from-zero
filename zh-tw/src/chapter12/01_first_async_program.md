# 第一個 `async` 程式

## 本集目標

直接用 Tokio 寫一個會回應瀏覽器的小小伺服器，先對 `async` 程式長什麼樣子有個印象。

## 概念說明

歡迎來到非同步的世界！這一章我們會花很多力氣，慢慢把 `async` 的原理一層一層挖開。不過第一集先不講原理，我們直接寫一個能跑的程式，讓你對 `async` 的程式碼長相先有個感覺。讀到這裡的你已經學過很多東西了，相信光看程式碼，大概就猜得出它在做什麼。

### Rust 的 `async` 需要一個 runtime

和很多語言不一樣，Rust 標準庫本身**沒有**內建非同步的執行引擎（我們之後會叫它 runtime）。標準庫只定義了非同步的「規格」，至於要怎麼真的把這些非同步的工作跑起來，是交給第三方套件決定的。這聽起來有點奇怪，但這個設計讓 Rust 的 `async` 可以用在從大型伺服器到小型嵌入式裝置等各種場合。

目前最多人用的 runtime 叫做 **Tokio**。這一章絕大多數時候，我們講到「實際能跑的 `async` 程式」用的就是 Tokio。要使用它，先在 `Cargo.toml` 加上依賴：

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

或是用指令：

```bash
cargo add tokio --features full
```

### 一個會數數的伺服器

下面這個程式會在你的電腦上開一個小伺服器，每當有人連進來，就回一句「這是第 N 個 request」。所有連線共用同一個計數器，所以你重新整理瀏覽器時，數字會一直往上加：

```rust,no_run
# extern crate tokio;
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
            let body = format!("這是第 {n} 個 request\n");
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

把它跑起來之後，打開瀏覽器連到 `http://127.0.0.1:8080`，重新整理幾次，你會看到數字一直增加。

### `.await` 是什麼意思

程式裡出現了好幾個 `.await`，這是 `async` 程式最核心的東西。你可以先這樣理解它：

> `.await` 的意思是「這件事可能要等一下才會好；在等的這段時間，請去做別的事，別呆呆站著」。

以 `listener.accept().await` 為例：接受一個新連線得等到真的有人連進來，這中間可能是幾毫秒，也可能是好幾秒。如果程式只是傻傻地卡在這裡，那這段時間整個程式什麼都不能做，太浪費了。`.await` 讓 runtime 在等待的空檔，把 CPU 拿去推進別的工作。

### 它真的能同時處理很多連線

注意我們用了 `tokio::spawn`，把「處理單一連線」這件事丟到背景。所以主迴圈不用等某個連線回應完，就能馬上回去 `accept` 下一個連線。也就是說，就算有很多人同時連進來，它們可以一起被處理，不會互相卡住。這種「同時推進很多件事」的能力，正是 `async` 的賣點。

下一集我們就來談談：為什麼要這樣寫？`async` 到底好在哪？

## 重點整理

- Rust 標準庫只定義 `async` 的規格，真正執行要靠第三方的 **runtime**，最常用的是 **Tokio**。
- `#[tokio::main]` 讓 `main` 可以寫成 `async fn`，幫你把 runtime 準備好。
- `.await` 的意思是「等這件事好，期間可以去做別的事」，而不是傻傻卡住。
- 搭配 `tokio::spawn` 把工作丟到背景，`async` 程式可以同時推進很多連線。
