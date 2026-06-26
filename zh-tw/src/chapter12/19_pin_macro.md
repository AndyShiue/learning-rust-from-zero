# `pin!`

## 本集目標

學會用 `pin!` 在 stack 上釘住一個 `Future`，並理解它為什麼非得是巨集不可。

## 正文

### stack pinning

前面要釘住一個 `Future`，我們都用 `Box::pin`——把它放到 heap 上。但有時候你不想為了釘住一個 `Future` 而特地做一次 heap 配置（heap allocation 是有成本的），尤其當這個 `Future` 只在目前這個 scope 裡用、不需要傳出去的時候。

這種情況可以用 `std::pin::pin!`。它會在**目前的 scope** 建立一個被釘住的 local，回傳一個 `Pin<&mut T>`：

```rust,editable
use std::future::Future;
use std::pin::pin;
use std::task::{Context, Poll, Waker};

async fn hello() -> i32 {
    42
}

fn main() {
    // 在 stack 上釘住這個 future，拿到 Pin<&mut _>
    let mut future = pin!(hello());

    let mut cx = Context::from_waker(Waker::noop());
    match future.as_mut().poll(&mut cx) {
        Poll::Ready(value) => println!("完成：{value}"),
        Poll::Pending => println!("還沒好"),
    }
}
```

注意 `hello()` 產生的 `async fn` `Future` 並不是 `Unpin`，但 `pin!` 還是能釘住它——因為它做的是 stack pinning，把這個 `Future` 釘在目前 frame 的一個 local 上。

### 為什麼 `pin!` 一定要是巨集

這是這集最有意思的問題。`pin!` 為什麼是巨集（有驚嘆號），不是一個普通函式？

先想想 stack pinning 的本質：它要「在**呼叫端**的 stack frame 放一個 local，再交出一個借用它的 `Pin<&mut T>`」。關鍵在「呼叫端的 frame」。

如果把它寫成普通函式，會是這樣：

```rust,ignore
fn pin<T>(value: T) -> Pin<&mut T> { /* ??? */ }
```

這行不通。`value` 是這個函式的參數，住在 **`pin` 函式自己的** stack frame 裡。函式一返回，它的 frame 就被回收，那 `value` 也跟著消失——於是回傳的那個 `Pin<&mut T>` 立刻變成懸垂參考，指向一塊已經作廢的記憶體。事實上 borrow checker 根本不會讓你回傳一個指向「自身 frame 裡 local」的參考，這個函式連編譯都過不了。

巨集就沒有這個問題。巨集會**就地展開到呼叫端**，所以它能直接在**你的** scope 裡宣告 local——這個 local 的壽命跟你周圍的 scope 一樣長，不會在 `pin!` 「返回」時消失（巨集沒有「返回」這回事，它只是把程式碼貼進來）。`pin!` 的展開簡化後大致像這樣：

```rust,ignore
// let future = pin!(hello());
// 大致展開成：
let mut future = hello(); // 在你的 scope 宣告 local
let future = unsafe { Pin::new_unchecked(&mut future) }; // 用同名 shadow 蓋掉原值
```

兩步驟各有用意：第一行把值放在你的 frame；第二行用 `Pin::new_unchecked` 釘住它，並用**同名 shadow**（第 2 章的 shadowing）把原本那個可以自由 move 的 `future` 蓋掉——蓋掉之後你就再也碰不到那個可移動的原值了，等於封死了「把它搬走」的後門。這就是為什麼 `pin!` 用起來安全，即使它內部用了 `unsafe`。

### 對照 `Box::pin`

那為什麼 `Box::pin` 可以是普通函式？因為它走的是完全不同的路：`Box::pin` 把值放到 **heap** 上，並把那塊 heap 記憶體的所有權包進 `Pin<Box<T>>` 交給你。heap 上的東西活得比「這次函式呼叫」久，函式返回也不會回收它，所以回傳一個擁有它的 `Pin<Box<T>>` 完全沒問題。

一句話總結兩者的差別：

- `pin!`：**stack 借用**——東西放在呼叫端的 frame，交出借用，不配置 heap，但不能傳出 scope。所以必須是巨集。
- `Box::pin`：**heap 擁有**——東西放 heap，交出所有權，可以到處傳，代價是一次 heap 配置。所以可以是普通函式。

## 重點整理

- `pin!` 做 **stack pinning**：在目前 scope 釘住一個值、回傳 `Pin<&mut T>`，不需 heap 配置，適合不必把 pinned 值傳出 scope 的情況
- `pin!` 必須是**巨集**：stack pinning 要在呼叫端的 frame 放 local，函式做不到（值住在函式自己的 frame，返回就懸垂，borrow checker 也禁止）
- 巨集就地展開，能在你的 scope 宣告 local，並用同名 shadow 蓋掉可移動的原值，封死 move 後門
- `Box::pin` 把值放 heap、交出所有權（活得比這次呼叫久），所以能當普通函式；差別就在「stack 借用 vs heap 擁有」
