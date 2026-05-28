# stack 與 heap

## 本集目標

理解 stack 和 heap 的差別，並揭秘第 1 集鑰匙圈比喻的真正含義。

## 概念說明

### 記憶體的兩個區域

程式執行的時候，資料會被放在記憶體裡。記憶體有兩個主要的區域：

**堆疊（stack）**：

- 快速
- 大小在編譯時就確定了
- 函數的區域變數、整數、浮點數、布林值、`char` 都放在這裡
- 函數結束時，這些變數就自動被清掉了

**堆積（heap）**：

- 比較慢，但更靈活
- 大小可以在程式執行時才決定（例如一段文字，你不知道使用者會輸入多長）
- 需要手動管理（在其他語言裡），或靠所有權系統自動管理（在 Rust 裡）

### 鑰匙圈比喻揭秘！

還記得第 1 集的鑰匙圈比喻嗎？現在來揭秘它真正的意思：

- **鑰匙圈上的裝飾** = stack 上的資料（小而固定，跟著鑰匙圈走）
- **保險箱** = heap 上的資料（大而靈活，存在別的地方）
- **鑰匙** = 指標（pointer），記錄了保險箱在記憶體中的位置

所以當我們說「move 是把鑰匙圈交出去」：

- 如果鑰匙圈上只有裝飾（stack 資料），交出去很便宜，甚至可以直接複製一份（這就是 `Copy`！）
- 如果鑰匙圈上有鑰匙（指標），交出去的是指標，保險箱（heap 資料）不會複製

### 為什麼整數是 `Copy`？

現在你應該懂了：整數（`i32` 等）就像鑰匙圈上的小裝飾，完全在 stack 上，小小的、複製起來零成本。所以 Rust 讓它們自動 `Copy`。

而像之後會學到的 `String` 那樣的型別，它的資料在 heap 上。如果隨便複製，就等於複製了整個保險箱裡的東西，代價很大。所以 Rust 需要用 move，要複製就得明確呼叫 `.clone()`。

## 範例程式碼

```rust,editable
#[derive(Debug, Copy, Clone)]
struct StackData {
    x: i32,
    y: i32,
    active: bool,
}

fn main() {
    // 這些都在 stack 上
    let a = 42;    // i32，4 bytes，stack
    let b = 3.14;  // f64，8 bytes，stack
    let c = true;  // bool，1 byte，stack
    let ch = '🦀'; // char，4 bytes，stack
    println!("整數：{}，浮點：{}，布林：{}，字元：{}", a, b, c, ch);

    // struct 裡面全是 stack 資料，所以整個 struct 也在 stack 上
    let data = StackData { x: 10, y: 20, active: true };
    let data2 = data; // Copy！data 還能用
    println!("data = {:?}", data);
    println!("data2 = {:?}", data2);

    // 陣列也在 stack 上（大小固定）
    let arr = [1, 2, 3, 4, 5];
    println!("陣列：{:?}", arr);

    // tuple 也在 stack 上
    let t = (42, true, 'A');
    println!("tuple：{:?}", t);

    // 之後會學 String 和 Vec，它們的資料在 heap 上
    // 到時候 move 和借用的重要性就更明顯了！
}
```

## 重點整理

- **stack（堆疊）**：快速、大小固定。整數、浮點、布林、`char`、小 `struct` 都在這裡
- **heap（堆積）**：靈活、大小可變。大型或動態大小的資料放在這裡
- 鑰匙圈比喻揭秘：裝飾 = stack 資料、保險箱 = heap 資料、鑰匙 = 指標
- 整數是 `Copy`，因為它們完全在 stack 上，複製幾乎沒有成本
- heap 資料預設 move（只轉移鑰匙），要完整複製就用 `clone`（複製整個保險箱的內容）
