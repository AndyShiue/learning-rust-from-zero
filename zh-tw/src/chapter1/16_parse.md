# `parse`

## 本集目標

學會把使用者輸入的文字轉換成數字。

## 正文

和上一集一樣，這集的語法先照抄就好，不用完全理解每一行在做什麼。之後學到更多概念會回來解釋。 

上一集我們學了怎麼讀取使用者的輸入，但讀進來的東西是**文字**。如果使用者輸入了 `42`，對 Rust 來說那是一串文字，不是數字 42。

你不能拿文字去做加減乘除，所以我們需要把它「轉換」成數字。

### 文字轉數字

```rust,no_run
fn main() {
    println!("請輸入一個數字：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let num = input.trim().parse::<i32>().expect("請輸入數字");

    println!("你輸入的數字是 {}", num);
}
```

跑起來：

```ignore
請輸入一個數字：
42
你輸入的數字是 42
```

### 關鍵在這行

```rust,no_run
# fn main() {
#     let mut input = String::new();
#     std::io::stdin().read_line(&mut input).expect("讀取失敗");
    let num = input.trim().parse::<i32>().expect("請輸入數字");
# }
```

拆開來看：

1. `input.trim()` → 去掉頭尾的空白和換行
2. `.parse::<i32>()` → 把文字**解析**成整數（`i32` 就是一種整數型別）
3. `.expect("請輸入數字")` → 如果轉換失敗（比如使用者輸入了 "abc"），就印這個錯誤訊息然後結束程式

### 完整的互動範例

```rust,no_run
fn main() {
    println!("請輸入一個數字：");

    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("讀取失敗");

    let num = input.trim().parse::<i32>().expect("請輸入數字");

    println!("{} 乘以 2 等於 {}", num, num * 2);
}
```

```ignore
請輸入一個數字：
7
7 乘以 2 等於 14
```

現在你可以讀取數字並拿來運算了！

## 重點整理

- 使用者輸入的東西是文字，要用 `.parse::<i32>()` 轉成整數才能做運算
- `.expect("錯誤訊息")` 在轉換失敗時會印出訊息並結束程式
- 完整流程：`input.trim().parse::<i32>().expect("請輸入數字")`
