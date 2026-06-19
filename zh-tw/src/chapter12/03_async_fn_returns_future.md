# `async fn` 回傳的是 Future

## 本集目標

建立一個關鍵的心智模型：呼叫 `async fn` 不會馬上執行它，只會得到一個「待辦事項」。

## 概念說明

### 呼叫 async 函數，什麼事都還沒發生

普通函數你很熟了：呼叫它，它就從頭跑到尾，把事情做完。

```rust,noplayground
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let x = add(1, 2); // 呼叫的當下就算好了，x 是 3
}
```

`async fn` 完全不一樣。呼叫一個 `async fn`，函數體**一行都不會執行**。你拿到的不是結果，而是一個代表「這件事還沒做、但之後可以做」的東西。這個東西叫做 **Future**（未來）。

可以把 Future 想成一張**待辦清單上的便利貼**：上面寫著「要做什麼」，但寫下來這個動作本身不會把事情做掉。要等到有人真的去「推進」這張便利貼，事情才會開始發生。

### 親眼驗證：函數體根本沒跑

光用講的不夠，我們來看一個**看得見**的證據。在 `say_hello` 的函數體裡放一句 `println!`，然後只呼叫它、不 `.await`：

```rust,ignore
async fn say_hello() {
    println!("你好"); // 注意這一行
}

#[tokio::main]
async fn main() {
    let _fut = say_hello(); // 只呼叫，沒有 .await
    println!("我呼叫 say_hello() 了——但上面那句「你好」有印出來嗎？");
}
```

跑起來,你只會看到：

```text
我呼叫 say_hello() 了——但上面那句「你好」有印出來嗎？
```

**「你好」沒有被印出來！** 這就是鐵證：呼叫 `say_hello()` 並沒有執行它的函數體，我們只是拿到一個 `_fut`（一個 future）放在那裡，從來沒去推進它，所以裡面那句 `println!` 一次都沒跑。

### 讓編譯器告訴你「這是一個 future」

還有一招很好用,可以讓你確認手上拿到的真的是 future：**故意把它標成一個錯誤的型別,讓編譯器抗議。** 編譯器在抱怨的時候,會順便告訴你它實際是什麼。

```rust,ignore
async fn say_hello() {
    println!("你好");
}

fn main() {
    let _x: () = say_hello(); // 故意標成 ()，看編譯器怎麼說
}
```

編譯會失敗,訊息大致是：

```text
error[E0308]: mismatched types
  |
  |     let _x: () = say_hello();
  |             --   ^^^^^^^^^^^^ expected `()`, found future
  |             |
  |             expected due to this
```

看那句 **`expected (), found future`**（預期是 `()`，但拿到的是一個 future）。編譯器親口證實了：`say_hello()` 給你的不是它函數體最後的值，而是一個 **future**。這招在你搞不清楚某個東西是不是 future 時隨時能用。

### 怎麼讓 future 真的動起來？`.await`

要讓一個 future 真正執行、把事情做完，就要用上一集看到的 `.await`。`.await` 的意思是「請推進這個 future，直到它做完，再把結果給我」。

但這裡有個雞生蛋的問題：`.await` 只能用在 `async` 的環境裡（例如另一個 `async fn` 裡）。那最外層怎麼辦？答案就是第 1 集的 `#[tokio::main]`——它幫我們把最外層的 `main` 接上 runtime，runtime 會負責推進 `main` 這個 future。把上面的例子加一個 `.await`：

```rust,ignore
async fn say_hello() {
    println!("你好");
}

#[tokio::main]
async fn main() {
    let fut = say_hello();
    println!("呼叫了，但還沒 await");
    fut.await; // 這次有 .await，函數體才真的執行
}
```

這次的輸出會是：

```text
呼叫了，但還沒 await
你好
```

注意「你好」是在 `fut.await` 那一刻才出現的——再次證明:**呼叫 async fn 只是拿到 future，真正執行是在 `.await`。**

### 最常踩的坑：忘了 `.await`

正因為 future 是「惰性」的（lazy，不主動執行），**忘記寫 `.await`** 是初學 async 最常見的 bug。

其實這個「惰性」你在第 6 章就見過了——**迭代器（iterator）也是惰性的**。還記得 `.map()`、`.filter()` 建出來只是一層層包住的 struct、什麼都還沒算，要等 `.collect()` 或 `for` 迴圈去「拉」它，才會真的開始跑嗎？future 是一模一樣的設計哲學，只是換成要用 `.await` 去推它：**先把「要做什麼」描述好，但不馬上做，等有人來取結果時才真的執行。** 認得這個共通點，future 的惰性就不陌生了。

你以為某段非同步的工作做了，結果它只是被你建出來、放在那裡，從來沒被推進過——就像剛剛那個沒印出「你好」的例子,只是這次是你不小心的。

好消息是，編譯器通常會幫你擋一下。Future 被標記成 `#[must_use]`，所以你建了一個 future 卻沒用它，會收到警告：

```text
warning: unused implementer of `Future` that must be used
  = note: futures do nothing unless you `.await` or poll them
```

看到 `futures do nothing unless you .await`（future 不被 await 就什麼都不做）這句話，多半就是你漏寫 `.await` 了。

## 範例程式碼

把「先只呼叫、再推進」整個串起來，感受那個時間差：

```rust,ignore
async fn make_coffee() -> String {
    println!("開始煮咖啡...");
    String::from("一杯咖啡")
}

#[tokio::main]
async fn main() {
    // 只呼叫、不 await：只拿到一張「待辦便利貼」，咖啡機還沒動
    let pending = make_coffee();
    println!("我手上有一個 future，但咖啡還沒開始煮");

    // 真的去推進它，咖啡才會煮好
    let coffee = pending.await;
    println!("拿到了：{}", coffee);
}
```

輸出順序會是：

```text
我手上有一個 future，但咖啡還沒開始煮
開始煮咖啡...
拿到了：一杯咖啡
```

「開始煮咖啡...」是在 `.await` 那一刻才印出來的，不是在呼叫 `make_coffee()` 的時候。

## 重點整理

- 呼叫 `async fn` 不會執行函數體，只會回傳一個 **Future**（代表「還沒做的事」）
- 看得見的證據：在函數體放一句 `println!`，只呼叫不 `.await`，那句**不會印出來**——證明函數體根本沒跑
- 想確認某個東西是不是 future，可故意標錯型別讓編譯器回報 `expected ..., found future`
- Future 是惰性的：不被推進就什麼都不會發生（像一張沒人去做的待辦便利貼）——和第 6 章的**迭代器**同一個道理（`.map`／`.filter` 也要 `.collect`／`for` 才動）
- 用 `.await` 推進一個 future，讓它執行並拿到結果；最外層靠 `#[tokio::main]` 接上 runtime
- 最常見的坑是**忘了 `.await`**——這時 future 不會執行；編譯器通常會用 `#[must_use]` 警告（`futures do nothing unless you .await`）提醒你
