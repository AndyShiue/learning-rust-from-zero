# 第八章第 11 集：mpsc

## 本集目標
學會用 channel 讓執行緒之間透過傳訊息溝通，以及和共享記憶體方式的比較。

## 概念說明

### 另一種思路

前面的 Mutex 和 RwLock 是「共享記憶體」的思路——多個執行緒存取同一份資料，用鎖來避免衝突。

channel 是完全不同的思路：**執行緒之間用傳訊息的方式溝通**。資料直接送過去，不共享。

### 建立 channel

`std::sync::mpsc::channel()` 建立一對發送端（tx）和接收端（rx）：

```rust
use std::sync::mpsc;

let (tx, rx) = mpsc::channel();
```

`mpsc` 代表 **multiple producer, single consumer**——可以有多個發送端，但接收端只有一個。

### 發送和接收

`tx.send(value)` 把值送出去（value 會被 move），`rx.recv()` 在另一端接收（會阻塞直到收到）：

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();

thread::spawn(move || {
    tx.send(String::from("hello")).expect("發送失敗");
});

let received = rx.recv().expect("接收失敗");
println!("收到：{}", received);
```

### 多個發送端

用 `tx.clone()` 產生新的發送端：

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();

for i in 0..3 {
    let tx = tx.clone();
    thread::spawn(move || {
        tx.send(format!("來自執行緒 {}", i)).expect("發送失敗");
    });
}

drop(tx); // 原始的 tx 也要 drop，不然 rx 永遠不會結束

for received in rx {
    println!("收到：{}", received);
}
```

### 什麼時候結束

所有 tx 都被 drop 之後，`rx.recv()` 會先把還沒收的訊息全部收完，收完之後再呼叫 `recv()` 才會回傳 `Err`。用 `for msg in rx` 迴圈也一樣——先把剩餘的訊息全部跑完，然後才結束。這是判斷「沒有人會再發送了，而且所有訊息都已經處理完了」的方式。

注意上面的例子裡的 `drop(tx)`——如果你 clone 了 tx 但沒有 drop 原始的 tx，接收端會認為還有發送端存活，永遠不會結束。

### channel vs 共享記憶體

什麼時候用哪個？

- **多個執行緒需要反覆讀寫同一份資料**（例如共用的計數器、共用的快取）→ Mutex / RwLock 比較直接
- **一邊產生資料、一邊消費資料**的流水線關係 → channel 更自然。資料的所有權直接轉移，不需要鎖，也不存在忘了放鎖的問題

## 範例程式碼

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    // 啟動 3 個 worker，各自做一些計算後把結果送回來
    for i in 0..3 {
        let tx = tx.clone();
        thread::spawn(move || {
            let result = i * i;
            println!("執行緒 {} 計算完成：{}", i, result);
            tx.send((i, result)).expect("發送失敗");
        });
    }

    // drop 原始的 tx，這樣當所有 clone 都完成後，rx 迴圈會結束
    drop(tx);

    // 接收所有結果
    let mut total = 0;
    for (id, result) in rx {
        println!("主執行緒收到：執行緒 {} 的結果是 {}", id, result);
        total += result;
    }

    println!("所有結果的總和：{}", total);
}
```

## 重點整理
- channel 讓執行緒之間用傳訊息溝通，資料直接送過去，不共享
- `mpsc::channel()` 建立發送端 tx 和接收端 rx
- `tx.send(value)` 會 move value，`rx.recv()` 阻塞直到收到
- `tx.clone()` 產生多個發送端，但接收端只有一個（mpsc）
- 所有 tx 都 drop 之後，rx 的迴圈自動結束
- 流水線關係用 channel，反覆讀寫同一份資料用 Mutex / RwLock
