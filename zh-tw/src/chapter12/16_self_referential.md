# 自我參照的 `Future`

## 本集目標

理解 `async` 狀態機為什麼可能變成「自己指向自己」的結構，以及為什麼這種結構被 move 會出事。

## 正文

### move 一個值，它的位址會變

先看一段**完全沒有** `async` 的普通程式。我們用 `{:p}`（印位址的格式）看一個值被 move 前後的位址：

```rust,editable
fn main() {
    let p1 = String::from("hello");
    println!("p1 的位址：{:p}", &p1);

    let p2 = p1; // move：把 p1 搬到 p2
    println!("p2 的位址：{:p}", &p2);
}
```

兩個位址不一樣。這很合理——`p1` 和 `p2` 是兩個不同的區域變數，住在 stack 上不同的地方，move 就是把值從一個地方搬到另一個地方。

對一般的值來說，這完全沒問題：move 之後舊變數 `p1` 就不能再用了（這是第 4 章的所有權規則），所以「舊位址作廢」根本不影響任何人。

### 但如果值裡存了「指向自己的位址」呢

問題出在一種特殊的值：**它的某個欄位，存著一個指向自己另一個欄位的位址**。

想像這種值被 move 到新位置。它內部那個存起來的位址**不會自動更新**——它還指著**舊**位置。可是舊位置的東西已經搬走了，於是這個指標就變成了**懸垂指標**（指向一塊不再有效的記憶體）。一旦有人順著它去讀，就是未定義行為，程式可能讀到垃圾、可能直接爆炸。

那這種「自己指向自己」的值，平常會遇到嗎？會——**自我參照的 `Future` 狀態機正是這種值**。回想上一集：`async fn` 被改寫成狀態機，跨 `.await` 還要用到的區域變數會被存進狀態機裡。如果其中一個區域變數是「另一個區域變數的參考」，那狀態機裡就會有一個欄位指向自己的另一個欄位——標準的自我參照結構。

```rust,ignore
async fn borrows() {
    let s = String::from("hello");
    let r = &s; // r 借用 s
    other().await; // 跨過一個 .await，s 和 r 都得被狀態機保存
    println!("{r}"); // .await 之後還用 r
}
```

這個 `async fn` 的狀態機，在 `.await` 那個狀態裡同時存著 `s` 和 `r`，而 `r` 指向 `s`。這就是自我參照。一旦它被 move，`r` 就會變成懸垂指標。所以結論是：**move 一個 `Future` 是有風險的**。

### 先證明「create → `poll` → move → `poll`」做得出來

不過在談怎麼防範之前，先確認一件事：一個 `Future` 真的可能在「被 `poll` 過之後又被 move、然後再被 `poll`」。我們寫一個最小的 `Future`——`Counter`，每次 `poll` 就把計數 +1，並用 `{:p}` 印出 `self` 的位址：

```rust,editable
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};

struct Counter {
    count: u32,
}

impl Future for Counter {
    type Output = ();

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        this.count += 1;
        println!("第 {} 次 poll，self 在位址 {:p}", this.count, this);
        Poll::Ready(())
    }
}

fn main() {
    let mut cx = Context::from_waker(Waker::noop());

    let mut counter = Counter { count: 0 };
    let _ = Pin::new(&mut counter).poll(&mut cx); // poll 一次

    let mut moved = counter; // move 到新位置
    let _ = Pin::new(&mut moved).poll(&mut cx); // 再 poll
}
```

跑起來會看到兩次 `poll` 印出的位址**不一樣**——證明這套「`poll` → move → 再 `poll`」的流程真的能發生，而且第二次 `poll` 時 `Future` 已經在新位址了。`Counter` 自己沒有自我參照，所以搬了也沒差；但如果換成上面那種自我參照的狀態機，這一搬就出事了。

### Rust 的防線：搬了會壞的，連門都不給進

那 Rust 怎麼防止自我參照的 `Future` 被亂搬？我們把同一套流程，套到剛剛那個「跨 `.await` 借用」的 `async fn` 上試試：

```rust,compile_fail
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Waker};

async fn other() {}

async fn borrows() {
    let s = String::from("hello");
    let r = &s;
    other().await;
    println!("{r}");
}

fn main() {
    let mut cx = Context::from_waker(Waker::noop());
    let mut fut = borrows();

    // 想做跟 Counter 一樣的事：poll 一次
    let _ = Pin::new(&mut fut).poll(&mut cx); // 編譯錯誤！

    // 然後 move 到新位置
    let mut moved = fut;

    // 再 poll 一次
    let _ = Pin::new(&mut moved).poll(&mut cx); // 這裡也不會被放行
}
```

編譯器直接擋下來：

```text
error[E0277]: `{async fn body of borrows()}` cannot be unpinned
```

這段程式碼把「`poll` 一次、move、再 `poll`」的動作都寫出來了，但編譯器其實在第一次 `Pin::new(&mut fut)` 就擋下來。

`Pin::new` 要求型別是 `Unpin`（「搬了不會壞」的意思，後面詳談）。`Counter` 是 `Unpin`，所以放行；但這個自我參照的 `async fn` 狀態機**不是** `Unpin`，於是 `Pin::new` 在你**還沒真的 poll、也還沒真的搬它之前**就把路擋死。

對照兩個例子，Rust 的防線就很清楚了：搬了不會壞的（像 `Counter`），給你方便、隨你搬；搬了會壞的（自我參照狀態機），連 `Pin::new` 這道門都不讓你進。至於 `Pin` 是怎麼用型別系統築起這道防線的，就是接下來的主題。

## 重點整理

- move 一個值，它的位址會變；對一般值無所謂，因為舊變數不能再用
- 若值裡存了「指向自己的位址」，一 move 那個位址沒人更新，就變成懸垂指標——很危險
- **自我參照的 `Future` 狀態機**正是這種值：跨 `.await` 的借用會讓狀態機某欄位指向自己另一欄位
- `Counter` 範例證明「`poll` → move → 再 `poll`」真的做得出來（兩次位址不同）
- Rust 用 `Unpin` 當防線：`Counter` 是 `Unpin` 可被 `Pin::new`，自我參照的 `async` 狀態機不是 `Unpin`，`Pin::new` 直接編譯失敗
