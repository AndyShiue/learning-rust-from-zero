# `Unpin`

## 本集目標

認識 `Unpin` 這個「搬了不會壞」的標籤，看懂為什麼有了它，被釘住的 `&mut` 就能變回普通的 `&mut`。

## 正文

### 先問一個問題：「不准搬」對誰有意義？

上一集 `Pin` 千方百計擋住 move。但先退一步想：這條規矩到底在防誰？

答案是——它幾乎只在防一種東西：**自我參照的 `Future` 狀態機**。除了這種少見的特例，你平常用的型別（`i32`、`String`、`Vec`、自己定義的 `struct`……）搬來搬去根本不會出事，move 對它們就是把幾個 bytes 換個位置存而已。對這些型別硬套上「不准搬」，純粹是多管閒事。

Rust 用一個標籤把這兩群分開，這個標籤就叫 **`Unpin`**：一個型別是 `Unpin`，意思就是「**我搬了不會壞，`Pin` 不必管我**」。

### `Unpin` 幾乎人人都有

`Unpin` 和第 9 章的 `Send` / `Sync` 一樣是 **auto trait**——你不用手寫，編譯器看你的型別欄位自動判斷。而你會發現它的判斷結果是：**絕大多數型別都是 `Unpin`**。

寫個小工具就能驗證。下面的 `assert_unpin` 只收 `Unpin` 的型別，把各種常見值丟進去都能過：

```rust,editable
fn assert_unpin<T: Unpin>(_: T) {}

fn main() {
    assert_unpin(42);
    assert_unpin(String::from("hi"));
    assert_unpin(vec![1, 2, 3]);
    println!("這些都是 Unpin");
}
```

連我們前面手寫的 `Delay`、`Counter`、`JoinAll`、`JoinHandle` 也都是 `Unpin`——它們的欄位都是普通可搬的東西。

那誰不是 `Unpin`？把同一個工具拿去檢查一個「跨 `.await` 借了區域變數」的 `async fn`（也就是第 16 集那種自我參照狀態機），就會被擋下來：

```rust,compile_fail
fn assert_unpin<T: Unpin>(_: T) {}

async fn other() {}

async fn demo() {
    let s = String::from("hi");
    let r = &s;
    other().await; // s 和 r 都跨過了 .await
    println!("{r}");
}

fn main() {
    assert_unpin(demo()); // 編譯錯誤：demo() 的 Future 不是 Unpin
}
```

編譯器會說 `... cannot be unpinned`。這就對了：`async fn` / `async` block 的 `Future` **不能假設是 `Unpin`**，因為它有可能正是那個搬了會壞的自我參照狀態機。

### `Unpin` 的型別，可以把值要回來

知道誰是 `Unpin` 之後，上一集留的伏筆就能解開了：「把釘住的值放回成普通 `&mut T`」這件事，對 `Unpin` 的型別是開放的。

道理很直接：既然這個型別搬了不會壞，`Pin` 的保護對它本來就是多餘的，那乾脆讓你把普通 `&mut T` 拿回去。具體來說，當 `T: Unpin`，`Pin<P<T>>` 才會實作 `DerefMut`，而 `Pin<&mut T>` 上才有 `get_mut` 把它變回 `&mut T`：

```rust,editable
use std::pin::Pin;

fn main() {
    let mut n = 10;
    let mut pinned: Pin<&mut i32> = Pin::new(&mut n);

    // i32 是 Unpin，所以 Pin<&mut i32> 實作 DerefMut
    *pinned = 100;
    println!("{}", pinned);

    // 也可以用 get_mut 拿回普通的 &mut i32
    let back: &mut i32 = pinned.get_mut();
    *back += 5;
    println!("{}", back);
}
```

因此，我們前面每個自訂 `Future` 的 `poll` 開頭都寫 `let this = self.get_mut();`，也沒有出問題。那些型別全是 `Unpin`，當然能用 `get_mut`。要是哪天你的 `Future` 不是 `Unpin`，這行就會編譯失敗，逼你改用 `Pin` 的方法小心處理。

### 兩條規則，其實同一個條件

把 `get_mut` 和上一集的 `Pin::new` 擺在一起看，會發現它們守的是**同一個條件**——`Unpin`：

```rust,ignore
// 把釘住的值變回普通 &mut：要 Unpin
impl<T: ?Sized> Pin<&mut T> {
    pub fn get_mut(self) -> &mut T where T: Unpin { /* ... */ }
}

// 不交出所有權就建立 Pin：被指的值要 Unpin
impl<P: Deref> Pin<P> {
    pub fn new(pointer: P) -> Pin<P> where P::Target: Unpin { /* ... */ }
}
```

換句話說，這兩個方法都繞過了 `Pin` 的平常限制——`get_mut` 讓你把釘住的值變回普通 `&mut`、`Pin::new` 讓你不交出所有權就把值釘起來——而 Rust 只把這兩道門開給 `Unpin` 的型別。第 16 集用到的 `Counter` 是 `Unpin`，使用 `Pin::new(&mut counter)`、`get_mut` 都暢行無阻；自我參照的 `async` 狀態機不是 `Unpin`，這兩道門都對它關上。

所以實務上的判斷很簡單：你手上的 `Future` 是 `Unpin` 嗎？是的話，`Pin::new`、`get_mut` 隨你用；不是的話（一般就是 `async fn`/ `async` block 生出來的 `Future`），你就得用「會交出所有權」的方式把它釘起來——`Box::pin` 放 heap，或下一集要登場的 `pin!` 釘在 stack 上。

## 重點整理

- `Pin` 的「不准搬」基本上只為一種東西而設：自我參照的 `async` 狀態機；其餘型別搬了都不會壞
- `Unpin` 就是「搬了不會壞」的標籤，是 auto trait，由編譯器自動判斷，**絕大多數型別都是 `Unpin`**
- `async fn` / `async` block 的 `Future` 不能假設是 `Unpin`（可能是自我參照狀態機）
- 當 `T: Unpin`，`Pin<P<T>>` 才實作 `DerefMut`、`Pin<&mut T>` 才能用 `get_mut` 變回普通 `&mut T`；我們手寫 `Future` 的 `self.get_mut()` 能用就是這個原因
- `Pin::new` 和 `get_mut` 守的是同一個條件——`Unpin`，意即「對搬了不會壞的型別，`Pin` 自動讓路」
- `Future` 不是 `Unpin` 時，就得用 `Box::pin` 或下一集的 `pin!` 來釘
