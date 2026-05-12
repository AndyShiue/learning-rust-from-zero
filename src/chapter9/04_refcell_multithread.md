# `RefCell` 在多執行緒

## 本集目標

理解為什麼 interior mutability 在多執行緒下是危險的，以及 `RefCell` 的 `Send` / `Sync` 特性。

## 概念說明

### interior mutability 是多執行緒的一大威脅

第五章學過，`RefCell` 能透過 `&T`（不可變參考）修改內部的值。在單執行緒的世界裡，`RefCell` 會在執行期檢查借用規則，不會出問題。

但在多執行緒的世界裡，事情就不一樣了。`&T` 看起來是「只讀」的，而 `Sync` 的定義就是 `&T` 能安全地在多個執行緒之間共享。如果一個型別能透過 `&T` 偷偷修改內容，多個執行緒同時這樣做就可能出事。

### `RefCell` 的借用計數不是 atomic

`RefCell` 用普通的整數來記錄目前的借用狀態（有幾個不可變借用、有沒有可變借用）。這個計數器的操作不是 **atomic** 的——atomic 的意思是「不可分割」，一個 atomic 操作要嘛完整執行完，要嘛完全沒發生，不會被其他執行緒打斷到一半。`RefCell` 的計數器讀取和寫入不是 atomic 的，代表一個執行緒讀到一半，另一個執行緒可能就插進來改了值。如果兩個執行緒同時透過 `&RefCell<T>` 呼叫 `borrow_mut()`，以下是可能發生的事：

1. 執行緒 A 呼叫 `borrow_mut()`，讀取計數器，看到值是 0（沒有人在借）
2. 執行緒 B 也呼叫 `borrow_mut()`，讀取計數器，也看到值是 0
3. 執行緒 A 判斷「沒有人在借，可以拿可變借用」，把計數器改成「可變借用中」
4. 執行緒 B 也判斷「沒有人在借」——因為它在步驟 2 讀到的是舊值——也拿到了可變借用

結果：兩個執行緒同時拿到了可變借用，`RefCell` 的執行期檢查完全被繞過了。

### `RefCell` 不是 `Sync`

因為上面的原因，`RefCell` 不是 `Sync`——`&RefCell<T>` 不能在多個執行緒之間共享。如果你試著這樣做，編譯器會擋住你。

### `RefCell` 是 `Send`

但 RefCell 可以被 **move** 到另一個執行緒。為什麼？因為 move 之後，只有那一個執行緒擁有這個 `RefCell`，不存在多個執行緒同時操作的問題。

```rust
use std::cell::RefCell;
use std::thread;

fn main() {
    let data = RefCell::new(vec![1, 2, 3]);

    // OK：RefCell 是 Send，可以 move 到另一個執行緒
    let handle = thread::spawn(move || {
        data.borrow_mut().push(4);
        println!("{:?}", data.borrow());
    });

    handle.join().expect("執行緒發生錯誤");
}
```

## 範例程式碼

```rust
use std::cell::RefCell;
use std::thread;

fn main() {
    // RefCell 可以 move 到另一個執行緒（Send）
    let data = RefCell::new(String::from("hello"));

    let handle = thread::spawn(move || {
        // 在這個執行緒裡，RefCell 運作正常
        data.borrow_mut().push_str(" world");
        println!("子執行緒：{}", data.borrow());
    });

    handle.join().expect("執行緒發生錯誤");

    // 但不能在多個執行緒之間共享 &RefCell（非 Sync）
    // 如果你試著讓兩個執行緒共享同一個 RefCell，編譯器會擋住你。
}
```

## 重點整理

- interior mutability 讓 `&T` 能修改內容，但這在多執行緒下很危險
- atomic 操作 = 不可分割的操作，要嘛完整執行完，要嘛完全沒發生，不會被其他執行緒打斷到一半
- `RefCell` 的 `borrow` 計數是普通整數，不是 atomic，多執行緒同時操作可能繞過檢查
- `RefCell` 不是 `Sync`——不能在多個執行緒之間共享 `&RefCell<T>`
- `RefCell` 是 `Send`——可以 move 到另一個執行緒，因為 move 後只有一個執行緒擁有
