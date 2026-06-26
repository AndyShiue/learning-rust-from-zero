# 為什麼 `poll` 需要 `Pin`

## 本集目標

理解 `poll` 的 `self` 為什麼是 `Pin<&mut Self>` 而不是 `&mut Self`，並認識 `Pin` 各個方法。

## 正文

### `&mut self` 權力太大

上一集知道了：自我參照的 `Future` 被 move 會壞掉。那 `poll` 要怎麼避免「在 poll 的過程中不小心把 `Future` 搬走」？

關鍵在於：如果 `poll` 收的是普通的 `&mut self`，那它**權力太大**了。有了 `&mut T`，你能用 `std::mem::swap`、`std::mem::replace` 之類的工具，神不知鬼不覺地把值搬到別的地方去。對自我參照的 `Future` 來說，這就是災難。

所以 Rust 改用一個「閹割版的 `&mut`」——`Pin<&mut T>`。它的能力剛好被砍到位：

- **能改內容**：你還是可以修改 `T` 內部的欄位（poll 本來就要更新狀態機的狀態）。
- **不准 move**：但你不能把 `T` 整個從它的位址搬走。

強制的手段很單純：`Pin<&mut T>` **不再洩漏**普通的 `&mut T` 給你（除非你保證搬了不會壞，那是下一集的事）。它只提供「接受 `Pin<&mut Self>` 的方法」。沒有 `&mut T`，就沒有 `mem::swap`，也就搬不走。

### `Pin` 釘住的到底是什麼

這裡有個超容易誤解的點，務必講清楚。

`Pin<P>` 釘住的，是 **`P` 指向的那個值的位址**——不是 `Pin<P>` 這個指標本身被存放的位址。

舉例：`Pin<Box<T>>` 釘住的是「heap 上那個 `T`」，而不是「`Pin<Box<T>>` 這個變數」。所以 `Pin<Box<T>>`、`Pin<&mut T>` 這些值**本身可以隨意 move**——你搬動的只是那個指標（指標換個地方放沒關係），被它指著的 `T` 一動也不動，仍然牢牢釘在原處。

這正好解開一個你可能早就有的困惑：前面手寫 executor 時，我們把 `Pin<Box<Fut>>` 丟進 queue、`pop` 出來、搬來搬去，那 `Fut` 不就被搬動了嗎？沒有。搬的是 `Pin<Box<Fut>>`（那個 box 指標），heap 上真正的 `Fut` 從頭到尾沒挪過位置。`Pin` 禁止的，**只有**「透過 `Pin` 把內部指標指向的那個值，從它原本的位址搬走」這一件事。

### `Pin` 能用的方法

為了讓你對 `Pin` 有個全貌，這裡把它常用的方法整理一遍。

**唯讀存取**永遠開放（讀又不會把值搬走，沒風險）。`Pin<P<T>>` 永遠可以解參考成 `&T`，這是透過 `Deref` 做到的：

```rust,ignore
impl<Ptr: Deref> Deref for Pin<Ptr> {
    type Target = Ptr::Target;
    fn deref(&self) -> &Ptr::Target { /* ... */ }
}
```

除了自動解參考，也有 `get_ref`（拿到 `&T`）和 `as_ref`（借成 `Pin<&T>`）。

**重新借用成另一個 `Pin`** 用 `as_mut`：它把 `Pin<Box<T>>` 借成 `Pin<&mut T>`，型別大致是 `fn as_mut(&mut self) -> Pin<&mut T>`。這正是第 6 集 executor 能反覆 `poll` 同一個 `Future` 的原因——`as_mut` 只是借用，不交出所有權，所以 `loop` 裡可以一次又一次借出 `Pin<&mut T>` 來 `poll`。

**建立一個 `Pin`** 有三種辦法：

- `Pin::new(value)`：最安全，但**只限 `Unpin` 的型別**（搬了不會壞的才給用，呼應上一集 `Counter` 可以、自我參照的 `async` 狀態機不行）。
- `Pin::new_unchecked(value)`：任何型別都能用，但是 `unsafe`——等於你向編譯器擔保「我保證不會把它搬走」。
- `Box::pin(value)`：把值放到 heap 上並釘住，回傳 `Pin<Box<T>>`，這個我們從第 6 集就一直在用。

至於**可變存取**（拿回普通的 `&mut T`，也就是 `DerefMut` 和 `get_mut`）——這正是有風險、需要 `Unpin` 才開放的部分，留到下一集專門講。

### 一般人其實碰不到 `Pin`

最後給你一顆定心丸：`Pin` 是**型別層面的約定**，主要是給「寫底層 `Future` 或 runtime 的人」用的。如果你只是平常寫 `async fn`、用 `.await`，編譯器和 runtime 會替你把 `Pin` 處理得好好的，你幾乎不會直接碰到它。所以這幾集的細節看不太懂也別焦慮，它們是讓你「知道底下發生什麼事」，而不是日常會手寫的東西。

## 重點整理

- `&mut self` 太強（能用 `mem::swap` 等搬走值），所以 `poll` 改用「閹割版」的 `Pin<&mut Self>`：能改內容、不准 move。
- 強制手段：`Pin<&mut T>` 不洩漏普通 `&mut T`，沒有 `&mut T` 就搬不走
- `Pin<P>` 釘住的是「`P` 指向的值」，不是 `Pin<P>` 本身；所以 `Pin<Box<T>>` 可以隨意 move（搬指標，被指的 `T` 不動），這解釋了 executor 為何能把 `Pin<Box<Fut>>` 搬來搬去
- 方法全貌：唯讀（`Deref` / `get_ref` / `as_ref`）永遠可用；`as_mut` 重新借用成 `Pin<&mut T>`；建立用 `Pin::new`（限 `Unpin`）/ `new_unchecked`（unsafe）/ `Box::pin`
- 可變存取（`get_mut` / `DerefMut`）要 `Unpin`，留到下一集
- `Pin` 是型別層面的約定，平常寫 `async` 幾乎碰不到，主要給寫 runtime 的人
