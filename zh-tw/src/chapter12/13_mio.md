# `mio`：Poll、Waker 與 Token

## 本集目標

認識 `mio`——下一集要拿來打造 async runtime 的 I/O 基礎工具。重點有三樣：

- `Poll`：睡著等事件。
- `Waker`：從別處把睡著的 `Poll` 叫醒。
- `Token`：等真正登記 I/O 來源時，用來辨識「是哪一個來源好了」。

這一集先用 `mio::Waker` 做一個最小範例：另一條 thread 叫醒睡在 `Poll` 上的主 thread。`Token` 先建立概念，真正拿來分辨 socket 事件會放到第 14 集 reactor。

## 概念說明

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

// 睡著，直到某個登記過的來源有事件，或被 Waker 叫醒
poll.poll(&mut events, None).unwrap();

for event in events.iter() {
    // 處理這次收到的事件
}
```

`poll.poll(&mut events, timeout)` 會把目前這條執行緒**睡著**，直到：

- 某個登記過的 I/O 來源有動靜
- 被 `mio::Waker` 叫醒
- timeout 到期

醒來後，`events` 裡裝著「這次有哪些事件」。

### `mio::Waker`：把睡著的 `Poll` 叫醒

第 11、12 集已經用 `park/unpark` 叫醒 executor。`mio::Waker` 這次不是拿來叫醒 executor，而是拿來叫醒**睡在 `mio::Poll` 上的 reactor thread**。

為什麼 reactor 也需要門鈴？因為 reactor thread 可能正在 `poll.poll()` 裡睡覺，但 executor thread 可能突然送來新指令，例如「幫我註冊這個 socket」或「幫這個 token 更新 Waker」。這時候就要用 `mio::Waker` 把 `Poll` 叫醒，讓 reactor 處理指令。

`mio::Waker` 建立時要綁一個 `Token`：

```rust,ignore
use mio::{Poll, Token, Waker};

let poll = Poll::new().unwrap();
let waker = Waker::new(poll.registry(), Token(0)).unwrap();
```

這個 token 只代表「這個 `mio::Waker` 被觸發了」。第 14 集會把它當成 reactor 的**指令門鈴**：token 不代表 socket ready，只代表「reactor 該醒來看一下 channel 裡有沒有新指令」。

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

所以請先記住分工：

```text
mio::Waker 的 token：
    代表「reactor 的指令門鈴響了」

I/O source 的 token：
    代表「是哪個 socket / listener ready」
```

## 範例程式碼

這個範例只有一個目的：主 thread 睡在 `poll.poll()` 上，另一條 thread 0.2 秒後呼叫 `mio::Waker::wake()`，把它叫醒。

```rust,ignore
use std::thread;
use std::time::Duration;
use mio::{Events, Poll, Token, Waker};

fn main() {
    let mut poll = Poll::new().unwrap();
    let waker = Waker::new(poll.registry(), Token(0)).unwrap();

    thread::spawn(move || {
        thread::sleep(Duration::from_millis(200));
        waker.wake().unwrap();
    });

    let mut events = Events::with_capacity(8);
    poll.poll(&mut events, None).unwrap();

    for event in events.iter() {
        println!("收到 event token = {:?}", event.token());
    }
}
```

跑起來會在約 0.2 秒後印出：

```text
收到 event token = Token(0)
```

重點是：`mio::Waker` 讓別的地方可以把睡著的 `Poll` 叫醒。第 14 集會用它叫醒 reactor thread，讓 reactor 處理 channel 指令；至於「哪個 I/O 來源好了」，第 14 集也會用 I/O token 來回答。

## 重點整理

- `mio` 把作業系統的事件等待能力包成跨平台介面，讓一條執行緒能同時盯住很多 I/O 來源
- `mio::Poll` 是「睡著等事件」的地方：`poll.poll(&mut events, timeout)` 睡到有事才醒
- `mio::Waker` 可以從別處叫醒睡在 `Poll` 上的 reactor thread
- `Token` 是事件來源的名牌；第 14 集會用它分辨 reactor 指令門鈴、socket、listener
- task 身份不放在 `Token` 裡；第 11 集已經用 ready queue 表示哪些 task 要被 poll
