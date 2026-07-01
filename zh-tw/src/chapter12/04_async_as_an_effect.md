# `async` 是一種 effect

## 本集目標

換一個角度看 `async`：把 `.await` 和你早就會的 `?` 放在一起，發現它們其實是同一類東西。

## 正文

### 兩個「小尾巴」

回想一下第 5 章的 `?`。當一個運算式的型別是 `Option` / `Result`，你在它後面黏一個 `?`，就能把裡面那個「成功的值」拉出來用，而「萬一失敗了怎麼辦」這件事交給編譯器自動處理：

```rust,ignore
let x = a.parse::<i32>()?; // ? 把 Result 裡的值拉出來
```

`.await` 做的事也很像。當一個運算式的型別是 `Future`，你在它後面黏一個 `.await`，就能把裡面那個「之後會算好的值」拉出來用，而「萬一還沒好怎麼辦」這件事交給 runtime 自動處理：

```rust,ignore
let x = some_async_thing().await; // .await 把 Future 裡的值拉出來
```

看出來了嗎？`?` 和 `.await` 都是**黏在運算式後面的小尾巴**，它們把「包在某個特殊世界裡的值」拉到你手上。

### 兩個世界，各有各的規矩

可以把這想成：有些值不是住在「普通世界」，而是住在一個被包起來的特殊世界裡。

- **`Option` / `Result` 世界**：值可能算不出來。這個世界的規矩是「可能失敗」。
- **`Future` 世界**：值可能還沒好，要等。這個世界的規矩是「或許還沒好」。

當你用 `?` 或 `.await` 把值拉出來，你寫的程式看起來就跟普通程式沒兩樣——一行接一行、把值拿來算。但背後編譯器其實在替你做一件事：把這些「包裝過的值」按照各自世界的規矩**串接起來**。每一個 `?` 或 `.await`，就是一道「套用規矩」的接縫：`?` 那道接縫會在出錯時自動提早回傳；`.await` 那道接縫則會在還沒好時自動暫停，把執行緒讓出去。

### 為什麼 `.await` 需要專屬的 `async` 語法

`?` 的規矩比較單純，編譯器只要插入一個「出錯就提早 `return`」的判斷就好。但 `.await` 的規矩複雜得多：在「還沒好」的時候，它得把整個函數**暫停**起來、記住現在跑到哪、把執行緒讓給別人，等好了再從原地接著跑。

要做到這件事，編譯器得把你的 `async` 函數**大幅改寫**成一個叫「狀態機」的東西（本章後面會解釋，現在先記得這個詞就好）。正因為改寫幅度這麼大，Rust 才需要 `async` 這個專屬的關鍵字——它等於是在告訴編譯器：「這一段請幫我改寫成可以暫停、可以恢復的形式」。

### `async` 會「傳染」

`?` 的限制是你只能在「回傳 `Option` / `Result` 的函數」裡用它。同理，`.await` 也只能在 `async` 的環境裡用。在一個普通函數裡直接 `.await` 會編譯失敗：

```rust,compile_fail
# extern crate tokio;
#
async fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn normal_function() {
    let sum = add(3, 4).await; // 編譯錯誤：一般函數裡不能 .await
}
#
# fn main() {}
```

換句話說，你只能在「世界裡面」拉值。想用 `.await`，你所在的函數自己也得是 `async`——於是 `async` 會一路往上「傳染」。這和 `?` 要求「呼叫端自己也得能處理錯誤」是同一回事。

### 作用總要「落地」

不管哪個世界，總有一刻要回到普通世界——把包裝拆掉、得到一個實實在在的值。先看錯誤處理是怎麼「落地」的，它有兩條路。

第一條：讓 `main` 自己回傳 `Result`，在程式的邊界給編譯器處理。

```rust,editable
fn parse_and_add(a: &str, b: &str) -> Result<i32, std::num::ParseIntError> {
    let x = a.parse::<i32>()?;
    let y = b.parse::<i32>()?;
    Ok(x + y)
}

fn main() -> Result<(), std::num::ParseIntError> {
    let sum = parse_and_add("3", "4")?;
    println!("結果是 {}", sum);
    Ok(())
}
```

第二條：自己用 `match` 當場把 `Result` 拆開，在普通程式裡處理掉。

```rust,editable
fn parse_and_add(a: &str, b: &str) -> Result<i32, std::num::ParseIntError> {
    let x = a.parse::<i32>()?;
    let y = b.parse::<i32>()?;
    Ok(x + y)
}

fn main() {
    match parse_and_add("3", "4") {
        Ok(sum) => println!("結果是 {}", sum),
        Err(e) => println!("出錯了：{}", e),
    }
}
```

### `async` 的落地，完全對應

`Future` 世界的落地也是這兩條路，而且一一對應：

**第一條：`#[tokio::main]`**，對應「回傳 `Result` 的 `main`」。你只管把 `main` 加上 `async`，用 Tokio 這個框架在程式的邊界處理：

```rust,editable
extern crate tokio;

async fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[tokio::main]
async fn main() {
    let sum = add(3, 4).await;
    println!("結果是 {}", sum);
}
```

**第二條：`block_on`**，對應「自己 `match`」。你在一個普通的 `main` 裡，當場叫 runtime 把一個 `Future` 跑到完成，結算成普通值：

```rust,editable
extern crate tokio;

async fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let runtime = tokio::runtime::Runtime::new().expect("無法建立 runtime");
    let sum = runtime.block_on(add(3, 4)); // 當場把 Future 結算成普通值
    println!("結果是 {}", sum);
}
```

兩兩對照：回傳 `Result` 的 `main` ↔ `#[tokio::main]`（交給框架在邊界結算），`match` ↔ `block_on`（自己在同步程式裡當場結算）。把這個對應記在心裡，`async` 對你來說就不再是全新的東西，而是「你早就會的 `?`，但換了一套更複雜的規矩」。

## 重點整理

- `?` 和 `.await` 都是黏在運算式後的小尾巴，把「特殊世界裡的值」拉出來
- `Result` 世界的規矩是「可能失敗」，`Future` 世界的規矩是「可能還沒好」；編譯器替你把包裝過的值按規矩串接起來
- `.await` 的規矩複雜，會把函數改寫成**狀態機**，所以需要 `async` 專屬語法
- `async` 的 `.await` 像 `?` 一樣會「傳染」：要 `.await`，所在的函數自己也得是 `async`
- 落地兩條路一一對應：回傳 `Result` 的 `main` ↔ `#[tokio::main]`，`match` ↔ `block_on`
