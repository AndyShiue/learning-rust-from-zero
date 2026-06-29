# `async` 遞迴

## 本集目標

理解為什麼 `async fn` 不能直接呼叫自己，以及怎麼用 `Box::pin` 解決。

## 正文

### 直接遞迴會編譯失敗

來試著寫一個 `async` 版的階乘——一個 `async fn` 在裡面 `.await` 自己：

```rust,compile_fail
async fn factorial(n: u64) -> u64 {
    if n == 0 {
        1
    } else {
        n * factorial(n - 1).await // 編譯錯誤
    }
}

fn main() {}
```

編譯器會直接拒絕：

```text
error[E0733]: recursion in an async fn requires boxing
```

### 為什麼？因為 `Future` 型別的大小無法決定

回想第 15 集：`async fn` 會被改寫成一個狀態機，而跨 `.await` 用到的東西都要存進這個狀態機。

這裡的關鍵不是遞迴執行時會不會停。`n == 0` 當然是 base case，真的跑起來時會停；但在程式開始跑之前，編譯器就要先決定 `factorial` 回傳的 `Future` 型別有多大。

粗略想像一下，它可能需要長得像這樣：

```rust,compile_fail
enum FactorialFuture {
    Start { n: u64 },
    Waiting {
        n: u64,
        child: FactorialFuture,
    },
    Done,
}
#
# fn main() {}
```

`Waiting` 狀態要保存正在 `.await` 的 `factorial(n - 1)`；而 `factorial(n - 1)` 回傳的又是同一種 `FactorialFuture`。於是這個型別直接包含自己，編譯器在算 `child` 欄位要占多少空間時，永遠算不出固定答案。

這個情境你其實見過。第 5 章講遞迴型別時就碰過一模一樣的問題：一個 `struct` 直接包含自己，大小會無限大。當時的解法是用 `Box` 把遞迴的部分放到 heap 上——`Box<T>` 不管 `T` 多大，它本身永遠只是一個指標大小。

### 解法：用 `Box::pin` 包住遞迴呼叫

`async` 遞迴的解法一樣：把遞迴呼叫產生的 `Future` 用 `Box::pin` 包起來。`Pin<Box<dyn Future<Output = u64>>>` 也實作了 `Future`。它被 `poll` 的時候，會把工作轉交給 `Box` 裡面真正的 `Future`。這樣狀態機裡存的就只是一個固定大小的指標，而不是直接存另一個同型別的狀態機：

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};

// 回傳型別改成 Pin<Box<dyn Future<...>>>，遞迴呼叫用 Box::pin 包起來
fn factorial(n: u64) -> Pin<Box<dyn Future<Output = u64>>> {
    Box::pin(async move {
        if n == 0 {
            1
        } else {
            n * factorial(n - 1).await
        }
    })
}

fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = Box::pin(future);
    let mut cx = Context::from_waker(Waker::noop());
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(v) => return v,
            Poll::Pending => {}
        }
    }
}

fn main() {
    let result = block_on(factorial(5));
    println!("5! = {}", result);
}
```

> 上面一併附上前面寫的最陽春的 `block_on`（這個 `factorial` 其實沒有真的需要等的 `.await`，所以用這種版本就夠了）。

我們把 `factorial` 從 `async fn` 改寫成一個普通函式，回傳 `Pin<Box<dyn Future<Output = u64>>>`，函式體則是一個 `Box::pin` 包起來的 `async` block。遞迴呼叫 `factorial(n - 1)` 回傳的也是 `Pin<Box<...>>`，是固定大小，所以狀態機的大小就能決定了。

這裡的 `Box` 和 `Pin` 各自負責不同的事：`Box` 讓外層大小固定，`Pin` 則讓裡面的 `Future` 可以被安全地 `poll`。只回傳 `Box<dyn Future<Output = u64>>` 不夠，因為 `dyn Future` 不保證 `Unpin`；而 `Box<dyn Future>` 不能直接安全地把盒子裡的 `Future` 當成已經被釘住。所以我們才回傳 `Pin<Box<dyn Future<Output = u64>>>`。

你可能也會注意到：`block_on` 接收的是 `F: Future`，可是 `factorial(5)` 回傳的是 `Pin<Box<dyn Future<Output = u64>>>`，這樣也能傳進去嗎？可以，因為 `Pin<Box<dyn Future<Output = u64>>>` 本身也實作了 `Future`，所以對 `block_on` 來說，它收到的仍然是一個可以 `poll` 的東西。

到這裡，我們把 `async` 底層的機制——`Future`、executor、reactor、狀態機、`Pin`——從頭到尾走過一遍了。下一集起，我們要回到 Tokio，看看一個真正成熟的 runtime 提供了哪些好用的工具方便使用者撰寫 `async` 程式碼。

## 重點整理

- `async fn` 直接呼叫自己會編譯失敗，因為編譯器無法決定狀態機型別的大小
- base case 只能決定執行時會不會停，不能決定編譯期的型別大小；問題和第 5 章的遞迴型別一樣：自己包含自己，大小無限
- 解法是把遞迴呼叫用 `Box::pin` 包起來，讓狀態機裡只存一個固定大小的指標
