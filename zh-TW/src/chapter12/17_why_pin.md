# 為什麼 `poll` 需要 `Pin`

## 本集目標

弄懂 `poll` 為什麼把 `self` 寫成 `Pin<&mut Self>`，以及 `Pin` 究竟是用什麼手段把「不准 move」這件事變成事實。

## 正文

### `poll` 想要的事

回顧：處於自我參照狀態的 `Future` 一旦被 move，內部那個指向自己的指標就會懸空。

還記得上一集對 `Counter` 做的那一串動作嗎？

```rust,ignore
let _ = Pin::new(&mut counter).poll(&mut cx); // poll 一次
let mut moved = counter; // 用 let 把它整個搬到新位置
let _ = Pin::new(&mut moved).poll(&mut cx); // 再 poll 一次
```

兩次 `poll` 印出的位址不一樣——這證明了一個 `Future` 真的可能「`poll` 過、被搬走、再 `poll`」。`Counter` 沒有自我參照，搬了無所謂；但同一套動作換成自我參照的 `Future`，第二次 `poll` 時它已經躺在新位址，內部那根指向自己的指標就懸空了。

所以負責推進 `Future` 的人（executor）得守住一條規矩：**在一連串 `poll` 之間，不可以把這個 `Future` 搬走**。問題是，`poll` 該收什麼樣的 `self`，才幫得上這條規矩？站在 `poll` 的角度，它同時想要兩個性質：

1. **要能動手腳**：每次 `poll` 都得改 `Future` 內部的欄位（推進狀態機、把進度往前帶），所以它需要某種「可變」的存取權。
2. **但不准搬家**：它不能讓人趁機把整個 `Future` 從原本的位址挪走，不然自我參照就毀了。

現成的工具——普通的 `&mut Self`——只滿足第一個性質。一旦 `poll` 收的是 `&mut Self`，那這個 `Future` 對 executor 來說就只是它手裡一個普通的值，executor 大可在兩次 `poll` 之間像上面那樣 `let moved = ...` 把它搬走，沒有東西攔得住。

所以 Rust 需要一種「能動手腳，但擋住搬家」的 `&mut`。這就是 `Pin<&mut T>`：你可以把它讀成「**一個被綁在原地、不准搬走的 `&mut T`**」。

不過要注意，「不准搬走」不是說這個值從建立開始就不能 move。一個值在被釘住以前，完全可以照一般 Rust 規則搬來搬去；`Pin` 保證的是：當你把需要釘住的值釘住之後，編譯器就不能再讓它被搬走。反正在開始 `poll` 之前，`async` 狀態機裡也還不會有自我指涉的參考；真正危險的是 `poll` 之後狀態機可能建立了自我參照，卻又被搬到別的位置。

### 關鍵：不能留下能搬走內部值的做法

`Pin<&mut T>` 號稱「不准搬走」，但它**憑什麼**做得到？

真正的關鍵有兩個：

1. 建立 `Pin` 的時候，不能留下另一條路讓你之後把值搬走。
2. 拿到 `Pin` 之後，安全 API 不能把能搬走內部值的普通指標交回給你。

先看第一點。

`Pin` 要守住「不准 move」的承諾，不能只看 `Pin` 本身裡面有沒有漏洞，還要看建立 `Pin` 之後，外面是不是仍然留著另一條路能把值搬走。

這就是 `Pin::new(&mut value)` 可疑的地方。`Pin<&mut T>` 只是暫時借用：借用結束後，外面原本那個變數還在，仍然可能被搬走。如果 `Pin::new(&mut value)` 對任何 `T` 都成立，那前面 `Counter` 那種「先 `poll`、再 move、再 `poll`」的流程，就可以原封不動套到一個自我參照的 `Future` 上。

所以對「搬了會壞」的型別來說，`Pin::new(&mut value)` 理應不該隨便成立。沒錯，原則上就是這樣；只是有些型別「搬了也不會壞」，所以 Rust 願意讓它們走這條路。這件事下一集會解釋。

再看第二點。

對 `Pin<&mut T>` 來說，危險的是普通的 `&mut T`。因為只要你拿到 `&mut T`，就能做 `Option::take` 之類的操作：

```rust,ignore
let old = option.take();
```

它不只把 `Some(value)` 變成 `None`，還會把裡面的 `value` 搬出來，回傳成 `Some(value)`。所以如果你有一個被 pin 住的 `Option<Future>`，又讓人從中拿到普通的 `&mut Option<Future>`，對方就可以 `.take()`，把那個 `Future` 從原本位址搬走。

所以對於一個未知的任意 `T`，`Pin<&mut T>` 不會給你普通的 `&mut T`。更一般地說，`Pin<P>` 會小心保護 `P` 這層指標。`P` 可能是 `&mut T`、`Box<T>`，或其他智慧指標。如果 `Pin<Box<T>>` 隨便把裡面的 `Box<T>` 還給你，你就又拿到能操作 `T` 的普通擁有者了，接著就可能把 `T` move 出來。所以對於任意 `T`，`Pin` 的安全 API 不把指向 `T` 的指標直接交回給你，而是只提供幾個不會破壞 pin 保證的操作。

### `Pin` 只有幾招能用

也因為它的任務就是「擋 move」，`Pin` 能讓你做的事不多。一般的用法就是：

**唯讀**——`Pin<P<T>>` 永遠能解參考成 `T`（讀又搬不走值，沒風險），這來自 `Deref`：

```rust,ignore
impl<Ptr: Deref> Deref for Pin<Ptr> {
    type Target = Ptr::Target;
    fn deref(&self) -> &Ptr::Target { /* ... */ }
}
```

**重新借出一根釘住的參考**——`as_mut` 把 `&mut Pin<Box<T>>` 之類的東西借成 `Pin<&mut T>`。`as_mut` 可以一次又一次地被呼叫，因為 `as_mut` 只是借而已，而且借出來的仍然是 `Pin<&mut T>`，不是普通的 `&mut T`。

當然，拿著一個 `Pin<&mut F>`，你還能做最關鍵的一件事——呼叫它的 `poll`。對於 `async fn` 或 `async` block 產生的 `Future`，你不需要自己實作 `poll`；編譯器會替你產生實作。第 6 集 executor 反覆跑的 `future.as_mut().poll(...)` 就是這樣：`as_mut` 重新借出一個 `Pin<&mut F>`，交給 `F` 自己的 `poll`——而當這個 `F` 來自 `async fn` / `async` block 時，跑的正是編譯器產生的那個 `poll`。

### `Pin` 釘的是「值」，不是「指標」

接著澄清一個很容易誤會的點：

> `Pin<P>` 釘住的，是 **`P` 指向的那個值**——而不是「`Pin<P>` 這個指標變數自己」。

所以 `Pin<Box<T>>` 這個東西**本身**是可以到處 move 的。你把它從一個變數搬到另一個、塞進 `Vec`、再拿出來，都沒問題——因為你搬的只是那根指標，被它指著的值始終待在 heap 上的原位。下面用 `{:p}` 印出「被指的值」的位址（`&*` 為 `Pin<P<T>>` 取得 `&T`），讓事實說話：

```rust,editable
use std::pin::Pin;

struct Data {
    value: i32,
}

fn main() {
    let mut queue: Vec<Pin<Box<Data>>> = Vec::new();

    let boxed = Box::pin(Data { value: 7 });
    println!("放進 queue 前，值在 {:p}", &*boxed);

    queue.push(boxed); // Pin<Box<Data>> 這根指標被搬進 Vec
    let popped = queue.pop().unwrap(); // 又被搬出來

    println!("從 queue 拿出後，值在 {:p}", &*popped); // 位址一模一樣
}
```

兩次印出的位址完全相同：指標在 `Vec` 裡進進出出，但 heap 上那個 `Data` 從頭到尾沒有被 move。`Pin` 唯一禁止的，是「**透過它，把被指的值從原位址搬走**」這個動作而已。

### `Pin` 通常藏在幕後

最後給你一顆定心丸：使用現成 runtime 撰寫 `async fn` + `.await` 時，`Pin` 通常都藏在幕後。編譯器會產生 `Future` 狀態機，runtime 則負責把它釘住並進行 `poll`。這一章會直接碰到 `Pin`，是因為我們正在親手探索這套底層機制。所以看不太懂這幾集的細節也別焦慮；這些內容是要讓你知道底下發生了什麼，而不是因為日常開發會把它們全部手寫一遍。

真有一天你要手刻底層 `Future`，需要從外層的 `Pin<P<外層>>` 取出某個欄位的 `Pin<P<內層>>`（這動作叫 projection），社群的 `pin-project` `crate` 可以替你安全地做掉，不必自己寫 `unsafe`。知道有這工具就夠了，這裡先不深入。

而如果你想「把 `Pin` 裡的值拿回成一個普通的 `&mut T`」，下一集也會講「搬了反正不會壞」時常常能用的辦法。

## 重點整理

- `poll` 想要「能改內部、但不准搬走」兩件事；普通 `&mut Self` 擋不住 move（executor 仍能在兩次 `poll` 之間 `let moved = ...` 把它搬走），所以不能用。
- `Pin<&mut T>` 是「綁在原地、不准搬走的 `&mut`」；`poll` 因此收 `Pin<&mut Self>`。
- 值在被釘住以前仍然可以照一般 Rust 規則 move；`Pin` 管的是「釘住之後」不能再把值搬走。
- `Pin` 擋 move 要守兩件事：建立時不能留下另一條外部路徑讓你之後搬走值；使用時安全 API 也不能把能搬走內部值的內層指標交給你。
- `Pin` 的用法很有限：唯讀靠 `Deref`，重新借出用 `as_mut`，當然還能餵給 `poll`。
- `Pin<P>` 釘的是「被指的值」不是「指標本身」，所以 `Pin<Box<T>>` 自己能隨意 move（連塞進 `Vec` 再拿出來都行），這就是 executor 能到處搬 `Pin<Box<Fut>>` 的原因。
- 使用現成 runtime 撰寫 `async fn` + `.await` 時，`Pin` 通常都藏在幕後：編譯器產生 `Future` 狀態機，runtime 負責把它釘住並進行 `poll`。這一章會直接碰到 `Pin`，是因為我們正在親手探索這套底層機制。
