# 第一個 async 程式

## 本集目標

照著抄出一個能跑的 async web server，先感受 async 程式長什麼樣子。

## 概念說明

### 先別急著理解每一行

還記得第 1 章教 `stdin` 的時候嗎？那時候我們先把一大段看不懂的程式照抄下來，讓它能動，之後才慢慢解釋。這一集也是一樣：我們要寫一個**網頁伺服器**——一個跑起來之後會在背景一直等人連線、有人連進來就回一句話的程式。大部分的語法你現在還不會，沒關係，先當黑盒子抄下來。

我們選網頁伺服器當第一個例子是有原因的：async 最擅長的就是這種「同時招呼很多人、但大部分時間都在等」的工作。等你抄完跑起來，會親眼看到一條執行緒就能同時服務好幾個瀏覽器分頁。我們還會讓伺服器記住「目前已經處理過幾個 request」，每個連進來的人都會看到自己是第幾個。

### 準備 Cargo.toml

先用 `cargo new hello_async` 開一個新專案（第 7 章教過），然後在 `Cargo.toml` 的 `[dependencies]` 底下加兩個外部 crate：

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
axum = "0.7"
```

`tokio` 是目前最主流的 async **runtime**（執行 async 程式的引擎，本章後面會詳細解釋它在做什麼）；`axum` 是一個建立在 tokio 上、用來寫網頁伺服器的 crate。`features = ["full"]` 代表「tokio 的功能我全都要」，初學階段先這樣最省事。

### 程式碼

把 `src/main.rs` 換成這樣：

```rust,ignore
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
use axum::{extract::State, routing::get, Router};

#[tokio::main]
async fn main() {
    // 一個所有 request 共用的計數器，從 0 開始
    let counter = Arc::new(AtomicUsize::new(0));

    // 設定：有人連到網址 "/" 時，交給 handler 處理，並把計數器分享給它
    let app = Router::new()
        .route("/", get(handler))
        .with_state(counter);

    // 在本機的 3000 連接埠開始聽
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    println!("伺服器跑在 http://127.0.0.1:3000");

    // 開始服務，這行會一直跑下去
    axum::serve(listener, app).await.unwrap();
}

// 每進來一個 request，這個函數就會被呼叫一次
async fn handler(State(counter): State<Arc<AtomicUsize>>) -> String {
    // 計數器加 1，並拿到「這是第幾個」
    let n = counter.fetch_add(1, Ordering::SeqCst) + 1;
    format!("這是第 {} 個 request", n)
}
```

`cargo run` 之後，打開瀏覽器連到 `http://127.0.0.1:3000`，會看到「這是第 1 個 request」。重新整理一次，變成「這是第 2 個 request」，再一次「第 3 個」……每連一次數字就加一。按 Ctrl-C 可以把伺服器關掉。

### 那個計數器先怎麼看

伺服器要能「記住已經處理過幾個 request」，就需要一份**所有 request 共用**的資料，這就是 `counter`。每個 request 進來時，`handler` 把它加一、讀出目前的數字回給對方。

這裡幾個東西先當黑盒子，但它們其實你都見過影子：`Arc`（第 8 章，讓多個地方安全共用同一份資料）、`AtomicUsize` 和 `fetch_add`（第 8 章的 atomic，多個 request 可能在不同執行緒上同時加這個計數器，atomic 保證不會加錯）。`fetch_add(1, ...)` 會「先把舊值拿出來、再加一」，所以我們補一個 `+ 1` 得到加完之後的數字。`with_state` 則是 axum 把這份共用資料交給每個 `handler` 的方式。這些細節之後都會更清楚，現在知道「它是一個大家共用、每次加一的計數器」就夠了。

### 三個值得先注意的地方

雖然大部分先當黑盒子，但有三個東西我們從這一集就要開始留意，因為接下來整章都圍著它們轉：

第一個是 `#[tokio::main]`。它放在 `main` 上面，作用是「幫我把 main 接到 tokio 這台引擎上」。少了它，async 的 `main` 是不會自己跑起來的——之後會解釋為什麼。

第二個是 `async fn`。我們的 `main` 和 `handler` 前面都有一個 `async` 關鍵字。一個函數只要標上 `async`，它就變成一個「非同步函數」。它和普通函數差在哪，下一集和第 3 集會講。

第三個、也是最重要的，是 `.await`。你看 `bind(...).await` 和 `serve(...).await` 後面都接了一個 `.await`。可以先這樣理解它：

> `.await` 是一個「**等待點**」。執行到這裡，如果要等的事情還沒好（例如還沒有人連進來），程式不會傻傻卡在這裡空等，而是會**把這條執行緒讓出去做別的事**，等事情好了再回到這裡繼續。

這就是 async 的核心魔法，也是它和第 8 章「一條執行緒卡著等」最不一樣的地方。一條執行緒之所以能同時服務很多連線，靠的就是每個 `.await` 都把等待的空檔讓出來給別人用。

## 範例程式碼

如果你想看到「一條執行緒同時招呼很多人」更明顯一點，可以讓每個 request 先假裝查一秒資料庫再回話。把 `handler` 改成這樣（其餘不變）：

```rust,ignore
use std::time::Duration;

async fn handler(State(counter): State<Arc<AtomicUsize>>) -> String {
    let n = counter.fetch_add(1, Ordering::SeqCst) + 1;
    // 假裝在查資料庫，等一秒
    tokio::time::sleep(Duration::from_secs(1)).await;
    format!("這是第 {} 個 request（等了一秒才回你）", n)
}
```

開兩、三個瀏覽器分頁「同時」連進去，你會發現它們幾乎是一起在一秒後拿到回應，而且分別顯示不同的 request 編號，而不是排隊一個等完一秒、下一個再等一秒。明明只有一條主執行緒，卻能同時招呼好幾個人——因為大家都卡在 `sleep` 的 `.await` 上等待，而那個等待是「讓得出去」的。

## 重點整理

- async 特別適合「同時處理很多連線、但大部分時間都在等」的工作，網頁伺服器是經典例子
- 寫 async 程式通常會用一個 runtime，本章用最主流的 **tokio**
- `#[tokio::main]` 把 async 的 `main` 接到 tokio 引擎上，少了它跑不起來
- `async fn` 是非同步函數；每個 request 會呼叫一次 `handler`
- 伺服器用一個共用的計數器（`Arc` + atomic，第 8 章的老朋友）記住處理過幾個 request，回給每個人它的編號
- `.await` 是「等待點」：要等的事情還沒好時，把執行緒讓出去做別的，好了再回來繼續——這是 async 能用一條執行緒招呼很多人的關鍵
- 這一集大部分語法先當黑盒子，後面幾集會逐一拆解
