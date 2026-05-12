# `Vec` 基礎

## 本集目標

學會使用 `Vec`——一個可以動態增長的陣列。

## 概念說明

### 陣列的限制

我們在第二章學了陣列 `[i32; 5]`，但陣列的大小是固定的——宣告時就決定了，之後不能加東西也不能減東西。

如果我們需要一個**大小可以變化**的集合呢？比如：使用者一筆一筆輸入資料，或者程式在執行過程中不斷累積結果。

這就需要 **`Vec`**。`Vec` 就像一個**可以伸縮的陣列**，資料存在 heap 上。

### 建立 `Vec`

最簡單的方式是用 `vec!` 巨集：

```rust,noplayground
# fn main() {
    let nums = vec![1, 2, 3, 4, 5];
# }
```

這樣就建立了一個包含 5 個 `i32` 的 `Vec`。Rust 會根據你放的值自動推斷型別。

你也可以建立空的 `Vec`，然後一個一個加：

```rust,noplayground
# fn main() {   
    let mut nums = Vec::new();
    nums.push(10);
    nums.push(20);
# }
```

Rust 會在你第一次 `push` 的時候推斷出型別。

### 索引和走訪

`Vec` 的索引跟陣列一樣，用 `[i]`：

```rust
# fn main() {
    let nums = vec![10, 20, 30];
    println!("{}", nums[0]); // 10
    println!("{}", nums[2]); // 30
# }
```

走訪也跟陣列一樣，用 `for`：

```rust
# fn main() {
#     let nums = vec![10, 20, 30];
    for n in &nums {
        println!("{}", n);
    }
# }
```

注意：走訪的時候用 `&nums`（借用），這樣 `nums` 不會被 move 走。下一集會詳細說明。

### `push`：加入新元素

```rust
# fn main() {
    let mut fruits = Vec::new();
    fruits.push("蘋果");
    fruits.push("香蕉");
    fruits.push("櫻桃");
    println!("{:?}", fruits);
# }
```

`push` 會把新元素加到最後面。注意 `Vec` 必須是 `let mut` 才能 `push`。

### `len`：取得長度

```rust
# fn main() {
    let nums = vec![1, 2, 3];
    println!("長度：{}", nums.len());
# }
```

## 範例程式碼

```rust
fn main() {
    // 用 vec! 建立
    let scores = vec![85, 92, 78, 95, 88];
    println!("成績：{:?}", scores);
    println!("第一筆：{}", scores[0]);
    println!("共 {} 筆", scores.len());

    // 空的 Vec，用 push 加入
    let mut names = Vec::new();
    names.push("小明");
    names.push("小花");
    names.push("阿旺");
    println!("名單：{:?}", names);

    // 走訪
    println!("逐一列出：");
    for name in &names {
        println!("  - {}", name);
    }

    // 用 for 走訪並加總
    let nums = vec![10, 20, 30, 40, 50];
    let mut total = 0;
    for x in &nums {
        total += x;
    }
    println!("總和 = {}", total);

    // Vec 可以一直 push
    let mut growing = Vec::new();
    for i in 0..5 {
        growing.push(i * 10);
    }
    println!("動態建立：{:?}", growing);
}
```

## 重點整理

- **`Vec`** 是可以動態增長的陣列，資料存在 heap 上
- `vec![1, 2, 3]` 建立有初始值的 `Vec`，Rust 自動推斷型別
- `Vec::new()` 建立空的 `Vec`
- `push` 在最後面加入元素（需要 `let mut`）
- 索引用 `v[0]`、`v[1]` 等，長度用 `v.len()`（method，回傳元素個數）
- 走訪用 `for x in &v`（借用，不 move）
- `Vec` 和陣列的操作方式很像，但 `Vec` 大小可以變化
