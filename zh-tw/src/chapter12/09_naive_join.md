# 手寫 `join`

## 本集目標

上一集看到連著兩個 `.await` 會**依序**等待。這一集自己寫一個 `Future`，把好幾個 future 包在一起、讓它們**並行**推進——這就是 `join` 在做的事。

## 概念說明

### 並行的關鍵：一次 poll，推進所有人

要讓好幾個 future 同時前進，訣竅很簡單：**寫一個外層 future，它每次被 poll 時，就把裡面每個還沒完成的子 future 都各 poll 一次。** 全部子 future 都完成了，外層才回 `Ready`。

我們做一個吃整個 `Vec`、用 `for` 迴圈推進全部的 `JoinAll`：

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

struct JoinAll<F: Future> {
    // 每個 slot：還沒完成是 Some(future)，完成後換成 None
    futures: Vec<Option<Pin<Box<F>>>>,
}

impl<F: Future> Future for JoinAll<F> {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        let mut all_done = true;

        for slot in this.futures.iter_mut() {
            if let Some(fut) = slot.as_mut() {
                // 還沒完成的，推進一次
                if fut.as_mut().poll(cx).is_ready() {
                    *slot = None;       // 做完了，換成 None
                } else {
                    all_done = false;   // 還有人沒做完
                }
            }
        }

        if all_done {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

fn join_all<F: Future>(futures: Vec<F>) -> JoinAll<F> {
    JoinAll {
        futures: futures.into_iter().map(|f| Some(Box::pin(f))).collect(),
    }
}
```

`poll` 裡就是一圈 `for`：每個還沒完成（`Some`）的子 future 各 poll 一次，做完的換成 `None`；只要還有任何一個沒做完，就回 `Pending`，全部都 `None` 才回 `Ready`。

（這裡用 `Vec<Option<Pin<Box<F>>>>`：`Box::pin` 把每個子 future 釘好以便 `poll`，`Option` 讓我們能把「做完的」標記成 `None`。`self.get_mut()` 能用，是因為 `JoinAll` 的欄位都能安全 move、它是 `Unpin`。）

### 故意放「要 poll 很多次才完成」的 future 進去

為了證明 `JoinAll` 真的能推進**複雜**的子 future，我們故意放一個**有多個 `.await`** 的 async 工作進去——這種 future 要被 poll 很多次、跨好幾個暫停點才會完成：

```rust,ignore
async fn work(id: u32) {
    println!("task {id} 開始");
    delay(1).await;
    println!("task {id} 中段");
    delay(1).await;
    println!("task {id} 完成");
}
```

把三個 `work` 丟進 `JoinAll`：

```rust,ignore
run(join_all(vec![work(1), work(2), work(3)]));
```

它們會**並行**推進——三個 task 的「開始 / 中段 / 完成」會交錯印出，而且整批大約只花 2 秒（兩個 `delay(1)` 重疊跑），不是 6 秒。

重點是：`JoinAll` **完全不必特別處理**那些多 `.await` 的 future。它只管「對每個還沒完成的子 future 各 poll 一次」；至於某個子 future 內部有幾個 `.await`、自己記到哪個進度，那是它**自己的事**（它自己是個會記進度的狀態機）。`JoinAll` 只負責「雨露均霑、每個都推一下」，剩下的交給每個 future 自理。

（注意：因為 `Vec<F>` 要求每個元素同型別，我們用「同一個 `async fn` 呼叫多次」（`work(1)`、`work(2)`…）來產生一批**同型別**的 future；如果直接寫好幾個 `async { }` 區塊，每個會是不同的匿名型別，塞不進同一個 `Vec`。）

## 範例程式碼

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};
use std::time::{Duration, Instant};

struct Delay {
    when: Instant,
}
impl Future for Delay {
    type Output = ();
    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        if Instant::now() >= self.when {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}
fn delay(secs: u64) -> Delay {
    Delay {
        when: Instant::now() + Duration::from_secs(secs),
    }
}

struct JoinAll<F: Future> {
    futures: Vec<Option<Pin<Box<F>>>>,
}
impl<F: Future> Future for JoinAll<F> {
    type Output = ();
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        let mut all_done = true;
        for slot in this.futures.iter_mut() {
            if let Some(fut) = slot.as_mut() {
                if fut.as_mut().poll(cx).is_ready() {
                    *slot = None;
                } else {
                    all_done = false;
                }
            }
        }
        if all_done {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}
fn join_all<F: Future>(futures: Vec<F>) -> JoinAll<F> {
    JoinAll {
        futures: futures.into_iter().map(|f| Some(Box::pin(f))).collect(),
    }
}

async fn work(id: u32) {
    println!("task {id} 開始");
    delay(1).await;
    println!("task {id} 中段");
    delay(1).await;
    println!("task {id} 完成");
}

// 第 6 集那台笨 executor
fn run<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let waker = Waker::noop();
    let mut cx = Context::from_waker(waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => {}
        }
    }
}

fn main() {
    run(join_all(vec![work(1), work(2), work(3)]));
}
```

## 重點整理

- 讓多個 future 並行的訣竅：寫一個外層 future，每次被 poll 就**把每個還沒完成的子 future 各 poll 一次**，全部完成才回 `Ready`
- `JoinAll` 用 `Vec<Option<Pin<Box<F>>>>`：做完的 slot 換成 `None`，`for` 一圈推進其餘的
- 連「內部有很多 `.await`、要 poll 很多次」的 future，`JoinAll` 也照樣推得動——它不必特別處理，每個子 future 自己記得進度（自己是狀態機）
- `.await` 依序、`join` 並行：三個各含兩段 `delay(1)` 的 task 一起跑，總共約 2 秒而非 6 秒
- `Vec<F>` 要求同型別，所以用「同一個 `async fn` 呼叫多次」產生同型別 future；多個 `async { }` 區塊彼此型別不同，塞不進同一個 `Vec`
