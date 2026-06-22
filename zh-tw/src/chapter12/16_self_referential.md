# 自我參照的 Future

## 本集目標

理解為什麼有些 future 一旦開始跑，就**不能被搬動（move）**——問題出在它可能變成「自己指向自己」的結構。

## 概念說明

### 一個再普通不過的 async 函數

先看一段完全正常、你可能天天會寫的程式：

```rust,ignore
async fn example() {
    let s = String::from("hello");
    let r = &s;        // 借用區域變數 s
    something().await; // 在這裡暫停
    println!("{}", r); // 暫停回來後，還要用 r
}
```

這裡 `r` 是一個指向 `s` 的參考。`.await` 之後還用到 `r`，所以 `r`（和它指向的 `s`）必須**活過那個暫停點**。

### 把它放進狀態機看看

回想第 15 集：跨 `.await` 還會用到的區域變數，都要存進狀態機的欄位。這裡 `.await` 之後同時用到 `s`（被 `r` 指著）和 `r`，所以**兩個都要存**。狀態機在「卡在 `something().await`」這個狀態時，大致長這樣：

```rust,ignore
struct ExampleAtAwait {
    s: String,    // 字串本體
    r: &String,   // 指向上面那個 s ——指向「自己的另一個欄位」！
    fut: SomethingFuture,
}
```

注意 `r` 這個欄位:它是一個參考，而且指向的正是**同一個 struct 裡的 `s` 欄位**。換句話說，這個 struct 裡有一個欄位指著自己的另一個欄位。這種結構就叫**自我參照(self-referential)**。

(這裡的 `r: &String` 是示意——真實的生命週期標注更複雜，重點是「`r` 指向 `s` 的記憶體位址」。)

### 先確認一件事：move 會換位址

在講為什麼出問題之前，先用一段**完全沒有 async** 的普通程式，確認一件很多人沒特別注意過的事:**把一個值 move 到別的地方,它的記憶體位址就變了。**

```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p1 = Point { x: 1, y: 2 };
    println!("p1 的位址：{:p}", &p1);

    let p2 = p1; // 把 p1 move 進 p2
    println!("p2 的位址：{:p}", &p2);
}
```

跑起來會印出兩個**不一樣**的位址,例如:

```text
p1 的位址：0x7ffd...a10
p2 的位址：0x7ffd...a18
```

`let p2 = p1;` 看起來只是「換個名字」,但實際上 Rust 把 `Point` 的 bytes 從 `p1` 的位置複製到 `p2` 的新位置,`p1` 之後就不能再用了。**搬動(move)＝把 bytes 搬到新位址。** 傳進函數、推進 `Vec`、塞進 `Box`……這些動作背後都可能發生這種搬動。

平常這完全不是問題:`p1` 用不了,`p2` 接手,裡面的 `x`、`y` 跟著一起搬,數值都對得上,Rust 也會擋住你誤用 `p1`。

**真正會出問題的,是當這個值「裡面存了一個指向自己的位址」的時候。** 一搬家,那個存起來的位址沒人幫它更新,就會繼續指著舊地方——而我們剛剛那個自我參照的 future 狀態機,正好就是這種值。

### 親手 poll、move、再 poll

把「move 會換位址」這件事搬到 future 上。我們手寫一個最小的 future（自己寫 `poll`），然後對它做「**建立 → poll → move → 再 poll**」，親眼看它在兩次 poll 之間被搬到新位址：

```rust
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};

// 自己手寫 poll：每次被 poll 就 +1，並印出「自己現在在哪」
struct Counter {
    count: u32,
}

impl Future for Counter {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        self.count += 1;
        println!("poll 第 {} 次，self 在 {:p}", self.count, &*self);
        if self.count >= 2 {
            Poll::Ready(())
        } else {
            Poll::Pending
        }
    }
}

fn main() {
    let waker = Waker::noop();
    let mut cx = Context::from_waker(waker);

    let mut fut = Counter { count: 0 };

    // poll 一次（Counter 沒有自我參照、是 Unpin，所以能用 Pin::new 安全地拿到 Pin<&mut>）
    let _ = Pin::new(&mut fut).poll(&mut cx);

    // 在兩次 poll 之間，把 future move 到別的變數
    let mut moved = fut;

    // 再 poll 一次——這次 self 的位址不一樣了
    let _ = Pin::new(&mut moved).poll(&mut cx);
}
```

跑起來會看到兩次 poll 的 `self` 位址**不同**：

```text
poll 第 1 次，self 在 0x7ffd...a10
poll 第 2 次，self 在 0x7ffd...a18
```

也就是說，「poll 一次 → move → 再 poll」是真的做得到、也跑得起來的——而且第二次 poll 時，這個 future 已經在**新位址**了。

這裡之所以安全，是因為 `Counter` 裡**沒有任何指向自己的指標**：搬家只是把 `count` 這個數字挪到新位置，下一次 poll 照常運作。

但請想像 `self` 換成上面那個**自我參照**的狀態機（有個 `r` 指著自己的 `s`）：第一次 poll 把自我參照建立起來（`r` 記下 `s` 的位址），接著我們 move 它、再 poll——`r` 還指著**舊位址**，`s` 卻已經搬走了。同一段「poll → move → poll」就會踩到懸垂指標。

（上面能用 `Pin::new(&mut fut)`，**只因為 `Counter` 是 `Unpin`**。換成自我參照的 future 就不是這樣了——下一段直接示範。）

### 換成「跨 `.await` 的借用」：連編譯都過不了

那如果 `self` 真的是自我參照的 future 呢？把上面那套 poll／move／poll 原封不動套到一個**跨 `.await` 借用**的 `async fn` 上：

```rust,ignore
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Waker};

async fn other() {}

async fn borrows_across_await() {
    let s = String::from("hello");
    let r = &s;          // 借用區域變數
    other().await;       // 在這裡暫停，r 跨過 .await
    println!("{}", r);   // 暫停回來還要用 r
}

fn main() {
    let waker = Waker::noop();
    let mut cx = Context::from_waker(waker);

    let mut fut = borrows_across_await();
    let _ = Pin::new(&mut fut).poll(&mut cx);   // ❌ 編譯不過

    let mut moved = fut;
    let _ = Pin::new(&mut moved).poll(&mut cx); // ❌ 編譯不過
}
```

這次**連編譯都過不了**，錯誤大致是：

```text
error[E0277]: `{async fn body of borrows_across_await()}` cannot be unpinned
   |
   | let _ = Pin::new(&mut fut).poll(&mut cx);
   |         -------- ^^^^^^^^ the trait `Unpin` is not implemented for ...
   |
   = note: consider using the `pin!` macro
           consider using `Box::pin` ...
note: required by a bound in `Pin::<Ptr>::new`
```

關鍵就是那句 **`the trait Unpin is not implemented`**：`Pin::new` 要求型別是 `Unpin`，而 `borrows_across_await` 這種**跨 `.await` 借用**的 future **不是 `Unpin`**。所以你根本拿不到它的 `Pin<&mut>`，也就**無從**對它做「poll → move → poll」——型別系統在你還沒搬之前就先把路擋住了。

對照前一段的 `Counter`（沒有自我參照、是 `Unpin`，可以隨便 `Pin::new`、隨便 move），就看出 Rust 的防線：**只有「搬了也不會壞」的 future 才放行用 `Pin::new` 自由搬；「搬了會壞」的自我參照 future，連門都不給你進。** 這正是 `Pin` / `Unpin` 在做的事（`Unpin` 第 18 集細講）。

### 為什麼自我參照怕被 move

剛剛示範的「搬家就換位址」,對整數、`String` 這些一般值都沒差(第 4 章),Rust 會把舊變數標記成不能用,一切照常。

但自我參照的 struct 一旦被 move 就會出大事。假設這個 struct 原本在記憶體位址 `0x1000`,裡面的 `s` 也就在 `0x1000` 附近,而 `r` 存的值是「`s` 的位址 = `0x1000`」。現在我們把整個 struct move 到 `0x2000`:

- `s` 的內容被搬到 `0x2000`。
- `r` 的內容(那個位址值)被**原封不動複製**過去,還是 `0x1000`。

於是 move 之後,`r` 還指著 `0x1000`——但 `s` 已經不在那裡了!`r` 變成了一個指向舊位址的**懸垂指標**。之後 `println!("{}", r)` 就會讀到垃圾,這正是 Rust 拼了命要防止的記憶體不安全。

### 所以結論是

- `async fn` / `async` 區塊產生的 future,因為背後是狀態機,**有可能**包含跨 `.await` 的借用,於是**有可能變成自我參照**。
- 自我參照的 future,一旦**開始被 poll**(裡面的自我參照真的建立起來了),就**不能再被 move**,否則內部指標會懸空。
- 但在開始 poll 之前,它還沒建立任何自我參照,這時候 move 是安全的(例如你 `let fut = example();` 之後把它傳給別人、放進 `Box`,都還好)。

這就帶出一個兩難:future 必須能被 poll(executor 要拿到它的 `&mut` 才能推進),但**開始 poll 之後又不能被 move**。Rust 要怎麼在型別系統裡同時滿足「可以改它」和「不准搬它」?

這個看似矛盾的需求,正是下一集 `Pin` 要解決的問題。現在你終於知道 `poll` 的簽名裡那個一直當黑盒子的 `Pin<&mut Self>` 是為了什麼了——它就是「給你一個能改、但不准搬」的存取權。

## 範例程式碼

這一集主要講編譯器內部的結構;能直接跑的有兩段：`Point` 那段證實「move 會換位址」，`Counter` 那段更進一步示範「poll → move → 再 poll」——兩次 poll 的 `self` 位址不同。其餘可以記住這個對照:

```text
async fn 裡的寫法                  狀態機裡變成
──────────────────────────        ──────────────────────────
let s = ...;                       一個欄位 s
let r = &s;  (跨 .await 還用到)     一個欄位 r,指向同 struct 的 s
                                   → 自我參照 → 開始跑之後不能 move
```

## 重點整理

- 一般程式也能觀察到:把值 move 到別處(`let p2 = p1`)位址就會變——平常無所謂,但「值裡存了指向自己的位址」時就會出事
- 手寫一個 future、做「poll → move → 再 poll」會發現兩次 poll 的 `self` 位址不同；對沒有自我參照的 `Counter` 無害
- 換成「跨 `.await` 借用」的 `async fn`，同一套 poll／move／poll **連編譯都過不了**（`the trait Unpin is not implemented`）：`Pin::new` 只收 `Unpin`，而自我參照 future 不是 `Unpin`——Rust 在你搬它之前就先擋下（`Unpin` 第 18 集）
- 跨 `.await` 的借用,會讓狀態機裡出現「一個欄位指向自己另一個欄位」的**自我參照**結構
- move 一個值 = 把 bytes 複製到新位址;自我參照的 struct 被 move 後,內部指標仍指著舊位址 → **懸垂指標**、記憶體不安全
- 所以這種 future **一旦開始被 poll,就不能再被 move**(開始 poll 之前 move 還是安全的)
- 這造成兩難:executor 要能 `&mut` 它來 poll,但又不能搬它——`Pin`(下一集)就是來解決這個矛盾的
- `poll` 簽名裡的 `Pin<&mut Self>`,就是「能改、但不准搬」的存取權
