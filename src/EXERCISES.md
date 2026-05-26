# 固定練習題題庫

這份文件是給 AI 用的固定題庫。讀者要練習題時，AI 必須優先從這裡挑題，而不是現場自由發揮。題庫可以慢慢補，不需要一次寫完整本書。

這份題庫不是「靈感來源」，而是「限制來源」。AI 不能看完本文件後自行加出一堆更進階、更完整、或更像一般 Rust 課程的題目；只能依讀者進度與條目狀態出題。

## 先看狀態，不能跳過

讀者要第 X 章第 Y 集題目時：

1. 找到該集條目。
2. 先看 `狀態`。
3. 只有 `可用` 可以直接出題。
4. `不出題` 代表作者刻意不安排題目；不要出題，先說明原因並建議前面最近的 `可用` 題目或繼續讀。只有讀者明確堅持要練該集時，才可以臨時出 1 題，並說明這不是固定題。
5. `TODO` 或找不到條目時，不要假裝有固定題目。
6. `草稿` 只能參考，除非讀者明確要求，否則優先挑 `可用` 題目。

這條規則優先於「讀者想要題目」本身；不能因為讀者指定某一集，就無視該集的 `不出題` 狀態。

## 使用規則

1. 題目只給讀者看「題目」部分；不要一開始就給「批改重點」「提示方向」「參考答案」。
2. 讀者作答後，先用「批改重點」判斷他是否抓到本題目標。
3. 讀者卡住時，照「提示方向」一層一層給，不要一次把答案攤開。
4. 讀者要求解答、或已經嘗試過仍卡住時，才可以給「參考答案」。
5. 固定題庫以「程式題」為主，不為了湊題目放操作確認或名詞問答。

## 題庫狀態

- `可用`：可以直接出給讀者。若讀者要求多題，從目前進度內的 `可用` 題目挑 1～3 題。
- `草稿`：題目方向可參考，但還沒定稿；除非讀者明確要求，否則優先挑 `可用` 題目。
- `TODO`：題目尚未填寫；AI 不要假裝有固定題目，應告訴讀者這一集題庫還沒有固定題目，並建議他做前面最近的 `可用` 題目，或先往後讀到下一個適合練習的集數。
- `不出題`：作者刻意不安排題目。AI 應簡短說明不出題原因，建議讀者做前面最近的 `可用` 題目，或繼續讀到下一個適合練習的集數；不要臨時補題，除非讀者明確堅持要練該集。

常見不出題原因包括：該集只是安裝或專案操作、題目會變成名詞問答、題目只是在重打正文範例、目前進度還缺少必要語法、或這個概念比較適合等幾集後放進綜合題。

## 題目格式

````md
### 第 X 章第 Y 集：標題

狀態：TODO / 不出題 / 草稿 / 可用

不出題原因：
- 若狀態是 `不出題`，簡短說明原因；其他狀態可省略這段。

練習目標：
- ...

題目：
1. ...
2. ...
3. ...

批改重點：
- ...

提示方向：
1. ...
2. ...
3. ...

參考答案：
```rust
// 若本題需要程式碼，放在這裡。
```
````

## 第 1 章

### 第 1 章第 1 集：安裝 Rust

狀態：不出題

不出題原因：
- 這集目標是安裝工具並確認 `rustc --version` 能跑，屬於環境設定，不適合出程式題。
- AI 可以協助確認安裝是否成功，或處理終端機找不到指令等問題，但不要硬出練習題。

### 第 1 章第 2 集：第一個程式

狀態：不出題

不出題原因：
- 這集主要是第一次用 `cargo new` 建專案、打開 `src/main.rs`、用 `cargo run` 跑範例，屬於專案操作與照著書跑第一個程式。
- 若硬出題，容易變成操作確認或名詞問答；請建議讀者先確定程式能跑，再繼續讀到下一個適合練習的集數。

### 第 1 章第 3 集：變數與輸出

狀態：可用

練習目標：
- 確認讀者會用 `let` 建立變數。
- 確認讀者會用 `{}` 把變數放進 `println!` 的輸出。
- 確認讀者知道 `let` 可以先宣告、之後再賦值，但使用前一定要有值。

題目：
1. 建立一個叫 `name` 的變數，值是你的名字，然後讓程式印出 `Hello, OOO!`。

批改重點：
- 變數要用 `let` 宣告。
- 這一集只練一個 `{}`，不要要求讀者使用多個佔位符；多個 `{}` 會在第 1 章第 5 集再處理。
- 文字要用雙引號包起來。
- 如果讀者使用先宣告再賦值的寫法，只要有在 `println!` 前完成賦值就可以。

提示方向：
1. `let name = "小明";` 這種寫法會建立一個文字變數。
2. `println!("Hello, {}!", name);` 裡的 `{}` 會被 `name` 的值取代。

參考答案：

```rust
fn main() {
    let name = "小明";
    println!("Hello, {}!", name);
}
```

### 第 1 章第 4 集：註解

狀態：可用

練習目標：
- 確認讀者知道 `//` 後面的內容不會被執行。
- 確認讀者會用註解暫時關掉一行程式碼。

題目：
1. 下面這段程式現在會印出兩行。請用 `//` 註解掉其中一行，讓程式只印出 `Hello, Rust!`。

參考起始程式：

```rust
fn main() {
    println!("Hello, world!");
    println!("Hello, Rust!");
}
```

批改重點：
- 讀者應該用 `//` 註解掉 `println!("Hello, world!");`。
- 不需要刪掉那一行。
- 不需要使用 `/* */`，這題只練單行註解。

提示方向：
1. `//` 後面的東西會被電腦忽略。
2. 這題要留下 `Hello, Rust!` 那一行能正常執行。

參考答案：

```rust
fn main() {
    // println!("Hello, world!");
    println!("Hello, Rust!");
}
```

### 第 1 章第 5 集：算術運算子

狀態：可用

練習目標：
- 確認讀者會用 `/` 做整數除法。
- 確認讀者會用 `%` 取得餘數。
- 確認讀者會讓多個 `{}` 依序對應後面的值。

題目：
1. 建立兩個變數 `total = 17` 和 `group = 5`，印出下面兩行：

```text
17 / 5 = 3
17 % 5 = 2
```

批改重點：
- 要使用兩個變數 `total` 和 `group`，不要只把數字直接寫死在字串裡。
- 第一行要用 `total / group`。
- 第二行要用 `total % group`。
- `println!` 裡的 `{}` 數量要和後面的值數量對上。
- 如果讀者問為什麼 `17 / 5` 是 `3`，用「整數除法會直接捨去小數部分」回答。

提示方向：
1. 可以先寫 `let total = 17;` 和 `let group = 5;`。
2. `println!("{} / {} = {}", total, group, total / group);`
3. `%` 可以算出除完後剩下多少。

參考答案：

```rust
fn main() {
    let total = 17;
    let group = 5;

    println!("{} / {} = {}", total, group, total / group);
    println!("{} % {} = {}", total, group, total % group);
}
```

### 第 1 章第 6 集：運算子優先順序

狀態：不出題

不出題原因：
- 這集重點是理解「先乘除後加減」以及用括號改變順序；若出題很容易只是重打正文範例。
- 這個概念會自然出現在後面的算式題裡，不需要在本集硬出獨立題目。

### 第 1 章第 7 集：比較運算子

狀態：不出題

不出題原因：
- 這集主要是認識 `==`、`!=`、`<`、`>`、`<=`、`>=` 以及比較結果是 `true` / `false`。
- 單獨出題容易太簡單或變成符號問答；比較運算子會從第 8 集 `if` 開始自然放進程式題裡練。

### 第 1 章第 8 集：`if`

狀態：可用

練習目標：
- 確認讀者會寫基本 `if`。
- 確認讀者知道條件為 `true` 才會執行大括號裡的程式碼。
- 確認讀者不會替 `if` 條件加小括號。

題目：
1. 建立一個變數 `score = 85`。如果 `score >= 60`，就印出 `及格`。

預期輸出：

```text
及格
```

批改重點：
- 要使用 `if score >= 60 { ... }`。
- `println!("及格");` 要放在 `if` 的大括號裡。
- 不要寫 `else`，`else` 下一集才會教。
- Rust 的 `if` 條件不需要小括號；如果讀者寫了小括號，可以提醒拿掉比較符合書中寫法。

提示方向：
1. 先建立變數：`let score = 85;`
2. 條件可以寫成 `score >= 60`。
3. 條件成立時要做的事放進 `{}` 裡。

參考答案：

```rust
fn main() {
    let score = 85;

    if score >= 60 {
        println!("及格");
    }
}
```

### 第 1 章第 9 集：作用域

狀態：可用

練習目標：
- 確認讀者知道 `{}` 會建立作用域。
- 確認讀者知道在作用域裡建立的變數，出了 `{}` 就不能用。
- 確認讀者能把變數放到正確的位置，讓程式可以編譯。

題目：
1. 下面這段程式會出錯，因為 `message` 在大括號外面用不到。請只移動 `let message = "Hello";` 這一行，讓程式可以印出 `Hello`。

起始程式：

```rust
fn main() {
    {
        let message = "Hello";
    }

    println!("{}", message);
}
```

批改重點：
- `let message = "Hello";` 應該移到外層，也就是 `println!` 看得到的地方。
- 不要只把 `println!` 移進內層；這樣雖然能跑，但沒有練到「讓外面也看得到」。
- 空的大括號可以保留，也可以拿掉。
- 不要解釋所有權或生命週期，這裡只講作用域。
- 修完後程式要能用 `cargo run` 跑。

提示方向：
1. 在 `{}` 裡建立的變數，出了那對 `{}` 就看不到了。
2. 想讓 `println!` 看得到 `message`，`message` 要放在跟 `println!` 同一層，或更外層。

參考答案：

```rust
fn main() {
    let message = "Hello";

    println!("{}", message);
}
```

### 第 1 章第 10 集：`else`

狀態：可用

練習目標：
- 確認讀者會寫 `if ... else ...`。
- 確認讀者知道條件成立走 `if`，不成立走 `else`。
- 確認讀者知道 `if...else...` 一次只會走其中一邊。

題目：
1. 建立一個變數 `temperature = 18`。如果 `temperature >= 25`，印出 `熱`；否則印出 `涼`。

預期輸出：

```text
涼
```

批改重點：
- 要使用 `if temperature >= 25 { ... } else { ... }`。
- `temperature = 18` 時應該走 `else` 那邊。
- 不要寫成兩個獨立的 `if`；這一題要練二選一。
- Rust 的 `if` 條件不需要小括號。

提示方向：
1. 先建立變數：`let temperature = 18;`
2. 條件是 `temperature >= 25`。
3. `else` 裡放條件不成立時要做的事。

參考答案：

```rust
fn main() {
    let temperature = 18;

    if temperature >= 25 {
        println!("熱");
    } else {
        println!("涼");
    }
}
```

### 第 1 章第 11 集：`else if`

狀態：可用

練習目標：
- 確認讀者會用 `else if` 處理三種以上情況。
- 確認讀者知道 Rust 會從上到下檢查條件。
- 確認讀者知道第一個成立後，後面分支就不會執行。

題目：
1. 建立一個變數 `temperature = 32`，依照下面規則印出結果：
   - `temperature >= 35`：印出 `很熱`
   - `temperature >= 25`：印出 `溫暖`
   - 其他情況：印出 `偏涼`

預期輸出：

```text
溫暖
```

批改重點：
- 要使用 `if ... else if ... else`。
- `temperature = 32` 時，第一個條件 `temperature >= 35` 不成立，第二個條件 `temperature >= 25` 成立，所以印出 `溫暖`。
- 條件順序不能反過來；如果先寫 `temperature >= 25`，那 `35` 以上也會先被抓走。
- 不要寫成三個獨立的 `if`。

提示方向：
1. 先判斷最嚴格的條件：`temperature >= 35`。
2. 第二段用 `else if temperature >= 25`。
3. 最後用 `else` 處理剩下的情況。

參考答案：

```rust
fn main() {
    let temperature = 32;

    if temperature >= 35 {
        println!("很熱");
    } else if temperature >= 25 {
        println!("溫暖");
    } else {
        println!("偏涼");
    }
}
```

### 第 1 章第 12 集：邏輯運算子

狀態：可用

練習目標：
- 確認讀者會用 `&&` 組合兩個條件。
- 確認讀者知道 `&&` 需要兩邊都成立才會執行。
- 確認讀者會用 `||` 和括號表達比較複雜的條件分組。

題目：
1. 建立兩個變數：`age = 20`、`has_ticket = true`。如果 `age >= 18` 而且 `has_ticket` 是 `true`，就印出 `可以入場`；否則印出 `不能入場`。
2. 建立三個變數：`age = 16`、`with_parent = true`、`has_ticket = true`。規則是：有票，而且「年滿 18 歲或者有家長陪同」，就可以入場。請印出 `可以入場` 或 `不能入場`。

預期輸出：

```text
可以入場
可以入場
```

批改重點：
- 第 1 題要使用 `age >= 18 && has_ticket`。
- 不需要寫 `has_ticket == true`，直接寫 `has_ticket` 就可以。
- 第 2 題應該使用 `has_ticket && (age >= 18 || with_parent)`。
- 第 2 題的括號很重要，因為題目要表達的是「有票」而且「年滿 18 或有家長陪同」。
- 不要寫成 `has_ticket && age >= 18 || with_parent`，這會讓 `with_parent` 看起來可以繞過「有票」這個條件。
- 如果讀者問運算順序，可以先提醒「不確定時加括號，讓條件更清楚」，不用展開太多細節。

提示方向：
1. 「而且」對應到 `&&`。
2. 「或者」對應到 `||`。
3. 第二題可以先把「年滿 18 或有家長陪同」寫成 `(age >= 18 || with_parent)`，再和 `has_ticket` 用 `&&` 接起來。

參考答案：

```rust
fn main() {
    let age = 20;
    let has_ticket = true;

    if age >= 18 && has_ticket {
        println!("可以入場");
    } else {
        println!("不能入場");
    }

    let age = 16;
    let with_parent = true;
    let has_ticket = true;

    if has_ticket && (age >= 18 || with_parent) {
        println!("可以入場");
    } else {
        println!("不能入場");
    }
}
```

### 第 1 章第 13 集：`let mut`

狀態：可用

練習目標：
- 確認讀者知道 Rust 變數預設不可變。
- 確認讀者會用 `let mut` 宣告可變變數。
- 確認讀者知道修改變數時不用再寫 `let`。

題目：
1. 下面這段程式想把 `coins` 從 `3` 改成 `5`，但現在會編譯失敗。請修正它，讓程式最後印出 `5`。

起始程式：

```rust
fn main() {
    let coins = 3;
    coins = 5;
    println!("{}", coins);
}
```

批改重點：
- `coins` 的宣告要改成 `let mut coins = 3;`。
- 修改值時應該寫 `coins = 5;`，不要寫 `let coins = 5;`。
- 不要在這裡引入 shadowing；shadowing 會在第 2 章第 2 集才講。
- 修完後程式應該印出 `5`。

提示方向：
1. Rust 的變數預設不能改值。
2. 如果之後要改，宣告時要加 `mut`。
3. 改值那一行不用再寫 `let`。

參考答案：

```rust
fn main() {
    let mut coins = 3;
    coins = 5;
    println!("{}", coins);
}
```

### 第 1 章第 14 集：複合賦值運算子

狀態：可用

練習目標：
- 確認讀者知道 `x += 5` 等同於 `x = x + 5`。
- 確認讀者會用複合賦值運算子更新可變變數。
- 確認讀者知道使用複合賦值時，變數必須是 `let mut`。

題目：
1. 老師正在調整學生的分數：原本是 `60` 分，先加 `10` 分鼓勵分，再把分數乘以 `2`。下面這段程式可以跑，請把更新 `score` 的兩行改成使用複合賦值運算子，讓最後輸出仍然是 `140`。

起始程式：

```rust
fn main() {
    let mut score = 60;

    score = score + 10;
    score = score * 2;

    println!("{}", score);
}
```

預期輸出：

```text
140
```

批改重點：
- 應該改成 `score += 10;`、`score *= 2;`。
- `score` 必須保留 `let mut`。
- 不要把結果直接寫成 `let score = 140;` 或 `score = 140;`。
- 最後輸出要仍然是 `140`。

提示方向：
1. `score = score + 10;` 可以改成 `score += 10;`。
2. 乘法也有對應的簡寫。
3. 因為 `score` 一直在改值，所以宣告時要保留 `mut`。

參考答案：

```rust
fn main() {
    let mut score = 60;

    score += 10;
    score *= 2;

    println!("{}", score);
}
```

### 第 1 章第 15 集：`stdin`

狀態：可用

練習目標：
- 確認讀者能照抄 stdin 固定寫法。
- 確認讀者會用 `input.trim()` 印出使用者輸入的內容。
- 確認讀者不需要在這裡理解 `String::new()`、`&mut`、`.expect()` 的細節。

題目：
1. 寫一個程式，請使用者輸入最喜歡的食物，然後印出 `你喜歡 OOO！`。

執行範例：

```text
請輸入你最喜歡的食物：
拉麵
你喜歡 拉麵！
```

批改重點：
- 可以直接沿用書中的 stdin 三行固定寫法。
- 輸出時要使用 `input.trim()`，避免把輸入尾巴的換行一起印出來。
- 不要要求讀者解釋 `String::new()`、`&mut`、`.expect()`。
- 不要改成讀數字；字串轉數字下一集才教。

提示方向：
1. 先照抄書中的三行讀取輸入寫法。
2. 把提示文字改成 `請輸入你最喜歡的食物：`。
3. 最後用 `println!("你喜歡 {}！", input.trim());`。

參考答案：

```rust
fn main() {
    println!("請輸入你最喜歡的食物：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    println!("你喜歡 {}！", input.trim());
}
```

### 第 1 章第 16 集：`parse`

狀態：可用

練習目標：
- 確認讀者能把使用者輸入的文字轉成 `i32`。
- 確認讀者會把轉換後的數字拿來做運算。
- 確認讀者繼續使用 `.expect("請輸入數字")`，不要用還沒學到的錯誤處理方式。

題目：
1. 寫一個程式，請使用者輸入一個數字，然後印出這個數字加 `10` 的結果。

執行範例：

```text
請輸入一個數字：
32
32 加 10 等於 42
```

批改重點：
- 要使用 `input.trim().parse::<i32>().expect("請輸入數字")`。
- 加法要用轉換後的數字變數，不要直接把輸入當文字處理。
- 不要使用 `.unwrap()` 或 `?`。
- 不要展開解釋 turbofish、泛型或 `Result`；這裡先照書的方式把 `.parse::<i32>()` 當固定寫法。

提示方向：
1. 先照抄 stdin 讀取輸入的固定寫法。
2. 用 `let num = input.trim().parse::<i32>().expect("請輸入數字");` 把文字轉成數字。
3. `num + 10` 就是加 10 後的結果。

參考答案：

```rust
fn main() {
    println!("請輸入一個數字：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let num = input.trim().parse::<i32>().expect("請輸入數字");

    println!("{} 加 10 等於 {}", num, num + 10);
}
```

### 第 1 章第 17 集：綜合練習

狀態：可用

練習目標：
- 確認讀者能把 `stdin`、`parse`、`if`、`else if`、`else` 組合起來。
- 確認讀者會在既有分數判斷程式中加入新的條件分支。
- 確認讀者知道 `else if` 的順序會影響結果。

題目：
1. 以書中的「輸入分數 → 判斷等第」程式為基礎，加入 D 等第：`60` 到 `69` 分印出 `你的成績是 D`。其他規則維持不變。

執行範例：

```text
請輸入你的分數：
65
你的成績是 D
```

批改重點：
- 要保留 stdin 和 parse 的固定寫法。
- 要在 `score >= 70` 後面、最後的 `else` 前面加入 `else if score >= 60`。
- 條件順序不能亂掉；如果把 `score >= 60` 放太前面，70、80、90 以上的分數會被錯誤歸到 D。
- 不要要求讀者處理超過 100 或小於 0；那可以留給之後或讀者主動挑戰。

提示方向：
1. 先找到書中判斷 C 的那一段：`else if score >= 70`。
2. D 應該放在 C 後面、F 前面。
3. 最後的 `else` 仍然處理 60 分以下。

參考答案：

```rust
fn main() {
    println!("請輸入你的分數：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let score = input.trim().parse::<i32>().expect("請輸入數字");

    if score >= 90 {
        println!("你的成績是 A");
    } else if score >= 80 {
        println!("你的成績是 B");
    } else if score >= 70 {
        println!("你的成績是 C");
    } else if score >= 60 {
        println!("你的成績是 D");
    } else {
        println!("你的成績是 F");
    }
}
```

### 第 1 章第 18 集：`loop` + `break`

狀態：可用

練習目標：
- 確認讀者會用 `loop` 重複要求輸入。
- 確認讀者會用 `break` 在條件成立時離開迴圈。
- 確認讀者能把 `stdin`、`parse`、`if`、`loop` 組合起來。

題目：
1. 寫一個程式，反覆請使用者輸入數字。如果輸入的數字大於 `0`，就印出 `收到正數！` 並結束程式；如果輸入的數字小於或等於 `0`，就印出 `請再試一次`，然後繼續要求輸入。

執行範例：

```text
請輸入一個正數：
-3
請再試一次
請輸入一個正數：
0
請再試一次
請輸入一個正數：
5
收到正數！
```

批改重點：
- 要使用 `loop` 包住「提示、讀取、parse、判斷」這整段流程。
- 每次迴圈裡都要建立新的 `input`，避免沿用上一輪輸入。
- 要使用 `.parse::<i32>().expect("請輸入數字")`。
- 當 `num > 0` 時，要印出 `收到正數！` 並 `break`。
- 當 `num <= 0` 時，要印出 `請再試一次`，但不要 `break`。
- 不要改用 `while` 或 `for`，那是後面才教。

提示方向：
1. 先寫出 `loop { ... }`。
2. 把 stdin 和 parse 的固定寫法放進 `loop` 裡。
3. 用 `if num > 0 { ... } else { ... }` 判斷要不要 `break`。

參考答案：

```rust
fn main() {
    loop {
        println!("請輸入一個正數：");

        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("讀取失敗");

        let num = input.trim().parse::<i32>().expect("請輸入數字");

        if num > 0 {
            println!("收到正數！");
            break;
        } else {
            println!("請再試一次");
        }
    }
}
```

### 第 1 章第 19 集：`while`

狀態：可用

練習目標：
- 確認讀者會用 `while` 在條件成立時重複執行。
- 確認讀者會在迴圈中更新變數，讓迴圈最後停下來。
- 確認讀者能把兩次 `stdin`、`parse`、`let mut`、`while` 組合起來。

題目：
1. 寫一個「存錢達標」程式，請使用 `while`。請使用者先輸入目標金額 `goal`，再輸入目前已經存到的金額 `money`。接著程式每一輪幫他多存 `30` 元，並印出目前存到多少錢。只要 `money` 還小於 `goal`，就繼續存；達標後印出 `達標！`。

執行範例：

```text
請輸入目標金額：
100
請輸入目前金額：
40
目前存到 70 元
目前存到 100 元
達標！
```

批改重點：
- 要讀取兩次輸入：一次給 `goal`，一次給 `money`。
- `goal` 可以不可變，`money` 必須是 `let mut`，因為迴圈中會改它。
- 兩次輸入都要用 `.parse::<i32>().expect("請輸入數字")`。
- 要使用 `while money < goal`。
- 迴圈裡要先讓 `money += 30;`，再印出目前金額。
- 迴圈結束後要印出 `達標！`。
- 不要改用 `loop` 或 `for`，這題要練 `while`。

提示方向：
1. 可以先照 stdin 固定寫法讀取 `goal`。
2. 再寫第二組 stdin 固定寫法讀取 `money`。
3. 因為 `money` 會在迴圈裡增加，所以要寫 `let mut money = ...`。
4. 條件可以寫成 `while money < goal`。

參考答案：

```rust
fn main() {
    println!("請輸入目標金額：");

    let mut goal_input = String::new();
    std::io::stdin().read_line(&mut goal_input).expect("讀取失敗");

    let goal = goal_input.trim().parse::<i32>().expect("請輸入數字");

    println!("請輸入目前金額：");

    let mut money_input = String::new();
    std::io::stdin().read_line(&mut money_input).expect("讀取失敗");

    let mut money = money_input.trim().parse::<i32>().expect("請輸入數字");

    while money < goal {
        money += 30;
        println!("目前存到 {} 元", money);
    }

    println!("達標！");
}
```

### 第 1 章第 20 集：`for` + range

狀態：可用

練習目標：
- 確認讀者會用 `for` 搭配 range 重複執行。
- 確認讀者知道 `a..b` 不包含 `b`，`a..=b` 包含 `b`。
- 確認讀者知道 `for` 裡的變數不需要自己用 `let` 宣告。
- 確認讀者能把 `for`、`%`、`if` / `else if` / `else`、`&&` 組合起來。

題目：
1. 寫一個程式，請使用 `for`。讓使用者輸入最後一個座位號碼 `last`，然後從 `1` 印到 `last`，每一行格式是 `座位 OOO 號`。
2. 寫一個 FizzBuzz 程式，請使用 `for`。讓使用者輸入一個正整數 `n`，從 `1` 印到 `n`：如果數字同時是 `3` 和 `5` 的倍數，印出 `FizzBuzz`；如果只是 `3` 的倍數，印出 `Fizz`；如果只是 `5` 的倍數，印出 `Buzz`；其他數字照原樣印出來。

執行範例：

```text
請輸入最後一個座位號碼：
4
座位 1 號
座位 2 號
座位 3 號
座位 4 號
```

```text
請輸入一個正整數：
15
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

批改重點：
- 要使用 stdin 固定寫法和 `.parse::<i32>().expect("請輸入數字")`。
- 第 1 題要使用 `for seat in 1..=last`，因為題目要包含最後一個座位。
- 第 1 題不要寫成 `1..last`，那會少印最後一號。
- 第 2 題要使用 `for i in 1..=n`，因為題目要從 1 印到 n。
- 第 2 題要先判斷 `i % 3 == 0 && i % 5 == 0`，再判斷單獨的 3 或 5；順序反過來會讓 `FizzBuzz` 永遠印不出來。
- 第 2 題不要改用 `i % 15 == 0`，這題要練 `&&` 組合兩個條件。
- 不需要寫 `let seat`；`for seat in ...` 會處理。
- 不要改用 `while`，這題要練 `for` + range。

提示方向：
1. 先讀取使用者輸入，轉成 `last`。
2. 因為要包含最後一個號碼，所以 range 要用 `..=`。
3. `println!("座位 {} 號", seat);` 可以印出每一個座位號碼。
4. FizzBuzz 要先處理「同時是 3 和 5 的倍數」。
5. 取餘數可以用 `%`，例如 `i % 3 == 0`。

參考答案：

```rust
fn main() {
    println!("請輸入最後一個座位號碼：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let last = input.trim().parse::<i32>().expect("請輸入數字");

    for seat in 1..=last {
        println!("座位 {} 號", seat);
    }
}
```

```rust
fn main() {
    println!("請輸入一個正整數：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let n = input.trim().parse::<i32>().expect("請輸入數字");

    for i in 1..=n {
        if i % 3 == 0 && i % 5 == 0 {
            println!("FizzBuzz");
        } else if i % 3 == 0 {
            println!("Fizz");
        } else if i % 5 == 0 {
            println!("Buzz");
        } else {
            println!("{}", i);
        }
    }
}
```

### 第 1 章第 21 集：巢狀迴圈

狀態：可用

練習目標：
- 確認讀者知道外層迴圈跑一次，內層迴圈會完整跑完一輪。
- 確認讀者會用 `print!` 和 `println!()` 做出二維輸出。
- 確認讀者知道 `break` 只跳出最內層，`break 'outer` 可以跳出指定外層。

題目：
1. 請使用者輸入高度 `height` 和寬度 `width`，印出一個星星方塊。
2. 請使用者輸入層數 `levels`，印出左靠齊的星星金字塔。
3. 請使用者輸入目標數字 `target`。用巢狀 `for` 在 `1..=9` 和 `1..=9` 裡找第一組 `a * b >= target` 的組合。找到後印出 `a = OOO, b = OOO`，並用 loop label 直接跳出兩層迴圈。

執行範例：

```text
請輸入高度：
3
請輸入寬度：
5
*****
*****
*****
```

```text
請輸入層數：
4
*
**
***
****
```

```text
請輸入目標數字：
20
a = 3, b = 7
```

批改重點：
- 三題都要使用 stdin 固定寫法和 `.parse::<i32>().expect("請輸入數字")`。
- 第 1 題要用兩層 `for`：外層控制高度，內層控制寬度。
- 第 1 題與第 2 題內層應該用 `print!("*");`，外層每一輪結束後用 `println!();` 換行。
- 第 2 題內層範圍要依照外層變數改變，例如 `1..=row`。
- 第 3 題要使用 loop label，例如 `'outer: for a in 1..=9 { ... }`。
- 第 3 題找到第一組後要 `break 'outer;`，不能只 `break` 內層。
- 第 1 題和第 2 題可能會出現「變數沒有使用」的 warning，這是正常的；不要用底線變數消掉 warning，底線變數到第 2 章第 3 集才教。
- 不要使用陣列、`Vec`、函數或遞迴。

提示方向：
1. 巢狀迴圈可以想成「外層控制第幾行，內層控制這一行裡要印幾次」。
2. `print!` 不會換行，`println!()` 可以用來換行。
3. 第 2 題的內層終點可以使用外層變數。
4. 如果要從內層直接跳出外層，外層迴圈前面要加 label。

參考答案：

```rust
fn main() {
    println!("請輸入高度：");

    let mut height_input = String::new();
    std::io::stdin().read_line(&mut height_input).expect("讀取失敗");

    let height = height_input.trim().parse::<i32>().expect("請輸入數字");

    println!("請輸入寬度：");

    let mut width_input = String::new();
    std::io::stdin().read_line(&mut width_input).expect("讀取失敗");

    let width = width_input.trim().parse::<i32>().expect("請輸入數字");

    for row in 1..=height {
        for col in 1..=width {
            print!("*");
        }
        println!();
    }
}
```

```rust
fn main() {
    println!("請輸入層數：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let levels = input.trim().parse::<i32>().expect("請輸入數字");

    for row in 1..=levels {
        for col in 1..=row {
            print!("*");
        }
        println!();
    }
}
```

```rust
fn main() {
    println!("請輸入目標數字：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let target = input.trim().parse::<i32>().expect("請輸入數字");

    'outer: for a in 1..=9 {
        for b in 1..=9 {
            if a * b >= target {
                println!("a = {}, b = {}", a, b);
                break 'outer;
            }
        }
    }
}
```

### 第 1 章第 22 集：`continue`

狀態：可用

練習目標：
- 確認讀者知道 `continue` 是跳過這一輪，不是結束整個迴圈。
- 確認讀者能在巢狀迴圈中使用 `continue 'outer` 跳到外層迴圈的下一輪。
- 確認讀者能把 `stdin`、`parse`、`for`、`%`、巢狀迴圈和 loop label 組合起來。

題目：
1. 請使用者輸入一個正整數 `n`，印出 `2` 到 `n` 之間所有質數。請使用 `continue 'outer`：當發現某個數可以被其他數整除時，直接跳到下一個候選數。這題的目標是練習 `continue 'outer`，不用追求最快的質數演算法。

執行範例：

```text
請輸入上限：
20
2
3
5
7
11
13
17
19
```

批改重點：
- 要使用 stdin 固定寫法和 `.parse::<i32>().expect("請輸入數字")`。
- 外層迴圈可以寫成 `'outer: for num in 2..=n`。
- 內層迴圈可以寫成 `for divisor in 2..num`，檢查有沒有數字可以整除 `num`。
- 如果 `num % divisor == 0`，代表 `num` 不是質數，要使用 `continue 'outer;`。
- 內層迴圈完整跑完都沒有跳過，才印出 `num`。
- 不要使用陣列、`Vec`、函數或遞迴。
- 不要改成只判斷單一數字；這題要列出一段範圍內的所有質數。
- 不要要求讀者最佳化到只檢查平方根、跳過偶數等；那些不是這題的重點。

提示方向：
1. 外層迴圈負責一個一個檢查 `num`。
2. 內層迴圈負責找有沒有 `divisor` 可以整除 `num`。
3. 一旦找到可以整除的 `divisor`，就代表這個 `num` 不是質數，可以 `continue 'outer` 換下一個 `num`。
4. 如果內層迴圈沒有觸發 `continue 'outer`，程式才會走到 `println!("{}", num);`。

參考答案：

```rust
fn main() {
    println!("請輸入上限：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let n = input.trim().parse::<i32>().expect("請輸入數字");

    'outer: for num in 2..=n {
        for divisor in 2..num {
            if num % divisor == 0 {
                continue 'outer;
            }
        }

        println!("{}", num);
    }
}
```

### 第 1 章第 23 集：型別（基礎）

狀態：不出題

不出題原因：
- 這集主要是認識 `i32`、`f64`、`bool`、型別推斷與手動標註型別。
- 若出題容易變成把範例重打一遍；這些型別會在後續程式題裡持續自然使用。

### 第 1 章第 24 集：型別（數字詳解）

狀態：不出題

不出題原因：
- 這集主要是補充數字型別、預設型別、數字後綴與浮點數精確度等觀念。
- 若出題容易變成型別名稱記憶題或表格問答；目前不需要要求讀者刻意練所有數字型別。

### 第 1 章第 25 集：`char`

狀態：不出題

不出題原因：
- 這集主要是認識 `char`、單引號與雙引號的差別，以及 Unicode 字元。
- 單獨出題練習價值不高；下一集「跳脫字元」更適合用輸出題練單引號、雙引號與特殊字元。

### 第 1 章第 26 集：跳脫字元

狀態：可用

練習目標：
- 確認讀者會用 `\n` 和 `\t` 控制輸出格式。
- 確認讀者會在字串裡印出雙引號 `"`。
- 確認讀者會在字串裡印出反斜線 `\`。

題目：
1. 寫一個程式，只用一個 `println!`，印出兩行文字：

```text
第一行
第二行
```

2. 寫一個程式，印出下面這句話，包含雙引號：

```text
他說："Rust 很有趣！"
```

3. 寫一個程式，印出下面這個路徑：

```text
C:\Users\Ferris\code
```

批改重點：
- 第 1 題要使用 `\n`，不要寫兩個 `println!`。
- 第 2 題要在字串裡使用 `\"` 印出雙引號。
- 第 3 題要使用 `\\` 印出反斜線。
- 不要要求讀者使用 raw string；raw string 會到附錄一才介紹。
- 如果讀者用單引號包字串，要提醒 Rust 字串用雙引號。

提示方向：
1. `\n` 代表換行。
2. 字串裡要印出 `"`，可以寫成 `\"`。
3. 字串裡要印出 `\`，可以寫成 `\\`。

參考答案：

```rust
fn main() {
    println!("第一行\n第二行");
}
```

```rust
fn main() {
    println!("他說：\"Rust 很有趣！\"");
}
```

```rust
fn main() {
    println!("C:\\Users\\Ferris\\code");
}
```

### 第 1 章第 27 集：`if` 當表達式

狀態：可用

練習目標：
- 確認讀者知道 `if` 可以直接回傳值。
- 確認讀者知道 `if` 和 `else` 兩邊型別要一致。
- 確認讀者知道當作回傳值的地方不要加分號。
- 確認讀者能把 `stdin`、`parse` 和 `if` 表達式組合起來。

題目：
1. 寫一個票價程式。請使用者輸入年齡 `age`，如果年齡小於 `18`，票價是 `50`；否則票價是 `100`。請使用 `if` 表達式直接決定 `ticket_price`，最後印出票價。

執行範例：

```text
請輸入年齡：
12
票價是 50 元
```

批改重點：
- 要使用 stdin 固定寫法和 `.parse::<i32>().expect("請輸入數字")`。
- 應該寫成 `let ticket_price = if age < 18 { 50 } else { 100 };`。
- 不需要 `let mut ticket_price`。
- `50` 和 `100` 後面不要加分號。
- `if` 和 `else` 兩邊都要回傳整數。
- 不要把這題改成一般 `if...else...` 指派；這題要練 `if` 表達式。

提示方向：
1. 先讀取使用者輸入，轉成 `age`。
2. `if age < 18 { 50 } else { 100 }` 整個可以放在 `let ticket_price =` 右邊。
3. 大括號裡的 `50` 和 `100` 是回傳值，不要加分號。

參考答案：

```rust
fn main() {
    println!("請輸入年齡：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let age = input.trim().parse::<i32>().expect("請輸入數字");

    let ticket_price = if age < 18 { 50 } else { 100 };

    println!("票價是 {} 元", ticket_price);
}
```

## 第 2 章

### 第 2 章第 1 集：`const`

狀態：可用

練習目標：
- 確認讀者會用 `const` 宣告常數。
- 確認讀者知道 `const` 一定要標型別。
- 確認讀者知道常數命名慣例是全大寫加底線。
- 確認讀者知道 `const` 可以放在 `fn main()` 外面。

題目：
1. 寫一個成績判斷程式。請在 `fn main()` 外面宣告常數 `PASS_SCORE: i32 = 60`。程式請使用者輸入分數，如果分數大於或等於 `PASS_SCORE`，印出 `及格`，否則印出 `不及格`。

執行範例：

```text
請輸入分數：
72
及格
```

批改重點：
- `PASS_SCORE` 應該用 `const` 宣告，不要用 `let`。
- `const PASS_SCORE: i32 = 60;` 應該放在 `fn main()` 外面。
- `const` 一定要標型別，不能寫成 `const PASS_SCORE = 60;`。
- 常數名稱要用全大寫加底線。
- 不要寫 `const mut`，常數不能加 `mut`。
- 判斷時要使用 `score >= PASS_SCORE`，不要直接把 `60` 寫死在 `if` 裡。

提示方向：
1. 常數可以寫在 `fn main()` 上方。
2. `const` 的格式是 `const 名稱: 型別 = 值;`。
3. 讀到分數後，用 `score >= PASS_SCORE` 判斷。

參考答案：

```rust
const PASS_SCORE: i32 = 60;

fn main() {
    println!("請輸入分數：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let score = input.trim().parse::<i32>().expect("請輸入數字");

    if score >= PASS_SCORE {
        println!("及格");
    } else {
        println!("不及格");
    }
}
```

### 第 2 章第 2 集：shadowing

狀態：不出題

不出題原因：
- 這集雖然重要，但題目容易變成重打正文範例，或刻意製造概念題。
- Shadowing 之後很適合自然放進綜合題裡練，不需要在這一集硬出題。

### 第 2 章第 3 集：底線變數

狀態：可用

練習目標：
- 確認讀者知道不需要迴圈變數時可以用 `_`。
- 確認讀者會用 `for _ in 0..n` 單純重複執行固定次數。
- 確認讀者知道 `_` 不是之後要拿來使用的變數。

題目：
1. 寫一個簡單的密碼檢查程式。正確密碼是 `"rust"`。讓使用者最多輸入 3 次密碼；如果輸入正確，就印出 `登入成功` 並結束迴圈；如果輸入錯誤，就印出 `密碼錯誤`。請使用 `for _ in 0..3`，因為這題不需要知道目前是第幾次。

執行範例：

```text
請輸入密碼：
abc
密碼錯誤
請輸入密碼：
rust
登入成功
```

批改重點：
- 要使用 `for _ in 0..3`。
- 不要寫成 `for i in 0..3` 後又完全不用 `i`。
- 每一輪都要讀取一次新的輸入。
- 可以用 `input.trim() == "rust"` 判斷密碼是否正確。
- 登入成功後要使用 `break` 跳出迴圈。
- 不要要求讀者處理「三次都錯」後的額外訊息；這題重點是 `_` 和固定次數迴圈。

提示方向：
1. `for _ in 0..3` 代表重複三次，但不需要知道目前是第幾次。
2. 每次迴圈裡都可以照 stdin 固定寫法讀一行。
3. 如果 `input.trim() == "rust"`，就印出成功並 `break`。

參考答案：

```rust
fn main() {
    for _ in 0..3 {
        println!("請輸入密碼：");

        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("讀取失敗");

        if input.trim() == "rust" {
            println!("登入成功");
            break;
        } else {
            println!("密碼錯誤");
        }
    }
}
```

### 第 2 章第 4 集：tuple

狀態：不出題

不出題原因：
- 這集主要是 tuple 的基本建立、取值與單元素 tuple 語法；單獨出題容易太簡單，或只是重打正文範例。
- Tuple 之後可以自然放進函數回傳值、解構或綜合題裡練，不需要在本集硬出題。

### 第 2 章第 5 集：`{:?}` `Debug` 格式

狀態：不出題

不出題原因：
- 這集主要介紹輸出格式工具：`{:?}`、`{:#?}`、`dbg!`。
- 單獨出題容易只是要求讀者把 `{}` 改成 `{:?}`，練習價值不高。
- `Debug` 格式之後會在 struct、enum、derive 等章節自然大量使用，到時再放進題目更有意義。

### 第 2 章第 6 集：簡單函數

狀態：可用

練習目標：
- 確認讀者會用 `fn 名字() { ... }` 定義函數。
- 確認讀者會在 `main` 裡呼叫自己定義的函數。
- 確認讀者知道函數可以呼叫多次。
- 確認讀者使用 snake_case 命名函數。

題目：
1. 寫一個程式，定義一個函數 `print_menu()`，裡面印出三行菜單。然後在 `main` 裡呼叫 `print_menu()` 兩次。

預期輸出：

```text
今日菜單
1. 拉麵
2. 咖哩飯
今日菜單
1. 拉麵
2. 咖哩飯
```

批改重點：
- 要定義 `fn print_menu() { ... }`。
- 要在 `main` 裡呼叫 `print_menu();` 兩次。
- 不要使用函數參數；函數參數下一集才教。
- 函數名稱要用 snake_case，不要寫成 `printMenu`。
- 函數可以放在 `main` 上面或下面，兩者都可以。

提示方向：
1. 先寫 `fn print_menu() { ... }`，把三行 `println!` 放進去。
2. 在 `main` 裡寫兩次 `print_menu();`。
3. 呼叫函數時，函數名稱後面要有 `()` 和分號。

參考答案：

```rust
fn print_menu() {
    println!("今日菜單");
    println!("1. 拉麵");
    println!("2. 咖哩飯");
}

fn main() {
    print_menu();
    print_menu();
}
```

### 第 2 章第 7 集：函數參數

狀態：可用

練習目標：
- 確認讀者會定義帶參數的函數。
- 確認讀者知道函數參數一定要標型別。
- 確認讀者會呼叫函數並傳入對應的值。
- 確認讀者知道本集還沒有函數回傳值，所以函數直接印出結果。

題目：
1. 寫一個程式，定義函數 `print_total(price: i32, count: i32)`，印出總價 `price * count`。在 `main` 裡請使用者輸入單價和數量，轉成數字後呼叫 `print_total(price, count)`。

執行範例：

```text
請輸入單價：
30
請輸入數量：
4
總價是 120 元
```

批改重點：
- 要定義 `fn print_total(price: i32, count: i32)`。
- 參數 `price` 和 `count` 都必須標型別。
- `print_total` 裡直接 `println!`，不要寫回傳值；函數回傳值下一集才教。
- `main` 裡要讀取兩次輸入，分別轉成 `price` 和 `count`。
- 呼叫時要寫 `print_total(price, count);`。
- 不要把所有邏輯都寫在 `main` 裡，這題要練函數參數。

提示方向：
1. 函數參數格式是 `參數名: 型別`。
2. 可以先在 `main` 裡讀到 `price` 和 `count`。
3. 再把兩個值傳給 `print_total(price, count);`。

參考答案：

```rust
fn print_total(price: i32, count: i32) {
    println!("總價是 {} 元", price * count);
}

fn main() {
    println!("請輸入單價：");

    let mut price_input = String::new();
    std::io::stdin().read_line(&mut price_input).expect("讀取失敗");

    let price = price_input.trim().parse::<i32>().expect("請輸入數字");

    println!("請輸入數量：");

    let mut count_input = String::new();
    std::io::stdin().read_line(&mut count_input).expect("讀取失敗");

    let count = count_input.trim().parse::<i32>().expect("請輸入數字");

    print_total(price, count);
}
```

### 第 2 章第 8 集：函數回傳值

狀態：可用

練習目標：
- 確認讀者會用 `-> 型別` 宣告函數回傳型別。
- 確認讀者知道最後一行不加分號就是回傳值。
- 確認讀者會在 `main` 裡接住函數回傳值。
- 確認讀者會用 tuple 回傳多個值。

題目：
1. 寫一個函數 `calculate_total(price: i32, count: i32) -> i32`，回傳總價 `price * count`。在 `main` 裡請使用者輸入單價和數量，呼叫函數後印出總價。
2. 寫一個函數 `buy_ticket(money: i32, price: i32) -> (i32, i32)`，回傳「可以買幾張票」和「剩下多少錢」。在 `main` 裡請使用者輸入手上的錢和票價，最後印出結果。

執行範例：

```text
請輸入單價：
30
請輸入數量：
4
總價是 120 元
```

```text
請輸入你有多少錢：
230
請輸入票價：
70
可以買 3 張，剩下 20 元
```

批改重點：
- 第 1 題函數要回傳 `i32`，不要直接在函數裡 `println!`。
- 第 1 題最後一行應該是 `price * count`，不要加分號。
- 第 2 題函數回傳型別應該是 `(i32, i32)`。
- 第 2 題可以用 `money / price` 和 `money % price` 算出兩個值。
- 第 2 題要用 tuple 回傳，例如 `(count, change)`。
- 呼叫 tuple 回傳值後，可以用 `.0`、`.1` 取出結果。
- 不要使用 `return`；early `return` 下一集才教，這集先練最後一行回傳值。

提示方向：
1. 回傳型別寫在參數後面：`fn name(...) -> i32`。
2. 函數最後一行不要加分號。
3. 回傳兩個值時，可以把它們包成 tuple。

參考答案：

```rust
fn calculate_total(price: i32, count: i32) -> i32 {
    price * count
}

fn main() {
    println!("請輸入單價：");

    let mut price_input = String::new();
    std::io::stdin().read_line(&mut price_input).expect("讀取失敗");
    let price = price_input.trim().parse::<i32>().expect("請輸入數字");

    println!("請輸入數量：");

    let mut count_input = String::new();
    std::io::stdin().read_line(&mut count_input).expect("讀取失敗");
    let count = count_input.trim().parse::<i32>().expect("請輸入數字");

    let total = calculate_total(price, count);

    println!("總價是 {} 元", total);
}
```

```rust
fn buy_ticket(money: i32, price: i32) -> (i32, i32) {
    let count = money / price;
    let change = money % price;

    (count, change)
}

fn main() {
    println!("請輸入你有多少錢：");

    let mut money_input = String::new();
    std::io::stdin().read_line(&mut money_input).expect("讀取失敗");
    let money = money_input.trim().parse::<i32>().expect("請輸入數字");

    println!("請輸入票價：");

    let mut price_input = String::new();
    std::io::stdin().read_line(&mut price_input).expect("讀取失敗");
    let price = price_input.trim().parse::<i32>().expect("請輸入數字");

    let result = buy_ticket(money, price);

    println!("可以買 {} 張，剩下 {} 元", result.0, result.1);
}
```

### 第 2 章第 9 集：early `return`

狀態：可用

練習目標：
- 確認讀者會用 `return 值;` 提前離開函數。
- 確認讀者知道 `return` 後面要加分號。
- 確認讀者知道一般最後一行仍然用不加分號的自然回傳。
- 確認讀者理解 guard clause 的用途。

題目：
1. 寫一個函數 `discount_price(price: i32, is_member: bool) -> i32`。如果 `price <= 0`，代表價格不合理，直接 `return 0;`。如果價格合理，會員打 8 折，非會員原價。請在 `main` 裡讓使用者輸入價格，並用一個變數 `is_member = true` 呼叫函數，最後印出折扣後價格。

執行範例：

```text
請輸入價格：
100
折扣後價格是 80 元
```

批改重點：
- 函數開頭要先檢查 `price <= 0`，並使用 `return 0;` 提前離開。
- `return 0;` 後面要有分號。
- 價格合理時，不要用 `return` 到處回傳；最後可以用 `if is_member { price * 8 / 10 } else { price }` 自然回傳。
- 函數回傳型別要寫 `-> i32`。
- 不要使用浮點數折扣；目前用整數運算就好。
- 不要引入 `Result` 或 `Option`；這些第五章才會教。

提示方向：
1. 先寫 guard clause：`if price <= 0 { return 0; }`。
2. 後面再處理會員和非會員的價格。
3. `if` 當表達式可以直接當函數最後一行的回傳值。

參考答案：

```rust
fn discount_price(price: i32, is_member: bool) -> i32 {
    if price <= 0 {
        return 0;
    }

    if is_member {
        price * 8 / 10
    } else {
        price
    }
}

fn main() {
    println!("請輸入價格：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let price = input.trim().parse::<i32>().expect("請輸入數字");

    let is_member = true;
    let final_price = discount_price(price, is_member);

    println!("折扣後價格是 {} 元", final_price);
}
```

### 第 2 章第 10 集：遞迴

狀態：可用

練習目標：
- 確認讀者知道遞迴函數要有停止條件。
- 確認讀者知道每次遞迴呼叫都要讓問題往停止條件靠近。
- 確認讀者能把「計算結果」和「印出過程」兩種遞迴情境分開。
- 確認讀者能把「讀取輸入」放在 `main` 裡，把「計算並回傳結果」放在函數裡。

題目：
1. 寫一個函數 `is_power_of_two(n: i32) -> bool`，判斷 `n` 是不是 2 的次方。這個函數只負責計算並回傳結果，不要在函數裡讀取 stdin 或印出文字。請特別擋掉負數和 0：它們都不是 2 的次方。請在 `main` 裡讀取一個整數，呼叫這個函數，並印出 `是 2 的次方` 或 `不是 2 的次方`。請用遞迴，不要用迴圈。
2. 寫一個函數 `print_collatz(n: i32)`，印出輸入數字的 Collatz sequence。規則是：如果 `n` 是 1，就印出 1 並停止；如果 `n` 是偶數，下一個數字是 `n / 2`；如果 `n` 是奇數，下一個數字是 `3 * n + 1`。請在 `main` 裡讀取一個正整數，呼叫這個函數，並用遞迴一路印到 1，不要用迴圈。

執行範例：

```text
請輸入數字：
16
是 2 的次方
```

```text
請輸入起始數字：
6
6
3
10
5
16
8
4
2
1
```

批改重點：
- `is_power_of_two` 必須只依靠參數 `n` 計算並回傳 `bool`，不要在函數裡讀取 stdin 或印出結果。
- `is_power_of_two` 至少要處理 `n == 1`、`n <= 0`、奇數、偶數這幾種情況；負數和 0 都應該回傳 `false`。
- `print_collatz` 要先印出目前的 `n`，再決定要不要繼續呼叫自己。
- `print_collatz` 的停止條件應該是 `n == 1`。
- 兩題都不要使用 `loop`、`while`、`for`、陣列或 `Vec`。
- 這一集的重點是練習遞迴，不是研究 Collatz 猜想的數學細節；可以假設輸入是正整數。

提示方向：
1. `is_power_of_two(1)` 應該回傳 `true`。
2. 小於等於 0 的數不是 2 的次方。
3. 如果 `n` 是奇數而且不是 1，就不可能是 2 的次方。
4. 如果 `n` 是偶數，可以把問題縮小成檢查 `n / 2`。
5. Collatz 的函數可以先 `println!("{}", n);`，再用 `if` 決定下一次呼叫要傳入哪個數字。

參考答案：

```rust
fn is_power_of_two(n: i32) -> bool {
    if n == 1 {
        true
    } else if n <= 0 {
        false
    } else if n % 2 != 0 {
        false
    } else {
        is_power_of_two(n / 2)
    }
}

fn main() {
    println!("請輸入數字：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let n = input.trim().parse::<i32>().expect("請輸入數字");

    if is_power_of_two(n) {
        println!("是 2 的次方");
    } else {
        println!("不是 2 的次方");
    }
}
```

```rust
fn print_collatz(n: i32) {
    println!("{}", n);

    if n == 1 {
        return;
    }

    if n % 2 == 0 {
        print_collatz(n / 2);
    } else {
        print_collatz(3 * n + 1);
    }
}

fn main() {
    println!("請輸入起始數字：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let n = input.trim().parse::<i32>().expect("請輸入數字");

    print_collatz(n);
}
```

### 第 2 章第 11 集：陣列基礎

狀態：可用

練習目標：
- 確認讀者會建立固定長度陣列。
- 確認讀者知道陣列元素必須是同一種型別。
- 確認讀者會用 `{:?}` 印出整個陣列。
- 確認讀者會用索引取出陣列中的元素，並知道索引從 0 開始。
- 避免偷跑下一集的陣列走訪。

題目：
1. 寫一個程式，讓使用者輸入三天的溫度，存成陣列 `temperatures`。接著印出整個陣列、第一天溫度、第三天溫度，以及第一天和第三天差幾度。差幾度不能是負數；請自己用 `if` 判斷並算出絕對值。請用索引取值。

執行範例：

```text
請輸入第一天溫度：
25
請輸入第二天溫度：
27
請輸入第三天溫度：
22
三天溫度：[25, 27, 22]
第一天溫度：25
第三天溫度：22
第一天和第三天差 3 度
```

批改重點：
- 要把三個溫度存成陣列，例如 `let temperatures = [day1, day2, day3];`。
- 要用 `{:?}` 印出整個陣列，不要用 `{}`。
- 第一天要用 `temperatures[0]`，第三天要用 `temperatures[2]`。
- 差幾度不能是負數；要用 `if` 自己判斷誰比較大，再做減法。
- 不要呼叫現成的絕對值函數；這題要練目前已學過的 `if` 和運算子。
- 不要使用 `for x in temperatures`；陣列走訪下一集才教。
- 不要讓讀者輸入索引再取值；這會引入 `usize` 型別轉換，容易讓焦點偏掉。

提示方向：
1. 先各自讀取 `day1`、`day2`、`day3`。
2. 再把三個變數放進陣列：`[day1, day2, day3]`。
3. 印整個陣列時使用 `{:?}`。
4. 陣列第一個元素的索引是 0。

參考答案：

```rust
fn main() {
    println!("請輸入第一天溫度：");

    let mut day1_input = String::new();
    std::io::stdin().read_line(&mut day1_input).expect("讀取失敗");
    let day1 = day1_input.trim().parse::<i32>().expect("請輸入數字");

    println!("請輸入第二天溫度：");

    let mut day2_input = String::new();
    std::io::stdin().read_line(&mut day2_input).expect("讀取失敗");
    let day2 = day2_input.trim().parse::<i32>().expect("請輸入數字");

    println!("請輸入第三天溫度：");

    let mut day3_input = String::new();
    std::io::stdin().read_line(&mut day3_input).expect("讀取失敗");
    let day3 = day3_input.trim().parse::<i32>().expect("請輸入數字");

    let temperatures = [day1, day2, day3];

    println!("三天溫度：{:?}", temperatures);
    println!("第一天溫度：{}", temperatures[0]);
    println!("第三天溫度：{}", temperatures[2]);
    let difference = if temperatures[2] >= temperatures[0] {
        temperatures[2] - temperatures[0]
    } else {
        temperatures[0] - temperatures[2]
    };

    println!("第一天和第三天差 {} 度", difference);
}
```

### 第 2 章第 12 集：陣列走訪

狀態：可用

練習目標：
- 確認讀者會用 `for x in arr` 走訪陣列。
- 確認讀者會在走訪陣列時對每個元素做處理。
- 確認讀者會使用可變變數作為累加器。
- 確認讀者能分辨「用索引把輸入放進陣列」和「直接走訪陣列元素」的差別。

題目：
1. 寫一個程式，先建立可變陣列 `expenses`，裡面有 5 個 `0`。接著用 `for i in 0..5` 讀取 5 筆今日花費，並把每一筆放進 `expenses[i]`。輸入完成後，用 `for expense in expenses` 走訪陣列，印出每一筆花費。如果某一筆花費大於或等於 100，就額外印出 `這筆比較高`。最後印出總花費。

執行範例：

```text
請輸入第 1 筆花費：
80
請輸入第 2 筆花費：
120
請輸入第 3 筆花費：
45
請輸入第 4 筆花費：
200
請輸入第 5 筆花費：
60
花費：80 元
花費：120 元
這筆比較高
花費：45 元
花費：200 元
這筆比較高
花費：60 元
總花費：505 元
```

批改重點：
- 要先建立可變陣列，例如 `let mut expenses = [0; 5];`。
- 讀取輸入時可以使用 `for i in 0..5`，並把讀到的花費放進 `expenses[i]`。
- 處理花費時要使用 `for expense in expenses` 走訪陣列。
- 要用 `let mut total = 0;` 或類似做法建立累加器。
- 每次走訪時要把 `expense` 加進 `total`。
- 判斷高花費時可以用 `if expense >= 100`。
- 不要在計算總花費時繼續用索引走訪，例如 `for i in 0..5 { total += expenses[i]; }`；這集的主角是 `for expense in expenses`。
- 不要使用 `len()`、slice 或 `Vec`。

提示方向：
1. 先寫 `let mut expenses = [0; 5];`。
2. 用 `for i in 0..5` 讀取輸入，提示文字可以印出 `i + 1`。
3. 讀到數字後，把它放進 `expenses[i]`。
4. 走訪前先準備 `let mut total = 0;`。
5. 在 `for expense in expenses` 裡印出花費、判斷是否大於等於 100，並累加總花費。

參考答案：

```rust
fn main() {
    let mut expenses = [0; 5];

    for i in 0..5 {
        println!("請輸入第 {} 筆花費：", i + 1);

        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("讀取失敗");

        let expense = input.trim().parse::<i32>().expect("請輸入數字");
        expenses[i] = expense;
    }

    let mut total = 0;

    for expense in expenses {
        println!("花費：{} 元", expense);

        if expense >= 100 {
            println!("這筆比較高");
        }

        total += expense;
    }

    println!("總花費：{} 元", total);
}
```

### 第 2 章第 13 集：切片 `&[T]`

狀態：不出題

不出題原因：
- 這集主要是認識切片語法、範圍邊界、`&` 先記起來，以及切片不是複製資料。
- 若出題容易只是把正文範例換一組陣列和範圍，練習價值不高。
- 若要求讀者自行輸入範圍，又會提早牽涉索引型別、越界處理和借用細節，焦點容易偏掉。
- 切片更適合在下一集「切片作為函數參數」裡一起練。

### 第 2 章第 14 集：切片作為參數

狀態：可用

練習目標：
- 確認讀者會把函數參數寫成 `&[i32]`。
- 確認讀者知道呼叫時可以傳整個陣列的切片，例如 `&steps`。
- 確認讀者知道呼叫時也可以傳陣列的一部分，例如 `&steps[..5]` 和 `&steps[5..]`。
- 確認讀者能在函數裡走訪切片。
- 確認讀者理解同一個函數可以處理不同長度的資料。

題目：
1. 寫一個函數 `count_goal_days(steps: &[i32]) -> i32`，計算有幾天步數大於或等於 `8000`。在 `main` 裡讓使用者輸入 7 天步數，存成陣列 `steps`。接著分別呼叫 `count_goal_days(&steps)`、`count_goal_days(&steps[..5])`、`count_goal_days(&steps[5..])`，印出一整週、平日、週末各有幾天達標。

執行範例：

```text
請輸入第 1 天步數：
9000
請輸入第 2 天步數：
7500
請輸入第 3 天步數：
8200
請輸入第 4 天步數：
6000
請輸入第 5 天步數：
10000
請輸入第 6 天步數：
3000
請輸入第 7 天步數：
12000
一整週達標 4 天
平日達標 3 天
週末達標 1 天
```

批改重點：
- 函數參數要寫成 `steps: &[i32]`，不要寫成固定長度陣列 `[i32; 7]`。
- `count_goal_days` 裡要用 `for step in steps` 走訪切片。
- 函數內要用可變累加器計算達標天數。
- 呼叫整週時要傳 `&steps`。
- 呼叫平日時要傳 `&steps[..5]`，代表第 1 天到第 5 天。
- 呼叫週末時要傳 `&steps[5..]`，代表第 6 天到第 7 天。
- 不要為整週、平日、週末各寫一個函數；這題重點是同一個切片參數函數可以接受不同長度資料。
- 不要使用 `Vec` 或 Iterator 方法。

提示方向：
1. 先寫 `fn count_goal_days(steps: &[i32]) -> i32`。
2. 函數裡準備 `let mut count = 0;`。
3. 用 `for step in steps` 走訪每一天步數。
4. 如果 `step >= 8000`，就讓 `count += 1`。
5. 在 `main` 裡可以用可變陣列 `[0; 7]` 搭配 `for i in 0..7` 讀取 7 天步數。

參考答案：

```rust
fn count_goal_days(steps: &[i32]) -> i32 {
    let mut count = 0;

    for step in steps {
        if step >= 8000 {
            count += 1;
        }
    }

    count
}

fn main() {
    let mut steps = [0; 7];

    for i in 0..7 {
        println!("請輸入第 {} 天步數：", i + 1);

        let mut input = String::new();
        std::io::stdin().read_line(&mut input).expect("讀取失敗");

        let step = input.trim().parse::<i32>().expect("請輸入數字");
        steps[i] = step;
    }

    let week_count = count_goal_days(&steps);
    let weekday_count = count_goal_days(&steps[..5]);
    let weekend_count = count_goal_days(&steps[5..]);

    println!("一整週達標 {} 天", week_count);
    println!("平日達標 {} 天", weekday_count);
    println!("週末達標 {} 天", weekend_count);
}
```

### 第 2 章第 15 集：字串切片 `&str`

狀態：可用

練習目標：
- 確認讀者知道字串字面值可以當作 `&str` 使用。
- 確認讀者會把函數參數寫成 `&str`。
- 確認讀者會把英文字串切片傳進函數。
- 確認讀者知道不要隨便切中文字串。

題目：
1. 寫一個函數 `print_ticket(name: &str, from: &str, to: &str)`，印出乘客姓名、出發站和抵達站。在 `main` 裡宣告 `let route = "TPE-TNN";`，用 `&route[0..3]` 取出出發站 `TPE`，用 `&route[4..7]` 取出抵達站 `TNN`。最後分別替 `"Andy"` 和 `"小明"` 印出車票資訊。

執行範例：

```text
乘客：Andy
出發：TPE
抵達：TNN
乘客：小明
出發：TPE
抵達：TNN
```

批改重點：
- 函數參數要寫成 `name: &str`、`from: &str`、`to: &str`。
- `route` 可以寫成 `let route = "TPE-TNN";`。
- 出發站要用 `&route[0..3]`，抵達站要用 `&route[4..7]`。
- `route` 是純英文字母和符號，這裡用 byte 索引切片是安全的。
- `"Andy"` 和 `"小明"` 都可以直接傳給 `name: &str`。
- 不要對 `"小明"` 做字串切片；中文不是一個字 1 byte，切錯位置會 panic。
- 不要引入 `String`；這一集先練 `&str`。

提示方向：
1. 先寫 `fn print_ticket(name: &str, from: &str, to: &str)`。
2. 函數裡用三個 `println!` 印出乘客、出發、抵達。
3. 在 `main` 裡從 `route` 切出 `from` 和 `to`。
4. 呼叫時可以寫 `print_ticket("Andy", from, to);`。

參考答案：

```rust
fn print_ticket(name: &str, from: &str, to: &str) {
    println!("乘客：{}", name);
    println!("出發：{}", from);
    println!("抵達：{}", to);
}

fn main() {
    let route = "TPE-TNN";
    let from = &route[0..3];
    let to = &route[4..7];

    print_ticket("Andy", from, to);
    print_ticket("小明", from, to);
}
```
