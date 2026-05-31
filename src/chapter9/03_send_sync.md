# `Send` / `Sync`

## 本集目標

理解 Rust 如何在編譯期保證型別能安全地跨執行緒使用。

## 概念說明

### 為什麼需要額外的保護

還記得第 4 章一開頭的鑰匙圈比喻嗎？現在你應該能理解鑰匙就是指標了。

Rust 有所有權規則以及借用規則——例如同時不能有兩個 `&mut`——的原因之一就是為了防止一個位址的值被同時讀寫，造成前面提到過的**資料競爭（data race）**。舉個具體的例子：假設有一個 `i32` 值是 0，執行緒 A 和執行緒 B 各自透過指標對它加 1。你預期結果是 2，但實際上可能是這樣：

1. 執行緒 A 讀取值：0
2. 執行緒 B 也讀取值：0
3. 執行緒 A 把 0 + 1 = 1 寫回去
4. 執行緒 B 也把 0 + 1 = 1 寫回去

結果是 1，不是 2。兩次加 1 只生效了一次。

注意這裡的關鍵是兩個執行緒同時對同一份資料做讀寫——事實上，只要有共用的資料而且有人在寫，就可能出事。即使另一方只是在讀，也可能讀到還沒完全完成寫入的資料。

Rust 的所有權和借用規則能防止很多問題——例如同時不能有兩個 `&mut`，`&` 和 `&mut` 也不能同時存在。但在多執行緒下，光靠這些還不夠。比如上面的例子：如果只是把 `i32` 的值傳給另一個執行緒，`i32` 是 `Copy` 的，會直接複製一份過去，兩邊各自操作自己的副本，不會出事。但有些型別不是這麼單純——把它 move 過去之後，原本的執行緒可能還持有共用的資料。哪些型別可以安全地跨執行緒？哪些不行？Rust 用兩個 `trait`——`Send` 和 `Sync`——來回答這個問題。

### spawn 實際上在做什麼

上一集用 `thread::spawn` 建立執行緒的時候，我們傳入了一個閉包。閉包會捕捉外部變數——而 `spawn` 實際上就是**把這些捕捉的變數送到另一個執行緒去**。這才是我們真正要關心的事：哪些東西可以被安全地送過去？

### `Send`

一個型別如果實作了 `Send`，代表它的值可以安全地 move 到另一個執行緒。大部分型別都是 `Send`——`i32`、`String`、`Vec<T>`（只要 `T` 是 `Send`）等等都是。

### `Sync`

一個型別如果實作了 `Sync`，代表它的 `&T`（不可變參考）可以安全地在多個執行緒之間共享。換句話說：

> `T: Sync` 等價於 `&T: Send`

如果 `&T` 能安全地送到另一個執行緒，那 `T` 就是 `Sync` 的。

### `Sync` 通常蘊含 `Send`

如果一個東西能被多個執行緒同時讀都沒問題（`Sync`），那把它整個搬到另一個執行緒去——連同時讀的可能性都不存在了——通常只會更安全。所以大部分 `Sync` 的型別也是 `Send`，但少數例外存在。

### `auto trait`：編譯器自動幫你實作的 `trait`

你不需要手動實作 `Send` 或 `Sync`。它們是所謂的 **`auto trait`**——編譯器會自動幫你的型別實作。規則很簡單：如果一個型別裡存的資料都是 `Send`，那它本身預設就是 `Send`。`Sync` 同理。

```rust,noplayground
struct MyData {
    x: i32,    // Send + Sync
    s: String, // Send + Sync
}
// MyData 自動就是 Send + Sync
#
# fn main() {}
```

### 不用死背

你不需要記住哪些型別是 `Send`、哪些是 `Sync`。試著把一個不安全的型別丟進 `thread::spawn`，編譯器會直接報錯告訴你：

```rust,compile_fail
use std::rc::Rc;
use std::thread;

fn main() {
    let data = Rc::new(42);
    thread::spawn(move || {
        println!("{}", data);
    });
    // 編譯錯誤！Rc<i32> 不是 Send
}
```

### 回頭看 `spawn` 的型別簽名

現在我們知道了 `Send` 和 `Sync`，可以回頭看看 `thread::spawn` 的型別簽名：

```rust,ignore
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
where
    F: FnOnce() -> T + Send + 'static,
    T: Send + 'static,
```

閉包 `F` 必須是 `Send`——閉包捕捉了什麼，它的型別就包含什麼，所以如果捕捉的變數不是 `Send`，閉包本身也不會是 `Send`，`spawn` 就會編譯失敗。回傳值 `T` 也必須是 `Send`，因為結果要從子執行緒傳回來。

還有那個 `'static`——為什麼需要它？因為我們完全不知道 `spawn` 出來的執行緒會活多久。你可能會 `join` 它，也可能不 `join` 讓它自己跑到 `main` 結束才被強制終止。Rust 的型別系統沒辦法保證你一定會在某個時間點 `join`，所以它要求最保守的保證：閉包和回傳值裡的所有東西都不能有會過期的借用。第 5 章第 29 集學過 lifetime bound，`T: 'a` 代表 `T` 裡面的所有參考都必須活得過 `'a`。`F: 'static` 就是這個概念的極端情況——閉包裡面的參考要活得跟整個程式一樣久。實務上最常見的做法就是上一集說的 `move`——把值搬進閉包之後，閉包不借用任何東西，自然滿足 `'static`。

## 範例程式碼

```rust,editable
use std::thread;

// 這個 struct 的所有欄位都是 Send + Sync，
// 所以它自動就是 Send + Sync
struct Config {
    name: String,
    max_retries: u32,
}

fn main() {
    let config = Config {
        name: String::from("my_app"),
        max_retries: 3,
    };

    // Config 是 Send，可以安全地 move 到另一個執行緒
    let handle = thread::spawn(move || {
        println!("設定名稱：{}", config.name);
        println!("最大重試次數：{}", config.max_retries);
    });

    handle.join().expect("執行緒發生錯誤");
}
```

## 重點整理

- 資料競爭（data race）：多個執行緒同時存取同一份資料且至少一方在寫，結果不可預期
- `thread::spawn` 的閉包會把捕捉的變數送到另一個執行緒，所以這些變數必須是 `Send`
- `Send` = 值可以安全地 move 到另一個執行緒
- `Sync` = `&T` 可以安全地在多個執行緒之間共享（`T: Sync` 等價於 `&T: Send`）
- `Sync` 通常蘊含 `Send`——能被多執行緒同時讀，搬過去只會更安全
- 編譯器自動推導 `Send` / `Sync`，不用手動標記