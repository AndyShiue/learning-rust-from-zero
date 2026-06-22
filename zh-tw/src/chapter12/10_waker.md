# 用 `Thread` 與 `Waker` 喚醒 executor

## 本集目標

補上一直跳過的 `Waker`：讓 future 在「之後好了」的時候主動叫醒 executor，executor 就能安心睡覺、不再空轉燒 CPU。

## 概念說明

### 問題回顧

到目前為止，我們的 executor 笨在「遇到 `Pending` 就猛 poll」。它不知道 future 什麼時候會好，只好一直問。

理想的流程應該是：future 回 `Pending` 之前，先留一張「叫醒卡」給 executor，說「等我好了我會通知你，你先去睡」。executor 拿到卡就**睡著**；等 future 真的好了，它**用那張卡把 executor 叫醒**，executor 醒來再 poll 一次，這次就 `Ready` 了。

那張「叫醒卡」就是 `poll` 簽名裡那個我們一直跳過的 **Waker**。它一直都在 `Context` 裡（`cx.waker()`），只是前面沒用。

### 親手做一個 Waker

Waker 不是黑魔法，我們可以自己做一個。做法是實作標準庫的 `std::task::Wake` trait——它只要求你回答一個問題：「被 wake 的時候，要做什麼？」

我們的 executor 打算用「睡著／叫醒」來省 CPU。標準庫剛好有現成的：`thread::park()` 讓目前這條執行緒睡著，`thread.unpark()` 把它叫醒。所以我們的 Waker 被 wake 時，就去 unpark executor 那條執行緒：

```rust,ignore
use std::sync::Arc;
use std::task::Wake;
use std::thread::Thread;

struct ThreadWaker(Thread); // 記住要叫醒哪條執行緒

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.0.unpark(); // 被通知時，把那條執行緒叫醒
    }
}
```

實作了 `Wake` 之後，標準庫就能幫我們把 `Arc<ThreadWaker>` 轉成一個真正的 `Waker`——用 `.into()` 或 `Waker::from(...)` 即可。

### 讓 executor 睡覺

有了會 unpark 的 Waker，executor 就能改成「`Pending` 就睡，被叫醒再 poll」：

```rust,ignore
use std::future::Future;
use std::sync::Arc;
use std::task::{Context, Poll, Waker};
use std::thread;

fn run<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);

    // 用「叫醒目前這條執行緒」做出 Waker
    let waker: Waker = Arc::new(ThreadWaker(thread::current())).into();
    let mut cx = Context::from_waker(&waker);

    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(), // 睡著，直到有人 unpark 我
        }
    }
}
```

對比第 6 集：唯一的差別是 `Pending` 那行從「什麼都不做、繼續 loop」變成 `thread::park()`（睡著）。executor 睡著後，CPU 就空下來了，不再空轉。

### `unpark` 可以發生在 `park` 之前

這裡藏著一個容易忽略、卻很關鍵的安全性。看 `poll` 回 `Pending` 到 `thread::park()` 之間，其實有個**空檔**：萬一就在這個空檔，`Delay` 的計時 thread 已經 `wake()` →`unpark()` 了呢？executor 不就變成「先被叫醒、然後才去睡」，結果一睡不醒、永遠卡住嗎？

幸好 `park` / `unpark` 不會這樣。`unpark` 會給目標 thread 留一張 **permit（許可）**：如果 `unpark()` 發生在 `park()` **之前**，那張 permit 會被記住，下一次 `park()` 看到 permit 就**立刻返回**、根本不會真的睡。所以不管 wake 落在 `park` 之前還是之後，executor 都不會漏接：

```text
poll 回 Pending
    ⋯ 空檔：這裡若先 unpark()，會留下一張 permit ⋯
thread::park()   // 有 permit 就立刻返回；沒有才真的睡
```

（這也是為什麼我們直接用 `park` / `unpark`，而不必自己用旗標加條件變數從頭刻——標準庫已經幫我們處理掉「喚醒比睡覺早到」這個 race。後面第 11 集把它換成 ready queue 版，以及第 14 集的 reactor，靠的都是同一個 permit 特性。）

### 讓 Delay 負起通知的責任

最後，把第 7 集的 `Delay` 補完整。它回 `Pending` 之前，要安排「時間到的時候 wake」。最直接的做法：另外開一條執行緒去睡到到期，醒來就呼叫 wake。

```rust,ignore
# use std::future::Future;
# use std::pin::Pin;
# use std::task::{Context, Poll};
# use std::time::Instant;
# use std::thread;
struct Delay {
    when: Instant,
    started: bool, // 是否已經派出計時執行緒
}

impl Future for Delay {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            return Poll::Ready(());
        }
        if !self.started {
            self.started = true;
            let waker = cx.waker().clone(); // 把 executor 給的 Waker 複製一份帶走
            let when = self.when;
            thread::spawn(move || {
                let now = Instant::now();
                if now < when {
                    thread::sleep(when - now); // 睡到到期
                }
                waker.wake(); // 時間到，叫醒 executor
            });
        }
        Poll::Pending
    }
}
```

`started` 這個旗標很重要：`poll` 可能被呼叫很多次，但「派一條計時執行緒」這件事只能做**一次**。所以第一次 poll 時設 `started = true` 並 spawn 計時 thread，之後再被 poll 就跳過，不會重複生 thread。

（這裡能直接改 `self.started`，是因為 `Delay` 的欄位都能安全搬動，所以它是 `Unpin`——這個詞第 18 集會解釋，現在先放著。）

現在整條鏈完整了：executor poll `Delay` → 還沒到期 → `Delay` 派一條計時執行緒、留下 Waker、回 `Pending` → executor `park` 睡著 → 時間到，計時執行緒 `wake` → executor 被 unpark 叫醒 → 再 poll 一次 → 這次到期了，`Ready`。全程不再空轉。

### `poll`／`Waker` 的兩條契約

趁這條鏈剛兜好，把標準庫對 `poll` 的兩條**契約**講清楚——之後自己手寫 future 時很容易踩到。

**1. 每次 poll 只有「最新的」Waker 算數。** 注意 `Delay` 是在**第一次** poll 時存一次 `cx.waker().clone()`（被 `started` 擋著）。但契約其實是：**每次 poll 拿到的 `cx.waker()` 可能不一樣**（同一顆 future 可能被搬到不同的 task／executor），所以你要喚醒的，永遠是**最近一次 poll 給你的那個 Waker**。嚴謹的 future 會在**每次 poll 都重新存一份** `cx.waker()`、覆蓋掉舊的。我們的 `Delay` 能偷懶只存一次，是因為這台 executor 從頭到尾 Waker 都不變；第 12 集的 `JoinHandle` 和第 14 集的 reactor 就會老實地「每次 poll 重存」，正好印證這條。

**2. 回了 `Ready` 之後，就不該再被 poll。** 看 `run`：它一拿到 `Ready` 就 `return`、收手。這也是契約——**一個 future 完成後再被 poll 是未定義的**（標準庫文件明說可能 panic、卡死或出其他問題）。所以 executor 要自己記得「這顆已經做完了」，別再去碰它（第 11 集起我們用計數、把做完的 task 從 queue 拿掉，就是在守這條）。

（這兩條的權威出處，就是標準庫 `std::future::Future::poll` 的文件。）

### 但「每件事開一條 thread」顯然不是好辦法

先別高興太早。我們的 `Delay` 為了計時，**另外開了一條執行緒**去睡。一個 `Delay` 開一條還好，但回想第 2 集講過的事：**執行緒很吃記憶體**——每條都要分一塊不小的 stack，作業系統還要花力氣在它們之間切換。

如果照這個做法，**每一個在等待的 future 都配一條執行緒去等**，那一台同時等一萬個連線的伺服器，就會開出一萬條執行緒——這**正是第 2 集說 async 要避免的那個問題**！我們繞一大圈用 async，結果在底層又掉回「一個等待綁一條執行緒」的老路，那就白忙一場了。

所以「開 thread 來等」只是這一集為了**先把喚醒模型跑通**而用的權宜手段。真正重要、會留下來的，是那套機制本身：**future 回 `Pending` 時留下 Waker，事件源頭好了就 `wake`**——至於事件源是計時器、是網路封包到了、還是別的，都套用同一套。

接下來的安排是：先把「被 wake 的 future 要怎麼回到 executor」做成 **ready queue**（第 11 集），再把「怎麼用少少幾條執行緒盯住很多 I/O」交給 **reactor**（第 14 集）。

## 範例程式碼

把上面的 `ThreadWaker`、`run`、`Delay` 拼起來：

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::thread::Thread;
use std::time::{Duration, Instant};

struct ThreadWaker(Thread);
impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.0.unpark();
    }
}

fn run<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let waker: Waker = Arc::new(ThreadWaker(thread::current())).into();
    let mut cx = Context::from_waker(&waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(),
        }
    }
}

struct Delay {
    when: Instant,
    started: bool,
}
impl Future for Delay {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            return Poll::Ready(());
        }
        if !self.started {
            self.started = true;
            let waker = cx.waker().clone();
            let when = self.when;
            thread::spawn(move || {
                let now = Instant::now();
                if now < when {
                    thread::sleep(when - now);
                }
                waker.wake();
            });
        }
        Poll::Pending
    }
}

fn main() {
    println!("開始等 2 秒（這次 executor 是睡著等，不燒 CPU）");
    run(async {
        Delay {
            when: Instant::now() + Duration::from_secs(2),
            started: false,
        }
        .await;
        println!("時間到！");
    });
}
```

行為和第 7 集一樣會等 2 秒，但這次 executor 是真的睡著，不再瘋狂 poll。

## 重點整理

- `Waker` 是 future 留給 executor 的「叫醒卡」，一直放在 `Context` 裡（`cx.waker()`）
- 自己做 Waker：實作 `std::task::Wake` trait（回答「被 wake 時做什麼」），再把 `Arc<W>` 用 `.into()` 轉成 `Waker`
- 喚醒模型讓 executor 可以「`Pending` 就睡（`thread::park`）、被 `wake`（`unpark`）才醒來再 poll」，不再空轉燒 CPU
- `unpark` 可以發生在 `park` 之前：它會留下一張 permit，下一次 `park()` 立刻返回——所以就算 wake 落在「`poll` 回 `Pending`」到「`park()`」的空檔，也不會漏接（不會睡死）
- future（如 `Delay`）回 `Pending` 前要負責安排：事件好了的時候呼叫 `cx.waker().clone()` 拿到的 Waker 的 `wake()`；用 `started` 旗標確保「派計時 thread」只做一次
- `poll` 契約一：**只有最近一次 poll 給的 Waker 算數**——`cx.waker()` 每次 poll 可能不同，嚴謹的 future 每次 poll 都重存一份（`Delay` 因 waker 不變才偷懶存一次；第 12、14 集會每次重存）
- `poll` 契約二：**`Ready` 後不可再 poll**（未定義行為，可能 panic／卡死）——executor 要記得把做完的 future 收手別再碰（第 11 集起用計數＋移出 queue 守這條）。兩條的出處是 `std::future::Future::poll` 文件
- 用 thread 計時只是這次的手段；真正通用的是「`Pending` 留 Waker、事件源 `wake`」這套機制
- 但「每個等待的 future 開一條 thread」顯然不理想——thread 很吃記憶體（第 2 集），一萬個連線就一萬條，正是 async 想避免的；接下來用 ready queue（第 11 集）與 reactor（第 14 集）解決
