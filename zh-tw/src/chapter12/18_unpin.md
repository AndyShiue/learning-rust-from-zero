# `Unpin` 與 `get_mut`

## 本集目標

理解為什麼「大部分型別其實不怕被 move」,以及 `Unpin` 這個逃生門讓 Pin 在這些型別上幾乎透明。

## 概念說明

### 其實大部分東西根本不怕 move

上一集把 Pin 講得很嚴格:不准搬。但冷靜想想,會怕被 move 的只有**自我參照**那種特殊結構。一個普通的 `i32`、`String`、`Vec<T>`、或我們第 7 集那種沒有內部指標的 `Delay`——把它搬到別的位址,一點事都沒有,因為它裡面沒有任何「指著自己」的指標。

所以 Pin 那套「不准搬」的保護,對這些普通型別來說是**多餘的**。Rust 用一個 trait 來標記「這個型別就算被 Pin 住,也照樣可以安全 move」,這個 trait 叫 **`Unpin`**。

名字有點繞:`Unpin` 不是「不能 pin」,而是「**就算被 pin 也無所謂**(pin 對我沒有約束力)」。

### `Unpin` 是 auto trait

`Unpin` 和第 8 章的 `Send`／`Sync` 一樣,是 **auto trait**——編譯器自動幫你判斷,不用手動實作。規則很直覺:一個型別如果它的欄位都是 `Unpin`,它自己就自動是 `Unpin`。

而幾乎所有你平常用的型別都是 `Unpin`:`i32`、`bool`、`String`、`Vec<T>`、你自己定義的一般 struct……全都是。會**不是** `Unpin` 的,主要就是 `async fn` / `async` 區塊產生的那些狀態機 future——因為它們**可能**包含跨 `.await` 的自我參照,編譯器不敢假設它們能安全 move,所以不給它們 `Unpin`。

> 一句話總結:**普通型別都是 `Unpin`;只有 async 產生的 future 不能假設是 `Unpin`。**

### `get_mut`:對 `Unpin` 型別,Pin 幾乎透明

既然 `Unpin` 的型別不怕 move,那把它 pin 住其實沒意義——我們應該能輕鬆從 `Pin<&mut T>` 拿回普通的 `&mut T`。標準庫正是這樣設計的:

```rust,ignore
impl<P> Pin<P> {
    // 只有當 T: Unpin 時才能用
    pub fn get_mut(self) -> &mut T where T: Unpin { ... }
}
```

`Pin::get_mut` 在 `T: Unpin` 的條件下,把 `Pin<&mut T>` 變回普通的 `&mut T`。這就是為什麼前面手寫 `Join`(第 9 集)時,`poll` 裡能直接 `let this = self.get_mut();`——因為那個 `Join` 的欄位都是 `Unpin`,所以 `Join` 自己是 `Unpin`,於是 `get_mut` 可用,我們就能像平常一樣存取它的欄位。

反過來,如果 `T` **不是** `Unpin`(例如一個 async fn future),`get_mut` 就不給你用——因為那等於洩漏了 `&mut T`、就能搬走它,違反 Pin 的保證。

### 哪些 API 會要求 `Unpin`

正因為 `Unpin` 讓 Pin 變透明、好處理,很多接受 future 的 API 會直接要求 `T: Unpin`,把麻煩擋在門外。例如一些工具函式、某些 combinator,簽名會寫 `where F: Future + Unpin`。

如果你手上有個**不是** `Unpin` 的 future(像直接從 `async fn` 拿到的),卻要傳給一個要求 `Unpin` 的 API,該怎麼辦?辦法是先把它**釘在一個固定位址**,因為「一個指向固定位址的指標」本身是可以安全 move 的(你搬的是指標,不是被指的東西)。`Box::pin`(第 20 集)會把 future 放到 heap 上釘住,得到的 `Pin<Box<F>>` 就是 `Unpin` 的;`pin!`(第 19 集)則把它釘在 stack 上。這也是實務上最常見「Pin 相關編譯錯誤」的解法:訊息常會說 `the trait Unpin is not implemented`,你就把那個 future 用 `Box::pin` 或 `pin!` 包一下。

## 範例程式碼

```rust,ignore
use std::pin::pin;

#[tokio::main]
async fn main() {
    // 一個從 async 區塊來的 future——它不是 Unpin
    let fut = async {
        let s = String::from("hello");
        // ... 想像這裡有跨 .await 的借用 ...
        s.len()
    };

    // 如果某個 API 要求 Unpin,直接傳 fut 會編譯失敗。
    // 先用 pin! 把它釘在 stack 上,就能滿足那類 API:
    let pinned = pin!(fut); // pinned: Pin<&mut _>,可以拿去 .await 或傳給要 Unpin 的 API

    println!("{}", pinned.await);
}
```

## 重點整理

- 會怕被 move 的只有**自我參照**結構;普通型別 move 完全沒事
- `Unpin` = 「就算被 pin 也能安全 move」的標記,是 **auto trait**(編譯器自動判斷)
- 幾乎所有型別都是 `Unpin`;**只有 `async fn` / `async` 區塊的 future 不能假設是 `Unpin`**
- `Pin::get_mut` 在 `T: Unpin` 時,把 `Pin<&mut T>` 變回普通 `&mut T`——所以第 9 集的 `Join` 能用 `get_mut`
- 有些 API 要求 `Unpin`;把不是 `Unpin` 的 future 用 `Box::pin`(第 20 集)或 `pin!`(第 19 集)釘住,就能滿足
