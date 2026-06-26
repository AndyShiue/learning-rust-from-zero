# `Future` `trait` 與最陽春的 executor

## 本集目標

看懂 `Future` `trait` 的正式定義，並親手寫一個最笨，但真的能跑的 executor。

## 正文

### `Future` `trait` 長什麼樣

前幾集一直講「`Future`」，現在來看它真正的定義。它是標準庫裡的一個 `trait`：

```rust,ignore
pub trait Future {
    type Output;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

拆開來看：

- `type Output` 是這個 `Future` 完成後會給出的值的型別
- `poll` 是核心方法。它會問這個 `Future`：「你好了沒？」
- 回傳值是 `Poll`，一個只有兩種狀態的 `enum`：

```rust,ignore
pub enum Poll<T> {
    Ready(T), // 好了，這是結果
    Pending,  // 還沒好，待會再來問
}
```

所以推進一個 `Future` 的方式就是不斷 `poll` 它：回 `Pending` 就代表還沒好，回 `Ready(value)` 就代表完成，可以把結果拿走。

### 為什麼 `poll` 的 `self` 是 `Pin<&mut Self>`

你大概注意到一個奇怪的地方：`poll` 的第一個參數不是我們熟悉的 `self` / `&self` / `&mut self`，而是 `self: Pin<&mut Self>`。

先別緊張，這一章後面會花好幾集慢慢講 `Pin` 的細節，現在你只要接受一件事：**`Pin` 是一個很特別的型別**。Rust 規定，除了我們之前認識的 `self` / `&self` / `&mut self`，能放在 `self` 位置的型別只有一小撮「智慧指標」：

- `Box<Self>`、`Rc<Self>`、`Arc<Self>`
- 以及 `Pin<...>`

一般你自訂的型別**不能**這樣用在 `self` 位置。`poll` 之所以能寫成 `self: Pin<&mut Self>`，正是因為它夠特別。目前你可以先把 `Pin<&mut Self>` 想成「一個受了限制的 `&mut Self`」——它讓你能改 `Future` 的內容，但不准你把它整個搬走。為什麼要有這個限制，之後會講。

### 最陽春的 executor

`poll` 是 `Future` 的引擎，但總得有人去發動它——這個「不斷 `poll` 直到完成」的角色就叫 **executor**。Rust 標準庫**不附**任何 executor，所以我們自己寫一個最笨的版本：

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

fn block_on<F: Future>(future: F) -> F::Output {
    // 把 Future 放到 heap 上並「釘住」，得到 Pin<Box<F>>
    let mut future = Box::pin(future);

    // 做一個 Context，裡面包什麼都不做的 Waker，之後再解釋它是幹嘛的
    let mut cx = Context::from_waker(Waker::noop());

    loop {
        // .as_mut() 把 Pin<Box<F>> 借用成 Pin<&mut F>，正是 poll 要的型別
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value, // 好了，把結果回傳
            Poll::Pending => {
                // 還沒好，這個最笨的 executor 就是回去再 poll 一次（空轉）
            }
        }
    }
}

fn main() {
    let value = block_on(async {
        println!("async block 開始跑");
        1 + 2
    });
    println!("結果是 {}", value);
}
```

### 兩個搬運值的小工具

這個 executor 用了兩個和 `Pin` 有關的工具，先簡單認識：

`Box::pin(x)` 的型別是 `fn pin(x: T) -> Pin<Box<T>>`——把值放到 heap 上，並用 `Pin` 把它釘住。目前你就把它當成「一個受限的指標」就好。

`Pin<Ptr>` 上 `as_mut` 的型別是 `fn as_mut(&mut self) -> Pin<&mut <Ptr as Deref>::Target>`，對 `Pin<Box<T>>` 來說就是 `-> Pin<&mut T>`，剛好就是 `poll` 需要的 `self: Pin<&mut Self>`。重點是 `as_mut` 只是可變借用，沒有把 `future` 交出去，所以我們的 `loop` 才能拿同一個 `future` 反覆 `poll`。

### 老實說：到目前為止其實「沒在等任何東西」

這裡要誠實交代一件事。從第 3 集到這一集，我們寫的那些 `async fn`、`async` block，其實**沒有真的在等什麼**——它們裡面都沒有會卡住的 `.await`。對於這種 `Future`，第一次 `poll` 就會直接回 `Ready`，我們的 `Pending` 分支根本不會跑到。

也就是說，前面這些例子純粹是拿來示範 `Future` 和 executor 的機制，還稱不上是「真正用到 `async` 功能」的程式。下一集我們要手寫一個 `Delay`——一個會真的回 `Pending`、需要等一段時間才完成的 `Future`，那才是第一個更像樣的非同步工作。

### executor 有很多種設計

最後提醒一個觀念：Rust 標準庫只定義了 `Future` `trait`，**怎麼實作 executor 完全留給 runtime 自由發揮**。我們這集寫的是「回 `Pending` 就忙著空轉重 poll」的笨版本——超級浪費 CPU 資源。真正的 runtime 會聰明得多：沒事做的時候去睡覺，有事了才被叫醒。

正因為標準庫不規定 executor 怎麼寫，才會有 Tokio、smol 等各有特色的 runtime。接下來幾集，我們會從這個最笨的版本出發，一步一步把它演進到接近真實 runtime 的樣子。

## 重點整理

- `Future` `trait` 的核心是 `poll`，回傳 `Poll::Ready(value)`（好了）或 `Poll::Pending`（還沒好）
- `poll` 的 `self` 是 `Pin<&mut Self>`， `Pin` 是少數能直接放在 `self` 位置的特別型別；目前先當成「受限的 `&mut Self`」
- **executor** 負責不斷 `poll` 一個 `Future` 直到 `Ready`；標準庫不附 executor，要自己或靠 runtime 提供
- `Box::pin` 把值放 heap 並釘住、`as_mut` 借出 `Pin<&mut T>`，兩者配合讓 `loop` 能反覆 `poll` 同一個 `Future`
- 前幾集的 `async` 其實都沒在等東西，`poll` 一次就 `Ready`；下一集的 `Delay` 才會真的 `Pending`
- 標準庫只定義 `Future`，executor 怎麼寫留給 runtime，這就是 Tokio、smol 等不同 runtime 存在的原因
