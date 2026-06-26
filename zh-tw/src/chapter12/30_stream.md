# `Stream`

## 本集目標

認識 `Stream`——`async` 版的 `Iterator`，以及怎麼走訪它。

## 概念說明

### `Stream` 是 `async` 版的 `Iterator`

第 6 章的 `Iterator` 是「一連串值，要一個一個取」。但它的 `next()` 是**同步**的——呼叫就馬上給你下一個值（或 `None`）。

`Stream` 是它的 `async` 版本：一樣是一連串值要一個一個取，但下一個值**可能要等**（例如等網路送來下一筆資料、等計時器、等使用者輸入）。所以 `Stream` 的 `next()` 回傳的是一個 `Future`，你要 `next().await` 才拿得到下一個值。

對照記就很好懂：

- `Iterator::next()` → 回傳 `Option<Item>`（同步、馬上給）。
- `Stream::next().await` → 回傳 `Option<Item>`（要 `.await`、可能等一下）。

兩者都用「`None` 代表結束」。

### 走訪一個 `Stream`

`Iterator` 可以用 `for` 走訪，但 `Stream` 不行（`for` 沒辦法 `.await`）。`Stream` 的標準走訪寫法是 **`while let Some(x) = stream.next().await`**——一個一個取，取到 `None` 就停：

```rust,no_run
# extern crate tokio;
# extern crate tokio_stream;
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    // 從一個 Vec 做出最簡單的 stream
    let mut stream = tokio_stream::iter(vec![1, 2, 3]);

    // 一個一個取值，取到 None 為止
    while let Some(value) = stream.next().await {
        println!("收到 {value}");
    }
}
```

### `Stream` 不在標準庫裡

有件事要特別說明：和 `Future` 不同，`Stream` **目前不在標準庫裡**，它定義在社群套件（`futures`）裡，Tokio 生態則提供 `tokio_stream`。要用 `next()`、`map`、`filter` 這些方法，得引入對應的擴充 trait `StreamExt`（就像第 6 章 `Iterator` 的各種方法那樣）：

```rust,no_run
# extern crate tokio;
# extern crate tokio_stream;
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    // 和 Iterator 一樣可以串接 map / filter 這些工具
    let mut stream = tokio_stream::iter(1..=5)
        .map(|x| x * 2)
        .filter(|x| x % 3 == 0);

    while let Some(value) = stream.next().await {
        println!("{value}");
    }
}
```

你會發現 `map`、`filter` 這些組合器跟第 6 章的 `Iterator` 幾乎一模一樣——因為 `Stream` 本來就是 `Iterator` 的 `async` 翻版，連惰性求值的特性都一樣（不 `.await` 走訪就什麼都不會算）。學過 `Iterator`，`Stream` 對你來說只是多了個 `.await`。

實務上 `Stream` 很適合表達「源源不絕、會陸續到來的資料」——例如一個一個進來的網路連線、資料庫查詢的逐筆結果、或定時觸發的事件。`tokio_stream` 和 `futures::StreamExt` 提供了一整套處理它們的工具。

## 重點整理

- `Stream` 是 `async` 版的 `Iterator`：一連串值一個一個取，但下一個值可能要等，所以是 `next().await`。
- 對照：`Iterator::next()` 同步回 `Option`；`Stream::next().await` 要 `.await` 才回 `Option`；都用 `None` 表示結束。
- 走訪用 **`while let Some(x) = stream.next().await`**（`Stream` 不能用 `for`）。
- `Stream` 不在標準庫，定義在 `futures`；用 `tokio_stream` / `futures::StreamExt` 取得 `next`、`map`、`filter` 等工具（用法和 `Iterator` 幾乎一樣，也一樣惰性）。
