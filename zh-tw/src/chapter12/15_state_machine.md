# `async fn` 背後的狀態機

## 本集目標

揭開 `async fn` 的真面目：它被編譯器改寫成一個能暫停、能恢復的**狀態機**。

## 正文

### `.await` 不是開新 thread

先破除一個常見的誤會。當你看到 `.await`，可能會以為它「在背後偷偷開了一條 thread 去等」。**完全不是。** 從第 6 集到現在，我們手寫的這套 runtime 從頭到尾就是一條 executor thread 在反覆 poll，`.await` 沒有變出任何新 thread。

那 `.await` 到底做了什麼？它把你的函數**切成好幾段**——每個 `.await` 是一個切點。函數可以在切點暫停、把控制權交還給 executor，之後再從同一個切點恢復。能做到這件事的東西，就叫**狀態機**。

### 一個 `async fn` 會被改寫成什麼

假設有這麼一個 `async fn`，裡面等兩次：

```rust,ignore
async fn two_delays() {
    Delay::new(Duration::from_secs(1)).await;
    println!("一秒到");
    Delay::new(Duration::from_secs(1)).await;
    println!("兩秒到");
}
```

編譯器看到它，會在心裡把它改寫成一個 `enum`——每個「狀態」代表「目前卡在哪一段」：

- `Start`：還沒開始。
- `FirstDelay`：正在等第一個 `Delay`（這個還沒完成的 `Delay` 本身也得存進來）。
- `SecondDelay`：正在等第二個 `Delay`。
- `Done`：跑完了。

然後它替這個 `enum` 實作 `Future`，`poll` 裡用 `match` 看現在在哪個狀態、該做什麼。我們把這個改寫**手動**寫出來，你就會看到 `async fn` 背後長什麼樣：

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::time::{Duration, Instant};

struct Delay { when: Instant, started: bool }
impl Delay {
    fn new(d: Duration) -> Delay { Delay { when: Instant::now() + d, started: false } }
}
impl Future for Delay {
    type Output = ();
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        if Instant::now() >= this.when { Poll::Ready(()) }
        else {
            if !this.started {
                this.started = true;
                let waker = cx.waker().clone();
                let when = this.when;
                std::thread::spawn(move || {
                    let now = Instant::now();
                    if now < when { std::thread::sleep(when - now); }
                    waker.wake();
                });
            }
            Poll::Pending
        }
    }
}

struct ThreadWaker { thread: std::thread::Thread }
impl Wake for ThreadWaker { fn wake(self: Arc<Self>) { self.thread.unpark(); } }
fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let waker = Waker::from(Arc::new(ThreadWaker { thread: std::thread::current() }));
    let mut cx = Context::from_waker(&waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(v) => return v,
            Poll::Pending => std::thread::park(),
        }
    }
}

// 這就是 two_delays 那個 async fn 背後大概的樣子
enum TwoDelays {
    Start,
    FirstDelay(Delay), // 正在等第一個 Delay，把它存著
    SecondDelay(Delay), // 正在等第二個 Delay
    Done,
}

impl Future for TwoDelays {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        loop {
            match this {
                TwoDelays::Start => {
                    // 進入第一段：建立第一個 Delay，切到下一個狀態
                    *this = TwoDelays::FirstDelay(Delay::new(Duration::from_secs(1)));
                }
                TwoDelays::FirstDelay(delay) => match Pin::new(delay).poll(cx) {
                    Poll::Ready(()) => {
                        println!("一秒到");
                        *this = TwoDelays::SecondDelay(Delay::new(Duration::from_secs(1)));
                    }
                    Poll::Pending => return Poll::Pending, // 卡在這一段，暫停
                },
                TwoDelays::SecondDelay(delay) => match Pin::new(delay).poll(cx) {
                    Poll::Ready(()) => {
                        println!("兩秒到");
                        *this = TwoDelays::Done;
                        return Poll::Ready(());
                    }
                    Poll::Pending => return Poll::Pending,
                },
                TwoDelays::Done => panic!("不該在 Ready 之後再 poll"),
            }
        }
    }
}

fn main() {
    println!("開始");
    block_on(TwoDelays::Start); // 等同於 block_on(two_delays())
}
```

> 上面一併列出 `Delay` 和 `block_on`，方便整段程式直接放進沙盒執行。

### 對照著看

把這個手寫狀態機和原本的 `async fn` 對照：

- 原本 `async fn` 裡的**進度**，變成 `enum` 的**哪一個 variant**。
- 原本跨 `.await` 還要用到的**區域變數**（這裡是還沒完成的 `Delay`），被存進 variant 裡帶著走。
- 每個 `.await`，變成「poll 子 `Future`：`Ready` 就切到下一個狀態繼續，`Pending` 就 `return Poll::Pending` 暫停」。
- 下次被 poll，`match` 直接跳到上次停下的狀態，從那裡接著跑——這就是「從原地恢復」。

這正解釋了前面幾集看到的現象：為什麼 `Future` 每次被 poll 都能記得自己跑到
