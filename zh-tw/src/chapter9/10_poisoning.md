# poisoning

## 本集目標

理解什麼是鎖的中毒（poisoning），以及該怎麼處理它。

## 概念說明

### `.lock()` 為什麼回傳 `Result`

前面幾集學 `Mutex` 和 `RwLock` 的時候，我們都寫 `.lock().expect("取得鎖失敗")`。但什麼時候取鎖會「失敗」？答案就是 **poisoning**。

### 什麼是 poisoning

如果一個執行緒在持有鎖的期間 panic 了，鎖會被標記為「中毒」（poisoned）。之後任何執行緒再嘗試取鎖，不管是 `lock`、`read` 還是 `write`，都會收到 `Err(PoisonError)`。

```rust,editable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let data = Arc::new(Mutex::new(vec![1, 2, 3]));
    let data2 = Arc::clone(&data);

    let handle = thread::spawn(move || {
        let mut guard = data2.lock().expect("取得鎖失敗");
        guard.push(4);
        panic!("哎呀！"); // panic 的時候 guard 還活著 → 鎖中毒
    });

    let _ = handle.join(); // 收集 panic，不讓它傳播

    // 之後再 lock → Err
    match data.lock() {
        Ok(guard) => println!("正常：{:?}", *guard),
        Err(poisoned) => println!("鎖中毒了！"),
    }
}
```

### 為什麼要有 poisoning

panic 通常代表程式出了預期外的錯誤。如果一個執行緒在修改資料修到一半就 panic 了，資料可能是半成品——比如 `Vec` `push` 了一半、或某兩個欄位只更新了一個。poisoning 是一個安全機制：讓你知道出事了，由你決定要不要繼續用。

### 三種處理方式

**1. 直接 panic（最常見）**

```rust,noplayground
use std::sync::Mutex;

fn main() {
    let data = Mutex::new(Vec::<i32>::new());
    let guard = data.lock().expect("取得鎖失敗");
}
```

如果鎖中毒了，你的執行緒也跟著 panic。大部分情況這樣就好——上一個執行緒 panic 了，通常代表整個程式該結束了。

**2. 忽略中毒，繼續用**

```rust,noplayground
use std::sync::{Mutex, PoisonError};

fn main() {
    let data = Mutex::new(Vec::<i32>::new());
    let guard = data.lock().unwrap_or_else(PoisonError::into_inner);
}
```

`PoisonError::into_inner` 讓你拿回 guard，跳過中毒的警告。如果你確定資料的狀態沒問題，或者你不在意，可以這樣做。

**3. 修復資料再繼續**

```rust,noplayground
use std::sync::{Mutex, PoisonError};

fn main() {
    let data = Mutex::new(Vec::<i32>::new());
    let guard = match data.lock() {
        Ok(g) => g,
        Err(poisoned) => {
            let mut g = poisoned.into_inner();
            *g = vec![]; // 重設成已知的安全狀態
            g
        }
    };
}
```

拿到 guard 之後把資料修復成合理的值，然後繼續用。

### 為什麼 `.into_inner()` 是安全的

你可能會好奇：中毒的鎖裡面的資料可能是半成品，存取它真的沒問題嗎？

從記憶體的角度來看是沒問題的。不管鎖有沒有中毒，裡面的資料都是合法的記憶體——不會存取到已經不能使用的記憶體、不會把型別搞混、沒有資料競爭。poisoning 保護的是**邏輯一致性**，不是**記憶體安全**。資料可能邏輯上不對，但從記憶體的角度看完全合法。所以可以安全地呼叫 `.into_inner()`。

### `RwLock` 的 poisoning

`RwLock` 的 poisoning 只在**寫鎖** panic 的時候觸發。讀鎖 panic 不會中毒——因為讀的時候不會修改資料，不會留下不一致的狀態。但一旦中毒了，`read` 和 `write` 都會回傳 `Err`。

## 範例程式碼

```rust,editable
use std::sync::{Arc, Mutex, PoisonError};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));

    // 啟動一個會 panic 的執行緒
    let counter2 = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut guard = counter2.lock().expect("取得鎖失敗");
        *guard += 1;
        panic!("糟糕，出事了！");
    });

    // 等待那個執行緒結束（那個執行緒會 panic，但我們用 let _ 忽略）
    let _ = handle.join();

    // 嘗試取鎖——會收到 PoisonError
    match counter.lock() {
        Ok(guard) => {
            println!("正常取得鎖，值 = {}", *guard);
        }
        Err(poisoned) => {
            println!("鎖中毒了！");

            // 拿到資料看看
            let guard = poisoned.into_inner();
            println!("裡面的值 = {}", *guard);
        }
    }

    // 或者用一行忽略中毒
    let guard = counter.lock().unwrap_or_else(PoisonError::into_inner);
    println!("忽略中毒，值 = {}", *guard);
}
```

## 重點整理

- 持有鎖的執行緒 panic 了 → 鎖中毒（poisoned）
- 之後 `lock` / `read` / `write` 都回傳 `Err(PoisonError)`
- `RwLock` 只有寫鎖 panic 才會中毒，讀鎖 panic 不會
- `PoisonError::into_inner` 可以拿回 guard——記憶體安全沒問題，只是邏輯一致性的問題
- 三種處理方式：
  - panic（`.unwrap()` 或 `.expect()`）
  - 忽略（`.unwrap_or_else(PoisonError::into_inner)`）
  - 修復資料再繼續