# ref pattern 與 match ergonomics

## 本集目標

了解 `ref` 關鍵字在模式匹配中的作用，以及為什麼在現代 Rust 中幾乎不需要手動寫 `ref`。

> 本集是**第三章**的補充。

## 概念說明

這集要講一個你可能在舊程式碼裡看過、但在現代 Rust 中幾乎用不到的語法：`ref`。理解它的存在和原理，有助於你讀懂別人的程式碼。

### `ref` 是什麼？

在模式中，`ref` 會把綁定的變數變成一個參考，而不是取得所有權：

```rust,no_run
# fn main() {
    let val = String::from("hello");
    let ref r = val; // r 的型別是 &String
    // 等同於：let r = &val;
# }
```

你可能會想：那我直接寫 `&val` 不就好了？沒錯，在 `let` 綁定中，兩者完全等價。`ref` 的存在感主要在 `match` 裡面。

### 在 match 中的 `ref`

以前（Rust 1.26 之前），如果你想在 match 裡借用而不是 move，必須手動寫 `ref`：

```rust
# fn main() {
    let opt = Some(String::from("hello"));
    match opt {
        Some(ref s) => println!("{}", s), // 借用，不 move
        None => println!("nothing"),
    }
    // opt 還能用，因為我們只是借用了裡面的值
# }
```

如果不寫 `ref`，`s` 會拿走 `String` 的所有權，之後就不能再用 `opt` 了。

### match ergonomics（Rust 1.26+）

從 Rust 1.26 開始，編譯器變聰明了。當你 match 一個**參考**的時候，裡面的綁定會自動變成參考：

```rust
# fn main() {
    let opt = Some(String::from("hello"));
    match &opt {     // 注意這裡是 &opt
        Some(s) => { // s 自動是 &String，不需要寫 ref
            println!("{}", s);
        }
        None => println!("nothing"),
    }
    // opt 還能用！
# }
```

這就是所謂的 **match ergonomics**。編譯器看到你 match 的是一個參考（`&opt`），就會自動幫你在模式裡加上 `ref`。

### 所以現在還需要寫 `ref` 嗎？

幾乎不需要了。99% 的情況你只要 match 參考（`match &value`），編譯器就會自動處理。但讀舊程式碼的時候，看到 `ref` 至少要知道它在做什麼。

## 範例程式碼

```rust
fn main() {
    // ===== ref 基本用法 =====
    let name = String::from("Rust");
    let ref r = name; // r: &String
    println!("ref 綁定：{}", r);
    println!("原本還能用：{}", name);

    // ===== 舊寫法：match 中用 ref 避免 move =====
    let data = Some(String::from("重要資料"));

    match data {
        Some(ref s) => println!("舊寫法借用：{}", s),
        None => println!("空的"),
    }
    println!("data 還在：{:?}", data); // 因為用了 ref，沒有 move

    // ===== 新寫法：match ergonomics =====
    let data2 = Some(String::from("新世界"));

    match &data2 {   // match 參考
        Some(s) => { // s 自動是 &String
            println!("新寫法借用：{}", s);
        }
        None => println!("空的"),
    }
    println!("data2 還在：{:?}", data2);

    // ===== 更複雜的例子 =====
    let pairs = vec![
        (String::from("台北"), 25),
        (String::from("東京"), 10),
        (String::from("紐約"), 5),
    ];

    // match ergonomics 讓 for 迴圈中的解構也很自然
    for (city, temp) in &pairs {
        // city: &String, temp: &i32（自動借用）
        println!("{} 氣溫 {} 度", city, temp);
    }
    println!("pairs 還在，共 {} 筆", pairs.len());
}
```

## 重點整理

- `let ref x = val;` 等同於 `let x = &val;`——在 `let` 中兩者完全一樣
- 在 match 中，`Some(ref x)` 會借用而不是 move 內部的值
- **match ergonomics（Rust 1.26+）**：match 一個參考時，模式中的變數自動變成參考
- 現代 Rust 幾乎不需要手動寫 `ref`，用 `match &value` 就好
- `for (k, v) in &collection` 也受 match ergonomics 影響，`k` 和 `v` 自動是參考
- 認識 `ref` 主要是為了讀懂舊程式碼
