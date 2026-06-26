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

### 為什麼？因為 `Future` 的大小會變無限大

回想第 15 集：`async fn` 會被改寫成一個狀態機，而跨 `.await` 用到的東西都要存進這個狀態機。

問題來了：`factorial` 的狀態機裡，存著它正在 `.await` 的那個 `factorial(n - 1)`——可那個 `factorial(n - 1)` 也是同一種狀態機，裡面又存著 `factorial(n - 2)`……一層包一層，沒有底。於是編譯器在算「這個狀態機到底要多大」時，得到的答案是**無限大**。一個大小無限的型別當然沒辦法存在，所以編譯失敗。

這個情境你其實見過。第 5 章講遞迴型別（像鏈結串列、樹）時就碰過一模一樣的問題：一個 `struct` 直接包含自己，大小會無限大。當時的解法是用 `Box` 把遞迴的部分放到 heap 上——`Box<T>` 不管 `T` 多大，它本身永遠只是一個指標大小。

### 解法：用 `Box::pin` 包住遞迴呼叫

`async` 遞迴的解法一樣：把遞迴呼叫產生的 `Future` 用 `Box::pin` 包起來。這樣狀態機裡存的就只是一個固定大小的指標，而不是另一個無限大的狀態機：

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

# fn block_on<F: Future>(future: F) -> F::Output {
#     let mut future = Box::pin(future);
#     let mut cx = Context::from_waker(Waker::noop());
#     loop {
#         match future.as_mut().poll(&mut cx) {
#             Poll::Ready(v) => return v,
#             Poll::Pending => {}
#         }
#     }
# }
#
fn main() {
    let result = block_on(factorial(5));
    println!("5! = {result}");
}
```

> 上面隱藏了一個最陽春的 `block_on`（這個 `factorial` 其實沒有真的需要等的 `.await`，所以用第 6 集那種版本就夠了）。

我們把 `factorial` 從 `async fn` 改寫成一個普通函式，回傳 `Pin<Box<dyn Future<Output = u64>>>`，函式體則是一個 `Box::pin` 包起來的 `async` block。遞迴呼叫 `factorial(n - 1)` 回傳的也是 `Pin<Box<...>>`，是固定大小，狀態機就不再無限大了。

### `Box::pin` 的另外兩個用途

`Box::pin`（以及更一般的「把 `Future` 裝進 `Box<dyn Future>`」）不只用在遞迴。每當你需要「把型別不同的 `Future` 當成同一種東西看待」時，它都是答案。兩個常見場景：

- **想把不同的 `Future` 塞進同一個 `Vec`**：每個 `async` block 的型別都不一樣，沒辦法直接放進 `Vec`；但 `Vec<Pin<Box<dyn Future<Output = T>>>>` 就可以，因為它們都被統一成 `dyn Future`。
- **`match` 的兩個分支要回傳不同的 `Future`**：兩個分支各自是不同型別的 `Future`，函式沒辦法回傳，包成 `Box::pin` 之後就統一了。

這其實就是第 9 章（多執行緒）裡 `Box<dyn Fn>` 那一招的翻版——當「型別不同、但想當成同一種來用」時，用 `Box<dyn Trait>` 把它們抹平成一個共同的型別。`Future` 也適用同一個道理。

到這裡，我們把 `async` 底層的機制——`Future`、executor、reactor、狀態機、`Pin`——從頭到尾走過一遍了。下一集起，我們要回到 Tokio，看看一個真正成熟的 runtime 提供了哪些好用的工具，而你現在已經有足夠的底子看懂它們背後在做什麼。

## 重點整理

- `async fn` 直接呼叫自己會編譯失敗（`recursion in an async fn requires boxing`），因為狀態機大小會變無限大
- 原因和第 5 章的遞迴型別一樣：自己包含自己，大小無底
- 解法是把遞迴呼叫用 `Box::pin` 包起來，讓狀態機裡只存一個固定大小的指標
- `Box::pin` 也用於「把不同型別的 `Future` 放進同一個 `Vec`」或「`match` 分支回傳不同 `Future`」，呼應第 9 章的 `Box<dyn Fn>`
