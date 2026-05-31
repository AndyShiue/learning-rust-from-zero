# `Rc` 在多執行緒

## 本集目標

理解為什麼 `Rc` 完全不能跨執行緒——既不是 `Send` 也不是 `Sync`。

## 概念說明

### `Rc` 不是 `Sync`

`Rc` 的參考計數和 `RefCell` 的 `borrow` 計數一樣，是普通整數，不是 atomic 操作。如果多個執行緒同時透過 `&Rc<T>` 做 `clone` 或 `drop`，參考計數的加減可能互相干擾，導致計數錯誤——可能提前釋放資料，或永遠不釋放。

所以 `Rc` 不是 `Sync`，理由和 `RefCell` 相同。

### `Rc` 連 `Send` 都不是

上一集說 `RefCell` 是 `Send`，因為 move 過去之後只有一個執行緒擁有。但 `Rc` 不一樣。

`Rc` 的設計就是讓多個 `Rc` 指向同一份資料。你把一個 `Rc` move 到另一個執行緒，但它的 `clone` 可能還留在原本的執行緒。兩邊同時操作參考計數，計數器就可能壞掉。

問題不在 move 本身，而在 **move 之後兩個執行緒仍然共享同一個計數器**。

```rust,compile_fail
use std::rc::Rc;

fn main() {
    let a = Rc::new(42);
    let b = a.clone(); // a 和 b 共享同一份資料和計數器

    // 如果把 a move 到另一個執行緒，
    // b 還在原本的執行緒——兩邊同時操作計數器就爆了
    std::thread::spawn(move || {
        println!("{}", a);
    });
    // 編譯錯誤！Rc<i32> 不是 Send
}
```

### `Rc` 完全不能跨執行緒

`Rc` 不是 `Send` 也不是 `Sync`。不能 move 到其他執行緒，也不能在多個執行緒之間共享參考。如果需要跨執行緒共享資料，得用別的工具。

## 範例程式碼

```rust,editable
use std::rc::Rc;
use std::thread;

fn main() {
    // Rc 在單執行緒中正常運作
    let a = Rc::new(String::from("hello"));
    let b = a.clone();
    println!("a = {}, b = {}", a, b);
    println!("計數 = {}", Rc::strong_count(&a));

    // 但不能跨執行緒——以下不會通過編譯：

    // let data = Rc::new(42);
    // thread::spawn(move || {
    //     println!("{}", data);
    // });
    // 編譯錯誤：Rc<i32> 不是 Send

    println!("Rc 只能在單執行緒中使用");
}
```

## 重點整理

- `Rc` 的參考計數是普通整數，不是 atomic，所以不是 `Sync`
- `Rc` 連 `Send` 都不是：move 一個 `Rc` 到另一個執行緒後，它的 `clone` 可能還在原執行緒，兩邊同時操作計數器就會出問題
- 也就是說 `Rc` 完全不能跨執行緒
