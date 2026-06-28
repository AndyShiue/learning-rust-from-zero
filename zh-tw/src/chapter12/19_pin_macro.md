# `pin!`

## 本集目標

學會用 `pin!` 在 stack 上釘住一個 `Future`，並理解它為什麼非得是巨集不可。

## 正文

### stack pinning

前面要釘住一個 `Future`，我們都用 `Box::pin`——把它放到 heap 上。但有時候你不想為了釘住一個 `Future` 而特地做一次 heap 配置（heap allocation 是有成本的），尤其當這個 `Future` 只在目前這個作用域裡用、不需要傳出去的時候。

這種情況可以用 `std::pin::pin!`。它會把一個值釘在目前作用域裡，給你一個 `Pin<&mut T>`：

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

這是一個很有意思的問題。`pin!` 為什麼是巨集，不是一個普通函式？

先抓住一個關鍵：`pin!` 交給你的 `Pin<&mut T>` 是一個**參考**，而參考一定要指著一個還活著的值。只要你還握著這個 `Pin<&mut T>`，被它借的那個值就不能消失。

所以問題不是「怎麼做出一個 `Pin<&mut T>`」而已；問題是這個 `Pin<&mut T>` 借用的值要活得夠久。

如果把它寫成普通函式，會是這樣：

```rust,ignore
fn pin<T>(value: T) -> Pin<&mut T> { /* ??? */ }
```

這行不通。`value` 是 `pin` 這個函式自己的區域變數。函式一返回，它的區域變數就被清掉，`value` 跟著消失——於是回傳的那個 `Pin<&mut T>` 立刻變成懸垂參考，指向一塊已經作廢的記憶體。事實上編譯器根本不會讓你回傳一個指向「函式自己區域變數」的參考。

`pin!` 不是普通函式，所以不會有「回傳指向自己 stack 上變數的參考」這個問題。`pin!` 產生的 `Pin<&mut T>` 借用的是使用 `pin!` 的那個作用域裡的值，而不是借用某個普通函式自己的暫時變數。因此，那個借用不會在函式返回時立刻懸垂，你可以安心拿來用。

### 對照 `Box::pin`

那為什麼 `Box::pin` 可以是普通函式？因為它走的是完全不同的路：`Box::pin` 把值放到 **heap** 上，並把那塊 heap 記憶體的所有權包進 `Pin<Box<T>>` 交給你。heap 上擁有所有權的東西活得比「這次函式呼叫」久，函式返回也不會丟掉它，所以回傳一個擁有它的 `Pin<Box<T>>` 完全沒問題。

一句話總結兩者的差別：

- `pin!`：**stack 借用**——在不配置 heap 的情況下，從目前區塊中的值取得 `Pin<&mut T>`；因為普通函式不能回傳指向自己 stack 上變數的的參考，所以這件事必須由巨集在呼叫位置完成。
- `Box::pin`：**heap 擁有**——東西放 heap，交出所有權，可以到處傳，代價是一次 heap 配置。所以可以是普通函數。

## 重點整理

- `pin!` 做 **stack pinning**：取得一個只在目前區塊內有效的 `Pin<&mut T>`，不需 heap 配置，適合不必把被釘住的值傳出作用域的情況
- `pin!` 必須是**巨集**而非函式：普通函式不能回傳指向自己 stack 上變數的 `Pin<&mut T>`；函式一返回，那個參考就會懸垂（編譯器也不准你這樣寫）
- `Box::pin` 交出所有權把值放 heap（活得比這次呼叫久），所以能當普通函式；差別就在「stack 借用 vs heap 擁有」
