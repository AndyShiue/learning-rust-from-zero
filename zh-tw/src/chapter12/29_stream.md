# `Stream`

## 本集目標

認識 `Stream`——把第 6 章的 iterator 概念搬到 async 世界:一連串「要等」才會出現的值。

## 概念說明

### 從 iterator 到 stream

第 6 章學過 iterator:`next()` 每次給你下一個值,給完回 `None`。它是**同步**的——下一個值立刻就有。

但很多 async 情境裡,值是**一個一個慢慢來**的:network 連線上一行一行進來的資料、channel 裡陸續送達的訊息、每隔一秒觸發一次的計時事件。這種「一連串、但每個都要等」的值,就是 **Stream**。

你可以一句話記住它們的對應關係:

> **`Stream` 之於 `Iterator`,就像 `Future` 之於一個普通的值。**
>
> - `Future`:一個**要等**的值 → `.await` 拿到它。
> - `Iterator`:一連串**立刻有**的值 → `.next()` 一個個拿。
> - `Stream`:一連串**要等**的值 → `.next().await` 一個個等著拿。

所以 stream 的核心動作就是 `next().await`:等下一個 item 出現,沒有了就回 `None`。

### 用 `while let` 走訪一個 stream

走訪 stream 的標準寫法,是 `while let Some(x) = stream.next().await`——和 channel 的 `recv` 迴圈長得很像,因為精神一樣:一個一個等、拿、處理,直到結束。

```rust,ignore
use tokio_stream::StreamExt; // 提供 .next() 等方法,要先 use 進來

#[tokio::main]
async fn main() {
    // tokio_stream 可以把一個 Vec 變成 stream(這裡每個值其實立刻就有)
    let mut stream = tokio_stream::iter(vec![1, 2, 3]);

    while let Some(value) = stream.next().await {
        println!("收到 {}", value);
    }
}
```

`.next()` 這些方法來自 `StreamExt` 這個擴充 trait(就像第 6 章 iterator 的各種方法),記得 `use` 進來。tokio 生態用 `tokio_stream`,另一個常見來源是 `futures` crate 的 `StreamExt`,兩者很類似。

### 哪裡會冒出 stream

實務上你很少自己從零做 stream,而是從別的東西**轉**出來:

- 一個 channel 的 receiver(第 26 集)可以包成 stream,於是「陸續送來的訊息」就成了一串 item。
- 一個網路連線可以包成「一行一行的文字」stream。
- 計時器可以做成「每隔 N 秒吐一個」的 stream。

### 熟悉的 combinators

既然 stream 是 async 版 iterator,第 6 章那些 iterator 的招式——`map`、`filter`、`take` 等——大多也有 stream 版本,一樣可以鏈式串接,只是它們是惰性地、隨著值慢慢到達而套用:

```rust,ignore
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    let mut stream = tokio_stream::iter(1..=10)
        .filter(|n| n % 2 == 0) // 只留偶數
        .map(|n| n * 10)        // 各自乘 10
        .take(3);               // 只取前 3 個

    while let Some(v) = stream.next().await {
        println!("{}", v); // 20, 40, 60
    }
}
```

如果你回想第 6 章 iterator 的惰性求值(一層層包住、`next` 逐層往內拉),stream 是完全一樣的機制,只是每次往內拉的時候可能要 `.await` 等一下而已。

## 範例程式碼

把一個 `mpsc` 的 receiver 當成 stream 來處理——這是很實用的模式:

```rust,ignore
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    let (tx, rx) = mpsc::channel::<i32>(16);

    // 生產者:陸續送一些值進來
    tokio::spawn(async move {
        for i in 1..=5 {
            tx.send(i).await.unwrap();
        }
    });

    // 把 receiver 包成 stream,就能用 stream 的 combinators 處理
    let mut stream = ReceiverStream::new(rx).map(|n| n * n); // 各自平方

    while let Some(value) = stream.next().await {
        println!("{}", value); // 1, 4, 9, 16, 25
    }
}
```

## 重點整理

- `Stream` 是 async 版的 iterator:一連串**要等**才會出現的值;核心動作是 `next().await`
- 記憶法:`Stream : Iterator = Future : 普通值`——前者是「一串要等的值」,後者是「一串立刻有的值」
- 走訪用 `while let Some(x) = stream.next().await`(和 channel 的 `recv` 迴圈神似)
- `.next()`、`.map()`、`.filter()` 等方法來自 `StreamExt`(`tokio_stream` 或 `futures`),記得 `use`
- 你通常是把 channel receiver、網路連線、計時器等**轉**成 stream,而不是自己從零做
- 它的惰性求值機制和第 6 章 iterator 一樣,只是逐個拉取時可能要 `.await`
