# `AsyncRead` 與 `AsyncWrite`

## 本集目標

認識 `async` 版的 byte I/O，並第一次接觸 `async` 特有的「取消（cancellation）」概念。

## 正文

### `async` 版的讀寫

第 11 章我們用過同步的 `Read` / `Write` trait。`async` 世界有對應的 `AsyncRead` / `AsyncWrite`，概念一樣，只是讀寫的動作變成可以 `.await`。

有個重要性質要先講：底層的 `read` / `write` 只承諾「**嘗試推進一次**，回傳這次實際處理了幾個 byte」。它**不保證**一次就讀滿你的 buffer，也不保證一次就把資料全部寫完。比方說你想讀 100 個 byte，某次 `read` 可能只給你 30 個——剩下的得你自己再讀。

### 用 `AsyncReadExt` / `AsyncWriteExt` 的便利 helper

每次都自己處理「沒讀滿、沒寫完」很煩。所以 Tokio 在 `AsyncReadExt` / `AsyncWriteExt` 這兩個擴充 trait 裡，提供了幾個幫你包好迴圈的 helper：

- `read_exact(&mut buf)`：一直讀，直到把 `buf` **填滿**為止。
- `write_all(buf)`：一直寫，直到把 `buf` **整個寫完**為止。

```rust,no_run
# extern crate tokio;
#
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

#[tokio::main]
async fn main() {
    let mut stream = TcpStream::connect("127.0.0.1:8080").await.expect("連線失敗");

    // write_all：保證把整個 buffer 寫完（內部可能呼叫底層 write 好幾次）
    stream.write_all(b"GET / HTTP/1.0\r\n\r\n").await.expect("寫入失敗");

    // read_exact：保證讀滿 16 個 byte
    let mut buf = [0u8; 16];
    stream.read_exact(&mut buf).await.expect("讀取失敗");
    println!("讀到 16 個 byte：{:?}", buf);
}
```

（要用這些 helper，記得 `use tokio::io::{AsyncReadExt, AsyncWriteExt};`，方法才會出現。）

### 第一次認識「取消」

`read_exact` 這類 helper，剛好帶我們碰到一個 `async` 非常重要、卻容易忽略的概念：**取消（cancellation）**。

還記得 `Future` 是惰性的嗎？它只有被 `poll` 才會動。反過來說——如果你**不再 `poll` 它**、直接把它 `drop` 掉，那這個 `async` 工作就等於被**喊停**了，它後面的程式碼再也不會執行。這就是 `async` 的取消：**`drop` 一個 `Future` 就是取消它**。

這是 `async` 特有的能力。普通的 `Thread` 做不到這種乾淨的喊停——你沒辦法從外面安全地把一條正在跑的 thread 中途叫停。但 `async` 工作只是一個還沒跑完的 `Future`，你不理它、把它丟掉，它就停了。

### `read_exact` 不是 cancellation safe

取消雖然方便，卻有個陷阱。像 `read_exact` 這種「**跨好幾次推進、中途累積狀態**」的操作要小心。

想像 `read_exact` 正要讀 100 個 byte，已經讀進 30 個、暫存在自己內部，正在 `.await` 等剩下的 70 個。這時如果它被取消（被 `drop`），那已經讀進來的 30 個 byte 就**跟著它一起消失**了——這 30 個 byte 已經從 socket 拿走、回不去了，但你也沒拿到。資料就這樣遺失了。

我們說 `read_exact` **不是 cancellation safe（取消安全）**：它被中途取消會留下爛攤子（遺失已讀的資料）。所以你**不該**把 `read_exact` 這類操作，放進「可能會被中途丟掉」的地方。

那「可能會被中途丟掉的地方」是哪裡？最典型的就是下一集要講的 `select!`——它天生就會在某個 branch 完成時，把其他還沒完成的 branch `drop` 掉（也就是取消）。所以下一集我們會再回到這個 cancellation safety 的話題，看看在 `select!` 裡怎麼避免踩到這個坑。

## 重點整理

- `AsyncRead` / `AsyncWrite` 是 `async` 版的 byte I/O；底層 `read` / `write` 只嘗試推進一次、回傳本次處理的 byte 數，不保證讀滿或寫完
- `AsyncReadExt` / `AsyncWriteExt` 提供 `read_exact`、`write_all` 等 helper，幫你包好「讀滿 / 寫完」的迴圈
- **取消**：`Future` 是惰性的，`drop` 掉一個 `Future`（不再 `poll`）就等於取消這個 `async` 工作——這是 `async` 特有、`Thread` 做不到的
- `read_exact` 這類「跨多次推進、累積中間狀態」的操作**不是 cancellation safe**：中途被取消會遺失已讀資料，不該放進會被中途 `drop` 的地方
