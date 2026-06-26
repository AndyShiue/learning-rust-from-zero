# 手寫 join

## 本集目標

自己寫一個 `Future`，把好幾個 `Future` 包成一個，讓它們**並行**推進。

## 正文

### 目標：一起等好幾個 `Future` 

上一集結尾留下一個問題：連續兩個 `.await` 會依序等待。如果我想讓好幾個工作**同時**進行、一起等它們全部完成，該怎麼辦？

辦法是自己寫一個 `Future`，叫它 `JoinAll`。它把一整個 `Vec` 的 `Future` 收進來，每次被 `poll` 的時候，就用 `for` 迴圈把裡面**每一個**還沒完成的 `Future` 各用 `poll` 試著推進一次。等到全部都完成了，自己才回 `Ready`。

### 寫出 `JoinAll`

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};
use std::time::Instant;

struct Delay {
    when: Instant,
}

impl Delay {
    fn new(duration: std::time::Duration) -> Delay {
        Delay { when: Instant::now() + duration }
    }
}

impl Future for Delay {
    type Output = ();
    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when { Poll::Ready(()) } else { Poll::Pending }
    }
}

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let mut cx = Context::from_waker(Waker::noop());
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => {}
        }
    }
}

use std::time::Duration;

type BoxFuture = Pin<Box<dyn Future<Output = ()>>>;

// 把一個 Vec 的 Future 包起來，每個都用 Some 裝著（完成後換成 None）
struct JoinAll {
    futures: Vec<Option<BoxFuture>>,
}

fn boxed<F>(future: F) -> BoxFuture
where
    F: Future<Output = ()> + 'static,
{
    Box::pin(future)
}

fn join_all(futures: Vec<BoxFuture>) -> JoinAll {
    JoinAll {
        futures: futures.into_iter().map(Some).collect(),
    }
}

impl Future for JoinAll {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut(); // JoinAll 是 Unpin，可以拿回普通的 &mut
        let mut all_done = true;

        for slot in &mut this.futures {
            // 把 Future 暫時取出來（slot 變成 None），poll 一次
            if let Some(mut fut) = slot.take() {
                match fut.as_mut().poll(cx) {
                    Poll::Ready(_) => {
                        // 完成了，就不放回去，slot 維持 None
                    }
                    Poll::Pending => {
                        *slot = Some(fut); // 還沒好，放回去下次再 poll
                        all_done = false;
                    }
                }
            }
        }

        if all_done {
            Poll::Ready(()) // 全部都完成了
        } else {
            Poll::Pending // 還有沒完成的
        }
    }
}

// 一個有「兩個 .await」的工作，所以要 poll 很多次才會完成
async fn worker(id: u32) {
    println!("worker {} 開始", id);
    Delay::new(Duration::from_secs(1)).await;
    println!("worker {} 過了第一秒", id);
    Delay::new(Duration::from_secs(1)).await;
    println!("worker {} 完成", id);
}

fn main() {
    block_on(async {
        let workers = vec![
            boxed(worker(1)),
            boxed(worker(2)),
            boxed(worker(3)),
        ];
        join_all(workers).await;
        println!("全部 worker 都完成了");
    });
}
```

這裡我們用 `type BoxFuture = Pin<Box<dyn Future<Output = ()>>>` 幫型別取了個短名字。`dyn Future<Output = ()>` 的意思是：「我不管裡面具體是哪一種 `Future`，只要它完成時回傳 `()` 就好。」`boxed(...)` 則負責把不同的 `Future` 放進 `Box`、用 `Pin` 釘住，再包成同一種 `BoxFuture`，這樣 `JoinAll` 裡的 `Vec` 才能裝下它們。

你可能會注意到這行：

```rust,ignore
let this = self.get_mut(); // JoinAll 是 Unpin，可以拿回普通的 &mut
```

`poll` 收到的 `self` 型別是 `Pin<&mut JoinAll>`，不是普通的 `&mut JoinAll`。但有些時候，Rust 允許我們把外面這層 `Pin` 拿掉，還原成裡面原本的可變參考。`get_mut()` 做的就是這件事：把 `Pin<&mut JoinAll>` 變回 `&mut JoinAll`。可以這麼做的正式原因後面講 `Unpin` 時會再補上；現在只要知道：拿到普通的 `&mut JoinAll` 之後，我們才能用熟悉的方式修改裡面的 `Vec`。

另一個值得注意的是這行：

```rust,ignore
if let Some(mut fut) = slot.take() { ... }
```

`slot` 的型別是 `&mut Option<BoxFuture>`。`Option::take()` 會把 `Option` 裡的值**拿出來**，並且在原本的位置留下 `None`。所以如果 `slot` 原本是 `Some(fut)`，呼叫 `take()` 之後，我們會拿到那個 `fut`，而 `slot` 會暫時變成 `None`。

這正好符合我們要做的事：先把子 `Future` 拿出來 `poll` 一次。如果它完成了，就不放回去，讓 `slot` 維持 `None`；如果它還沒完成，就用 `*slot = Some(fut)` 放回去，下一輪再繼續 `poll`。

### 它為什麼是並行的

跑起來你會發現：三個 worker 幾乎同時開始、同時結束，總共只花**兩秒**，而不是六秒。

原因是 `JoinAll` 的 `poll` 在一輪裡就把三個 worker 各推進一次。三個 `Delay` 同時在計時，所以兩秒後三個 worker 全部到期。這就是並行——同一段時間裡，三件「都在等」的事一起被推著走。對照上一集，如果你寫成 `worker(1).await; worker(2).await; worker(3).await;`，那會是一個跑完才換下一個，總共六秒。

### 連「要 `poll` 很多次」的 `Future` 也照樣推得動

特別注意我們故意挑了 `worker` 這個有**兩個 `.await`** 的工作放進去。這種 `Future` 不是 `poll` 一次就好，得 `poll` 很多很多次（兩個 `Delay` 各要等一秒，期間 executor 會狂 `poll`）才會走完。

而 `JoinAll` 完全不用為這件事操心——它只管「對每個還沒完成的 `Future` 各 `poll` 一次」，至於某個 `Future` 內部卡在第幾個 `.await`、還要 `poll` 幾次才完成，那是那個 `Future` 自己記著的（記得嗎？`Future` 會記住自己的進度）。`JoinAll` 只要重複地一輪一輪 `poll`，每個 `Future` 自然會一步步往前，直到全部回 `Ready`。`poll` 這套設計正有這樣的威力：單純組合 `Future` 的人不必理解被組合者的內部實作細節。

不過，我們的 executor 還是那個瘋狂空轉的笨版本。下一集就來解決這件事——讓 executor 在沒事做的時候去睡覺，等該醒了再被叫醒。

## 重點整理

- 把多個 `Future` 並行推進的辦法，是自己寫一個 `Future`（`JoinAll`），在 `poll` 裡用 `for` 迴圈把每個子 `Future` 各 `poll` 一次
- 完成的子 `Future` 換成 `None`，全部都 `None`（完成）時 `JoinAll` 才回 `Ready`
- `JoinAll` 不必處理「某個 `Future` 要 `poll` 很多次」的情況——子 `Future` 自己記得進度，只管一輪一輪 `poll` 即可
