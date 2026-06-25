# 為什麼 `poll` 需要 `Pin`

## 本集目標

理解 `Pin<&mut Self>` 到底是什麼、它怎麼用型別系統同時做到「可以改」和「不准搬」。

## 概念說明

### 回到那個兩難

上一集的結論是：開始跑之後的 future 不能被 move（否則自我參照的內部指標會懸空），但 executor 又必須拿到它的可變存取權才能 `poll` 它。「能改」和「不能搬」要同時成立。

如果 `poll` 的簽名是 `fn poll(&mut self, ...)`，那就糟了——有了 `&mut self`，使用者就能做出搬走它的事，例如 `std::mem::replace`、`std::mem::swap` 都能透過 `&mut` 把值換掉(等於搬走原本的)。`&mut` 給的權力太大了。

我們需要一種「閹割版的 `&mut`」:可以拿來改裡面的東西、拿來 poll,但**就是不准你把值整個搬走**。這就是 `Pin`。

### `Pin` 是包在指標外面的一層保證

`Pin<P>` 不是一種新的指標,它是**包在某個指標 `P` 外面的一層約束**。最常見的是 `Pin<&mut T>`,意思是:

> 「這是一個指向 `T` 的可變參考,但我向你保證(而且型別系統會強制):透過我,你**沒辦法把 `T` 搬走**。你可以改它的內容,但它會一直待在原本的記憶體位址,直到它被銷毀。」

所以 `Pin<&mut Self>` 給 `poll` 的,正是我們要的那把「閹割版鑰匙」:executor 可以用它推進 future(改內部狀態),但無法把這個 future 從它的位址上搬走。自我參照的內部指標於是永遠有效。

一個比喻:`&mut T` 像是「你可以隨意搬動的家具」;`Pin<&mut T>` 像是「**被鎖在地板上的家具**」——你還是能打開抽屜、拿東西、整理內容(改它),但你沒辦法把整個櫃子搬到別的房間(move)。

### 釘住的是「被指的值」,不是「指標本身」

這裡要敲掉一個最常見的誤解。`Pin<P>` 保證固定的,**永遠是 `P` 所指向的那個值(pointee)的位址**——而**不是** `Pin<P>` 這個指標自己被存放在哪裡。

換句話說:**`Pin<Box<T>>`、`Pin<&mut T>` 這些值,你還是可以隨意搬。** 你可以把一個 `Pin<Box<T>>` 從函式回傳出去、塞進 `Vec`、move 給別人——完全合法。因為搬走 `Pin<Box<T>>` 只是搬走那個 box 指標(就幾個 byte),**heap 上的 `T` 一步都沒動**,位址照舊;而 `Pin` 保證的,正是 heap 上那個 `T` 不會搬。

```rust,ignore
let pinned: Pin<Box<MyFuture>> = Box::pin(make_future());
let moved = pinned;    // OK！搬走的是 Box 指標，不是 heap 上的 future
let v = vec![moved];   // OK！照樣能塞進容器
// 自始至終，heap 上那個 MyFuture 的位址都沒變——它才是被「釘住」的東西
```

這也解開一個常見困惑:「executor 不是一直把 `Pin<Box<Fut>>` 丟進 queue、搬來搬去嗎?那 future 到底哪裡被釘住了?」答案就是:**被釘住的是 heap 上的 `Fut`,不是裝著它的那個指標。move 指標 ≠ move 被指的值。**

對 `Pin<&mut T>` 也一樣:這個參考本身可以傳來傳去、move,被指的 `T` 不會因此移動。唯一被禁掉的,是「**透過 Pin 把 pointee 從它原本的位址上搬走**」(像用 `mem::replace`／`swap` 把 `T` 換出來那樣)。

### Pin 怎麼「強制」不准搬

關鍵在於:`Pin` 包起來之後,**不再提供 `&mut T`**。前面說過,只要能拿到 `&mut T`,就有辦法搬走 `T`。所以 `Pin` 的招數就是:把 `&mut T` 藏起來,只給你一些「不會洩漏出 `&mut T`」的操作。

你能對 `Pin<&mut T>` 做的,是呼叫那些「接受 `Pin<&mut Self>`」的方法——`poll` 就是一個。這些方法被設計成在 pinned 的前提下安全運作。你不能憑空從 `Pin<&mut T>` 拿回一個普通的 `&mut T`(除非 `T` 滿足某個條件,那是下一集的 `Unpin`)。

### `Pin` 能用哪些方法

既然 `Pin` 把普通的 `&mut T` 藏起來了，那手邊還能對它做什麼？整理一下常用的幾個。（其中「拿回可變的 `&mut T`」那一招——`get_mut`——跟 `Unpin` 有關，留到下一集。）

**讀取：`Deref`（永遠可用）。** `Pin<P>` 一定實作 `Deref`，目標就是 `&T`：

```rust,ignore
impl<P: Deref> Deref for Pin<P> {
    type Target = P::Target;
    fn deref(&self) -> &P::Target { /* ... */ }
}
```

所以你隨時能透過 `Pin<&mut T>` 拿到一個**唯讀的** `&T`——寫 `&*pin`，或直接呼叫 `T` 上吃 `&self` 的方法。這安全，因為 `&T` 沒辦法把值搬走。上一集 `Counter::poll` 裡印位址的 `&*self` 走的就是這條 `Deref`。

（相對地，可變方向的 `DerefMut`（拿到 `&mut T`）**不是**永遠可用，它只在 `T: Unpin` 時才有——這也是為什麼 `Counter`（`Unpin`）的 `poll` 裡能直接 `self.count += 1`。一般 future 怎麼安全拿到 `&mut T`，是下一集 `Unpin` / `get_mut` 的事。）

**重新借用：`as_mut` / `as_ref`。**

- `Pin::as_mut(&mut self) -> Pin<&mut T>`：從「擁有的 pin」（如 `Pin<Box<F>>`）借出一個「指向的 pin」（`Pin<&mut F>`），借完原本的還在。第 6 集 executor 迴圈反覆 poll 同一個 future，靠的就是它。
- `Pin::as_ref(&self) -> Pin<&T>`：同樣是重新借用，但借出 shared 版的 `Pin<&T>`。

```rust,ignore
let mut boxed = Box::pin(fut);     // Pin<Box<F>>
boxed.as_mut().poll(&mut cx);      // 借出 Pin<&mut F> 來 poll
boxed.as_mut().poll(&mut cx);      // 還能再借、再 poll
```

**拿唯讀參考：`get_ref`。** 對一個 `Pin<&T>`（shared 版），`Pin::get_ref(self) -> &T` 直接把裡面的 `&T` 拿出來。也安全（`&T` 搬不動值）。它和 `Deref` 拿到的 `&T` 是同一種東西，只是另一種寫法。

**怎麼「做出」一個 `Pin`。**

- `Pin::new(ptr) -> Pin<P>`：**安全**，但**只在 `T: Unpin` 時可用**。上一集 `Pin::new(&mut counter)` 能用，正是因為 `Counter` 是 `Unpin`；對自我參照 future 它會編譯失敗（就是上一集最後那個例子）。
- `Pin::new_unchecked(ptr) -> Pin<P>`：**unsafe**，任何型別都能用——但你得**自己保證**之後不會把值搬走，違背了就是 UB。
- 平常不直接碰這兩個，而是用包好的 `Box::pin`（第 6、20 集）或 `pin!`（第 19 集）——它們內部用 `new_unchecked`，但把「不會搬走」這個保證安全地包起來，直接給你一個現成的 `Pin<...>`。

一句話：**`Pin` 對「唯讀」（`Deref` / `get_ref` / `as_ref`）和「重新借用成另一個 pin」（`as_mut`）很大方，但對「普通可變的 `&mut T`」很小氣——那道門要 `Unpin` 才開（下一集）。**

### 為什麼是 executor 要面對 Pin

把前面幾集串起來:executor 要 poll 一個 future,而 future 可能是自我參照、不能被 move 的。所以 executor 必須先想辦法把 future「釘」在一個固定位址上,拿到它的 `Pin<&mut F>`,才能呼叫 `poll`。

這正是為什麼我們手寫 executor 時,都要先把 future 用 `Box::pin`(第 6 集那個黑盒子)或 `pin!` 處理過——那兩個工具做的,就是「把 future 釘在某個固定位址,給你一個 `Pin<&mut F>`」。下一集和第 18、19 集會把這兩個工具講清楚。

### Pin 是一種「約定」,不是真的鎖

要澄清一個常見誤解:`Pin` 並沒有在記憶體層面真的把東西鎖死,它是一套**型別層面的約定**。它的安全性建立在「實作 future 的人遵守規則」之上。對你來說——身為 `async fn` 的使用者——你幾乎永遠不會直接碰到 Pin 的麻煩,因為編譯器生成的狀態機都正確遵守規則。Pin 的細節主要是寫底層 future、或實作 runtime 的人才需要深究。我們把它攤開來,是為了讓你看懂 `poll` 的簽名、以及「future 不能亂搬」這件事背後的道理。

## 範例程式碼

這一集是觀念,沒有新的可執行範例。把這條因果鏈記起來就夠了:

```text
自我參照的 future 不能 move
   → poll 不能用普通的 &mut self(太容易搬走它)
      → 改用 Pin<&mut Self>:能改內容、但不准 move
         → executor 必須先把 future「釘住」(pin! / Box::pin)才能 poll
```

## 重點整理

- `&mut self` 權力太大(可用 `mem::replace`／`swap` 搬走值),不能拿來 poll 不可 move 的 future
- `Pin<&mut T>` 是「包在參考外的一層保證」:能改內容,但**不准把 `T` 搬走**(比喻:鎖在地板上的家具)
- `Pin<P>` 釘住的是 **`P` 指向的那個值(pointee)的位址**,不是 `Pin<P>` 這個指標本身的位址——所以 `Pin<Box<T>>`／`Pin<&mut T>` 本身可以隨意 move(搬的是指標,heap／被指的 `T` 不動),被禁的只有「透過 Pin 把 pointee 從它的位址搬走」
- 強制方式:`Pin` 不再洩漏普通的 `&mut T`,只給你接受 `Pin<&mut Self>` 的方法(如 `poll`)
- `Pin` 能用的方法：唯讀走 `Deref`（永遠可用，`&*pin`）、`get_ref`、`as_ref`；重新借用成另一個 pin 用 `as_mut`；建立用 `Pin::new`（限 `Unpin`）/ `new_unchecked`（unsafe）/ `Box::pin` / `pin!`。可變的 `&mut T`（`DerefMut` / `get_mut`）要 `Unpin` 才有——下一集講
- executor 要 poll future,得先用 `pin!` / `Box::pin` 把它釘在固定位址,拿到 `Pin<&mut F>`
- Pin 是型別層面的約定;`async fn` 的一般使用者幾乎不會直接碰到它,細節主要給寫底層 future／runtime 的人
