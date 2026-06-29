# 回到 Tokio

## 本集目標

從手寫 runtime 回到 Tokio，搞懂 `tokio::spawn` 的 `Send + 'static` 要求、Tokio 中 `block_on` 和我們手寫 `block_on` 的差別，以及 Tokio runtime 的多執行緒 / 單執行緒模式。

## 正文

### 你已經懂底層了

恭喜你撐過了最硬的幾集！前面我們從零手寫了 executor、reactor、`Task`、`JoinHandle`，還拆開了狀態機和 `Pin`。Tokio 真正的實作當然複雜得多，但現在回頭看它的 API，很多名詞和設計取捨應該不會讓人陌生。

### `tokio::spawn` 與 `Send + 'static`

`tokio::spawn` 就是我們手寫過的 `spawn`：把一個 `Future` 包成 `Task` 交給 runtime 排程，回傳一個 `JoinHandle`：

```rust,editable
# extern crate tokio;
#
#[tokio::main]
async fn main() {
    let handle = tokio::spawn(async {
        21 * 2
    });
    let result = handle.await.expect("背景 task panic 了");
    println!("結果：{}", result);
}
```

（Tokio 的 `JoinHandle` `.await` 回傳的是 `Result`，因為背景 `Task` 有可能 panic，所以這裡用 `expect`。）

但 `tokio::spawn` 有個我們手寫版沒強制的要求：傳進去的 `Future`、以及它的輸出，都必須是 **`Send + 'static`**。為什麼？因為 Tokio 預設是**多執行緒** runtime，它可能把一個 `Task` 從這條 `Thread` 搬到另一條去跑，這樣才能讓閒著的 `Thread` 幫忙。為了能在 `Thread` 之間搬動，就需要 `Send`；而 `Task` 可能活很久、不知道何時結束，所以也需要 `'static`。

相對地，`tokio::runtime::Runtime::block_on` **不需要** `Send` 或 `'static`。因為它只是把你給它的那個 `Future`，在目前這條呼叫的 `Thread` 上跑到完成，不會搬到別條 `Thread`，所以沒有 `Send` 的顧慮。

### 和手寫 `block_on` 的語意差異

這裡要特別點出一個容易忽略的差異。我們第 11 集後手寫的 `block_on` 會等 ready queue 裡所有 `Task` 都完成才回傳。Tokio 的 `block_on` 不一樣：它是「**傳給它的那個 `Future` 一完成就回傳**」，不會等其他用 `tokio::spawn` 開出去的背景 `Task`。那些還沒做完的背景 `Task` 會留在 runtime 上。

一句話對比：手寫版是「跑完整批才繼續」，Tokio 是「跑完我指定的這一個就繼續」。所以在 Tokio 裡，`block_on` 回傳時，只代表你傳進去的那個 `Future` 完成了；你 `spawn` 出去的背景 `Task` 可能還沒跑完。如果 runtime 接著結束，這些背景 `Task` 就沒有機會繼續做完。

### 新手最常見的編譯錯誤：`.await` 期間持有非 `Send` 的值

`tokio::spawn` 要求 `Future: Send`，而一個 `Future` 是不是 `Send`，取決於它**跨 `.await` 時保存了什麼**。如果在 `.await` 期間還持有一個非 `Send` 的值（像 `Rc`、`RefCell`），整個 `Future` 就不是 `Send`，於是不能 `spawn`：

```rust,compile_fail
# extern crate tokio;
#
use std::rc::Rc;

async fn some_async() {}

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let rc = Rc::new(5);
        some_async().await; // 跨 .await 還持有 rc，而 Rc 不是 Send
        println!("{}", rc);
    });
}
```

編譯器會說 `future cannot be sent between threads safely`，並指出 `Rc<i32>` 在一個 `.await` 上被跨越使用。

解法有幾種：

**用 `Send` 的替代品。** `Rc` 換成 `Arc`（第 9 章），它就是 `Send` 的：

```rust,noplayground
# extern crate tokio;
#
use std::sync::Arc;

async fn some_async() {}

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let arc = Arc::new(5);
        some_async().await;
        println!("{}", arc);
    });
}
```

**在 `.await` 之前就把非 `Send` 的值處理掉。** 用 `{}` 縮小它的 scope，讓它在 `.await` 之前就被 `drop`，這樣狀態機跨 `.await` 時根本不持有它：

```rust,noplayground
# extern crate tokio;
#
use std::rc::Rc;

async fn some_async() {}

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let n = {
            let rc = Rc::new(5);
            *rc
        }; // rc 在這個 block 結束就 drop 了，沒有跨 .await
        some_async().await;
        println!("{}", n);
    });
}
```

（明確呼叫 `drop(rc)` 把它在 `.await` 前丟掉，也是同樣的效果。）

### `#[tokio::main]` 的 flavor

最後，雖然 `#[tokio::main]` 預設用多執行緒 runtime，但你可以改：

```rust,editable
extern crate tokio;

// 單執行緒 runtime
#[tokio::main(flavor = "current_thread")]
async fn main() {
    println!("我跑在單一執行緒上");
}
```

或指定 worker `Thread` 的數量：

```rust,editable
extern crate tokio;

// 多執行緒，指定 4 條 worker
#[tokio::main(flavor = "multi_thread", worker_threads = 4)]
async fn main() {
    println!("我有 4 條 worker threads");
}
```

單執行緒 runtime 的好處是沒有跨 `Thread` 搬動的問題，缺點是不能真平行。

## 重點整理

- `tokio::spawn` 把 `Future` 交給 runtime，回傳 `JoinHandle`（`.await` 後得到 `Result`，因為可能 panic）
- Tokio 預設多執行緒，可能在 thread 間搬 `Task`，所以 `spawn` 的 `Future` 與輸出要 `Send + 'static`；`block_on` 在當前 thread 跑，不需要
- 語意差異：手寫 `block_on` 等**所有** `Task` 完成；Tokio `block_on` 是**指定的 `Future`** 一完成就回傳
- `.await` 期間持有非 `Send` 的值（`Rc`、`RefCell`）會讓 `Future` 不是 `Send`，不能 `spawn`；解法是改用 `Arc`、或用作用域 / `drop` 讓它在 `.await` 前消失
- `#[tokio::main]` 預設多執行緒，但可用 `flavor = "current_thread"` 或 `worker_threads = N` 調整
