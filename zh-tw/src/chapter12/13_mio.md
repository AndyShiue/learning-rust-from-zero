# `mio`

## 本集目標

認識 `mio`——下一集要拿來打造 **reactor** 的 I/O 基礎工具。重點有兩樣：

- `Poll`：睡著等 I/O 事件的地方。
- `Token`：登記 I/O 來源時貼的「名牌」，用來辨識「是哪一個來源好了」。

這一集用一個最小範例把它們串起來：登記一個真正的 TCP listener，讓 `Poll` 被**真實的連線事件**叫醒——這是 mio 跟 I/O 的關係第一次具體出現。把 socket readiness 完整接進 reactor、用 `Token` 對應回 waker，則留到第 14 集。

## 概念說明

### 先講 reactor 是什麼

`mio` 是拿來打造 **reactor** 的工具,所以先把 reactor 的角色講清楚,後面才知道 mio 為什麼重要。

到目前為止我們做出的是 **executor**:它從 ready queue 拿 task 出來 poll,queue 空了就睡。但 executor 只管「跑 task」,它**不知道外面的世界發生了什麼**——哪個 socket 的資料到了、哪個連線可以讀了,executor 一概不曉得。

少了的那一塊,就是負責「盯住外部 I/O 事件」的角色。在第 7 到 10 集,每個 `Delay` 都自己開一條 thread 去等,等到了再 wake;但這種做法沒辦法擴張到成千上萬個連線。

**reactor 就是專門接手這件事的那一塊:它盯住所有 I/O 來源,哪個 ready 了就去 wake 對應的 task,把它排回 ready queue。** reactor 不 poll future、不跑業務邏輯,本身也不是一個 task;它只是個外部事件來源——負責「等事件,然後喚醒在等那個事件的人」。

於是一個 runtime 就拆成分工明確的兩半:

```text
executor:從 ready queue 拿 task 出來 poll   → 「跑 task」
reactor :盯住所有 I/O 來源,ready 就 wake 對應 task → 「等事件」
```

剩下的問題是:reactor 要怎麼用一條 thread 同時盯住那麼多 I/O 來源?這正是 `mio` 要解決的事。

### 為什麼需要 mio

前面幾集的 `Delay` 還是用一條 thread 來等計時完成。這很適合教 Waker，但真實伺服器不能為每個連線都開一條 thread：一台等一萬個連線的伺服器，不可能開一萬條 thread。

我們需要的是「**用一條執行緒，同時盯著成千上萬件事**，哪個好了就通知哪個 task」。

這種能力作業系統本來就有（Linux 的 `epoll`、macOS 的 `kqueue`、Windows 的 IOCP 等），`mio` 這個 crate 把它們包成一個好用、跨平台的介面。先在 `Cargo.toml` 加上：

```toml
[dependencies]
mio = { version = "1", features = ["os-poll", "net"] }
```

### `mio::Poll`：一個「睡著等事件」的地方

`mio` 的核心是 `Poll`。你可以把它想成一個**睡覺、等事件的地方**：

```rust,ignore
use mio::{Events, Poll};

let mut poll = Poll::new().unwrap();
let mut events = Events::with_capacity(64);

// 睡著，直到某個登記過的來源有事件（或 timeout）
poll.poll(&mut events, None).unwrap();

for event in events.iter() {
    // 處理這次收到的事件
}
```

`poll.poll(&mut events, timeout)` 會把目前這條執行緒**睡著**，直到：

- 某個登記過的 I/O 來源有動靜
- timeout 到期

醒來後，`events` 裡裝著「這次有哪些事件」。

### `Token`：幫事件來源貼一張名牌

`Token` 是一個小編號，用來讓 `Poll` 醒來時告訴你：「是哪個事件來源好了」。

第 14 集 reactor 會把 `TcpListener`、`TcpStream` 這些 I/O 來源登記給 `Poll`，每個來源各自拿一個 token。

到時候流程會像這樣：

```text
socket readable
    -> mio::Poll 醒來
    -> event.token() 告訴 reactor 是哪個 socket
    -> reactor 找到正在等這個 socket 的 Waker
    -> waker.wake()
    -> 對應 task 回到 ready queue
```

### 把真正的 I/O 來源登記給 `Poll`

前面都在講概念,現在直接登記一個**真正的 I/O 來源**,看 `Poll` 被真實事件叫醒。最簡單的來源是一個 TCP listener(等別人連進來的伺服器 socket):

```rust,ignore
use mio::net::TcpListener;
use mio::{Interest, Poll, Token};

let mut poll = Poll::new().unwrap();
let mut listener = TcpListener::bind("127.0.0.1:9000".parse().unwrap()).unwrap();

// 把 listener 登記給 poll，關心它「可讀」——有新連線進來時它就會變可讀
poll.registry()
    .register(&mut listener, Token(0), Interest::READABLE)
    .unwrap();
```

`register` 有三個重點:

- 要登記的 I/O 來源(`&mut listener`);
- 給它一個 `Token`(這裡 `Token(0)`),醒來時靠它認出是誰;
- `Interest`:你關心哪一種 readiness。`READABLE` = 可讀(有資料可收、或有連線可 `accept`),`WRITABLE` = 可寫。

登記之後,`poll.poll()` 就會睡著,直到**真的有人連進來**——這時 listener 變可讀,`poll` 醒來,`event.token()` 是 `Token(0)`,你就能去 `accept()` 那條連線。這就是 mio 跟 I/O 的關係:**你把 socket 交給它盯著,它替你睡著等,真有事件才叫醒你。** 第 14 集 reactor 做的事,核心就是把這一步擴大到很多 socket、並在醒來後拿 token 去 wake 對應的 task。

## 範例程式碼

主 thread 登記一個 TCP listener、睡在 `poll.poll()` 上;另一條 thread 過 0.2 秒連進來,製造一個**真實的連線事件**,把 `Poll` 叫醒。(用另一條 thread 當「客戶端」只是為了讓範例自己跑得起來;真實情況是外面的程式連進來。)

```rust,ignore
use std::io::Write;
use std::net::TcpStream; // 標準庫的 client，純粹拿來「製造一個連線」
use std::thread;
use std::time::Duration;

use mio::net::TcpListener;
use mio::{Events, Interest, Poll, Token};

const SERVER: Token = Token(0);

fn main() {
    let mut poll = Poll::new().unwrap();
    let mut events = Events::with_capacity(8);

    // 真正的 I/O 來源：一個 TCP listener，登記給 poll、關心「可讀」
    let mut listener = TcpListener::bind("127.0.0.1:9000".parse().unwrap()).unwrap();
    poll.registry()
        .register(&mut listener, SERVER, Interest::READABLE)
        .unwrap();

    // 另一條 thread 過 0.2 秒連進來，製造一個真正的連線事件
    thread::spawn(|| {
        thread::sleep(Duration::from_millis(200));
        let mut client = TcpStream::connect("127.0.0.1:9000").unwrap();
        let _ = client.write_all(b"hi");
    });

    println!("等待連線...");
    poll.poll(&mut events, None).unwrap(); // 睡著，直到 listener 可讀

    for event in events.iter() {
        if event.token() == SERVER {
            let (_stream, peer) = listener.accept().unwrap();
            println!("有人連進來了：{} (token = {:?})", peer, event.token());
        }
    }
}
```

跑起來約 0.2 秒後印出（埠號每次不同）：

```text
等待連線...
有人連進來了：127.0.0.1:56808 (token = Token(0))
```

叫醒 `Poll` 的是**作業系統回報的真實 I/O readiness**——有人連上了 9000 埠。`event.token()` 回報 `Token(0)`,正好對上我們登記 listener 時給的名牌。

reactor 要做的事,核心就是這個範例的放大版:把很多 socket 都登記給一個 `Poll`、睡在 `poll.poll()` 上,醒來後用 `event.token()` 認出是哪個來源好了,再去 wake 對應的 task。這條完整的線會在第 14 集接起來。

## 重點整理

- `mio` 把作業系統的事件等待能力包成跨平台介面，讓一條執行緒能同時盯住很多 I/O 來源
- `mio::Poll` 是「睡著等事件」的地方：`poll.poll(&mut events, timeout)` 睡到有事才醒
- 把真正的 I/O 來源(如 `TcpListener`)用 `registry().register(&mut src, token, Interest::READABLE)` 登記給 `Poll`，`poll` 就會被**真實的 I/O readiness**(例如有人連進來)叫醒，`event.token()` 告訴你是哪個來源
- `Token` 是事件來源的名牌；第 14 集 reactor 會用它分辨是哪個 I/O 來源(socket / listener)好了
- task 身份不放在 `Token` 裡；第 11 集已經用 ready queue 表示哪些 task 要被 poll
