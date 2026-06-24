# `join!`

## 本集目標

用 tokio 內建的 `join!` 讓多個 future 並行,不用自己手寫第 9 集那個 `Join`;並看清 `join!` 的並行是「一條執行緒上輪流」、不是 CPU 平行——一個分支若霸佔執行緒,會連兄弟分支一起拖住(這正是第 22 集「不要 block worker 執行緒」的具體案例)。

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

### 為什麼 `join!` 是巨集

`join!` 跟前面的 `pin!` 一樣是巨集，不是函式。原因和第 9 集的 `JoinAll` 一對照就清楚了。

第 9 集手寫的 `JoinAll` 吃的是一個 `Vec<F>`——**同一種型別、數量可以在執行期變動**。這種「同型別、動態數量」用一般的 struct／函式就能表達。

但 `join!(a, b, c)` 剛好是相反的情況：

- **每個 branch 的型別可以不一樣**：`a`、`b`、`c` 可以是三個完全不同型別的 future，輸出型別也各異；
- **回傳值是一個 tuple，形狀跟你傳幾個、傳什麼一一對應**：`join!(a, b, c)` 回 `(A::Output, B::Output, C::Output)`；
- **數量任意**：`join!(a)`、`join!(a, b)`、`join!(a, b, c, d, …)` 都行。

Rust 的**函式不能 variadic（參數個數不固定）**，更不可能「參數個數任意、每個型別不同、還回傳一個形狀隨之變化的 tuple」。要支援這種寫法，要嘛替每個數量各寫一個函式（`join`、`join3`、`join4`……，很醜又有上限），要嘛用**巨集**——`join!` 是後者：它在編譯期看你實際傳了幾個 future、各是什麼型別，**生成**一段「把這些 branch 釘好、輪流 poll、各自記錄完成了沒、最後湊成對應 tuple」的程式碼。

對照記：

```text
第 9 集 JoinAll：同型別、數量動態（執行期 Vec）        → 一般 struct／函式就行
join!         ：異型別、數量固定（編譯期，回傳對應 tuple） → 必須巨集
```

（`try_join!` 同理——一樣是不定數量、異型別，所以也是巨集。）

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

### 重要警告:並行 ≠ CPU 平行

這是非常容易誤會的一點。`join!` 的並行,是「在**同一顆 task、同一條執行緒**上輪流推進各分支」,**不是**讓 CPU 同時開好幾顆核心算(那叫平行,parallelism)。實際上 `join!` 在自己被 `poll` 的那一次裡,會把各分支**一個接一個**地 `poll` 過去;一個分支回 `Pending` 才換下一個。

這帶來一個直接後果:如果你 `join!` 的某個分支裡做了一件**長時間不 `.await`** 的事——一個跑很久的純計算迴圈,或一個**會卡住的同步呼叫**——那這個分支會把執行緒**霸佔住**,在它做完之前,**同一個 `join!` 裡的其他分支連被 `poll` 的機會都沒有**,全被它拖住。你以為寫了 `join!` 就會「同時發生」,結果一個 block 的分支就讓並行的假象破功。

這其實就是第 22 集那條「**不要 block 住 worker 執行緒**」原則在 `join!` 上的具體案例——只是這裡被拖住的不只是別的 task,還包括你 `join!` 在一起的兄弟分支。要在 async 裡做不得不做的 blocking 工作,一樣是用第 22 集的 `tokio::task::spawn_blocking` 把它隔離出去。

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
- `join!` 是**巨集**不是函式：因為它要吃「任意數量、各自不同型別」的 future，回傳一個形狀對應的 tuple——Rust 函式不能 variadic，只有巨集能在編譯期按你傳的 branch 生成程式碼（對照第 9 集 `JoinAll` 是「同型別、動態數量」，用一般 struct 就行）
- `try_join!`:任一分支回 `Err` 就提早回傳該錯誤(`join!` 一定等全部)
- `join!` 的並行**不是 CPU 平行**:各分支在**同一顆 task、同一條執行緒**上被輪流 `poll`;某分支長時間不 `.await`(重計算或同步 blocking 呼叫)會連兄弟分支一起卡死——這是第 22 集「不要 block worker 執行緒 / `spawn_blocking`」在 `join!` 上的具體後果
