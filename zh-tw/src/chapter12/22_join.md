# `tokio::join!`：在同一個 task 裡並行

## 本集目標

用 tokio 內建的 `join!` 讓多個 future 並行,不用自己手寫第 9 集那個 `Join`;順帶認識 `spawn_blocking` 與「不要在 async 裡做 blocking」這條重要原則。

## 概念說明

### `join!`:第 9 集那個 Join 的成品版

第 9 集我們手寫了一個 `Join`,讓兩個 `Delay` 並行。tokio 直接提供 `join!` 巨集,做的是同一件事,但好用多了:

```rust,ignore
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let start = std::time::Instant::now();

    // 同時等三件事,全部完成才往下走
    let (a, b, c) = tokio::join!(
        async { sleep(Duration::from_secs(1)).await; 1 },
        async { sleep(Duration::from_secs(1)).await; 2 },
        async { sleep(Duration::from_secs(1)).await; 3 },
    );

    println!("{} {} {}", a, b, c);
    println!("總共 {:?}", start.elapsed()); // 約 1 秒,不是 3 秒
}
```

`join!` 接受好幾個 future,**並行**推進它們,等**全部**完成後,把每個的結果包成一個 tuple 還給你。三件各 1 秒的事,並行只花約 1 秒。

### `join!` 是在「同一個 task」裡並行

這裡有個和 `spawn` 的重要區別。`tokio::spawn`(第 21 集)是把 future 交給 runtime 變成**獨立的 task**,可能被丟到別條 worker 執行緒上跑。`join!` 不一樣:它把那幾個 future **multiplex(多工)在目前這一個 task 裡**——就是我們第 9 集做的那招,在同一個地方輪流 poll 它們,沒有產生新 task、不跨執行緒。

這帶來幾個實際差別:

- `join!` 的 future **不需要 `Send + 'static`**(因為沒跨執行緒、沒交給排程器),所以可以放心借用周圍的區域變數。
- `join!` 適合**固定數量**、生命週期就綁在目前這個函式裡的並行(「我要同時做這幾件事,等它們都好」)。

### `try_join!`:有人失敗就提早收手

如果你的 future 回傳的是 `Result`,常常會希望「只要有一個出錯,就不必等其他的了,直接回報錯誤」。這時用 `try_join!`:

```rust,ignore
use tokio::try_join;

async fn task_ok() -> Result<i32, String> { Ok(1) }
async fn task_err() -> Result<i32, String> { Err(String::from("壞了")) }

#[tokio::main]
async fn main() {
    match try_join!(task_ok(), task_err()) {
        Ok((a, b)) => println!("都成功：{} {}", a, b),
        Err(e) => println!("有人失敗：{}", e), // 走這裡
    }
}
```

`join!` 一定等全部跑完;`try_join!` 一遇到第一個 `Err` 就提早回傳那個錯誤。

### 重要警告:並行 ≠ CPU 平行,別在裡面做 blocking

這是非常容易誤會、也很容易出事的一點。`join!` 的並行,是「在一條執行緒上輪流推進」,**不是**讓 CPU 同時開好幾顆核心算(那叫平行,parallelism)。所以:

如果你 `join!` 的某個分支裡,做了一件**長時間不 `.await`** 的事——例如一個跑很久的純計算迴圈,或呼叫了一個**會卡住的同步函式**(像 `std::thread::sleep`、`std::fs` 的同步讀檔、一個慢的同步資料庫呼叫)——那這個分支會把整條執行緒**霸佔住**,在它做完之前,同一條執行緒上的其他 future(包括 `join!` 的其他分支、甚至整個 runtime 上別的 task)全都被**卡住、動彈不得**。

記住這條原則:**不要在 async 程式裡做會 blocking 的事。** async 的「讓出執行緒」只在 `.await` 時發生;一段不 `.await` 的程式碼,執行緒就一直被它佔著。

### 真要做 blocking 的事:`spawn_blocking`

那如果你**就是**得做一件耗時的同步工作(一個沒有 async 版本的函式庫、一段很重的計算)呢?tokio 提供 `spawn_blocking`:把這件事丟到一個**專門給 blocking 工作用的執行緒池**去做,不要卡到負責跑 async 的 worker 執行緒。

```rust,ignore
#[tokio::main]
async fn main() {
    let result = tokio::task::spawn_blocking(|| {
        // 這裡可以安心做會卡住的同步工作,因為它在專用的 blocking 執行緒上
        let mut sum: u64 = 0;
        for i in 0..1_000_000_000 { sum += i; } // 很重的純計算
        sum
    })
    .await
    .unwrap();

    println!("{}", result);
}
```

`spawn_blocking` 回傳一個可以 `.await` 的 handle。重點是:它把「會卡執行緒」的工作隔離到專用的池子,你的 async 主流程就不會被拖垮。判準很簡單——**如果一段程式碼會長時間不還執行緒(重計算、同步 I/O),就用 `spawn_blocking` 包起來。**

## 範例程式碼

```rust,ignore
use tokio::time::{sleep, Duration};

async fn fetch(name: &str, secs: u64) -> String {
    sleep(Duration::from_secs(secs)).await; // 假裝在等網路
    format!("{} 的資料", name)
}

#[tokio::main]
async fn main() {
    // 同時抓三個來源(各自借用了字串字面值,不需要 Send + 'static)
    let (a, b, c) = tokio::join!(
        fetch("使用者", 2),
        fetch("訂單", 1),
        fetch("商品", 3),
    );
    println!("{a} / {b} / {c}"); // 約 3 秒(最久的那個),不是 2+1+3=6 秒
}
```

## 重點整理

- `join!` 並行推進多個 future,**全部完成**後回傳一個結果 tuple——是第 9 集手寫 `Join` 的成品版
- `join!` 在**同一個 task** 裡多工(不像 `spawn` 變獨立 task、跨執行緒),所以 future **不需要 `Send + 'static`**,適合固定數量、就地的並行
- `try_join!`:任一分支回 `Err` 就提早回傳該錯誤(`join!` 一定等全部)
- `join!` 的並行**不是 CPU 平行**;某個分支若長時間不 `.await`(重計算或同步 blocking 呼叫),會卡住整條執行緒
- **不要在 async 裡做 blocking 的事**;真的得做,就用 `tokio::task::spawn_blocking` 丟到專用執行緒池
