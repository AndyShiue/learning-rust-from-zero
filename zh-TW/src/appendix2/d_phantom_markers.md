# `PhantomData` 與 `PhantomPinned`

## 本集目標

理解 marker type 如何在不儲存實際資料的情況下，把型別設計者的承諾告訴編譯器；分辨 `PhantomData` 與 `PhantomPinned` 的不同用途。

> 本集是**第 5 章泛型**、本附錄的 variance，以及**非同步一章** `Pin` 的補充。

## 概念說明

標準庫有些型別本身不攜帶有用的執行時期資料，存在的目的只是影響型別檢查。這類型別常叫 **marker type**。

本集的兩位主角名字很像，但工作完全不同：

- `PhantomData<T>`：表示「這個型別在邏輯上使用了 `T`」。
- `PhantomPinned`：表示「這個型別不能自動成為 `Unpin`」。

### 問題：泛型參數沒有出現在欄位裡

先假設我們想替資料庫編號加上不同標記，讓 `Id<User>` 和 `Id<Article>` 在編譯時期成為不同型別，避免使用者編號和文章編號混在一起：

```rust,compile_fail
struct Id<T> {
    value: u64,
}
#
# fn main() {}
```

我們只想讓 `T` 當作型別標記，不需要真的存一個 `User` 或 `Article`。但 Rust 不允許宣告一個完全沒用在欄位裡的泛型參數，因此上面的程式無法編譯。編譯器無法知道這是刻意留下的標記，還是不小心漏用了 `T`。

這時可以加入 `PhantomData<T>`，明確表示「我確實要讓這個型別和 `T` 有關」：

```rust,editable
use std::marker::PhantomData;

struct User;
struct Article;

struct Id<T> {
    value: u64,
    _kind: PhantomData<T>,
}

fn show_user(id: Id<User>) {
    println!("使用者編號：{}", id.value);
}

fn main() {
    let user_id = Id::<User> {
        value: 7,
        _kind: PhantomData,
    };
    show_user(user_id);

    let _article_id = Id::<Article> {
        value: 7,
        _kind: PhantomData,
    };
    // show_user(_article_id); // Id<Article> 不是 Id<User>
}
```

`PhantomData<T>` 不會真的放一個 `T` 進去，所以 `Id<T>` 的執行時期內容仍只有 `u64`。但在型別系統眼中，`Id<User>` 與 `Id<Article>` 已經是不同型別。

### 「邏輯上使用」不只為了消除錯誤

`PhantomData<T>` 會告訴編譯器：分析這個外層型別時，請把它當成與 `T` 有關。這會影響：

- **variance**：例如 `PhantomData<&'a T>` 會攜帶 `'a` 與 `T` 的關係。
- **`auto trait`**：`T` 是否為 `Send`、`Sync` 等，可能影響外層型別。

不同寫法表達的關係也不同：

```rust,ignore
PhantomData<T>     // 像是邏輯上擁有 T
PhantomData<&'a T> // 像是邏輯上借用了 &'a T
PhantomData<fn(T)> // T 位於函數輸入位置
```

這些差異在底層函式庫中很重要。一般應用程式最常見的是第一個 `Id<T>` 例子：用型別標記防止相同底層資料被混用。

### 實務案例：讓 executor 留在建立它的執行緒

非同步一章第 11 集後的 executor 在 `Executor::new()` 中用 `thread::current()` 記住當下的執行緒。之後，`Task::wake` 會透過這個 `Thread` handle 呼叫 `.unpark()`；executor 沒有工作時則用 `thread::park()` 暫停目前正在執行它的執行緒。

這裡藏著一個型別系統沒有自動看出的限制：`Executor` 必須一直留在建立它的執行緒。以下是簡化過的版本：

```rust,no_run
use std::thread::{self, Thread};

struct Task {
    executor_thread: Thread,
}

impl Task {
    fn wake(self) {
        self.executor_thread.unpark();
    }
}

struct Executor {
    executor_thread: Thread,
}

impl Executor {
    fn new() -> Self {
        Self {
            executor_thread: thread::current(),
        }
    }

    fn run_once(&self) {
        let task = Task {
            executor_thread: self.executor_thread.clone(),
        };

        thread::spawn(move || task.wake())
            .join()
            .expect("執行緒發生錯誤");
        thread::park();
    }
}

fn main() {
    let executor = Executor::new(); // 記住主執行緒

    // Executor 的欄位都是 Send，所以這段能通過編譯，卻可能無限期卡住。
    thread::spawn(move || executor.run_once())
        .join()
        .expect("執行緒發生錯誤");
}
```

`Thread` handle 本身可以跨執行緒傳送，但搬動 handle 不會改變它所指向的執行緒。上例把 `executor` 搬到新執行緒之後：

1. `task.wake()` 對建立 executor 的**主執行緒**呼叫 `.unpark()`。
2. `run_once()` 卻在**新執行緒**呼叫 `thread::park()`。

所以 `.unpark()` 並不是沒有作用，而是把喚醒 token 送給了錯的執行緒；真正執行 executor 的新執行緒沒有收到 token，可能無限期阻塞。

這個 executor 只能留在建立它的執行緒，也不該讓其他執行緒透過共享參考呼叫 `.run()`。因此可加入一個零大小的 marker，阻止它自動實作 `Send` 與 `Sync`：

```rust,compile_fail
use std::marker::PhantomData;
use std::rc::Rc;
use std::thread::{self, Thread};

struct Executor {
    executor_thread: Thread,
    _not_send_sync: PhantomData<Rc<()>>,
}

impl Executor {
    fn new() -> Self {
        Self {
            executor_thread: thread::current(),
            _not_send_sync: PhantomData,
        }
    }

    fn run(&self) {
        thread::park();
    }
}

fn main() {
    let executor = Executor::new();

    // 編譯錯誤：Executor 不再能跨執行緒傳送。
    thread::spawn(move || executor.run());
}
```

`Rc<()>` 同時不是 `Send` 與 `Sync`，而 `PhantomData<Rc<()>>` 會讓 `auto trait` 的分析把 `Executor` 當成邏輯上含有一個 `Rc<()>`。因此 `Executor` 也同時不是 `Send` 與 `Sync`：非 `Send` 防止它被搬到其他執行緒，非 `Sync` 則防止其他執行緒透過 `&Executor` 呼叫 `.run()`。上面的 `move` 範例直接展示的是 executor 現在非 `Send`；若嘗試跨執行緒分享 `&Executor`，也會因為非 `Sync` 被拒絕。這個欄位不會真的配置或儲存 `Rc`；正確的使用方式是在同一條執行緒中建立並執行 executor，而 waker 仍可從其他執行緒呼叫該 executor `Thread` 的 `.unpark()`。

### `PhantomPinned`：阻止自動 `Unpin`

非同步一章學過，幾乎所有普通型別都會自動實作 `Unpin`。只要所有欄位都是 `Unpin`，外層 `struct` 通常也是 `Unpin`。

但設計一個位址敏感的型別時，我們可能需要明確告訴編譯器：「即使其他欄位都能搬，這個型別一旦被 pin 住就不准搬。」把 `PhantomPinned` 放進欄位即可阻止自動實作 `Unpin`：

```rust,compile_fail
use std::marker::PhantomPinned;

struct AddressSensitive {
    name: String,
    _pin: PhantomPinned,
}

fn assert_unpin<T: Unpin>(_: T) {}

fn main() {
    let value = AddressSensitive {
        name: String::from("不能假設我可以搬"),
        _pin: PhantomPinned,
    };

    assert_unpin(value);
}
```

錯誤的重點是 `PhantomPinned` 沒有實作 `Unpin`，因此包含它的 `AddressSensitive` 也不會自動實作 `Unpin`。

但加入 `PhantomPinned` **不等於已經把值 pin 住**。它只改變型別是否自動實作 `Unpin`；要真正建立 `Pin<&mut T>` 或 `Pin<Box<T>>`，仍然要使用 `pin!`、`Box::pin` 等方式。

### 建立時仍然可以 move

`PhantomPinned` 不是讓值從出生開始就完全不能 move。和非同步一章的規則相同：**pin 住以前仍可 move，pin 住以後才要維持位址**。

```rust,editable
use std::marker::PhantomPinned;
use std::pin::Pin;

struct AddressSensitive {
    name: String,
    _pin: PhantomPinned,
}

fn show(value: Pin<&AddressSensitive>) {
    println!("{} 在 {:p}", value.name, &*value);
}

fn main() {
    let value = AddressSensitive {
        name: String::from("固定位置"),
        _pin: PhantomPinned,
    };

    // value 在這之前仍是普通值，可以 move 進 Box::pin。
    let pinned = Box::pin(value);
    show(pinned.as_ref());
}
```

`Box::pin` 把值搬進 heap 的最終位置並建立 `Pin<Box<T>>`。之後可以搬動 `Pin<Box<T>>` 這根指標，但不能透過安全 API 把裡面的 `AddressSensitive` 搬出原位址。

## 範例程式碼

```rust,editable
use std::marker::{PhantomData, PhantomPinned};
use std::pin::Pin;

struct Meters;
struct Seconds;

struct Measurement<Unit> {
    value: f64,
    _unit: PhantomData<Unit>,
}

struct AddressSensitive {
    name: String,
    _pin: PhantomPinned,
}

fn print_record(record: Pin<&AddressSensitive>) {
    println!("紀錄：{}，位址：{:p}", record.name, &*record);
}

fn main() {
    let distance = Measurement::<Meters> {
        value: 12.5,
        _unit: PhantomData,
    };
    let time = Measurement::<Seconds> {
        value: 3.0,
        _unit: PhantomData,
    };

    println!("距離：{}，時間：{}", distance.value, time.value);

    let record = AddressSensitive {
        name: String::from("距離測量"),
        _pin: PhantomPinned,
    };
    let pinned = Box::pin(record);
    print_record(pinned.as_ref());
}
```

## 重點整理

- marker type 不必存放執行時期資料，也能影響型別檢查。
- `PhantomData<T>` 表示外層型別在邏輯上使用、擁有或借用某種 `T`。
- `PhantomData<T>` 會影響 variance 與 `auto trait`。
- 只能留在建立它的執行緒的型別，可用 `PhantomData<Rc<()>>` 阻止自動實作 `Send` 與 `Sync`，避免被搬到其他執行緒或透過共享參考跨執行緒使用。
- `PhantomPinned` 會阻止外層型別自動實作 `Unpin`。
- `PhantomPinned` 本身不會 pin 住值；仍然要透過 `pin!`、`Box::pin` 等方式建立 `Pin`。
- `PhantomPinned` 不禁止 pin 以前的 move；真正的位址保證從 pin 住之後開始。
