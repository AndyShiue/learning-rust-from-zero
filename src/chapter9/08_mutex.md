# `Mutex<T>`

## 本集目標

學會用 `Mutex<T>` 讓多個執行緒安全地修改共享資料。

## 概念說明

### 想修改複雜的共享資料怎麼辦？

上一集學了 atomic，但它只能用在整數和布林等簡單型別。如果你想讓多個執行緒修改一個 `Vec`、`String` 或任何複雜的資料結構呢？

### `Mutex`：多執行緒版的 interior mutability

`Mutex<T>` 和 `RefCell` 有些像——都提供一種 interior mutability，讓你在不需要 `&mut` 的情況下修改值。差別在於：

- **`RefCell`**：單執行緒，用普通整數做借用檢查
- **`Mutex`**：多執行緒，用作業系統的鎖（lock）保護資料

### `lock` 和 `MutexGuard`

用 `mutex.lock().expect("取得鎖失敗")` 取得鎖。它會回傳一個 `MutexGuard`：

```rust,editable
use std::sync::Mutex;

fn main() {
    let m = Mutex::new(42);
    {
        let mut guard = m.lock().expect("取得鎖失敗");
        *guard += 1; // 透過 guard 修改值
        println!("{}", *guard); // 43
    } // guard 被 drop，自動解鎖
}
```

`MutexGuard` 實作了 `Deref` 和 `DerefMut`（第 5 章學的），所以它也是一種智慧指標——你可以直接把它當 `&T` 或 `&mut T` 使用。

同一時間只有一個執行緒能 `lock` 成功。其他執行緒呼叫 `.lock()` 時會**阻塞**（等待），直到持有鎖的執行緒把 guard `drop` 掉。

### `Arc` + `Mutex`

實際上多半是這樣搭配使用——`Arc` 負責讓多個執行緒共享 `Mutex`，`Mutex` 負責保護裡面的資料：

```rust,editable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().expect("取得鎖失敗");
            *num += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("執行緒發生錯誤");
    }

    println!("結果：{}", *counter.lock().expect("取得鎖失敗")); // 10
}
```

### `MutexGuard` 不要活太久

guard 活著的期間，鎖都不會放開，其他執行緒全部在等。所以盡量縮短 guard 的生命週期：

```rust,ignore
// 不好：guard 活到作用域結束，鎖持有太久
let mut guard = mutex.lock().expect("取得鎖失敗");
*guard += 1;
// ... 做了很多不需要鎖的事情 ...
// guard 到後面才被 drop

// 好：用完就放
{
    let mut guard = mutex.lock().expect("取得鎖失敗");
    *guard += 1;
} // guard 立刻被 drop，鎖立刻釋放
// ... 做其他事情 ...
```

### `Mutex` 把 `Send` 變成 `Sync`

第 3 集學了 `Send` 和 `Sync`。有些型別是 `Send` 但不是 `Sync`——例如第 4 集講的 `RefCell<T>`，它能安全地被 move 到另一個執行緒（`Send`），但不能讓多個執行緒同時透過 `&RefCell<T>` 存取（不是 `Sync`）。

`Mutex` 能解決這個問題。`Mutex<T>` 保證同一時間只有一個執行緒能存取 `T`——即使多個執行緒共享同一個 `&Mutex<T>`，也只有拿到鎖的那一個能操作裡面的 `T`。所以 `Mutex<T>` 只要求 `T: Send`，就能讓 `Mutex<T>` 本身成為 `Sync`。

換句話說：`T` 不是 `Sync` 沒關係，`Mutex` 的鎖機制已經確保不會有同時存取的問題。`T` 需要 `Send` 是因為：當執行緒 A 拿到鎖、操作完 `T`、放鎖之後，下一個拿到鎖的可能是執行緒 B。從 `T` 的角度來看，它原本被 A 獨佔使用，現在換成被 B 獨佔使用——效果等同於 `T` 從 A 被「送」到了 B。所以 `T` 必須是 `Send`。

## 範例程式碼

```rust,editable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            // 縮小 guard 的作用域
            {
                let mut num = counter.lock().expect("取得鎖失敗");
                *num += 1;
                println!("執行緒 {} 把計數器改成 {}", i, *num);
            } // guard 在這裡就被 drop 了

            // 這裡已經不持有鎖了
            println!("執行緒 {} 做完了", i);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("執行緒發生錯誤");
    }

    println!("最終結果：{}", *counter.lock().expect("取得鎖失敗"));
}
```

## 重點整理

- `Mutex<T>` 是多執行緒版的 interior mutability，用鎖保護資料
- `lock().expect(...)` 回傳 `MutexGuard`，透過 `DerefMut` 直接當 `&mut T` 用
- 同一時間只有一個執行緒能持有鎖，其他執行緒會等待
- guard 被 `drop` 時自動解鎖
- 常見搭配：`Arc<Mutex<T>>`——`Arc` 負責共享，`Mutex` 負責安全修改
- `MutexGuard` 不要活太久，鎖住的期間其他執行緒全部在等
- `Mutex<T>` 只要求 `T: Send` 就能是 `Sync`——`Mutex` 的鎖機制讓不是 `Sync` 的型別也能安全地被多個執行緒共享
