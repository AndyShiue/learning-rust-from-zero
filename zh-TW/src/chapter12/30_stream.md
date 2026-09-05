# `Stream`

## 本集目標

認識 `Stream`——`async` 版的 `Iterator`，以及怎麼走訪它。

## 正文

### `Stream` 是 `async` 版的 `Iterator`

第 6 章的 `Iterator` 是「一連串值，要一個一個取」。它的 `.next()` 是**同步**呼叫，完成後回傳下一個值（或 `None`）。如果取值需要耗時計算或阻塞 I/O，這次呼叫也得等它完成。

`Stream` 是它的 `async` 版本：一樣是一連串值要一個一個取，但可以**非同步地等待下一個值**，例如等網路送來下一筆資料。它的 `.next()` 回傳一個 `Future`，透過 `.next().await` 取得下一個值；資料尚未準備好時，可以讓出執行權，讓 runtime 處理其他 `Task`。

對照記就很好懂：

- `iterator.next()` → 同步呼叫，完成後回傳 `Option<Item>`。
- `stream.next().await` → 透過 `.await` 非同步等待，完成後得到 `Option<Item>`。

兩者都用「`None` 代表結束」。

本集的範例會用到 `tokio-stream` 這個 `crate`（它不在 Tokio 本體裡），使用前要加上依賴：

```toml
[dependencies]
tokio-stream = "0.1"
```

一個小地方要注意：`crate` 名稱在 `Cargo.toml` 裡寫 `tokio-stream`（連字號），但在程式碼裡要寫成 `tokio_stream`（底線）——`crate` 名稱裡的 `-` 到了程式碼裡一律變成 `_`。

### 走訪一個 `Stream`

`Iterator` 可以用 `for` 走訪，但 `Stream` 不行（`for` 沒辦法 `.await`）。`Stream` 的標準走訪寫法是 **`while let Some(x) = stream.next().await`**——一個一個取，取到 `None` 就停：

```rust,editable
extern crate tokio;
extern crate tokio_stream;

use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    // 從一個 Vec 做出最簡單的 stream
    let mut stream = tokio_stream::iter(vec![1, 2, 3]);

    // 一個一個取值，取到 None 為止
    while let Some(value) = stream.next().await {
        println!("收到 {}", value);
    }
}
```

### `Stream` 不在標準庫裡

有件事要特別說明：和 `Future` 不同，`Stream` **目前不在標準庫裡**。`Stream` `trait` 定義在 `futures-core` `crate` 中；`tokio-stream` 會重新匯出它，並提供自己的 `StreamExt`。要用本集的 `next`、`map`、`filter` 等方法，得引入 `tokio_stream::StreamExt`：

```rust,editable
extern crate tokio;
extern crate tokio_stream;

use tokio_stream::StreamExt;

#[tokio::main]
async fn main() {
    // 和 Iterator 一樣可以串接 map / filter 這些工具
    let mut stream = tokio_stream::iter(1..=5)
        .map(|x| x * 2)
        .filter(|x| x % 3 == 0);

    while let Some(value) = stream.next().await {
        println!("{}", value);
    }
}
```

你會發現 `map`、`filter` 這些方法跟第 6 章的 `Iterator` 幾乎一模一樣——因為 `Stream` 本來就是 `Iterator` 的 `async` 翻版。學過 `Iterator`，`Stream` 對你來說只是多了 `.await`。

實務上 `Stream` 很適合表達「源源不絕、會陸續到來的資料」——例如一個一個進來的網路連線、資料庫查詢的逐筆結果或定時觸發的事件。`tokio_stream` 提供了一整套處理它們的工具。

## 重點整理

- `Stream` 是 `async` 版的 `Iterator`：一連串值一個一個取，可以用 `.next().await` 非同步等待下一個值。
- 對照：`iterator.next()` 同步回 `Option`；`stream.next().await` 要 `.await` 才回 `Option`；都用 `None` 表示結束。
- 走訪用 **`while let Some(x) = stream.next().await`**（`Stream` 不能用 `for`）。
- `Stream` 不在標準庫，定義在 `futures`；用 `tokio_stream::StreamExt` 取得 `next`、`map`、`filter` 等方法（用法和 `Iterator` 幾乎一樣）。
