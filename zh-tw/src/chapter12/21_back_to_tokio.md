# 回到 Tokio

## 本集目標

從手寫 executor 回到真實世界的 tokio，看懂 `block_on` 和 `tokio::spawn` 的差別，以及那個常常擋住新手的 `Send + 'static` 是怎麼回事。

## 概念說明

### 你手寫過的東西，tokio 都幫你做好了

前面十幾集，我們親手做了一台迷你 runtime:executor(排程＋poll)、reactor(等 I/O)、Waker(串接)、spawn(把 future 交給排程器)。tokio 就是這一整套的工業級成品——同樣的零件,但寫得完整、高效、跨平台。所以接下來你看到的每個 tokio 功能,背後的原理你其實都摸過了。

### `block_on`:從同步世界跨進 async 世界的橋

第 4 集留了一個問題:普通(同步)的世界要怎麼跨進 async 的世界?答案是 `block_on`。

```rust,ignore
fn main() {
    let runtime = tokio::runtime::Runtime::new().unwrap();
    let result = runtime.block_on(async {
        // 這裡面是 async 世界,可以 .await
        42
    });
    println!("{}", result);
}
```

`block_on` 做的事,和我們第 6 集那個 `run` 函式一模一樣:**把一個 future 在「目前這條執行緒」上推到完成,回傳結果**。它會卡住目前這條執行緒直到 future 跑完——這也是它名字 block(阻塞)的由來。

> **和我們手寫版的一個差別,要點出來。** 第 11～14 集我們把入口也叫 `block_on`,但那個版本會等到 **ready queue 裡所有 task 都完成**才回傳(它的迴圈條件就是「還有 task 沒做完就繼續跑」)。tokio 的 `block_on` **不是**這樣——它是 **傳給它的那個 future 一完成就回傳**,不會等你另外 `tokio::spawn` 出去的背景 task;那些還沒跑完的 task 會繼續留在 runtime 上,直到 runtime 被 drop 才一起收掉。我們手寫版那樣寫,只是為了單一執行緒下好觀察、好收尾;**「那個 future 一完成就回傳」才是一般 runtime 的標準語意**。換句話說,手寫版的 `block_on` 比較像「跑完整批工作」,tokio 的 `block_on` 是「跑完我指定的這一個」。

那 `#[tokio::main]` 呢?它只是個語法糖。你寫:

```rust,ignore
#[tokio::main]
async fn main() {
    // ...
}
```

編譯器大致幫你展開成「建一個 runtime,然後 `block_on` 你的 async main」。所以從第 1 集用到現在的 `#[tokio::main]`,本質就是 `block_on`。

因為 `block_on` 是在「呼叫它的那條執行緒」上跑那個 future,它**不要求** future 是 `Send` 或 `'static`——反正不會把這個 future 送到別條執行緒去。

### `tokio::spawn`:把 task 交給 runtime 排程

`tokio::spawn` 對應的是我們第 12 集手寫的 `spawn`，再加上第 13 集的 `JoinHandle` 取結果機制：把一個 future 變成 task，交給 runtime 的排程器，讓它在背景被推進。它回傳一個 `JoinHandle`，`.await` 它可以拿到 task 的結果。

```rust,ignore
#[tokio::main]
async fn main() {
    let handle = tokio::spawn(async {
        // 這個 task 會被 runtime 排程,在背景跑
        1 + 2
    });

    // 同時 main 可以做別的事 ...

    let result = handle.await.unwrap(); // 等 task 跑完,拿回結果
    println!("{}", result);
}
```

和 `thread::spawn`(第 8 章)的關鍵差別,還是那句老話:`tokio::spawn` **不開新的 OS 執行緒**,只是把 future 交給排程器。你可以 spawn 幾萬個都沒問題。

### 為什麼 `spawn` 要求 `Send + 'static`

這裡就是新手最常撞牆的地方。`tokio::spawn` 的 future 必須是 **`Send + 'static`**,`block_on` 卻不用。差別在哪?

預設情況下,tokio 是 **multi-thread runtime**:它底下有好幾條 worker 執行緒,而排程器可能把一個 task 從這條 worker 搬到那條 worker 上跑。既然 task 會在執行緒之間移動:

- 它必須是 **`Send`**——值要能安全地在執行緒間搬動(第 8 章學過)。
- 它必須是 **`'static`**——因為 runtime 不知道這個 task 會活多久、由哪條執行緒跑,所以不能讓它借用任何「可能比它早消失」的東西(第 8 章 `thread::spawn` 也要求 `'static`,同樣的道理)。

`block_on` 不用這兩個,正因為它只在原本那條執行緒上跑,沒有跨執行緒的問題。

### 最常見的編譯錯誤:`.await` 期間抓著非 `Send` 的東西

`Send + 'static` 衍生出一個惡名昭彰、幾乎每個人都會中一次的錯誤。看這段:

```rust,ignore
use std::rc::Rc;

#[tokio::main]
async fn main() {
    tokio::spawn(async {
        let data = Rc::new(5); // Rc 不是 Send(第 8 章學過)
        some_async_work().await; // 在持有 data 的情況下 .await
        println!("{}", data);    // .await 之後還用到 data
    });
}
```

編譯器會抱怨這個 future 不是 `Send`,所以不能 `spawn`。為什麼?回想第 15 集:跨 `.await` 還會用到的變數,會被存進狀態機的欄位。這裡 `data`(一個 `Rc`)跨越了 `.await`,所以它變成 future 的一個欄位;而一個 struct 只要有任何一個欄位不是 `Send`,它自己就不是 `Send`(第 8 章)。於是整個 future 不是 `Send`,`spawn` 就失敗了。

**關鍵在「跨 `.await` 持有」**,不是「用過」。解法是讓那個非 `Send` 的值不要活過 `.await`——用完就丟:

```rust,ignore
#[tokio::main]
async fn main() {
    tokio::spawn(async {
        {
            let data = Rc::new(5);
            println!("{}", data); // 在 .await 之前用完
        } // data 在這裡就 drop 了,不會跨越 .await

        some_async_work().await; // 此時手上沒有任何非 Send 的東西
    });
}
```

用一個 `{}` 區塊把 `Rc` 的生命週期限制在 `.await` 之前,它就不會被存進狀態機、不會汙染 future 的 `Send`。記住這個診斷:**看到「future is not Send」,先找哪個非 `Send` 的值跨過了 `.await`。** 後面講 tokio 的鎖時(第 29 集)還會再遇到這個坑。

### 可以改 runtime 的種類

`#[tokio::main]` 預設是 multi-thread runtime。你也可以指定別種:

```rust,ignore
#[tokio::main(flavor = "current_thread")] // 單執行緒 runtime
async fn main() { }

#[tokio::main(flavor = "multi_thread", worker_threads = 4)] // 指定 4 條 worker
async fn main() { }
```

`current_thread` 整個 runtime 只用一條執行緒(task 不會跨執行緒,所以不少 `Send` 限制會放寬);多執行緒版可以指定要幾條 worker。初學階段用預設就好,知道有得調即可。

（還有一條和 worker 執行緒密切相關的重要原則:一個 task 不能長時間**霸佔** worker 執行緒,否則會拖垮整台 runtime。這牽涉到「不要在 async 裡做 blocking 工作」以及解法 `spawn_blocking`,下一集會專門講。）

## 範例程式碼

```rust,ignore
#[tokio::main]
async fn main() {
    // spawn 三個 task,讓它們在背景並行
    let mut handles = Vec::new();
    for i in 1..=3 {
        let handle = tokio::spawn(async move {
            // async move:把 i 搬進 task(滿足 'static)
            i * 10
        });
        handles.push(handle);
    }

    // 收集每個 task 的結果
    for handle in handles {
        let result = handle.await.unwrap();
        println!("結果：{}", result);
    }
}
```

## 重點整理

- tokio 就是我們手寫那台迷你 runtime 的工業級版本:executor、reactor、Waker、spawn 一應俱全
- `block_on`(= `#[tokio::main]` 的本質)把傳給它的 future 在**目前這條執行緒**跑到完成,所以**不要求** `Send`／`'static`
- tokio 的 `block_on` 是「**傳給它的 future 一完成就回傳**」,不等其他 `spawn` 的背景 task;這跟我們第 11～14 集手寫的「等所有 task 都完成才回傳」不同——後者只是教學版好觀察的簡化
- `tokio::spawn` 把 future 交給排程器在背景跑(不開 OS 執行緒),回傳 `JoinHandle`,`.await` 拿結果
- 預設 multi-thread runtime 會把 task 在 worker 執行緒間搬動,所以 spawn 的 future 要 **`Send + 'static`**
- 最常見錯誤:**非 `Send` 的值(如 `Rc`、稍後的 `MutexGuard`)跨越 `.await`** → future 不是 `Send`;解法是別讓它活過 `.await`(用 `{}` 限制範圍)
- runtime 種類可調:`current_thread` 單執行緒、`multi_thread` + `worker_threads = N`
- worker 執行緒會輪流 `poll` 很多 task,所以一個 task 不能長時間霸佔 worker——這條原則與解法 `spawn_blocking` 留到下一集
