# 用 `pin!` 做 stack pinning

## 本集目標

學會 `pin!` 巨集:把一個 future 釘在目前的 stack 上,不用 heap 配置就能拿到 `Pin<&mut T>`。

## 概念說明

### 為什麼需要一個「把東西釘住」的工具

前面幾集反覆遇到同一個需求:要 poll 一個 future,得先有一個 `Pin<&mut F>`;要把不是 `Unpin` 的 future 傳給要求 `Unpin` 的 API,也得先把它釘住。那「釘住」具體要怎麼做?

「釘住」的意思是:把這個 future 放在一個**之後不會再被搬動**的位址,然後給你一個指向它的 `Pin` 指標。標準庫提供兩條路:釘在 stack 上(這一集的 `pin!`),或釘在 heap 上(下一集的 `Box::pin`)。

### `pin!`:釘在目前的 stack

`std::pin::pin!` 是一個巨集。你給它一個值,它會在**目前這個 scope** 配置一塊 stack 空間放這個值,並回傳一個 `Pin<&mut T>` 指向它:

```rust,ignore
use std::pin::pin;

#[tokio::main]
async fn main() {
    let fut = async { 1 + 2 };

    let pinned = pin!(fut); // pinned: Pin<&mut {async block}>
    // 從現在起,fut 被釘在這個 scope 的 stack 上,不會再被 move

    println!("{}", pinned.await);
}
```

回想第 6 集那台手寫 executor：我們是用 `Box::pin` 把 future 釘在 **heap** 上的。`pin!` 提供另一個選擇——把同一個 future 改釘在 **stack** 上。對那台 `run` 來說，future 只是要在函式內反覆 `poll`、不必帶出去，所以其實用 `pin!` 就夠了，還能省掉 `Box::pin` 那一次 heap 配置：`let mut future = pin!(future);`，後面照樣 `future.as_mut().poll(cx)`。

### `pin!` 的限制:不能把它帶出 scope

`pin!` 把東西釘在**目前 scope 的 stack** 上。stack 上的東西,在離開 scope(函式返回)時就會被回收。所以 `pin!` 釘住的 future,**生命週期被綁在這個 scope 裡**——你不能把它 return 出去,也不能把它存到一個活得比這個 scope 久的地方。

```rust,ignore
use std::pin::{pin, Pin};
use std::future::Future;

fn make_pinned() -> Pin<&'static mut impl Future> {
    let fut = async { 1 };
    pin!(fut) // 編譯錯誤!fut 釘在這個函式的 stack 上,函式一返回就沒了
}
```

如果你需要把一個釘住的 future「帶著走」(return、存進 struct、丟給別的執行緒),`pin!` 就不夠了,要改用下一集的 `Box::pin`——它把 future 放到 heap 上,自然能活得比目前 scope 久。

### 什麼時候用 `pin!`

`pin!` 的甜蜜點是:你只是要在**當下這個函式裡**把某個 future 釘住用一下(poll 它、`.await` 它、或傳給一個要求 `Unpin` 的 API),用完就算了,不需要把它送到別處去。這種情況下 `pin!` 最理想——因為它**不需要 heap 配置**,比 `Box::pin` 省一次記憶體分配,更快更輕。

一個常見場景是:有些工具(例如某些 stream 或 select 相關的 API,後面會遇到)要求你傳進去的 future 是 `Unpin` 的,而你手上的 async fn future 不是。這時在呼叫前一行 `let fut = pin!(fut);` 把它釘在 stack 上,就過關了,而且零額外配置。

## 範例程式碼

```rust,ignore
use std::pin::pin;
use std::future::Future;

// 一個要求傳進來的 future 是 Unpin 的假想 API
async fn run_it<F: Future<Output = i32> + Unpin>(mut f: F) -> i32 {
    (&mut f).await
}

#[tokio::main]
async fn main() {
    let fut = async { 41 + 1 }; // async 區塊的 future——不是 Unpin

    // 直接把 fut 傳給 run_it 會因為「不是 Unpin」而編譯失敗。
    // 用 pin! 釘在 stack 上,得到的 Pin<&mut _> 是 Unpin,就能傳:
    let pinned = pin!(fut);
    let result = run_it(pinned).await;

    println!("{}", result); // 42
}
```

## 重點整理

- 「釘住」= 把 future 放在之後不會再被 move 的位址,並給出指向它的 `Pin` 指標
- `pin!` 巨集把 future 釘在**目前 scope 的 stack** 上,回傳 `Pin<&mut T>`,**不需要 heap 配置**
- 第 6 集 executor 用的是 `Box::pin`(heap 版);`pin!` 是它的 stack 版本,只在函式內 poll、不帶出去時更省（少一次 heap 配置）
- 限制:釘住的東西生命週期綁在這個 scope,**不能 return 或存到活更久的地方**
- 要把釘住的 future 帶出 scope,改用 `Box::pin`(下一集);只在當下用一下就 `pin!`,更省更快
