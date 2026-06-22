# async 遞迴

## 本集目標

學會 `Box::pin`(heap pinning),並用它解決「async fn 不能直接遞迴」這個會卡住很多人的問題。

## 概念說明

### 一個會編譯失敗的 async 遞迴

第 2 章學過遞迴——函數呼叫自己。你可能會很自然地寫出一個 async 版的遞迴:

```rust,ignore
async fn count_down(n: u32) {
    if n == 0 {
        return;
    }
    println!("{}", n);
    count_down(n - 1).await; // async 函數呼叫自己
}
```

但這會編譯失敗,錯誤訊息大致是:`recursion in an async fn requires boxing`(async fn 的遞迴需要 boxing)。為什麼?

### 為什麼:future 的大小會變成無限大

回想第 15 集:`async fn` 會變成一個狀態機,而跨 `.await` 用到的東西要存進它的欄位。`count_down` 裡有 `count_down(n - 1).await`,所以 `count_down` 的狀態機,**欄位裡要存一個 `count_down` 的狀態機**(它正在等的那個內層 future)。

這就形成了無解的循環:`count_down` 的大小 = 它自己的欄位 + 一個 `count_down` 的大小 = …… 算下去是無限大。編譯器要在編譯期決定每個型別佔多少 bytes,碰到「大小是無限大」當然算不出來,只好報錯。

這其實和第 5 章的**遞迴型別**是一模一樣的問題!還記得那時候:

```rust,ignore
enum List {
    Cons(i32, List), // 錯:List 裡面又有一個 List,大小無限大
    Nil,
}
```

當時的解法是用 `Box` 把遞迴的部分放到 heap 上:`Box<List>`。因為 `Box` 是一個指標,大小固定(就一個位址),這樣型別的大小就有限了。async 遞迴的解法,完全是同一招。

### `Box::pin`:把 future 放到 heap 上釘住

`Box::pin(some_future)` 做兩件事:把 future 放到 **heap** 上(像 `Box` 一樣),並且把它**釘住**,回傳一個 `Pin<Box<F>>`。它就是 `pin!` 的 heap 版本:`pin!` 釘在 stack、生命週期綁在 scope;`Box::pin` 釘在 heap,可以自由地 return、存進 struct、帶著走。

用 `Box::pin` 把遞迴呼叫包起來,遞迴的那一層就變成一個固定大小的指標,大小無限大的問題就解決了:

```rust,ignore
use std::future::Future;
use std::pin::Pin;

fn count_down(n: u32) -> Pin<Box<dyn Future<Output = ()>>> {
    Box::pin(async move {
        if n == 0 {
            return;
        }
        println!("{}", n);
        count_down(n - 1).await; // 遞迴呼叫的結果是 Pin<Box<...>>,大小固定
    })
}
```

注意我們把函數從 `async fn` 改寫成「一個普通 fn,回傳 `Pin<Box<dyn Future>>`,函數體是一個 `Box::pin(async move { ... })`」。這是 async 遞迴的標準寫法。(如果不想手寫這一坨,社群有個 `async-recursion` crate 提供一個 `#[async_recursion]` 標註,自動幫你做這層 boxing。)

### `Pin<Box<dyn Future>>`:能裝「不同」future 的盒子

上面那個回傳型別 `Pin<Box<dyn Future<Output = ()>>>` 還有另一個超好用的身分,值得單獨講。

`dyn Future` 是第 10 章學過的 trait object——它把「具體是哪一種 future」抹除掉,只記得「這是一個 `Output` 為 `()` 的 future」。包成 `Pin<Box<dyn Future<...>>>` 之後,**不同的 future 就有了相同的型別**,於是你能把它們放進同一個 `Vec`、或從 `match` 的不同分支回傳:

```rust,ignore
use std::future::Future;
use std::pin::Pin;

fn pick(which: bool) -> Pin<Box<dyn Future<Output = i32>>> {
    if which {
        Box::pin(async { 1 })        // 這是一種 future
    } else {
        Box::pin(async { 2 + 2 })    // 這是「另一種」future,本來型別不同
    }
    // 兩個分支的 future 具體型別不一樣,但包成 Pin<Box<dyn Future>> 後型別一致,才能這樣寫
}
```

這完全對應第 6 章我們用 `Box<dyn Fn>` 把不同的閉包裝進同一個 `Vec` 的招數——閉包每個都是獨立型別,`Box<dyn Fn>` 把它們統一;future 也每個都是獨立型別,`Pin<Box<dyn Future>>` 把它們統一。你甚至會發現,第 9 集手寫 `Join` 時用的 `Pin<Box<dyn Future<Output = ()>>>`,正是這個東西——當時我們先當黑盒子,現在你懂它了。

`Pin<Box<dyn Future<...>>>` 這個型別很常出現,社群常把它簡寫成 `BoxFuture`(`futures` crate 裡有現成的型別別名)。

## 範例程式碼

```rust,ignore
use std::future::Future;
use std::pin::Pin;

fn count_down(n: u32) -> Pin<Box<dyn Future<Output = ()>>> {
    Box::pin(async move {
        if n == 0 {
            println!("發射！");
            return;
        }
        println!("{}", n);
        count_down(n - 1).await;
    })
}

#[tokio::main]
async fn main() {
    count_down(3).await; // 印出 3, 2, 1, 發射！
}
```

## 重點整理

- `async fn` 直接遞迴會編譯失敗:狀態機欄位裡要存一個自己,大小變成無限大(和第 5 章遞迴型別同一個問題)
- 解法和當年一樣:用 `Box` 把遞迴那層放到 heap、變成固定大小的指標
- `Box::pin(future)` = 把 future 放到 **heap** 上並釘住,回傳 `Pin<Box<F>>`;是 `pin!` 的 heap 版,可以自由帶出 scope
- async 遞迴的標準寫法:普通 `fn` 回傳 `Pin<Box<dyn Future<...>>>`,函數體是 `Box::pin(async move { ... })`
- `Pin<Box<dyn Future<...>>>`(常簡寫 `BoxFuture`)能讓**不同的 future 有相同型別**,可放進同一個 `Vec`、從 `match` 分支回傳——對應第 6 章 `Box<dyn Fn>` 的招數
