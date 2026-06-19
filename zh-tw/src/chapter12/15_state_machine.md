# `async fn` 背後的狀態機

## 本集目標

揭曉編譯器到底把 `async fn` 變成了什麼——一台可以暫停與恢復的狀態機。

## 概念說明

### 一個謎題

我們說 `.await` 會「暫停函數，之後從同一個地方接著跑」。但函數要怎麼「暫停又接著跑」？普通函數一旦開始,就是一路跑到底,中間那些區域變數放在 stack 上,函數一返回就沒了。如果一個 `async fn` 跑到一半要暫停、把執行緒讓出去,那它跑到一半的進度——跑到哪一行了、區域變數現在是什麼值——存到哪去？

答案是:編譯器把你的 `async fn` 改寫成一個 **struct**(更精準說是 enum),用它的欄位來存這些進度。這個東西就叫**狀態機(state machine)**。

### 用一個例子來看

假設你寫了這個 async 函數:

```rust,ignore
async fn example() {
    let a = step_one().await; // 暫停點 1
    let b = step_two(a).await; // 暫停點 2
    println!("{}", b);
}
```

它有兩個 `.await`,也就是兩個可以暫停的地方。編譯器大致會把它想成這樣一台狀態機(這是**示意**,不是真實產生的程式碼):

```rust,ignore
enum ExampleStateMachine {
    Start,                                   // 還沒開始
    WaitingOnStepOne { fut: StepOneFuture },  // 卡在暫停點 1,存著正在等的 future
    WaitingOnStepTwo { fut: StepTwoFuture, a: i32 }, // 卡在暫停點 2,還要記住變數 a
    Done,                                    // 跑完了
}
```

看出重點了嗎?每一個「卡住的地方」都是 enum 的一個 variant,而 variant 裡面的欄位,存的正是**那個當下需要記住的東西**:正在等的內層 future、以及之後還會用到的區域變數(像是 `a`,因為暫停點 2 還要用它)。

### poll 一次 = 在狀態機裡往前走一步

這台狀態機怎麼實作 `poll`?它就是一個 `match`,看自己現在卡在哪個狀態,試著往下一個狀態推:

```rust,ignore
// 同樣是示意
fn poll(&mut self, cx: &mut Context) -> Poll<()> {
    loop {
        match self {
            Start => {
                let fut = step_one();          // 開始做 step_one
                *self = WaitingOnStepOne { fut };
            }
            WaitingOnStepOne { fut } => {
                match fut.poll(cx) {
                    Poll::Ready(a) => {         // step_one 好了,拿到 a
                        let fut2 = step_two(a);
                        *self = WaitingOnStepTwo { fut: fut2, a };
                    }
                    Poll::Pending => return Poll::Pending, // 還沒好,把暫停「往外傳」
                }
            }
            WaitingOnStepTwo { fut, .. } => {
                match fut.poll(cx) {
                    Poll::Ready(b) => {
                        println!("{}", b);
                        *self = Done;
                        return Poll::Ready(());
                    }
                    Poll::Pending => return Poll::Pending,
                }
            }
            Done => panic!("不該再 poll 一個跑完的 future"),
        }
    }
}
```

每次被 poll,它就從目前的狀態試著往前走;遇到內層 future 還沒好(`Pending`),就**把自己停在那個狀態、回 `Pending`**——這就是「暫停」。下次再被 poll,`match` 會落在同一個狀態,從那裡**接著跑**——這就是「恢復」。進度和區域變數,全都好好存在 enum 的欄位裡,完全不靠 stack。

### 所以,`.await` 不是開新執行緒

這解開了一個常見的誤會。`.await` 暫停一個函數,**完全沒有開新的執行緒**,也沒有什麼魔法。它只是:編譯器把你那條「從上到下」的程式,沿著每個 `.await` 切成好幾段,打包成一台 `match` 自己狀態的機器。「暫停」就是停在某個狀態回 `Pending`,「恢復」就是下次 poll 從那個狀態接著跑。

你之所以能把 async 程式寫得跟同步程式幾乎一樣(`let a = ...; let b = ...;`),就是因為編譯器在背後幫你做了這整套又繁瑣又容易錯的改寫。前面幾集我們手刻 `Delay`、`Join` 的時候,是自己用 struct 存狀態、自己寫 `poll`——`async fn` 不過是讓編譯器自動幫你生出同一種東西而已。

## 範例程式碼

這一集沒有可以獨立執行的新範例,因為狀態機是編譯器在背後生成的,你平常看不到也碰不到。真正要記住的是那張對應關係:

```text
你寫的 async fn          編譯器生成的狀態機
────────────────────    ────────────────────
每個 .await         →    一個「卡住」的狀態(enum variant)
跨 .await 用到的區域變數 →  存進那個 variant 的欄位
.await 的內層 future    →  存進 variant 的欄位,在該狀態裡被 poll
函數從上到下的流程     →    poll 裡的 match + 狀態轉移
```

## 重點整理

- 編譯器把 `async fn` 改寫成一台**狀態機**:用一個 enum,每個 `.await` 對應一個「卡住」的狀態
- 跨 `.await` 還會用到的區域變數、正在等的內層 future,都存進狀態機的欄位裡(不靠 stack)
- `poll` 就是「看現在卡在哪個狀態,試著往下一個狀態推」;遇到內層 `Pending` 就停在原狀態回 `Pending`
- **暫停 = 停在某狀態回 `Pending`;恢復 = 下次 poll 從那狀態接著跑**——完全沒有開新執行緒
- 我們手刻 `Delay`／`Join` 做的事,就是編譯器幫 `async fn` 自動做的事
