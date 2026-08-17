# `async` 閉包

## 本集目標

學會 `async |...|` 語法，理解 `async` 閉包為什麼能借用捕獲的環境，以及 `AsyncFn`、`AsyncFnMut`、`AsyncFnOnce` 的用途。

> 本集是**第 6 章閉包**與**第 12 章非同步**的補充。

## 概念說明

第 12 章已經用過 `async fn` 與 `async` block。如果想把一段非同步工作傳給另一個函數使用，過去常見的寫法是讓普通閉包回傳 `async` block：

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

下面的可執行範例會呼叫 `block_on`。它不是標準庫 API，而是藏在範例測試骨架裡的一個最小 executor；本章只借它把立即可完成的 `Future` 跑完，避免為了示範語言語法而綁定特定 runtime。

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

這裡沒有 `move`，所以 `async` block 會嘗試借用參數 `name`。但普通閉包一回傳 `Future`，這次呼叫的參數 `name` 就該離開作用域；若 Future 仍借用它，之後執行時參考就可能失效，因此 Rust 不允許這段程式。

加上 `move` 後，`name` 會被搬進 Future：

```rust,editable
fn main() {
    let greet = |name: String| async move {
        println!("哈囉，{name}");
    };

    let _future = greet(String::from("小明"));
}
```

現在普通閉包回傳時，`name` 不會被留在已經結束的呼叫裡，而是由回傳的 Future 擁有，會跟著 Future 活到執行完畢或被丟棄。這就是 `|參數| async move { ... }` 比 `|參數| async { ... }` 常見的原因。

不過，`async move` 並非所有情況都必須使用。如果 `async` block 沒有借用這次閉包呼叫裡的參數或區域變數，就不一定需要 `move`。重點是：**Future 不能借用普通閉包呼叫結束時就會失效的資料。**

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

普通閉包和它回傳的 `async move` block 是兩個不同東西。`move` 會要求產生的 `Future` 擁有捕獲值；若值來自閉包自己的環境，每次呼叫時就可能想再次把同一個值 move 出去：

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

第一次呼叫已經要把 `prefix` 搬進回傳的 `Future`，普通閉包不能在第二次呼叫時再搬一次。

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

`action` 的每個 `Future` 可以借用當次傳入的 `item`，也能借用閉包捕獲的 `heading`。每次 `.await` 完成後才進到下一項，因此這些借用不會互相重疊。

## 重點整理

- `async |參數| { ... }` 建立 `async` 閉包；呼叫它會產生 `Future`。
- 相較於普通閉包回傳 `async move` block，`async` 閉包能自然表達 Future 借用閉包捕獲環境的情況。
- `AsyncFnOnce`、`AsyncFnMut`、`AsyncFn` 對應普通閉包的 `FnOnce`、`FnMut`、`Fn`。
- `async move` 控制建立閉包時如何捕獲外部值，不代表每次呼叫都會消耗那些值。
