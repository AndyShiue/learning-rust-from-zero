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
        Poll::Ready(value) => println!("完成：{}", value),
        Poll::Pending => println!("還沒好"),
    }
}
```

這裡有個容易誤會的點：目前編譯器保守地把 `hello()` 這種 `async fn` 產生的 `Future` 一律當成**不是** `Unpin`——連這個沒有任何 `.await`、根本不可能自我參照的 `hello` 也一樣（編譯器不想逐一判斷，乾脆全部不實作 `Unpin`）。所以上一集的 `Pin::new` 對它行不通，但 `pin!` 可以：因為 `pin!` 做的是 **stack pinning**，而它釘的辦法不要求 `Unpin`。

### 為什麼 `pin!` 一定要是巨集

這是這集最有意思的問題。`pin!` 為什麼是巨集，不是一個普通函式？

先抓住一個關鍵：`pin!` 交給你的 `Pin<&mut T>` 是一個**借用**，而借用一定要指著一個還活著的值。只要你還握著這個 `Pin<&mut T>`，被它借的那個值就不能消失。

所以那個被釘住的值，必須放在**你的程式碼裡**（也就是你呼叫 `pin!` 的地方），才能跟你手上的那個借用活得一樣久。

如果把它寫成普通函式，會是這樣：

```rust,ignore
fn pin<T>(value: T) -> Pin<&mut T> { /* ??? */ }
```

這行不通。`value` 是 `pin` 這個函式自己的區域變數。函式一返回，它的區域變數就被清掉、`value` 跟著消失——於是回傳的那個 `Pin<&mut T>` 立刻變成懸垂參考，指向一塊已經作廢的記憶體。事實上編譯器根本不會讓你回傳一個指向「函式自己區域變數」的參考。

巨集就沒有這個問題。巨集會**把程式碼就地貼進你的函式裡**，所以它要釘的那個值，是當成**你這個函式的區域變數**放著（壽命跟你周圍的 scope 一樣長），而不是放在某個一返回就被清掉的別的函式裡。它也沒有「返回」這回事——只是把程式碼貼進來——所以那個借用這個值的 `Pin<&mut T>` 不會懸垂，你可以安心拿來用。

### 對照 `Box::pin`

那為什麼 `Box::pin` 可以是普通函式？因為它走的是完全不同的路：`Box::pin` 把值放到 **heap** 上，並把那塊 heap 記憶體的所有權包進 `Pin<Box<T>>` 交給你。heap 上擁有所有權的東西活得比「這次函式呼叫」久，函式返回也不會丟掉它，所以回傳一個擁有它的 `Pin<Box<T>>` 完全沒問題。

一句話總結兩者的差別：

- `pin!`：**stack 借用**——值放在你自己的函式裡（當區域變數），交出借用，不配置 heap，但不能傳出 scope，所以必須是巨集。
- `Box::pin`：**heap 擁有**——東西放 heap，交出所有權，可以到處傳，代價是一次 heap 配置。所以可以是普通函數。

## 重點整理

- `pin!` 做 **stack pinning**：在目前 scope 釘住一個值、回傳 `Pin<&mut T>`，不需 heap 配置，適合不必把被釘住的值傳出 scope 的情況
- `pin!` 必須是**巨集**而非函式：被釘的值若放進一個函式，函式一返回、它的區域變數就被清掉，回傳的 `Pin<&mut T>` 立刻懸空（編譯器也不准你回傳這種借用）
- 巨集則把程式碼直接貼進你的程式裡，被釘的值跟著你的程式碼一起活著，`Pin<&mut T>` 才不會懸垂；而編譯器讓你只拿得到那個 `Pin<&mut T>`，已經碰不到值本身，所以搬不走它
- `Box::pin` 交出所有權把值放 heap（活得比這次呼叫久），所以能當普通函式；差別就在「stack 借用 vs heap 擁有」
