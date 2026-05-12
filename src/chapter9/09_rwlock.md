# `RwLock<T>`

## 本集目標

學會用 `RwLock<T>` 實現讀寫分離的鎖，以及和 `Mutex` 的比較。

## 概念說明

### `Mutex` 的限制

`Mutex` 不管你要讀還是要寫，都要鎖住。但很多時候多個執行緒只是要讀資料——讀和讀之間不會衝突，全部鎖住太浪費了。

### `RwLock`：讀寫分離

`RwLock<T>` 區分讀鎖和寫鎖：

- **讀鎖**（`read().expect(...)`）：多個執行緒可以**同時**持有讀鎖
- **寫鎖**（`write().expect(...)`）：寫鎖是獨佔的，持有寫鎖時不能有任何讀鎖或其他寫鎖

```rust
use std::sync::RwLock;

fn main() {
    let lock = RwLock::new(42);

    // 多個讀者可以同時讀
    {
        let r1 = lock.read().expect("取得讀鎖失敗");
        let r2 = lock.read().expect("取得讀鎖失敗"); // OK，可以同時持有多個讀鎖
        println!("r1 = {}, r2 = {}", *r1, *r2);
    }

    // 寫入時獨佔
    {
        let mut w = lock.write().expect("取得寫鎖失敗");
        *w += 1;
    }
}
```

### guard 的行為

讀鎖回傳 `RwLockReadGuard`，寫鎖回傳 `RwLockWriteGuard`。跟 `MutexGuard` 一樣，它們也是智慧指標——可以直接操作內容，`drop` 時自動放鎖。

一樣要注意 guard 不要活太久。

### 和 RefCell 的對照

|  | `RefCell` | `RwLock` |
|--|-----------|----------|
| 執行緒 | 單執行緒 | 多執行緒 |
| 規則 | 多個 `borrow()` 或一個 `borrow_mut()` | 多個 `read()` 或一個 `write()` |
| 檢查方式 | 執行期，違反會 panic | 作業系統的鎖，違反會阻塞等待 |

### `Mutex` vs `RwLock`

什麼時候用哪個？

- **`Mutex`**：簡單、開銷小。適合讀寫都頻繁，或鎖持有時間很短的場景。大部分情況下 `Mutex` 就夠了
- **`RwLock`**：在讀遠多於寫的時候有優勢，因為多個讀者可以同時進行。但鎖本身的開銷比 `Mutex` 大，而且有**寫者飢餓**（writer starvation）的風險——如果讀者一直源源不斷，寫者可能永遠拿不到鎖

## 範例程式碼

```rust
use std::sync::{Arc, RwLock};
use std::thread;

fn main() {
    let data = Arc::new(RwLock::new(vec![1, 2, 3]));

    let mut handles = vec![];

    // 啟動 3 個讀者
    for i in 0..3 {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            let read_guard = data.read().expect("取得讀鎖失敗");
            println!("讀者 {}：{:?}", i, *read_guard);
            // 多個讀者可以同時持有讀鎖
        });
        handles.push(handle);
    }

    // 啟動 1 個寫者
    {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            let mut write_guard = data.write().expect("取得寫鎖失敗");
            write_guard.push(4);
            println!("寫者：寫入完成，現在是 {:?}", *write_guard);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("執行緒發生錯誤");
    }

    println!("最終結果：{:?}", *data.read().expect("取得讀鎖失敗"));
}
```

## 重點整理

- `RwLock<T>` 區分讀鎖和寫鎖：多個讀者可以同時讀，寫者獨佔
- `read().expect(...)` 取得讀鎖，`write().expect(...)` 取得寫鎖
- guard 透過 `Deref` 操作內容，`drop` 時自動放鎖
- 和 `RefCell` 的對照：`RefCell` 是單執行緒版本，`RwLock` 是多執行緒版本
- `Mutex` 簡單、開銷小，大部分情況夠用；`RwLock` 適合讀遠多於寫的場景，但開銷較大且有寫者飢餓的風險
