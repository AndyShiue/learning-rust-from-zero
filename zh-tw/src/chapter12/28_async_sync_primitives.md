# `async` 的 `Mutex`、`RwLock` 與 `Notify`

## 本集目標

從第 8 章的 `Send`／`Sync` 開門見山:大部分型別只要是 `Sync`、通常也是 `Send`,而 `Mutex`／`RwLock` 的 guard 正是少數例外(`Sync` 但 `!Send`)。由此切入 tokio 的 `Mutex`／`RwLock`,搞懂「何時用 tokio 鎖、何時用 std 鎖」,以及為什麼不能抓著鎖去 `.await`。

## 概念說明

### 開門見山：guard 是「`Sync` 但不 `Send`」的例外

先接回第 8 章的 `Send`／`Sync`。那時可以歸納出一條經驗：**你日常碰到的型別，只要是 `Sync`（能多執行緒共享），幾乎也都是 `Send`（能搬到別條執行緒）。** 但有一組著名的例外：**`Mutex` / `RwLock` 鎖起來拿到的那個 guard——`MutexGuard`、`RwLockReadGuard`、`RwLockWriteGuard`——是 `Sync`，卻 `!Send`。**

為什麼 guard 不能 `Send`？因為在某些平台上，鎖**必須由當初鎖它的那條執行緒來解鎖**。如果你把 guard 搬到另一條執行緒、在那邊 drop（＝解鎖），就是從錯誤的執行緒解鎖 → UB。所以標準庫乾脆讓 guard `!Send`，從型別上擋掉「把鎖中的 guard 搬到別條 thread」這件事。

把這條記著——它等下會直接決定 async 裡一個大坑（抓著鎖跨 `.await`）。我們先從 tokio 的鎖講起。

### 用 tokio 的 `Mutex` 保護共享狀態

有些情況，幾個 task 就是需要**共用同一份會變動的資料**——一個共享計數器、一份大家都讀寫的快取。這時用第 8 章的老朋友 `Mutex`／`RwLock`；tokio 提供了它們的 **async 版**（而且 guard 是 `Send`，所以**可以**抓著跨 `.await`——這正是它和 std 版的關鍵差別）。

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

和第 8 章的差別主要是 `lock()` 後面要 `.await`——因為鎖被別人佔著時,tokio 的鎖會讓出執行緒去做別的,而不是卡住整條執行緒。

### `RwLock`:多讀或一寫

`RwLock` 和 `Mutex` 都是保護共享資料,差別在它把「讀」和「寫」分開:**可以同時很多個讀者,或同時只有一個寫者**(沿用第 8 章的「多讀或一寫」規則)。適合「**讀遠多於寫**」的資料——例如一份大家都在讀、偶爾才更新的設定或快取。tokio 的 async 版是 `read().await`(共享讀鎖)/ `write().await`(獨佔寫鎖):

```rust,ignore
use std::sync::Arc;
use tokio::sync::RwLock;

#[tokio::main]
async fn main() {
    let config = Arc::new(RwLock::new(String::from("v1")));

    // 很多個讀者可以同時進來
    let r1 = config.clone();
    tokio::spawn(async move {
        let cfg = r1.read().await; // 共享讀鎖：可以和其他讀者並存
        println!("讀到 {}", *cfg);
    });

    // 寫者要獨佔
    {
        let mut cfg = config.write().await; // 獨佔寫鎖：擋掉所有讀者和其他寫者
        *cfg = String::from("v2");
    } // 寫鎖在這裡放開

    println!("現在是 {}", *config.read().await);
}
```

什麼時候用 `RwLock` 而不是 `Mutex`?**只有在「讀遠多於寫、而且讀本身值得讓多個讀者並行」**時才划算。如果讀寫差不多、或臨界區很短,`Mutex` 通常更簡單也更快(`RwLock` 要多記「現在有幾個讀者」,記帳成本較高)。

而且和 `Mutex` 一模一樣的判準照樣適用:**需不需要「持鎖期間 `.await`」**——需要才用 tokio 的 `RwLock`,不需要就用更快的 `std::sync::RwLock`;後者的 read/write guard 也**不是 `Send`**,抓著它跨 `.await` 一樣會讓 future 變 `!Send`(下面就講這個坑)。

### tokio 的鎖 vs 標準庫的鎖:該用哪個?

這裡有個常見困惑:`std::sync::Mutex` 和 `tokio::sync::Mutex` 都在,到底用哪個?判準其實很簡單:

> **你需要「**抓著鎖的同時去 `.await`**」嗎?需要 → 用 tokio 的鎖;不需要 → 用標準庫的鎖。**

大多數時候你只是「鎖起來、改個值、馬上解鎖」,中間沒有任何 `.await`。這種情況**標準庫的 `std::sync::Mutex` 反而更好**——它更快,而且鎖的範圍很短,不會卡住執行緒多久。只有當你確實需要「持有鎖期間還要 `.await` 別的事情」時,才需要 tokio 的 async 鎖。

### 為什麼抓著標準庫的鎖去 `.await` 會出事

這直接呼應第 21 集那個「非 `Send` 的東西跨 `.await`」的坑——而且坑的主角，就是**開頭講的那個例外**:`std::sync::Mutex` 的 `MutexGuard` 是 `Sync` 但 `!Send`。所以如果你抓著它跨過一個 `.await`:

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

`Notify` 適合搭配共享狀態使用:資料放在 `Mutex` 裡,改動之後用 `Notify` 通知別人「資料變了,來看」。但要記住——它**不是佇列**:如果在沒人等待的時候連續通知好幾次,這些通知**可能被合併成一次**,不會排隊累積。所以它只適合「有事了,去檢查一下狀態」,而不適合用來精確地數「發生了幾次」。要傳資料或精確計數,還是用 channel。

順帶釐清它和第 27 集 `watch` 的差別(很容易混):**`Notify` 不帶資料、無狀態;`watch` 帶一個「最新值」、有狀態。** `Notify` 是「我改了那份(放在你自己 `Mutex` 裡的)資料,戳你去看」;`watch` 則是那個要廣播的東西**本身就是一個值**(設定、狀態、shutdown 旗標),它幫你保存最新值、變動時通知,而且**晚來的訂閱者一 `borrow()` 就能讀到當下值**——這點 `Notify` 做不到(它沒存狀態)。一句話:`watch` ≈ 只保留最新一格的廣播 channel,`Notify` ≈ 無資料版的 wake。

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

- 大部分型別只要是 `Sync` 通常也是 `Send`，但 `Mutex`／`RwLock` 的 guard 是少數例外（`Sync` 但 `!Send`，因為鎖得由原執行緒解鎖）——這正是「抓著鎖跨 `.await`」會出事的根源
- 當 task 需要共用一份會變動的資料(而非傳訊息),用 `Mutex`／`RwLock` 保護;tokio 有 async 版(`.lock().await`，guard 是 `Send`)
- `RwLock`：把讀寫分開——**同時多讀，或同時一寫**(`read().await` / `write().await`)；只在「讀遠多於寫」時比 `Mutex` 划算，否則 `Mutex` 更簡單更快
- 選哪種鎖:**需要持鎖期間 `.await` → 用 `tokio` 的鎖;否則用更快的 `std::sync` 鎖**(大多數情況)
- `std::sync::MutexGuard` 不是 `Send`,**抓著它跨 `.await` 會讓 future 變 `!Send`、`spawn` 失敗**——這是個有益的警告
- 不論哪種鎖,**範圍要短,絕不要抓著鎖去等 I/O**;`.await` 前先 `drop` 掉 guard(用 `{}` 限制範圍)
- `Notify` 是不帶資料的純喚醒原語,適合搭配共享狀態用;它**不是佇列**,多次通知可能被合併
- `Notify` vs `watch`：`Notify` 不帶資料、無狀態（狀態自己管）；`watch` 帶「最新值」、有狀態，晚來的訂閱者能立刻讀到當下值——`watch` ≈ 只留最新一格的廣播 channel，`Notify` ≈ 無資料版的 wake
