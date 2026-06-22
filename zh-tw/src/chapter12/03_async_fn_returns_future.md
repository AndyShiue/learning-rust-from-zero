# `async fn` 回傳的是 `Future`

## 本集目標

建立一個關鍵心智模型：**呼叫 `async fn`，並不會執行它的內容，只會拿到一個還沒跑的 `Future`。** 我們用兩個看得見的方式證明這件事。

## 概念說明

### 方法一：呼叫了，但函數體沒執行

先看一個會印東西的 `async fn`：

```rust,ignore
async fn say_hello() {
    println!("hello");
}

fn main() {
    let _f = say_hello(); // 呼叫了……
    println!("main 結束");
}
```

直覺上你可能以為會印 `hello` 再印 `main 結束`。但實際上**只會印 `main 結束`**——`say_hello()` 裡的 `println!` 完全沒執行。

為什麼？因為呼叫 `async fn` **不會跑它的內容**，只會回傳一個「代表這段工作、但還沒開始」的東西。函數體要等到這個東西被**驅動**（之後會講的 `.await` 或交給 runtime）才會真的執行。

### 方法二：讓編譯器告訴你它的型別

那「回傳的東西」到底是什麼型別？故意把它指定成錯的型別，讓編譯器報出來：

```rust,ignore
async fn say_hello() {}

fn main() {
    let _x: () = say_hello(); // 故意說它是 ()
}
```

編譯器會回報類似：

```text
expected `()`, found future
```

`async fn say_hello()` 看起來「回傳 `()`」，但其實呼叫它得到的是一個 **future**（編譯器叫它 opaque future）。換句話說：

> 呼叫 `async fn` 得到的不是「函數的結果」，而是一個**還沒跑、之後會產出那個結果的 `Future`**。

### `Future` 是惰性的

這帶出新手最常踩的坑：**`Future` 是惰性（lazy）的——你不去驅動它，它什麼都不會做。**

```rust,ignore
async fn do_work() {
    println!("做事");
}

fn main() {
    do_work(); // 只是建立 future，沒人驅動 → 「做事」不會印
}
```

這段不只什麼都不印，編譯器還會給你一個 `#[must_use]` 警告：「這個 future 沒被使用」——提醒你「你拿到了一個 future 卻沒去 `.await` 或交出去跑」。

### 似曾相識？跟迭代器一樣

這個「先描述、晚執行」的設計，你其實在第 6 章的**迭代器**就見過了。`Iterator` 也是惰性的：

```rust,ignore
let it = vec![1, 2, 3].into_iter().map(|x| {
    println!("處理 {x}");
    x * 2
});
// 到這裡一個字都還沒印——map 只是「描述」要做什麼
// 要等 .collect() 或 for 真正去「拉」值，閉包才會跑
let _doubled: Vec<_> = it.collect();
```

`Iterator` 的 `.map` / `.filter` 不會立刻跑，要等 `.collect()` 或 `for` 去拉值才動。`Future` 是同一個哲學的另一個例子：**先把「要做什麼」描述出來（建立 future / iterator），真正執行延後到有人來驅動的時候。** 記住這個類比，後面看 `Future` 會親切很多。

## 重點整理

- 呼叫 `async fn` **不執行函數體**，只回傳一個還沒跑的 `Future`（用「函數體的 `println!` 沒印」「指定錯型別讓編譯器回報 found future」兩招可以親眼確認）
- `Future` 是**惰性**的：不去驅動（`.await` 或交給 runtime）就什麼都不會發生，還會收到 `#[must_use]` 警告
- 這跟第 6 章的 **`Iterator`** 是同一個「先描述、晚執行」的設計：`.map` 要等 `.collect` / `for` 才動，future 要等被驅動才跑
