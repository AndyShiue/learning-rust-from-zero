# `async` 的 `Mutex`、`RwLock` 與 `Notify`

## 本集目標

學會 async 版的共享狀態保護工具,搞懂「什麼時候該用 tokio 的鎖、什麼時候用標準庫的」,以及為什麼鎖不能抓著 `.await`。

## 概念說明

### 有時候 message passing 不夠用

前面兩集都在傳訊息(channel)。但有些情況,幾個 task 就是需要**共用同一份會變動的資料**——例如一個共享的計數器、一份大家都要讀寫的快取。這時候回到第 8 章的老朋友:`Mutex`、`RwLock`。tokio 提供了它們的 async 版本。

```rust,ignore
use std::sync::Arc;
use tokio::sync::Mutex;

#[tokio::main]
async fn main() {
    let counter = Arc::new(Mutex::new(0));

    let mut handles = Vec::new();
    for _ in 0..10 {
        let c = counter.clone();
        handles.push(tokio::spawn(async move {
            let mut guard = c.lock().await; // 注意:async 版是 .lock().await
            *guard += 1;
        }));
    }
    for h in handles { h.await.unwrap(); }

    println!("總共 {}", *counter.lock().await); // 10
}
```

和第 8 章的差別主要是 `lock()` 後面要 `.await`——因為鎖被別人佔著時,tokio 的鎖會讓出執行緒去做別的,而不是卡住整條執行緒。`RwLock`(`read().await` / `write().await`)概念也一樣,沿用第 8 章的「多讀或一寫」規則。

### tokio 的鎖 vs 標準庫的鎖:該用哪個?

這裡有個常見困惑:`std::sync::Mutex` 和 `tokio::sync::Mutex` 都在,到底用哪個?判準其實很簡單:

> **你需要「**抓著鎖的同時去 `.await`**」嗎?需要 → 用 tokio 的鎖;不需要 → 用標準庫的鎖。**

大多數時候你只是「鎖起來、改個值、馬上解鎖」,中間沒有任何 `.await`。這種情況**標準庫的 `std::sync::Mutex` 反而更好**——它更快,而且鎖的範圍很短,不會卡住執行緒多久。只有當你確實需要「持有鎖期間還要 `.await` 別的事情」時,才需要 tokio 的 async 鎖。

### 為什麼抓著標準庫的鎖去 `.await` 會出事

這直接呼應第 21 集那個「非 `Send` 的東西跨 `.await`」的坑。`std::sync::Mutex` 的 `MutexGuard`(鎖起來拿到的那個守衛)**不是 `Send`**。所以如果你抓著它跨過一個 `.await`:

```rust,ignore
use std::sync::Mutex; // 注意這是「標準庫」的 Mutex

async fn bad(data: &Mutex<i32>) {
    let mut guard = data.lock().unwrap();
    *guard += 1;
    some_async_work().await; // 抓著 std 的 guard 跨過 .await —— guard 會被存進狀態機
    // → future 變成 !Send → 不能 tokio::spawn,編譯失敗
}
# async fn some_async_work() {}
```

`guard` 跨越 `.await` 就被存進狀態機欄位,而它不是 `Send`,於是整個 future 不是 `Send`,`tokio::spawn` 就編譯失敗。

這其實是個**有益的**錯誤——它在提醒你一件危險的事:抓著鎖去 `.await`,意味著你在「等某件可能很久的事」的整段時間裡,**鎖都不放開**,其他想拿這個鎖的 task 全都被你卡住。這幾乎一定是 bug。

解法分兩種:

- 大多數時候——**在 `.await` 之前就把鎖放掉**(用 `{}` 限制 guard 的範圍,或在 await 前 `drop(guard)`)。鎖只應該在「真正改資料」的瞬間握著。
- 真的需要「持鎖期間 `.await`」——這時才換成 `tokio::sync::Mutex`,它的 guard 是 `Send` 的,專為這種情況設計。

不論用哪種鎖,原則都一樣:**鎖的範圍要短,絕對不要抓著鎖去等 I/O。**

### `Notify`:只負責「叫醒」,不傳資料

最後介紹一個小而美的工具 `Notify`。它是一個**不帶任何資料**的喚醒原語——就是純粹「拍一下肩膀說『欸,有狀況了,你去看看』」。一邊 `notified().await` 等通知,另一邊 `notify_one()` 發通知。

```rust,ignore
use std::sync::Arc;
use tokio::sync::Notify;

#[tokio::main]
async fn main() {
    let notify = Arc::new(Notify::new());

    let n = notify.clone();
    tokio::spawn(async move {
        n.notified().await; // 等通知
        println!("收到通知,該幹活了");
    });

    notify.notify_one(); // 拍一下肩膀
    tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
}
```

`Notify` 適合搭配共享狀態使用:資料放在 `Mutex` 裡,改動之後用 `Notify` 通知別人「資料變了,來看」。但要記住兩個提醒——它**不是佇列**:如果在沒人等待的時候連續通知好幾次,這些通知**可能被合併成一次**,不會排隊累積。所以它只適合「有事了,去檢查一下狀態」,而不適合用來精確地數「發生了幾次」。要傳資料或精確計數,還是用 channel。

## 範例程式碼

最常見的實戰組合:`Arc<Mutex<T>>`——`Arc` 負責讓多個 task 共享(第 8 章),`Mutex` 負責安全修改。這裡用標準庫的 `Mutex`,因為鎖的範圍裡沒有 `.await`:

```rust,ignore
use std::sync::{Arc, Mutex};

#[tokio::main]
async fn main() {
    let cache = Arc::new(Mutex::new(Vec::<String>::new()));

    let mut handles = Vec::new();
    for i in 0..5 {
        let cache = cache.clone();
        handles.push(tokio::spawn(async move {
            // 鎖的範圍只包住「改資料」這一下,裡面沒有任何 .await
            let mut v = cache.lock().unwrap();
            v.push(format!("項目 {}", i));
        })); // guard 在這裡就 drop,鎖馬上放開
    }
    for h in handles { h.await.unwrap(); }

    println!("{:?}", cache.lock().unwrap());
}
```

## 重點整理

- 當 task 需要共用一份會變動的資料(而非傳訊息),用 `Mutex`／`RwLock` 保護;tokio 有 async 版(`.lock().await`)
- 選哪種鎖:**需要持鎖期間 `.await` → 用 `tokio` 的鎖;否則用更快的 `std::sync` 鎖**(大多數情況)
- `std::sync::MutexGuard` 不是 `Send`,**抓著它跨 `.await` 會讓 future 變 `!Send`、`spawn` 失敗**——這是個有益的警告
- 不論哪種鎖,**範圍要短,絕不要抓著鎖去等 I/O**;`.await` 前先 `drop` 掉 guard(用 `{}` 限制範圍)
- `Notify` 是不帶資料的純喚醒原語,適合搭配共享狀態用;它**不是佇列**,多次通知可能被合併
