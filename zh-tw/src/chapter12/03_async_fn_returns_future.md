# `async fn` 回傳的是 `Future`

## 本集目標

建立一個關鍵的心智模型：呼叫 `async fn` 並不會執行它，你只是拿到一個還沒開始跑的 `Future`。

## 正文

### 呼叫 `async fn` 不會執行它

這是新手最常踩的坑，所以我們用實驗來證明。先看一個普通的 `async fn`：

```rust,no_run
# extern crate tokio;
#
async fn say_hello() {
    println!("hello");
}

#[tokio::main]
async fn main() {
    say_hello(); // 注意：這行不會印出 hello！
}
```

直覺上你會以為呼叫 `say_hello()` 就會印出 `hello`，但實際上**什麼都不會發生**。函數體裡的 `println!` 完全沒有執行。不只如此，編譯器還會給你一個警告：

```text
warning: unused implementor of `Future` that must be used
note: futures do nothing unless you `.await` or poll them
```

這個警告（來自 `#[must_use]`）已經把真相說出來了：呼叫 `say_hello()` 得到的是一個 **`Future`**——一個「還沒跑的工作」。你只是把這個工作描述出來，但沒有人去執行它，所以它就被丟掉了。

要真的讓它跑，得加上 `.await`：

```rust,no_run
# extern crate tokio;
#
async fn say_hello() {
    println!("hello");
}

#[tokio::main]
async fn main() {
    say_hello().await; // 這次才會印出 hello
}
```

### 讓編譯器親口證實它是 `Future`

如果你還不信，我們可以用另一招逼編譯器說實話：故意把回傳值的型別標錯，看它怎麼罵人。

```rust,compile_fail
# extern crate tokio;
#
async fn say_hello() {
    println!("hello");
}

#[tokio::main]
async fn main() {
    let x: () = say_hello(); // 編譯錯誤
}
```

`say_hello` 的函數體沒有回傳值，照理說「應該」回傳 `()`，所以我們故意寫 `let x: () = ...`。但編譯器會報錯：

```text
expected `()`, found future
```

它清楚地告訴你：`say_hello()` 的型別**不是** `()`，而是一個 future。這就確認了——呼叫一個 `async fn`，拿到的是一個 `Future`，而不是函數體執行後的結果。

### `Future` 是惰性的

把上面兩個實驗合起來，我們得到這一集最重要的一句話：

> 呼叫 `async fn` 只是得到一個 `Future`，這個 `Future` 是**惰性的**。

「惰性」這個詞你應該不陌生。回想第 6 章的**迭代器**：當你寫 `v.iter().map(...).filter(...)`，這幾個方法其實一個元素都還沒處理，它們只是把「之後要做的事」描述出來；真正開始跑，是等到你 `.collect()` 或用 `for` 走訪的那一刻。

`Future` 和 `Iterator`骨子裡是同一套設計哲學：**先描述，晚執行**。`Iterator` 描述「一連串值要怎麼算出來」，等你索取才動；`Future` 描述「一個非同步工作要做什麼」，等你被 runtime 推進才動。

下一集我們換個角度，把 `.await` 和你早就學過的 `?` 放在一起看，你會發現它們其實是同一類東西。

## 重點整理

- 呼叫 `async fn` **不會**執行函數體，你只會拿到一個 `Future`
- `async fn main` 裡不做像是 `.await` 的動作的話，函數體裡的程式碼一行都不會跑，還會收到 `#[must_use]` 警告
- 把回傳值標成 `()` 會讓編譯器報 `expected (), found future`，證明它真的是 `Future`
- `Future` 是**惰性的**，和第 6 章的 `Iterator` 一樣，都是「先描述、晚執行」的設計
