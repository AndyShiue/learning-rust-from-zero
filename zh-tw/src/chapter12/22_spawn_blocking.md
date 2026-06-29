# `spawn_blocking`

## 本集目標

學會「不要 block 住執行緒」這條紀律，以及碰到非得 block 的工作時，用 `spawn_blocking` 把它安置好。

## 正文

### 一條鐵律：不要 block 住執行緒

`async` 能用少少幾條執行緒推進大量工作，靠的是大家**輪流**——每個 `Task` 跑到 `.await` 就能讓出執行緒，換別人跑。執行緒只有在 `.await` 的時候才會被讓出。

這就帶出一條鐵律：**一個 `Task` 不能長時間不 `.await`**。如果某個 `Task` 卡著執行緒不放——可能是在做一個很重的計算（幾秒的數學運算），也可能是呼叫了某個**同步**的阻塞函式（`std::thread::sleep`、同步讀檔、慢的同步資料庫呼叫）——那它就霸佔了這條執行緒，**同一條執行緒上的其他 `Task` 全都得不到 `poll`**，整個並行就卡死了。

舉個不好的示範：

```rust,no_run
# extern crate tokio;
#
#[tokio::main]
async fn main() {
    // 在 async task 裡做很重的同步計算——壞示範
    let sum: u64 = (0..2_000_000_000u64).sum(); // 這段期間完全沒有 .await
    println!("總和：{}", sum);
}
```

這段計算從頭到尾沒有 `.await`，所以它會霸佔執行緒直到算完，期間 runtime 沒辦法去推進任何其他 `Task`。

### 解法：`spawn_blocking`

碰到這種「非 block 不可」的工作，解法是 `tokio::task::spawn_blocking`。它把工作丟到一個**專用的 blocking 執行緒池**去做（那個池子裡的執行緒就是設計來被卡住的），回傳一個可以 `.await` 的 handle：

```rust,no_run
# extern crate tokio;
#
#[tokio::main]
async fn main() {
    let handle = tokio::task::spawn_blocking(|| {
        // 重計算丟到專用的 blocking 池裡做
        (0..2_000_000_000u64).sum::<u64>()
    });

    // 你的 Task 在這裡 .await，會讓出執行緒，等計算好了再被喚醒
    let sum = handle.await.expect("blocking task 失敗");
    println!("總和：{}", sum);
}
```

關鍵在於：因為你用 `.await` 等那個 handle，你自己的 `Task` 會**乖乖讓出**執行緒，runtime 可以拿去推進別的 `Task`；等 blocking 池那邊算好了，再把你喚醒。慢的計算被隔離在專用池裡，不會拖累負責 `async` 工作的 `Thread`。

（順帶一提：想在 `async` 裡「睡一下」，別用 `std::thread::sleep`，那會 block 住執行緒；要用 `tokio::time::sleep(...).await`，它是 `async` 的，會乖乖讓出執行緒。）

### 為什麼不乾脆用 `std::thread::spawn`

你可能會問：要把工作丟到別條 `Thread`，多執行緒章不是有 `std::thread::spawn` 嗎？

問題出在「怎麼拿回結果」。`std::thread::spawn` 給你的 `JoinHandle`，要拿結果得呼叫 `.join()`——而 `.join()` 是**阻塞**的，它不是 `async`、不能 `.await`。如果你在 `async` 裡呼叫 `.join()`，就又把執行緒卡住了，繞回原來的問題。

`spawn_blocking` 的價值，是它把「同步工作在 blocking 池做完後，通知正在 `.await` 的 `async` `Task` 繼續跑」這件事包好了。你不用自己拿 `std::thread::JoinHandle` 去 `.join()`，也不用自己接 `Waker`；只要對它回傳的 handle `.await`，`Task` 就會先讓出執行緒，等結果好了再被喚醒。

### 但長命的背景執行緒還是該用 `thread::spawn`

最後值得提的是：`spawn_blocking` 適合的是**會結束**的一次性工作。如果你要的是一條**長命的獨立背景執行緒**（例如一個跑著無窮迴圈，整個程式生命週期都在的監聽器），那還是該用 `std::thread::spawn`。

為什麼？因為 blocking 池的空間有限。把一個無窮迴圈丟進 `spawn_blocking`，它會**永久佔住**池子裡的一個名額再也不還，這屬於誤用——久了池子被佔滿，真正需要它的短工作就排不進去了。

## 重點整理

- 鐵律：執行緒只在 `.await` 時能被讓出，所以 `Task` 不能長時間不 `.await`，否則會霸佔執行緒、拖住同條執行緒上的其他 `Task`
- 昂貴計算、同步阻塞呼叫（`thread::sleep`、同步 I/O、慢的同步 DB）都會 block 住執行緒
- `tokio::task::spawn_blocking` 把這種工作丟到專用 blocking 池，回傳可 `.await` 的 handle，你的 `Task` 因此會讓出執行緒
- 不用 `std::thread::spawn` 是因為它的 `.join()` 是阻塞的、不能 `.await`；`spawn_blocking` 幫你接好了「做完 → 喚醒 `Task`」這座橋
- 但長命的獨立背景執行緒仍該用 `thread::spawn`；把無窮迴圈丟進 `spawn_blocking` 會永久佔住池子名額，是誤用
