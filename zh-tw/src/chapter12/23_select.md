# `tokio::select!` 與取消（cancellation）

## 本集目標

用 `select!` 同時等多件事、誰先好就處理誰,並認識 async 一個關鍵特性——**取消(cancellation)**。

## 概念說明

### `join!` 等全部,`select!` 等第一個

`join!` 是「我要這幾件事**全部**做完」。但很多時候你要的是相反:「這幾件事,**誰先好我就先處理誰**」。例如「等網路回應,但最多等 5 秒」——是「網路回來」和「5 秒到了」在比快。這種「比快、取第一個」用 `select!`:

```rust,ignore
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let work = async {
        sleep(Duration::from_secs(5)).await;
        "工作完成"
    };
    let timeout = async {
        sleep(Duration::from_secs(2)).await;
        "逾時了"
    };

    // 兩個一起等,誰先好就跑哪個分支
    tokio::select! {
        result = work => println!("{}", result),
        result = timeout => println!("{}", result), // 2 秒先到,走這裡
    }
}
```

`select!` 同時推進每個分支的 future,只要**第一個**完成,就執行它對應的處理程式碼,然後——這是重點——**其他還沒完成的分支,直接被丟掉(drop)**。

### 被丟掉的 future = 被取消

上面那個 5 秒的 `work`,在 2 秒的 `timeout` 先完成後,就被 drop 了。一個 future 被 drop,代表它**從此不會再被 poll**,它的工作就停在那裡、永遠不會完成了。這就是 **取消(cancellation)**。

這是 async 和執行緒很不一樣的地方,值得停下來體會:

> 在第 8 章,一條執行緒一旦開始跑,你**沒有**乾淨的辦法從外面把它喊停。但一個 future 是惰性的、靠別人 poll 才前進——所以你只要**不再 poll 它(把它 drop 掉)**,它就停了。取消一個 async 工作,就只是丟掉它的 future 這麼簡單。

`select!` 天生就帶來取消:沒搶贏的分支自動被取消。這也是為什麼「逾時」在 async 裡這麼自然——你不需要真的去中斷那個工作,只要讓「計時器」這個 future 贏,工作的 future 自然就被丟掉了。

### `select!` 的常見場景

`select!` 適合任何「同時等好幾種事件,處理最先發生的那個」:

- **逾時**:工作 vs 計時器(上面的例子)。
- **等多個來源**:同時等好幾個 channel(第 26 集),誰先送來就處理誰。
- **等關機訊號**:一邊做正常工作,一邊等「該關機了」的通知,收到就收尾離開。
- **比快**:同時向兩個伺服器要同一份資料,用先回來的那個。

### 幾個補充功能

`select!` 還有一些好用的細節,先知道有就好:

- **分支條件(precondition)**:可以在分支前加 `if 條件`,條件不成立時這個分支不參與這次競爭。
- **`else`**:當所有分支都「沒得選了」(例如對應的 channel 都關了),走 `else`。
- **公平性**:`select!` 預設會**隨機**挑選順序,避免某個分支老是被優先,造成別的分支餓死。你可以在最前面加 `biased;` 改成「永遠由上到下依序檢查」。

### 一個要小心的坑:loop 裡的 `select!` 與取消安全

`select!` 常和 `loop` 一起用,反覆地等事件。但既然沒搶贏的分支每一輪都會被 drop(取消),你要確定那些分支裡的 future 被「中途丟掉」是安全的——也就是它不會因為被取消在半途,而搞壞什麼狀態(例如讀到一半的資料就這樣丟了)。這個性質叫 **cancellation safety(取消安全)**。

```rust,ignore
// 示意:在 loop 裡反覆等兩種事件
loop {
    tokio::select! {
        msg = receive_message() => { /* 處理訊息 */ }
        _ = shutdown_signal() => { break; } // 收到關機訊號,離開迴圈
    }
}
```

判準先記個大方向:**不要把「中途被丟掉會出問題」的 future 放進會反覆被取消的 `select!` 分支。** 哪些操作是取消安全的、哪些不是,各家 API 的文件通常會註明。下一章(實作層面)和第 24 集講 I/O 時會再碰到這個概念,現在先有個警覺即可。

## 範例程式碼

```rust,ignore
use tokio::time::{sleep, Duration};

async fn fetch_from(server: &str, secs: u64) -> String {
    sleep(Duration::from_secs(secs)).await;
    format!("來自 {} 的回應", server)
}

#[tokio::main]
async fn main() {
    // 同時問兩台伺服器,用先回來的那個,慢的那個自動被取消
    let answer = tokio::select! {
        a = fetch_from("A", 3) => a,
        b = fetch_from("B", 1) => b, // B 比較快,贏
    };
    println!("{}", answer); // 來自 B 的回應(A 的請求被丟掉、取消了)
}
```

## 重點整理

- `select!` 同時等多個分支,**第一個**完成就執行它的處理程式;其他未完成的分支被 **drop**
- 一個 future 被 drop = 不再被 poll = **取消(cancellation)**;這是 async 特有、執行緒做不到的乾淨喊停
- `select!` 天生帶來取消,所以逾時、比快、等關機訊號這些都很自然
- 補充功能:分支 `if` 條件、`else`(全部沒得選時)、預設隨機公平、`biased;` 改成依序
- 在 `loop` 裡用 `select!` 要注意 **cancellation safety**:別把「中途被丟掉會壞掉」的 future 放進會反覆被取消的分支
