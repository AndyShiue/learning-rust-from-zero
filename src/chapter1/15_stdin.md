# stdin

## 本集目標
讓程式讀取使用者的鍵盤輸入——先照抄，不用完全理解每一行。

## 正文

到目前為止，我們程式裡的值都是寫死的。但如果想讓使用者自己輸入呢？比如讓使用者輸入名字，然後程式跟他打招呼？

### 先照抄這段程式碼

```rust,no_run
fn main() {
    println!("請輸入你的名字：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    println!("你好，{}！", input.trim());
}
```

跑起來的效果：

```ignore
請輸入你的名字：
Andy
你好，Andy！
```

### 這段在幹嘛？

我知道這段看起來有點嚇人，但別擔心，我們先把它當成一個**黑盒子**——你只要知道它能讀取使用者輸入就好。

大概的意思是：

1. `let mut input = String::new();` → 建立一個空的文字變數，準備接收輸入
2. `std::io::stdin().read_line(&mut input).expect("讀取失敗");` → 從鍵盤讀一行文字，存到 `input` 裡
3. `input.trim()` → 把多餘的空白和換行符號去掉

至於 `String::new()`、`&mut`、`.expect()` 這些是什麼意思？以後會慢慢教，現在先照抄就好。

### 為什麼先不解釋？

因為要解釋這段程式碼，需要先理解好幾個還沒學的觀念。與其硬塞一堆看不懂的解釋，不如先學會用，之後自然就懂了。

就像小時候你學騎腳踏車，不用先學力學和陀螺效應——先騎就對了。

### 重要的事

每次要讀使用者輸入，就把這三行拿去用：

```rust,no_run
# fn main() {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");
    let name = input.trim(); // 去掉尾巴的換行
# }
```

## 重點整理
- 讀取使用者輸入的三行固定寫法：`String::new()` → `stdin().read_line()` → `.trim()`
- 這段先當成黑盒子照抄即可，背後的觀念之後會慢慢學
- `.trim()` 用來去掉輸入尾巴的換行符號
