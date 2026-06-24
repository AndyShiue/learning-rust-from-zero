# `AsyncRead` 與 `AsyncWrite`

## 本集目標

認識 async 版的位元組讀寫 trait,理解 `read`／`write` 「只承諾推進一次」的本質,以及方便的 helper;並藉著這些 helper,**第一次帶到「取消(cancellation)」** 這個 async 特有的概念。

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

### 帶出一個新概念:取消(cancellation)

這些 helper 很方便,但會牽出一個 async 特有的概念——**取消(cancellation)**。我們在這裡第一次遇到它。

先講什麼是取消。future 是惰性的,靠別人 poll 才前進;所以你只要**不再 poll 它、把它 drop 掉**,它的工作就停在原地、永遠不會完成——這就是「取消」一個 async 工作。這跟執行緒很不一樣:第 8 章那種 thread 一旦跑起來,你沒有乾淨的辦法從外面把它喊停;但 async 工作只要丟掉它的 future 就停了。(下一集的 `select!` 會大量用到這個特性——沒搶贏的分支會被自動丟掉、取消。)

麻煩在於:像 `read_exact` 這種「內部跑迴圈、分好幾次推進」的操作,被取消在半途**不安全**。想想看:`read_exact` 要讀 100 個 byte,可能已經讀進 60 個、暫存在內部,正等剩下的 40 個。如果這時整個 `read_exact` future 被 drop(取消),那已經讀進的 60 個 byte 就**跟著消失**——它們從連線上被讀走了、卻沒交到你手上,等於遺失。

一個操作「就算被中途取消,也不會搞壞或遺失東西」的性質,叫 **cancellation safety(取消安全)**。`read_exact`、`write_all` 這類會累積中間狀態的,**不是**取消安全的。所以原則是:**別把它們放進「會中途把它丟掉」的地方**(最常見的就是下一集 `select!` 的分支)。如果需要「邊讀邊可被取消」,改用取消安全的做法(例如先 `read` 單次、自己管 buffer)。各方法的文件會註明它是否 cancellation safe。

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
- **取消(cancellation)**:把一個 future drop 掉(不再 poll)就等於取消這個 async 工作——這是 async 特有、執行緒做不到的乾淨喊停;這一集第一次遇到它(下一集 `select!` 會大量用到)
- 這些「跨多次推進」的 helper **不是取消安全的**:被中途丟掉(典型是 `select!` 分支)時已讀進的資料會遺失——別放進會反覆取消的地方
- 背後仍是前面的 poll／wake／reactor 模型;用 `read` 時記得只處理 `&buf[..n]`
