# `async` 閉包

## 本集目標

學會 `async |...|` 語法，理解 `async` 閉包為什麼能借用捕獲的環境，以及 `AsyncFn`、`AsyncFnMut`、`AsyncFnOnce` 的用途。

> 本集是**第 6 章閉包**與**非同步一章**的補充。

## 概念說明

非同步一章已經用過 `async fn` 與 `async` block。如果想把一段非同步工作傳給另一個函數使用，過去常見的寫法是讓普通閉包回傳 `async` block：

```rust,ignore
|name| async move {
    println!("哈囉，{name}");
}
```

現代 Rust 可以直接寫成 `async` 閉包：

```rust,ignore
async |name| {
    println!("哈囉，{name}");
}
```

它和普通閉包一樣可以捕獲環境，但呼叫後不會立刻執行閉包內容，而是產生一個 `Future`；等這個 `Future` 被 `.await`，內容才會前進。

下面的可執行範例會呼叫 `block_on`。它不是標準庫 API，而是非同步一章第 6 集那個最陽春的 executor；本集只借它把立即可完成的 `Future` 跑完，避免為了示範語言語法而綁定特定 runtime。

### 為什麼普通閉包常搭配 `async move`？

普通閉包被呼叫時，會先執行閉包本身，再把 `async` block 產生的 `Future` 回傳。`Future` 之後才會被 `.await`，所以它可能在普通閉包的這次呼叫結束後才真正執行。

假設普通閉包收進一個 `String`，再讓 `async` block 使用它：

```rust,compile_fail
fn main() {
    let greet = |name: String| async {
        println!("哈囉，{name}");
    };

    let _future = greet(String::from("小明"));
}
```

這裡沒有 `move`，所以 `async` block 會嘗試借用參數 `name`。但普通閉包一回傳 `Future`，這次呼叫的參數 `name` 就該離開作用域；若 `Future` 仍借用它，之後執行時參考就可能失效，因此 Rust 不允許這段程式。

加上 `move` 後，`name` 會被搬進 `Future`：

```rust,editable
fn main() {
    let greet = |name: String| async move {
        println!("哈囉，{name}");
    };

    let _future = greet(String::from("小明"));
}
```

現在普通閉包回傳時，`name` 不會被留在已經結束的呼叫裡，而是由回傳的 `Future` 擁有，會跟著 `Future` 活到執行完畢或被丟棄。這就是 `|參數| async move { ... }` 比 `|參數| async { ... }` 常見的原因。

不過，`async move` 並非所有情況都必須使用。如果 `async` block 沒有借用這次閉包呼叫裡的參數或區域變數，就不一定需要 `move`。重點是：**`Future` 不能借用普通閉包呼叫結束時就會失效的資料。**

### 第一個 `async` 閉包

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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

fn main() {
    let greet = async |name: &str| {
        std::future::ready(()).await;
        println!("哈囉，{name}");
    };

    block_on(async {
        greet("小明").await;
        greet("小美").await;
    });
}
```

`greet("小明")` 產生一個 `Future`，`.await` 才執行裡面的 `ready` 和 `println!`。同一個閉包能被呼叫兩次，和普通 `Fn` 閉包很像。

### 那為什麼不一直使用 `|x| async move { ... }`？

普通閉包和它回傳的 `async move` block 是兩個不同東西。下面的 `async move` block 必須擁有 `prefix`，因此外層的普通閉包被呼叫時，必須把自己捕獲的 `prefix` 搬進新產生的 `Future`：

```rust,compile_fail
fn main() {
    let prefix = String::from("訊息");

    let make_future = || async move {
        println!("{prefix}");
    };

    let _first = make_future();
    let _second = make_future();
}
```

`String` 沒有實作 `Copy`。外層閉包第一次呼叫時會把 `prefix` 搬進回傳的 `Future`，等於把捕獲值移出自己的環境，因此這個閉包只能實作 `FnOnce`。第一次呼叫會消耗 `make_future`，第二次便不能再呼叫。

`async` 閉包能讓回傳的 `Future` **借用閉包捕獲的環境**：

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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

fn main() {
    let prefix = String::from("訊息");

    let show = async || {
        std::future::ready(()).await;
        println!("{prefix}");
    };

    block_on(async {
        show().await;
        show().await;
    });
}
```

兩次呼叫產生的 `Future` 都只借用 `show` 捕獲的 `prefix`，不必把同一個 `String` 搬走兩次。

### `AsyncFn` 三兄弟

第 6 章學過普通閉包依捕獲方式實作 `FnOnce`、`FnMut`、`Fn`。`async` 閉包有一組對應的 `trait`：

| 普通閉包 | `async` 閉包 | 呼叫方式 |
| --- | --- | --- |
| `FnOnce` | `AsyncFnOnce` | 至少能呼叫一次，可能消耗捕獲值 |
| `FnMut` | `AsyncFnMut` | 能呼叫多次，但呼叫時要可變借用閉包 |
| `Fn` | `AsyncFn` | 能透過共享借用重複呼叫 |

#### 編譯器大致實作了什麼？

第 6 章第 3 集曾把普通閉包想成「儲存捕獲值的匿名 `struct`，再替它實作 `FnOnce`、`FnMut` 或 `Fn`」。`async` 閉包的前半段相同；差別在於呼叫方法不會直接算出結果，而是回傳一個 `Future` 狀態機。

省略一些實作細節後，三個 `trait` 的關係大致如下。這是用來說明結構的簡化版本，不是標準庫中可自行實作的定義：

```rust,noplayground
use std::future::Future;

trait AsyncFnOnce<Args> {
    type Output;
    type CallOnceFuture: Future<Output = Self::Output>;

    fn async_call_once(self, args: Args) -> Self::CallOnceFuture;
}

trait AsyncFnMut<Args>: AsyncFnOnce<Args> {
    type CallRefFuture<'a>: Future<Output = Self::Output>
    where
        Self: 'a;

    fn async_call_mut(&mut self, args: Args) -> Self::CallRefFuture<'_>;
}

trait AsyncFn<Args>: AsyncFnMut<Args> {
    fn async_call(&self, args: Args) -> Self::CallRefFuture<'_>;
}
```

三種呼叫方式的 `self` 與回傳型別如下：

| `trait` | `self` | 呼叫所回傳的型別 |
| --- | --- | --- |
| `AsyncFnOnce` | `self` | `CallOnceFuture` |
| `AsyncFnMut` | `&mut self` | `CallRefFuture<'_>` |
| `AsyncFn` | `&self` | 同一個 `CallRefFuture<'_>` |

`Output` 是等待 `Future` 後得到的最終結果，不是 `Future` 本身。`CallOnceFuture` 來自消耗閉包的呼叫，因此可以直接擁有被搬出的捕獲值，不需要生命週期參數。

普通 `FnMut` 可以把回傳型別寫成固定的 `Self::Output`：`call_mut` 會在這次借用 `&mut self` 期間同步執行完整個閉包，回傳時工作已經完成，因此它的基本設計不必讓結果繼續借用閉包。

`AsyncFnMut` 若要支援 `Future` 借用捕獲環境，就不能只使用一個固定的 `Future` 型別。呼叫 `async` 閉包只會建立 `Future`，閉包本體要等到之後 `poll` 這個 `Future` 時才會執行，因此 `Future` 可能在呼叫結束後繼續借用閉包。`CallRefFuture<'a>` 中的 `'a` 就是這次呼叫對閉包的借用生命週期；每次呼叫的生命週期可能不同，所以必須用 GAT 表示整組 `CallRefFuture<'a>`。

`AsyncFn` 沒有另外宣告 associated type，而是沿用 `AsyncFnMut` 的 `CallRefFuture<'a>`。`async_call` 與 `async_call_mut` 都不會消耗閉包，回傳的 `Future` 都可能繼續借用捕獲環境，兩者只需要用同一組帶生命週期的 `Future` 型別來表示。

它們可用來替接收非同步處理函數的 API 寫 bound：

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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

async fn run_twice<F>(job: F)
where
    F: AsyncFn(&str),
{
    job("第一次").await;
    job("第二次").await;
}

fn main() {
    let prefix = String::from("執行");

    block_on(run_twice(async |name| {
        std::future::ready(()).await;
        println!("{prefix}：{name}");
    }));
}
```

`AsyncFn(&str)` 的讀法是：「可以透過共享借用呼叫，參數是 `&str`，呼叫結果是可以等待的非同步工作。」

和 `Fn(&str)` 一樣，這裡省略的參數生命週期具有 HRTB 的效果：`run_twice` 每次呼叫 `job` 時，都可以傳入當下那次借用的 `&str`。

### `async move |...|`

`async` 閉包也能加 `move`：

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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

fn main() {
    let label = String::from("背景工作");

    let job = async move || {
        println!("{label}");
    };

    block_on(job());
}
```

這裡的 `move` 控制閉包如何從**外層環境**捕獲 `label`：閉包取得 `label` 的所有權。它不代表每次呼叫都要把 `label` 從閉包裡搬走；閉包內容只共享讀取它，所以 `job` 仍可符合 `AsyncFn`。

要分清楚兩層：

- `async move || { ... }`：建立閉包時，把外部值 move 進閉包。
- 呼叫 `job()`：產生一個可能借用該閉包的 `Future`。

### 什麼時候該用？

如果這段非同步工作有固定名稱，而且會從不同地方呼叫，通常寫成 `async fn` 最清楚。

如果想把一段非同步工作當成值，傳給另一個函數使用，就適合用 `async` 閉包。例如下一段的 `for_each_async` 會接收一個 `action`，再對每個項目執行它。

簡單判斷就是：**直接呼叫一項工作，用 `async fn`；把工作傳給別人呼叫，用 `async` 閉包。**

## 範例程式碼

```rust,editable
use std::future::Future;
use std::task::{Context, Poll, Waker};

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

async fn for_each_async<F>(items: &[String], action: F)
where
    F: AsyncFn(&str),
{
    for item in items {
        action(item).await;
    }
}

fn main() {
    let items = vec![
        String::from("alpha"),
        String::from("beta"),
        String::from("gamma"),
    ];
    let heading = String::from("處理");

    block_on(for_each_async(&items, async |item| {
        std::future::ready(()).await;
        println!("{heading}：{item}");
    }));

    println!("共處理 {} 筆", items.len());
}
```
## 重點整理

- `async |參數| { ... }` 建立 `async` 閉包；呼叫它會產生 `Future`。
- 相較於普通閉包回傳 `async move` block，`async` 閉包能自然表達 `Future` 借用閉包捕獲環境的情況。
- `AsyncFnOnce`、`AsyncFnMut`、`AsyncFn` 對應普通閉包的 `FnOnce`、`FnMut`、`Fn`。
- `async move` 控制建立閉包時如何捕獲外部值，不代表每次呼叫都會消耗那些值。
