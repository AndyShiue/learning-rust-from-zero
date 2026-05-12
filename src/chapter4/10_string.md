# `String`

## 本集目標

認識 Rust 的 `String` 型別——一個擁有資料、可以修改的字串。

## 概念說明

### 之前的字串都是借來的

從第一章開始，我們一直在用 `&str` 這個型別：

```rust,noplayground
# fn main() {
    let greeting: &str = "你好";
# }
```

`"你好"` 這個字串是直接寫在程式碼裡的，它的資料被編譯進程式本身。`&str` 是一個借用——你只是在看這段文字，但你**不擁有**它，也**不能修改**它。

### `String`：你擁有的字串

`String` 是一個你可以擁有、可以修改的字串型別。它的資料存在 heap 上。

用 `String::from()` 來建立：

```rust,noplayground
# fn main() {
    let s = String::from("你好");
# }
```

`String::from` 是一個 associated function（跟第三章學的一樣，用 `::` 呼叫），它會把 `&str` 的內容複製一份到 heap 上，建立一個你擁有的 `String`。

### `push_str`：在後面加上文字

`String` 可以修改！用 `push_str` 來接上更多文字：

```rust
# fn main() {
    let mut s = String::from("你好");
    s.push_str("，世界！");
    println!("{}", s); // 你好，世界！
# }
```

注意變數要宣告成 `let mut`，因為我們要修改它。

### `format!`：組合多個值成字串

`format!` 跟 `println!` 的用法一模一樣，只是它不會印出來，而是回傳一個 `String`：

```rust
# fn main() {
    let name = "小明";
    let age = 20;
    let msg = format!("我叫{}，今年{}歲", name, age);
    println!("{}", msg);
# }
```

### `String` 也適用所有權規則

因為 `String` 的資料在 heap 上，所以它**不是 `Copy`**。賦值和傳入函數都會 move：

```rust,noplayground
# fn main() {
    let s1 = String::from("hello");
    let s2 = s1; // move！s1 不能再用了
# }
```

這跟之前學的一樣——想保留 `s1` 就用 `.clone()` 或 `&` 借用。

## 範例程式碼

```rust
fn main() {
    // 建立 String
    let mut greeting = String::from("你好");
    println!("{}", greeting);

    // push_str：接上更多文字
    greeting.push_str("，世界");
    greeting.push_str("！");
    println!("{}", greeting);

    // format!：組合多個值
    let name = "小花";
    let score = 95;
    let report = format!("{}同學的成績是{}分", name, score);
    println!("{}", report);

    // String 會 move（不是 Copy）
    let s1 = String::from("Rust");
    // let s2 = s1; // 如果這樣寫，s1 就被 move 走了，不能再用
    let s2 = s1.clone(); // 用 clone 複製一份，s1 還在
    println!("s1 = {}", s1);
    println!("s2 = {}", s2);

    // 傳進函數：用借用就不會 move
    let s3 = String::from("哈囉");
    print_string(&s3);
    println!("s3 還在：{}", s3);

    // Debug 格式也能用
    let s4 = String::from("debug 測試");
    println!("{:?}", s4);
}

fn print_string(s: &String) {
    println!("函數收到：{}", s);
}
```

## 重點整理

- `String` 是擁有資料的字串型別，資料存在 heap 上
- `String::from("...")` 建立新的 `String`
- `push_str` 在字串後面接上更多文字（需要 `let mut`）
- `format!` 跟 `println!` 語法一樣，但回傳 `String` 而不是印出來
- String **不是 `Copy`**，賦值和傳入函數會 move
- 要保留原本的 `String`，用 `.clone()` 或 `&` 借用
