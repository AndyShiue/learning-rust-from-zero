# 第八章第 7 集：atomic 型別

## 本集目標
學會用 atomic 型別在多個執行緒之間安全地讀寫簡單的值。

## 概念說明

### 什麼是 atomic 操作

上一集學了 Arc，它的引用計數用的是 atomic 操作。到底什麼是 atomic？

假設兩個執行緒同時對一個變數做 `count += 1`。這看起來是一步，但實際上分成三步：讀出目前的值、加 1、寫回去。如果兩個執行緒同時做這三步，可能會發生這樣的事：

1. 執行緒 A 讀出 count = 0
2. 執行緒 B 讀出 count = 0
3. 執行緒 A 寫入 count = 1
4. 執行緒 B 寫入 count = 1

兩邊各加了一次，結果卻是 1 而不是 2。

**atomic 操作**把讀、改、寫合成一個不可分割的動作——其他執行緒不可能看到做到一半的狀態。用 atomic 操作做 `count += 1`，兩個執行緒同時跑，結果一定是 2。

### AtomicI32 和 AtomicBool

標準庫在 `std::sync::atomic` 提供了幾種 atomic 型別，最常用的是整數和布林：

```rust
use std::sync::atomic::{AtomicI32, AtomicBool, Ordering};

let counter = AtomicI32::new(0);
let flag = AtomicBool::new(false);
```

### 基本操作

```rust
use std::sync::atomic::{AtomicI32, Ordering};

let counter = AtomicI32::new(0);

counter.store(10, Ordering::Relaxed);             // 寫入
let val = counter.load(Ordering::Relaxed);        // 讀取：10
let old = counter.fetch_add(5, Ordering::Relaxed); // 加 5，回傳舊值 10
// 現在 counter 是 15
```

每個操作都要傳一個 `Ordering` 參數。為什麼需要這個？

現代處理器為了效能，可能會**重新排列指令的執行順序**。在單執行緒下這不會造成問題——處理器保證結果跟按順序執行一樣。但在多執行緒下，一個執行緒裡的指令重排，可能讓另一個執行緒看到不一致的狀態。

`Ordering` 就是告訴處理器「這個操作前後的指令不能隨便重排」，一般來說，限制越嚴格，效能代價越高。

舉個例子：假設執行緒 A 把資料寫進一個 Vec，然後把一個 atomic 旗標設成 `true`；執行緒 B 看到旗標是 `true` 就去讀那個 Vec：

```rust
// 執行緒 A
data.push(42);                          // 第 1 步：寫入資料
ready.store(true, Ordering::Relaxed);   // 第 2 步：設旗標

// 執行緒 B
if ready.load(Ordering::Relaxed) {      // 看到 true
    println!("{}", data[0]);            // 但資料可能還沒寫進去！
}
```

用 `Relaxed` 的話，處理器可能把執行緒 A 的第 1 步和第 2 步重排——執行緒 B 看到旗標已經是 `true`，但資料還沒寫進去。處理器之所以敢重排，是因為從執行緒 A 自己的角度來看，先設旗標再寫資料和先寫資料再設旗標結果完全一樣——它不知道還有另一個執行緒在看。用 `SeqCst` 就不會有這個問題，它保證所有執行緒看到的操作順序一致。

細節很複雜，初學的話可以先記住兩個：

- `Ordering::Relaxed`：只保證這個 atomic 操作本身是正確的，不限制其他指令的順序。適合單純的計數器
- `Ordering::SeqCst`：最嚴格，所有執行緒看到的操作順序都一致

不確定的時候用 `SeqCst` 最安全。

### Interior mutability

注意看上面的程式碼——`store` 和 `fetch_add` 明明在修改值，卻不需要 `&mut self`，只要 `&self` 就行。這跟第五章學的 Cell 一樣，是 interior mutability。

為什麼一定要這樣設計？因為如果要 `&mut self` 才能修改，那就只有一個執行緒能拿到 `&mut`，其他執行緒根本碰不到這個值——那還跨什麼執行緒？Atomic 的重點就是讓多個執行緒透過 `&` 同時存取同一個值，所以必須是 interior mutability。

Cell 也是 interior mutability，但 Cell 不是 Sync（不能跨執行緒共享）。Atomic 是 Sync——因為底層硬體保證了操作的原子性，多個執行緒同時透過 `&` 修改也不會出問題。

### 搭配 Arc 使用

Atomic 最常見的用法就是搭配 Arc，讓多個執行緒共同修改一個計數器：

```rust
use std::sync::Arc;
use std::sync::atomic::{AtomicI32, Ordering};
use std::thread;

let counter = Arc::new(AtomicI32::new(0));

let mut handles = vec![];

for _ in 0..10 {
    let counter_clone = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        for _ in 0..1000 {
            counter_clone.fetch_add(1, Ordering::Relaxed);
        }
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().expect("執行緒發生錯誤");
}

println!("最終結果：{}", counter.load(Ordering::Relaxed)); // 一定是 10000
```

10 個執行緒各加 1000 次，結果一定是 10000——不會少算。

### atomic 型別 vs 鎖

atomic 操作只能用在簡單的型別——例如整數（`AtomicI32`、`AtomicU64`、`AtomicUsize` 等）和布林（`AtomicBool`）。如果你要保護一個 `Vec`、`String` 或任何複雜的資料結構，atomic 型別做不到，需要用下一集教的鎖。

但對於簡單的計數器或旗標，atomic 操作比鎖快——每個執行緒都能直接操作，不需要排隊等別人用完。

## 範例程式碼

```rust
use std::sync::Arc;
use std::sync::atomic::{AtomicI32, Ordering};
use std::thread;

fn main() {
    let counter = Arc::new(AtomicI32::new(0));

    let mut handles = vec![];

    // 三個執行緒，每個加到不同的上限
    for limit in [100, 200, 300] {
        let counter_clone = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..limit {
                counter_clone.fetch_add(1, Ordering::Relaxed);
            }
            println!("加了 {} 次，目前值：{}", limit, counter_clone.load(Ordering::Relaxed));
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("執行緒發生錯誤");
    }

    // 100 + 200 + 300 = 600，不管執行順序如何
    println!("最終結果：{}", counter.load(Ordering::Relaxed));
}
```

## 重點整理
- atomic 操作把讀、改、寫合成一個不可分割的動作，多個執行緒同時做也不會出錯
- 常用型別：`AtomicI32`、`AtomicUsize`、`AtomicBool`
- 常用方法：`load`（讀）、`store`（寫）、`fetch_add`（加並回傳舊值）
- `Ordering` 控制記憶體排序，不確定就用 `SeqCst`
- Atomic 是 interior mutability——用 `&self` 就能修改，而且是 Sync（可以跨執行緒共享）
- 只能用在簡單型別，複雜資料需要用鎖