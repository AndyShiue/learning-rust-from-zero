# `async` 的 `Mutex`、`RwLock` 與 `Notify`

## 本集目標

搞懂為什麼有時候得用 Tokio 版的鎖、什麼時候用標準庫的就好，並認識喚醒工具 `Notify`。

## 正文

### 從 `Send` / `Sync` 的一個例外講起

先回到多執行緒一章的 `Send` / `Sync`。日常的型別有個規律：一個型別只要是 `Sync`（能被多條 `Thread` 同時借用），通常它也是 `Send`（能搬到別條 `Thread`）。

但有些少數的例外：`std::sync::Mutex` 和 `RwLock` 的 **guard**（`lock()` 回傳的那個 `MutexGuard` / `RwLockReadGuard` / `RwLockWriteGuard`）是 **`Sync` 但不是 `Send`**。為什麼？因為在某些作業系統上，一把鎖**必須由當初上鎖的那條 `Thread` 來解鎖**；如果把 guard 搬到別條 `Thread` 才 `drop`（解鎖），就會出錯。所以標準庫乾脆禁止這些 guard 被 `Send`。

### 這些例外會影響到 `async`

這樣不實作 `Send` 的特性，在 `async` 裡會變成一個讓人困惑的編譯錯誤。回想第 21 集：一個 `Future` 跨 `.await` 時持有非 `Send` 的東西，整個 `Future` 就不是 `Send`，於是不能 `tokio::spawn`。而標準庫內的 guard 正是非 `Send` 的——所以**抓著標準庫的 guard 跨 `.await`** 就會中招：

```rust,compile_fail
# extern crate tokio;
#
use std::sync::{Arc, Mutex};

async fn do_io() {}

#[tokio::main]
async fn main() {
    let data = Arc::new(Mutex::new(0));
    tokio::spawn(async move {
        let mut guard = data.lock().expect("取得鎖失敗"); // 標準庫的 MutexGuard，不是 Send
        do_io().await; // 抓著 guard 跨 .await
        *guard += 1;
    }); // 編譯錯誤：future 不是 Send，不能 spawn
}
```

這個錯誤其實是個**有益的警告**——它正好提醒你違反了一條重要紀律：**`Mutex` 保護的是共享的可變狀態，lock 的 scope 應該越短越好，絕對不要抓著 lock 去等 I/O。** 拿著鎖等 I/O 的話，其他人在這段時間全被擋在鎖外面，並行就崩了。

所以最好的解法通常不是「想辦法跨 `.await` 持有鎖」，而是**縮短 lock scope**：在 `.await` 之前就把該改的改完、讓 guard 離開 scope：

```rust,no_run
# extern crate tokio;
#
use std::sync::{Arc, Mutex};

async fn do_io() {}

#[tokio::main]
async fn main() {
    let data = Arc::new(Mutex::new(0));
    tokio::spawn(async move {
        {
            let mut guard = data.lock().expect("取得鎖失敗");
            *guard += 1;
        } // guard 在這裡就 drop 了，沒有跨 .await
        do_io().await; // 等 I/O 時手上沒抓著鎖
    });
}
```

### 必要時才用 Tokio 的鎖

但有時候你真的**需要**抓著鎖跨 `.await`（例如要在持有鎖的狀態下做一個 `async` 操作，且邏輯上不能拆開）。這種時候才改用 `tokio::sync::Mutex`——它的 guard 是 `Send` 的，可以安全地跨 `.await`：

```rust,no_run
# extern crate tokio;
#
use std::sync::Arc;
use tokio::sync::Mutex; // 注意是 tokio 的 Mutex

#[tokio::main]
async fn main() {
    let data = Arc::new(Mutex::new(0));
    let d = data.clone();
    tokio::spawn(async move {
        let mut guard = d.lock().await; // 注意 lock() 要 .await
        *guard += 1; // 這個 guard 是 Send，可以跨 .await
    });
}
```

但請記得：**標準庫的鎖比 Tokio 的鎖快**（Tokio 的鎖為了能跨 `.await` 付出額外成本）。所以預設用 `std` 的鎖、縮短作用域；只有「非抓著鎖跨 `.await` 不可」時，才動用 Tokio 的 `Mutex`。

和標準庫一樣，Tokio 也有 `RwLock`，把讀寫分開：`read().await` 允許多個讀者同時進入，`write().await` 則獨佔給單一寫者。

### `Notify`：不帶資料的喚醒

最後介紹 `tokio::sync::Notify`。它是一個**不帶 payload（不帶資料）的喚醒工具**——它能讓一個 `Task` 睡著等（`notified().await`），讓另一個 `Task` 戳它一下叫它起來（`notify_one()`），但**不傳任何值**。

```rust,no_run
# extern crate tokio;
#
use std::sync::Arc;
use tokio::sync::Notify;

#[tokio::main]
async fn main() {
    let notify = Arc::new(Notify::new());
    let n = notify.clone();

    tokio::spawn(async move {
        n.notified().await; // 睡著等通知
        println!("被通知了，醒來做事");
    });

    notify.notify_one(); // 戳醒一個等待者
}
```

`Notify` 通常搭配一塊**自己用 `Mutex` 管理的共享狀態**使用：你改完共享狀態後，`notify` 一下，被叫醒的 `Task` 自己去看狀態變成什麼。它**不是 queue**——多次 `notify` 可能被合併成一次（如果還沒有人在等，通知可能就只記一筆），所以別拿它來當「一則訊息對一次喚醒」的訊息佇列。

### `Notify` 和 `watch` 的差別

`Notify` 容易和上一集的 `watch` 搞混，但兩者定位不同：

- **`Notify`**：**不帶資料、無狀態**。它只負責「戳人起床」，至於起床要看什麼，得你自己用 `Mutex` 之類的東西管著。
- **`watch`**：**帶「最新值」、有狀態**。它本身就存著一份最新的狀態，接收端醒來直接讀得到。

## 重點整理

- 標準庫的 `Mutex` / `RwLock` guard 是 `Sync` 但非 `Send`（某些作業系統規定上鎖的 `Thread` 才能解鎖），抓著它跨 `.await` 會讓 `Future` 非 `Send`、不能 `spawn`
- 這個編譯錯誤是有益的警告：`Mutex` 的 lock 作用域要短，別抓著鎖等 I/O；通常縮短作用域（`.await` 前就 `drop` guard）即可
- 一定要抓著鎖跨 `.await` 時才用 `tokio::sync::Mutex`（guard 是 `Send`，`.lock().await`），但優先用標準庫更快的鎖。
- Tokio `RwLock` 把讀寫分開：`read().await` 多讀、`write().await` 一寫
- `Notify` 是不帶資料的喚醒工具，搭配自己管理的共享狀態用，不是 queue（多次通知可能合併）；對比 `watch`：`Notify` 無狀態（戳你去看），`watch` 有狀態（帶最新值）
