# `Arc<T>`

## 本集目標

學會用 `Arc<T>` 在多個執行緒之間安全地共享資料。

## 概念說明

### 問題回顧

前面說了 `Rc` 不能跨執行緒，因為參考計數不是 atomic。但我們確實需要在多個執行緒之間共享資料——怎麼辦？

### `Arc`：atomic reference counting

`Arc<T>` 就是把 `Rc` 的參考計數換成 **atomic 操作**的版本。atomic 操作保證即使多個執行緒同時修改計數器，也不會互相干擾。

用法跟 `Rc` 幾乎一樣：

```rust,editable
use std::sync::Arc;

fn main() {
    let a = Arc::new(String::from("hello"));
    let b = Arc::clone(&a); // 增加計數，不複製資料
    println!("計數 = {}", Arc::strong_count(&a)); // 2
}
```

### 跨執行緒共享

把 `Arc::clone` 出來的東西 move 到另一個執行緒：

```rust,editable
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3]);

    let data_clone = Arc::clone(&data);
    let handle = thread::spawn(move || {
        println!("子執行緒：{:?}", data_clone);
    });

    println!("主執行緒：{:?}", data);
    handle.join().expect("執行緒發生錯誤");
}
```

### `T` 必須是 `Send + Sync`

`Arc` 要求 `T: Send + Sync`。為什麼？

**`Sync`**：多個執行緒透過各自的 `Arc` 同時存取同一份 `T`。第 5 章學了 `Deref`——`Arc` 實作了 `Deref`，所以你可以透過 `Arc` 直接存取 `T` 的內容。這等於多個執行緒同時持有 `T` 的不可變參考，所以 `T` 必須是 Sync。

**`Send`**：最後一個 `Arc` 被 `drop` 的時候，`T` 也會被 `drop`。而哪個執行緒持有最後一個 `Arc` 是不確定的，所以 `T` 的 `drop` 可能發生在任何執行緒上——`T` 等於被「送」到那個執行緒去銷毀，所以 `T` 必須是 `Send`。

## 範例程式碼

```rust,editable
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3, 4, 5]);

    let mut handles = vec![];

    for i in 0..3 {
        let data_clone = Arc::clone(&data);
        let handle = thread::spawn(move || {
            let sum: i32 = data_clone.iter().sum();
            println!("執行緒 {} 算出的總和：{}", i, sum);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("執行緒發生錯誤");
    }

    println!("最終計數 = {}", Arc::strong_count(&data)); // 1
}
```

## 重點整理

- `Arc<T>` 是 `Rc<T>` 的多執行緒版本，參考計數用 atomic 操作
- 用法跟 `Rc` 幾乎一樣：`Arc::new()`、`Arc::clone()`
- `Arc::clone` 後把 `clone` move 到其他執行緒，就能共享資料
- `T` 必須是 `Send + Sync`：`Sync` 因為多執行緒同時存取，`Send` 因為 `drop` 可能發生在任何執行緒
