# `AsyncRead` 與 `AsyncWrite`

## 本集目標

認識 async 版的位元組讀寫 trait,理解 `read`／`write` 「只承諾推進一次」的本質,以及方便的 helper 與它們的取消風險。

## 概念說明

### 同步 I/O 的 async 版

第 11 章學過同步的 `Read`／`Write` trait——從檔案、網路連線讀寫位元組。async 世界有對應的 `AsyncRead`／`AsyncWrite`(tokio 提供),概念一樣,只是讀寫的時候若資料還沒到、或還寫不出去,它不會卡住執行緒,而是 `.await`(讓出去做別的)。

```rust,ignore
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

async fn talk(mut stream: TcpStream) -> std::io::Result<()> {
    stream.write_all(b"hello").await?; // 把 hello 全部寫出去
    let mut buf = [0u8; 1024];
    let n = stream.read(&mut buf).await?; // 讀一些資料進 buf
    println!("讀到 {} 個 byte", n);
    Ok(())
}
```

### 關鍵觀念:`read`／`write` 只「嘗試一次」

這是最容易誤會、也最重要的一點。`read(&mut buf).await` **不保證**把你的 buffer 填滿,`write(buf).await` 也**不保證**把你的資料全部寫出去。它們只承諾:

> 「我嘗試推進**一次**,然後告訴你這次實際處理了幾個 byte。」

`read` 回傳這次讀進了幾個 byte(可能比 buffer 小很多;回傳 `0` 通常代表對方關閉連線了)。`write` 回傳這次寫出了幾個 byte(可能只寫了一部分)。這是因為底層的網路、管線一次能搬多少資料是不一定的。

所以如果你要「讀剛好 N 個 byte」或「把這段資料全部寫完」,自己用 `read`／`write` 就得寫一個迴圈,反覆呼叫直到湊足數量。這很常見,於是有了 helper。

### `AsyncReadExt`／`AsyncWriteExt`:好用的 helper

tokio 在 `AsyncReadExt` / `AsyncWriteExt` 這兩個擴充 trait 裡,提供了一堆「幫你把迴圈寫好」的方法(用之前 `use` 進來就行):

- `read_exact(&mut buf)`:**讀滿**整個 buffer 才回來(內部幫你迴圈)。
- `write_all(buf)`:把 buffer **全部寫完**才回來。
- `read_to_end(&mut vec)`:一路讀到對方關閉,全部塞進一個 `Vec`。
- `read_to_string(&mut s)`:同上,但讀成 `String`。

上面範例用的 `write_all` 就是其中之一——它保證 `hello` 五個 byte 全部寫出去,你不用自己數。

### helper 的便利,與取消風險

這些 helper 很方便,但要小心它們和上一集 `select!`「取消」的互動。像 `read_exact` 這種會「內部跑迴圈、分好幾次推進」的操作,**不是取消安全的**。

想想看:`read_exact` 要讀 100 個 byte,它可能已經讀進了 60 個、暫存在內部,正等剩下的 40 個。如果這時候它所在的 `select!` 分支沒搶贏、整個 `read_exact` future 被 drop(取消)了,那已經讀進來的 60 個 byte 就**跟著消失了**——它們從連線上被讀走了,卻沒交到你手上,等於遺失。

所以原則是:**別把 `read_exact`、`write_all` 這類「跨多次推進、會累積中間狀態」的 helper,放進會反覆被取消的 `select!` 分支裡。** 如果真的需要「邊讀邊可被取消」,要用取消安全的做法(例如先 `read` 單次、自己管 buffer)。各方法的文件會註明它是否 cancellation safe。

### 和前面 runtime 模型的連結

別忘了這些 async I/O 背後就是前面幾集那套東西:`read().await` 在資料還沒到時回 `Pending`,並把 Waker 登記給 reactor(第 14 集);網路封包到了,reactor `wake` 你的 task,`read` 才繼續、回傳這次讀到的 byte 數。`buffer` 的所有權、一次讀多少、partial read/write,全都是建立在這個 poll／wake 模型上的。

## 範例程式碼

一個極簡的 TCP echo 邏輯:把對方傳來的東西原封不動寫回去。

```rust,ignore
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    println!("在 8080 等連線");

    loop {
        let (mut socket, _) = listener.accept().await?; // 等一個連線進來
        // 每個連線開一個 task 去服務,主迴圈馬上回去等下一個連線
        tokio::spawn(async move {
            let mut buf = [0u8; 1024];
            loop {
                let n = match socket.read(&mut buf).await {
                    Ok(0) => return,         // 0 = 對方關閉連線
                    Ok(n) => n,              // 這次讀到 n 個 byte
                    Err(_) => return,
                };
                // 把這 n 個 byte 原封不動寫回去
                if socket.write_all(&buf[..n]).await.is_err() {
                    return;
                }
            }
        });
    }
}
```

注意 `read` 回傳的 `n` 怎麼用:我們只把「這次真的讀到的」`&buf[..n]` 寫回去,而不是整個 `buf`。這正是「`read` 只讀到一些、要看回傳值」的實際應用。

## 重點整理

- `AsyncRead`／`AsyncWrite`(tokio)是同步 `Read`／`Write` 的 async 版:資料沒好時 `.await` 讓出執行緒,不卡死
- **`read`／`write` 只嘗試推進一次**,回傳這次實際處理的 byte 數;`read` 回 `0` 通常代表對方關閉
- `AsyncReadExt`／`AsyncWriteExt` 提供 helper:`read_exact`、`write_all`、`read_to_end`、`read_to_string`(內部幫你迴圈)
- 這些「跨多次推進」的 helper **不是取消安全的**:被 `select!` 中途丟掉,已讀進的資料會遺失——別放進會反覆取消的分支
- 背後仍是前面的 poll／wake／reactor 模型;用 `read` 時記得只處理 `&buf[..n]`
