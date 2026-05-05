# 死鎖

## 本集目標
理解死鎖是什麼、為什麼 Rust 的編譯器擋不住它、以及如何避免。

## 概念說明

### 什麼是死鎖

死鎖（deadlock）就是兩個或多個執行緒互相等待對方放鎖，結果誰都動不了，程式永遠卡住。

最經典的情況：執行緒 A 拿著鎖 1 等鎖 2，執行緒 B 拿著鎖 2 等鎖 1。兩邊永遠等下去。

### 程式碼示範

```rust,ignore,mdbook-runnable
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let lock1 = Arc::new(Mutex::new(0));
    let lock2 = Arc::new(Mutex::new(0));

    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);

    let a = thread::spawn(move || {
        let _g1 = l1.lock().expect("取得鎖失敗"); // 拿到鎖 1
        // 假設這裡有一些延遲...
        let _g2 = l2.lock().expect("取得鎖失敗"); // 等待鎖 2
    });

    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);

    let b = thread::spawn(move || {
        let _g2 = l2.lock().expect("取得鎖失敗"); // 拿到鎖 2
        // 假設這裡有一些延遲...
        let _g1 = l1.lock().expect("取得鎖失敗"); // 等待鎖 1
    });

    // 如果時機剛好，程式會永遠卡在這裡
    a.join().expect("執行緒發生錯誤");
    b.join().expect("執行緒發生錯誤");
}
```

執行緒 A 先拿到鎖 1，然後想拿鎖 2。但鎖 2 被執行緒 B 拿走了，B 又在等鎖 1——結果誰都走不動。

### 編譯器不會擋死鎖

Send 和 Sync 保護的是**資料競爭**（data race）——多個執行緒同時存取資料造成的未定義行為。死鎖是**邏輯問題**，程式不會壞掉或出現未定義行為，只是永遠卡住。Rust 的編譯器無法偵測死鎖。

### 同一個執行緒也會死鎖

就算只有一個執行緒，對同一個 Mutex lock 兩次也會死鎖——因為第一次 lock 還沒放開，第二次 lock 就永遠等不到：

```rust,ignore,mdbook-runnable
use std::sync::Mutex;

fn main() {
    let m = Mutex::new(42);
    let _g1 = m.lock().expect("取得鎖失敗");
    let _g2 = m.lock().expect("取得鎖失敗"); // 死鎖！第一個鎖還沒放，第二次 lock 永遠等不到
}
```

### 如何避免

- **所有執行緒以相同順序取鎖**：如果每個人都先拿鎖 1 再拿鎖 2，就不會互相卡住
- **減少同時持有多個鎖**：能用一個鎖解決就不要用兩個
- **guard 不要活太久**：用完趕快 drop，縮短持有鎖的時間

## 範例程式碼

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let lock1 = Arc::new(Mutex::new(String::from("資源 A")));
    let lock2 = Arc::new(Mutex::new(String::from("資源 B")));

    // 正確的方式：兩個執行緒以相同順序取鎖

    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);
    let a = thread::spawn(move || {
        let g1 = l1.lock().expect("取得鎖失敗"); // 先鎖 1
        let g2 = l2.lock().expect("取得鎖失敗"); // 再鎖 2
        println!("執行緒 A：{} 和 {}", *g1, *g2);
    });

    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);
    let b = thread::spawn(move || {
        let g1 = l1.lock().expect("取得鎖失敗"); // 也是先鎖 1
        let g2 = l2.lock().expect("取得鎖失敗"); // 再鎖 2
        println!("執行緒 B：{} 和 {}", *g1, *g2);
    });

    a.join().expect("執行緒發生錯誤");
    b.join().expect("執行緒發生錯誤");
    println!("沒有死鎖！");
}
```

## 重點整理
- 死鎖：多個執行緒互相等待對方放鎖，程式永遠卡住
- Rust 的編譯器不會擋死鎖——Send/Sync 保護的是資料競爭，死鎖是邏輯問題
- 同一個執行緒對同一個 Mutex lock 兩次也會死鎖，因為第一次的鎖還沒放開
- 避免方法：統一取鎖順序、減少同時持有多個鎖、guard 用完趕快 drop
