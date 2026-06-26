# `mio`

## 本集目標

認識 `mio`——讓「一條 thread 盯住一大堆 I/O 來源」成為可能的工具，它是下一集 reactor 的基礎。

## 正文

### reactor 在 runtime 裡的角色

先把我們手寫 runtime 的全貌再講一次。一個 runtime 其實有兩個各司其職的角色：

- **executor**：從 ready queue 拿 `Task` 出來 poll，也就是「跑 `Task`」。它對外部世界一無所知——它不知道網路封包到了沒、檔案讀好了沒。
- **reactor**：負責盯住所有的 I/O 來源，哪個 ready 了就 `wake` 對應的 `Task`，也就是「等事件」。它**不** poll `Future`、它不是 `Task`，它只盯著外部事件來源。

前幾集我們的「等待」是靠替每個 `Delay` 開一條 thread，這太浪費了。reactor 的任務，就是用**一條** thread 盯住**很多** I/O 來源。要做到這件事，靠的就是這一集的主角：`mio`。

### `mio` 的兩個主角

`mio` 是 Rust 生態裡負責跨平台 I/O 事件通知的底層套件（Tokio 內部也是用它）。先用前要安裝：

```toml
[dependencies]
mio = { version = "1", features = ["os-poll", "net"] }
```

我們這集只要認識它的兩個東西：

- **`mio::Poll`**：一個可以「睡著等 I/O 事件」的地方。一條 thread 把很多 I/O 來源登記給它之後，就能用一次 `poll.poll(...)` 同時盯住全部，哪個有動靜就醒來。
- **`Token`**：事件來源的「名牌」。登記某個 I/O 來源時，你給它一個 `Token`；之後 `Poll` 通知你「有事件」時，會把當初的 `Token` 還給你，你就知道是哪個來源在叫。

### 看 `mio` 怎麼盯住一個 `TcpListener`

下面這個例子把一個 `TcpListener`（負責接受連線的東西）登記給 `Poll`，然後另開一條 thread 過一秒去連它。主 thread 就睡在 `poll.poll()` 上，等到連線進來才醒：

```rust,no_run
# extern crate mio;
#
use mio::net::TcpListener;
use mio::{Events, Interest, Poll, Token};
use std::time::Duration;

// 給 listener 的名牌
const SERVER: Token = Token(0);

fn main() {
    let mut poll = Poll::new().expect("建立 Poll 失敗");
    let mut events = Events::with_capacity(128); // 一次最多收 128 個事件

    let addr = "127.0.0.1:8080".parse().expect("位址解析失敗");
    let mut listener = TcpListener::bind(addr).expect("綁定失敗");

    // 把 listener 登記給 Poll：名牌是 SERVER，我們關心「可讀」事件（有人連進來就算可讀）
    poll.registry()
        .register(&mut listener, SERVER, Interest::READABLE)
        .expect("登記失敗");

    // 另一條 thread 過一秒後連進來
    std::thread::spawn(|| {
        std::thread::sleep(Duration::from_secs(1));
        let _ = std::net::TcpStream::connect("127.0.0.1:8080");
    });

    println!("睡在 poll 上，等 I/O 事件……");
    loop {
        // poll 會睡在這裡，直到有登記過的來源發生事件
        poll.poll(&mut events, None).expect("poll 失敗");

        for event in events.iter() {
            match event.token() {
                SERVER => {
                    // 名牌對上了，表示 listener 可讀，可以 accept 出新連線
                    let (_stream, addr) = listener.accept().expect("accept 失敗");
                    println!("有人連進來了：{addr}");
                    return; // 範例就收工
                }
                _ => {}
            }
        }
    }
}
```

### 把流程看一遍

1. `Poll::new()` 做出一個 `Poll`。
2. `registry().register(&mut listener, SERVER, Interest::READABLE)` 把 `listener` 登記進去，給它名牌 `SERVER`，並說明我們關心的是「可讀」（`Interest::READABLE`）。如果是要等「可寫」，就用 `Interest::WRITABLE`。
3. `poll.poll(&mut events, None)` 讓這條 thread **睡著**，直到有登記過的來源發生事件（`None` 代表不設逾時、睡到有事為止）。
4. 醒來後，逐一檢查 `events`。`event.token()` 還給我們當初登記的名牌；對上 `SERVER`，就知道是 `listener` 有動靜，於是 `accept()` 把新連線收下來。

關鍵在於：就算你登記了**一百個** I/O 來源，也只要**一條** thread 睡在同一個 `poll.poll()` 上。哪個來源有事，`Poll` 就把對應的名牌交給你。這正是 reactor 用少少幾條 thread 盯住大量 I/O 的祕密武器。

下一集，我們就把 `mio` 接到前面手寫的 executor 上，做出真正的 reactor，讓我們的 runtime 第一次能處理真實的網路 I/O。

## 重點整理

- runtime 有兩個角色：**executor** 跑 `Task`（poll），**reactor** 等事件（盯 I/O、`wake` 對應 `Task`）；reactor 不是 `Task`、不 poll `Future`
- `mio::Poll` 是「睡著等 I/O 事件」的地方，一條 thread 就能同時盯住很多 I/O 來源
- `Token` 是事件來源的名牌：登記時給，事件發生時 `Poll` 還給你，讓你認出是哪個來源
- 用 `registry().register(&mut source, token, Interest::READABLE)` 登記，`poll.poll()` 睡著等事件，`event.token()` 認名牌後再 `accept` / `read`
