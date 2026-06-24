# `spawn_blocking`：在 async 裡做 blocking 工作

## 本集目標

搞懂一條 async 程式的重要紀律——**不要 block 住 worker 執行緒**——以及真的非做不可的同步工作該怎麼用 `tokio::task::spawn_blocking` 處理;順便回答一個很自然的疑問:那為什麼不乾脆 `std::thread::spawn` 就好?

## 概念說明

### 別讓一個 task 霸佔住 worker 執行緒

上一集講過,tokio 預設是 multi-thread runtime:底下有**固定幾條** worker 執行緒,輪流跑著很多 task。worker 推進一個 task 的方式是 `poll` 它,而**一個 task 只會在遇到 `.await` 時才把執行緒讓出來**;`.await` 之間的程式碼,執行緒就一直被它佔著。

所以如果某個 task 做了一件**長時間不 `.await`** 的事——一個跑很久的純計算迴圈,或呼叫了一個**會卡住的同步函式**(像 `std::thread::sleep`、`std::fs` 的同步讀檔、一個慢的同步資料庫呼叫)——它就會把那條 worker 執行緒**霸佔住**。在它做完之前,被排到同一條 worker 上的其他 task 全都**動彈不得**,即使它們早就 ready 了。一條 worker 被卡住,等於這台 runtime 的一部分算力憑空消失。

記住這條原則:**不要在 async 程式裡做會 blocking 執行緒的事。** async 的「讓出執行緒」只發生在 `.await`;一段不 `.await` 的程式碼,對 runtime 來說就是一段「還不回來」的霸佔。

### 真的得做 blocking 工作:`spawn_blocking`

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

    println!("計算結果：{}", result);
}
```

`spawn_blocking` 回傳一個可以 `.await` 的 handle,把「會卡執行緒」的工作隔離到專用的池子,你的 async 主流程就不會被拖垮。判準很簡單——**如果一段程式碼會長時間不還執行緒(重計算、同步 I/O),就用 `spawn_blocking` 包起來。**

### 那為什麼不乾脆 `std::thread::spawn` 就好?

你可能會想:要把卡住的工作丟到別條執行緒,第 8 章的 `std::thread::spawn` 不就能做到了嗎?確實可以,而且有時候那才是對的選擇——但 `spawn_blocking` 解決的是一個 `thread::spawn` 自己處理不漂亮的問題:**怎麼把結果接回 async,而過程中不卡住 worker。**

**核心差別:結果怎麼拿回來。** `std::thread::spawn` 回的是 `std::thread::JoinHandle`,它的 `.join()` 是**阻塞**的,不是 `Future`、不能 `.await`。所以你在 async task 裡如果想拿那條 thread 的結果,只能呼叫 `.join()`——而那會把目前的 worker 執行緒卡住,正好踩回你想避開的坑。要避免,你得自己接一條 channel(像第 12 集那種「完成的一方透過共享狀態通知等待的一方」):thread 算完把結果送出去,async 這邊 `.await` 收。**`spawn_blocking` 就是把這件事打包好**:它回傳一個本身是 `Future` 的 handle,你 `.await` 它,你的 task 就乖乖讓出 worker、等結果好了再被喚醒。其實這跟第 10 集你手寫的東西是同一招——當時是計時 thread 算完用 `Waker` 把 executor 叫醒,`spawn_blocking` 只是把「另一條 thread 做完 → 喚醒等待的 async task」這個橋產品化了。

次要、但實務上很重要的差別還有:

- **執行緒池 vs 每次開新的。** `spawn_blocking` 跑在 tokio 管理的 blocking 執行緒池,執行緒會**重複利用**;`thread::spawn` 每呼叫一次就**建一條全新的 OS 執行緒**、做完再拆掉。對「頻繁、短」的 blocking 呼叫,反覆建拆 OS 執行緒很貴,池子能攤平這個成本。而且池子有**數量上限**,等於有個天花板;`thread::spawn` 放在迴圈裡可以無限開,真的會把系統資源開爆。
- **還在 runtime 的 context 裡。** `spawn_blocking` 的閉包裡仍拿得到 runtime handle,可以再 `tokio::spawn` 等等;裸 `thread::spawn` 開的執行緒在 runtime 之外,要用 tokio 的 API 得自己把 handle 帶進去。

**不過要誠實講反面:`thread::spawn` 有自己的甜蜜點。** `spawn_blocking` 是設計給**有限的、會結束的**離散工作;如果你要的是一條**長命、整個程式都在跑的背景執行緒**(例如專門盯著某個裝置、跑一個 `loop` 一直讀),那 `thread::spawn` 反而更合適——你要是把一個無窮迴圈丟進 `spawn_blocking`,它會**永久佔住池子裡的一條**名額,那是誤用。

一句話總結:**`spawn_blocking` =「一段會結束的 blocking 工作 ＋ 自動接回 async ＋ 池化」;`thread::spawn` =「我就是要一條獨立、(通常)長命的執行緒,結果自己想辦法傳」。** 工作是「短、要把值接回 async 主流程」就用前者;是「長、自成一格、跟 async 流程關係不大」就用後者。

## 範例程式碼

一個常見的實戰情境:在 async 的 web handler 裡,需要呼叫一個**只有同步版本**的函式庫(這裡用一段重計算代替),用 `spawn_blocking` 把它隔離出去,主流程其餘部分照常並行:

```rust,ignore
async fn handle_request(id: u32) -> u64 {
    // 這段同步、耗時的工作丟到 blocking 池,不卡 worker
    let heavy = tokio::task::spawn_blocking(move || {
        let mut sum: u64 = 0;
        for i in 0..200_000_000 { sum += i % (id as u64 + 1); }
        sum
    })
    .await
    .unwrap(); // spawn_blocking 的 handle .await 後是 Result，內層 panic 會變成 Err

    heavy
}

#[tokio::main]
async fn main() {
    // 三個請求同時處理：各自的重計算在 blocking 池裡跑，彼此不卡
    let (a, b, c) = tokio::join!(
        handle_request(1),
        handle_request(2),
        handle_request(3),
    );
    println!("{a} {b} {c}");
}
```

(這裡先用到了下一集才正式介紹的 `join!`,你只要知道它是「同時等這三個」就好。)

## 重點整理

- worker 執行緒是「輪流 `poll` 很多 task」,task 只在 `.await` 時才還執行緒;**長時間不 `.await`(重計算、同步 blocking 呼叫)會霸佔 worker、拖住其他 task**——這就是「不要在 async 裡做 blocking 工作」的原因
- 真的得做 blocking 工作,用 `tokio::task::spawn_blocking` 丟到**專用的 blocking 執行緒池**;它回傳一個可 `.await` 的 handle,所以你的 task 會讓出 worker、等它好了再被喚醒
- **為什麼不直接 `thread::spawn`**:`std::thread::JoinHandle::join()` 是阻塞的、不能 `.await`,拿結果就會卡 worker;`spawn_blocking` 幫你把「另一條 thread 做完 → 喚醒 async task」這座橋接好(同第 10 集 `Waker` 的精神),還附帶池化與數量上限
- 但**長命的獨立背景執行緒**還是用 `thread::spawn`;`spawn_blocking` 是給會結束的離散工作,把無窮迴圈丟進去會永久佔住池子一個名額
