# 多行字串 & raw string literal

## 本集目標

學會在 Rust 中撰寫多行字串、行接續符號、以及不需要跳脫字元的 raw string。

> 本集是**第一章**的補充。

## 概念說明

寫程式的時候，我們常常需要處理多行文字、檔案路徑、或是包含特殊字元的字串。Rust 提供了幾種好用的語法來應對這些情況。

### 多行字串

在 Rust 裡，字串字面值可以直接跨行：

```rust,no_run
# fn main() {
    let poem = "床前明月光，
疑是地上霜。";
# }
```

換行符號會直接被包含在字串裡。

### 行接續符 `\`

如果你想把很長的字串分行寫，但**不要**換行符號出現在結果裡，可以在行尾加 `\`。它會吃掉換行以及下一行開頭的空白：

```rust,no_run
# fn main() {
    let long = "這是一段很長的句子，\
                但其實只有一行。";
    // 結果："這是一段很長的句子，但其實只有一行。"
# }
```

### raw string literal

有時候字串裡有很多反斜線（例如 Windows 路徑），每個都要跳脫很煩。`r"..."` 語法讓你完全不需要跳脫：

```rust,no_run
# fn main() {
    let path = r"C:\Users\test\documents";
    // 不需要寫成 "C:\\Users\\test\\documents"
# }
```

### 包含引號的 raw string

如果 raw string 裡面需要有雙引號怎麼辦？用 `r#"..."#` 語法：

```rust,no_run
# fn main() {
    let json = r#"{"name": "Andy", "age": 29}"#;
# }
```

如果字串裡面連 `"#` 都有？那就多加幾層 `#`：

```rust,no_run
# fn main() {
    let tricky = r##"這裡有 "#" 符號"##;
# }
```

你可以加任意多層 `#`，只要開頭和結尾的數量一致就好。

## 範例程式碼

```rust
fn main() {
    // 多行字串
    let haiku = "古池や
蛙飛び込む
水の音";
    println!("俳句：\n{}", haiku);
    println!("---");

    // 行接續符：\ 吃掉換行和前導空白
    let sentence = "Rust 是一門注重安全性、\
                    效能和並行的程式語言。";
    println!("{}", sentence);
    println!("---");

    // Raw string：不處理跳脫字元
    let win_path = r"C:\Users\Andy\Desktop\project";
    println!("路徑：{}", win_path);

    // 正則表示式之類的場景也很好用
    let pattern = r"\d+\.\d+";
    println!("正則：{}", pattern);

    // 包含雙引號的 raw string
    let json = r#"{"name": "小明", "score": 95}"#;
    println!("JSON：{}", json);

    // 多層 # —— 當字串裡有 "# 的時候
    let code_sample = r##"
        let s = r#"hello"#;
        println!("{}", s);
    "##;
    println!("程式碼範例：{}", code_sample);

    // raw string 也能多行
    let html = r#"
<html>
    <body>
        <h1>Hello, Rust!</h1>
    </body>
</html>
"#;
    println!("{}", html);
}
```

## 重點整理

- 字串字面值可以直接跨行，換行符號會被保留
- 行尾加 `\` 可以接續下一行，同時忽略換行和下一行的前導空白
- `r"..."` 是 raw string，不處理任何跳脫字元（`\n`、`\\` 等都照原樣保留）
- `r#"..."#` 讓 raw string 裡可以包含雙引號
- `#` 的層數可以增加（`r##"..."##`、`r###"..."###`），只要前後一致
- raw string 特別適合 Windows 路徑、正則表示式、JSON、嵌入程式碼等場景
