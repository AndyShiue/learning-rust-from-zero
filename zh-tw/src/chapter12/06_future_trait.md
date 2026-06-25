# `Future` trait 與最陽春的 executor

## 本集目標

打開 future 的蓋子，看看 `Future` trait 長什麼樣子，並親手寫一個最笨的 executor 把 future 推到完成。

## 概念說明

### Future 其實是個 trait

前幾集我們一直說「future 是一個代表還沒做的事的東西」。現在揭曉：future 之所以是 future，是因為它實作了標準庫的 `Future` trait。它的核心長這樣：

```rust,ignore
pub trait Future {
    type Output; // 這個 future 完成後會給出什麼型別的結果

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
```

`Output` 是一個 associated type（第 5 章學過），代表「這件事做完之後產出的值的型別」。例如一個「讀檔案」的 future，`Output` 可能是 `String`。

重點是 `poll` 這個方法。它就是「**推進一次**」的意思——你呼叫一次 `poll`，這個 future 就往前走一小段。

`poll` 的回傳值是一個叫 `Poll` 的 enum，只有兩種可能：

```rust,ignore
pub enum Poll<T> {
    Ready(T),   // 做完了！結果在這裡
    Pending,    // 還沒好，等等再來推我一次
}
```

所以推進一個 future，結果不是「好了，拿去」（`Ready`），就是「還沒好，待會再來」（`Pending`）。

### 先別管 `Pin` 和 `Context`

`poll` 的簽名裡有兩個現在還看不懂的東西，先當黑盒子：

- `self: Pin<&mut Self>`：你可以暫時把 `Pin<&mut Self>` 想成「一種包裝過的 `&mut self`」。為什麼要包這一層，第 17 集會解釋，現在只要知道 `poll` 是借用這個 future 來推進它。
- `cx: &mut Context<'_>`：這裡面裝著一個叫 **Waker**（喚醒器）的東西。當 future 回傳 `Pending`、之後又好了的時候，要靠這個 Waker 通知別人「我好了，再來 poll 我」。第 10 集會詳細用到它，現在先放著。

你可能會愣一下：`self` 不是只能寫成 `self`、`&self`、`&mut self` 嗎？怎麼能寫成 `self: Pin<&mut Self>`？這其實是因為 `Pin` 是一個**很特別的型別**。Rust 規定方法的 `self` 位置只能放一小撮「智慧指標類」的型別——除了最常見的 `self`／`&self`／`&mut self`，就只有 `Box<Self>`、`Rc<Self>`、`Arc<Self>`，以及 `Pin<...>` 這幾種。你自己隨手定義的型別**不能**這樣擺在 `self` 位置；`poll` 能寫成 `self: Pin<&mut Self>`，正是沾了 `Pin` 被列入這份特別名單的光。

### 最笨的 executor：一直 poll 到好為止

知道 `poll` 之後，我們就能自己寫一個 **executor**（執行器）——一個負責「不斷推進 future 直到它完成」的東西。最笨的寫法就是用一個迴圈，一直 poll，`Pending` 就再來一次，直到 `Ready`：

```rust,ignore
use std::future::Future;
use std::task::{Context, Poll, Waker};

fn run<F: Future>(future: F) -> F::Output {
    // Box::pin 把 future 放到 heap 上並「釘住」，得到一個 Pin<Box<F>>
    // （為什麼要釘、Pin 是什麼，第 16、19 集會講；這裡先看型別就好）
    let mut future = Box::pin(future);

    // 一個什麼都不做的假 Waker，這一集先用它頂著
    let waker = Waker::noop();
    let mut cx = Context::from_waker(waker);

    loop {
        // as_mut() 從 Pin<Box<F>> 借出一個 Pin<&mut F>，正是 poll 要的型別
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value, // 好了，回傳結果
            Poll::Pending => {
                // 還沒好——這個笨 executor 直接再 loop 一次，繼續猛 poll
            }
        }
    }
}
```

這個 `run` 就是一台迷你 runtime 了。它做的事和 `#[tokio::main]` 背後做的是同一類：把一個 future 推到完成、拿到結果。

### `Box::pin` 和 `as_mut` 的 signature

剛剛用到的兩個方法，看它們的型別簽名就懂在做什麼了。

先看 `Box::pin`：

```rust,ignore
impl<T> Box<T> {
    pub fn pin(x: T) -> Pin<Box<T>>
}
```

它把一個值 `x: T` 吃進去，回傳 `Pin<Box<T>>`——白話就是「把這個值放到 heap 上（`Box`，第 5 章），再用 `Pin` 釘住」。`poll` 需要一個被 `Pin` 包住的東西，`Box::pin` 一步幫你弄好。（`Pin` 為什麼存在，第 17 集；`Box::pin` 的細節與它和遞迴的關係，第 20 集。這裡先把 `Pin<Box<T>>` 讀成「一個釘住的盒子」。）

再看 `Pin::as_mut`：

```rust,ignore
impl<Ptr: DerefMut> Pin<Ptr> {
    pub fn as_mut(&mut self) -> Pin<&mut Ptr::Target>
}
```

對我們手上的 `Pin<Box<F>>` 來說，`Ptr` 是 `Box<F>`、`Ptr::Target` 是 `F`，所以這個 `as_mut` 實際上是：

```rust,ignore
// 對 Pin<Box<F>> 而言
fn as_mut(&mut self) -> Pin<&mut F>
```

也就是從「**擁有** future 的 `Pin<Box<F>>`」借出一個「**指向**它的 `Pin<&mut F>`」。為什麼每次 poll 都要先 `as_mut`？因為 `poll` 的 `self` 型別是 `Pin<&mut Self>`（看前面 `Future` trait 的簽名），它要的就是 `Pin<&mut F>`；而我們手上是 `Pin<Box<F>>`，得先借出 `Pin<&mut F>` 才接得上。`as_mut` 是**借用**，所以借完 `future` 還在，下一輪可以再借、再 poll——這正是 `loop` 能反覆 poll 同一個 future 的原因。

### 試跑看看

```rust,ignore
# use std::future::Future;
# use std::task::{Context, Poll, Waker};
#
# fn run<F: Future>(future: F) -> F::Output {
#     let mut future = Box::pin(future);
#     let waker = Waker::noop();
#     let mut cx = Context::from_waker(waker);
#     loop {
#         match future.as_mut().poll(&mut cx) {
#             Poll::Ready(value) => return value,
#             Poll::Pending => {}
#         }
#     }
# }
fn main() {
    // 不需要 #[tokio::main]，我們用自己的 executor
    let result = run(async {
        println!("async 區塊在我們自己的 executor 上跑");
        1 + 2
    });
    println!("結果：{}", result);
}
```

我們沒有用 tokio，卻成功把一個 `async` 區塊跑到完成了——因為 executor 要的只是一個實作了 `Future` 的東西，而 `async` 區塊正是。

### 這個笨 executor 笨在哪

它能動，但有個明顯的問題：遇到 `Pending` 時，它**瘋狂空轉**，一遍又一遍地 poll，把 CPU 燒好燒滿。聰明的做法應該是「先睡著，等 future 真的好了再被叫醒」——而「叫醒」這件事，靠的就是我們剛剛跳過的那個 Waker。接下來幾集，我們會一步步把這台引擎變聰明。

### executor 有很多種設計選擇

不過先講清楚一件事：我們寫的只是「最笨」的那一種，但 executor **沒有標準答案**。標準庫只規定了 `Future` / `poll` 這個**介面（契約）**：「給你一個 future，你負責一直 poll 到它 `Ready`」。至於**怎麼做到**，完全留給每個 runtime 自由發揮——而且選擇非常多。光是下面這幾件事，每一件都是一個設計上的取捨：

- **遇到 `Pending` 怎麼辦？** 本集直接空轉再 poll；聰明的做法是睡著、等 `Waker` 把自己叫醒（第 10 集）。
- **怎麼睡、怎麼被叫醒？** 可以用標準庫的 `thread::park` / `unpark`（第 10、11 集），也可以用作業系統的事件機制。
- **一次只顧一個 future，還是同時管很多 task？** 我們的 `run` 只推一個 future 到完成；真正的 runtime 要同時養很多 task，於是需要一個 **ready queue** 讓 task 排隊（第 11 集）。
- **單執行緒還是多執行緒？** 本章手寫的都是單執行緒；Tokio 預設用多條 worker thread，還會在 thread 之間搬移 task（work-stealing）來平衡負載（第 21 集）。
- **怎麼等 I/O？** 每個等待各開一條 thread 是權宜之計（第 10 集）；用一條 **reactor** thread 同時盯住成千上萬個 I/O 來源才是正解（第 14 集）。

正因為這些都是「選擇」而不是「定論」，Rust 標準庫**乾脆不內建 runtime**，只定義 `Future` 這個共通介面，把 executor、reactor、排程策略統統留給社群——這就是為什麼會有 Tokio、smol 等不同 runtime，各自做不同取捨（第 34 集）。

所以接下來幾集，我們就是從這台「最笨」的版本出發，一步步把上面這些選擇補進去，最後長成一個更接近真實 runtime 的樣子。

### 老實說：到目前為止的 async 都「沒在等東西」

這裡要坦白一件事：從第 3 集到這一集，我們寫的 async 程式——`async { 1 + 2 }`、印一句話的 `say_hello`、`make_coffee`——其實**都沒在等任何東西**。它們一被 poll 就馬上 `Ready`，從來不會 `Pending`。也就是說，這些 async 程式根本沒用到 async 真正的本事（在等待時把執行緒讓出去），它們存在的唯一目的，就是當**最單純的範例**，讓我們看清楚「future 是什麼」「executor 怎麼推進它」這些機制而已，並不是真正的 async 程式。

下一集（第 7 集）就不一樣了。我們會寫第一個**真的會 `Pending`、真的得等一段時間才完成**的 future——`Delay`。那才開始像真正的 async：有東西還沒好、得等。前面這些「跑一下就結束」的範例，是為了先把機制看懂；接下來才輪到讓這台機器去處理真正的「等待」。

## 範例程式碼

上面的 `run` 加上 `main` 就是一個可以獨立執行的完整範例。它示範了 executor 最核心的骨架：**拿到 future → 不斷 poll → 等到 `Ready` 就收工**。

## 重點整理

- future 之所以是 future，是因為實作了 `Future` trait，核心是 `poll` 方法
- `poll` 是「推進一次」；回傳 `Poll`：`Ready(結果)` 代表做完了，`Pending` 代表還沒好
- `Output`（associated type）是 future 完成後產出的值的型別
- `poll` 簽名裡的 `Pin<&mut Self>`（第 17 集）和 `Context`／`Waker`（第 10 集）先當黑盒子
- `poll` 能把 `self` 寫成 `self: Pin<&mut Self>`，是因為 `Pin` 是少數被允許放在 `self` 位置的特殊型別之一（和 `Box`／`Rc`／`Arc` 一樣）；你自己定義的型別不能這樣用
- 要 poll 一個 future，先用 **`Box::pin`** 得到 `Pin<Box<F>>`（`fn pin(x: T) -> Pin<Box<T>>`），再用 **`Pin::as_mut`** 借出 `Pin<&mut F>`（`fn as_mut(&mut self) -> Pin<&mut F>`）——正是 `poll` 的 `self` 要的型別
- **executor** 就是「不斷 poll 一個 future 直到 `Ready`」的東西；我們用一個 `loop` 就寫出了最陽春的版本
- executor 沒有標準答案：標準庫只定義 `Future`／`poll` 介面，「遇到 `Pending` 怎麼辦、怎麼睡、單還是多執行緒、怎麼等 I/O」全是設計選擇；本章從最笨版本一步步演進到接近真實 runtime，Rust 也因此不內建 runtime（第 34 集）
- 這個笨版本遇到 `Pending` 會空轉燒 CPU；後面會用 Waker 讓它學會「睡著、被叫醒」
- 到此為止（第 3–6 集）寫的 async 都「沒在等東西」、一 poll 就 `Ready`，純粹是示範機制用的；下一集的 `Delay` 才是第一個真的會 `Pending`、更像真正 async 的 future
