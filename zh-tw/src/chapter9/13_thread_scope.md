# `thread::scope` 簡介

## 本集目標

學會用 `thread::scope` 建立有限生命週期的執行緒，不需要 `move` 或 `Arc` 就能借用外部資料。

## 概念說明

### `thread::spawn` 的限制

前面用 `thread::spawn` 的時候，閉包裡要用外面的變數都得 `move` 進去，或用 `Arc` 包起來。這是因為 `spawn` 出來的執行緒可能活得比呼叫它的函數還久——Rust 沒辦法保證資料在執行緒結束前不會被丟掉。

### 為什麼 `spawn` 不能借用

第 3 集看過 `thread::spawn` 的型別簽名，閉包和回傳值都要求 `'static`——必須活得跟整個程式一樣久。這就是為什麼你不能借用局部變數：局部變數不是 `'static` 的。

### `thread::scope`

`thread::scope` 解決了這個問題。它保證裡面 `spawn` 的所有執行緒在 `scope` 結束前都會被 `join`：

```rust,editable
use std::thread;

fn main() {
    let data = vec![1, 2, 3, 4, 5];

    thread::scope(|s| {
        s.spawn(|| {
            println!("子執行緒：{:?}", data); // 直接借用，不需要 move
        });
    }); // 所有 scoped thread 在這裡保證已經結束

    // data 還能用
    println!("主執行緒：{:?}", data);
}
```

因為 `scope` 保證所有執行緒在 `}` 之前都跑完了，所以 `data` 不可能被提前丟掉——閉包可以安全地借用它，不需要 `move` 也不需要 `Arc`。

### 對比 `spawn` + `Arc` 的寫法

同一件事，用 `thread::spawn` 要這樣寫：

```rust,editable
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3, 4, 5]);
    let data_clone = Arc::clone(&data);

    let handle = thread::spawn(move || {
        println!("{:?}", data_clone);
    });

    handle.join().expect("執行緒發生錯誤");
 }
```

用 `thread::scope` 簡潔很多：

```rust,editable
use std::thread;

fn main() {
    let data = vec![1, 2, 3, 4, 5];

    thread::scope(|s| {
        s.spawn(|| {
            println!("{:?}", data);
        });
    });
}
```

不需要 `Arc`、不需要 `clone`、不需要 `move`、不需要手動 `join`。

## 範例程式碼

```rust,editable
use std::thread;

fn main() {
    let mut results = vec![];
    let input = vec![1, 2, 3, 4, 5];

    thread::scope(|s| {
        // 多個執行緒同時借用 input（不可變借用）
        let h1 = s.spawn(|| {
            let sum: i32 = input.iter().sum();
            sum
        });

        let h2 = s.spawn(|| {
            let max = input.iter().max().expect("空的 input");
            *max
        });

        let h3 = s.spawn(|| {
            let min = input.iter().min().expect("空的 input");
            *min
        });

        // scope 裡面也可以 join 拿回傳值
        results.push(h1.join().expect("執行緒發生錯誤"));
        results.push(h2.join().expect("執行緒發生錯誤"));
        results.push(h3.join().expect("執行緒發生錯誤"));
    });

    println!("input 還能用：{:?}", input);
    println!("總和 = {}, 最大 = {}, 最小 = {}", results[0], results[1], results[2]);
}
```

## 重點整理

- `thread::spawn` 要求 `'static`，所以閉包不能借用局部變數
- `thread::scope` 保證所有 scoped thread 在 `scope` 結束前 `join`，因此可以安全借用外部資料
- 不需要 `move`、不需要 `Arc`、不需要手動 `join`——程式碼簡潔很多
- 當你只需要在一個區域內使用多執行緒，`thread::scope` 比 `thread::spawn` 方便

恭喜你完成了多執行緒這一章！🎉 這一章從指標的底層概念出發，一路學到了執行緒、`Send` / `Sync`、`Arc`、`Mutex`、`RwLock`、poisoning、channel 和 `thread::scope`。多執行緒程式設計在很多語言裡是讓人頭痛的領域，但 Rust 的型別系統在編譯期就幫你擋住了資料競爭——你不需要靠經驗和直覺來避免 bug，編譯器就是你最好的隊友。下一章我們將進入進階語言功能！
