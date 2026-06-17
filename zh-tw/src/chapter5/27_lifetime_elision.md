# 生命週期省略規則

## 本集目標

理解 Rust 的生命週期省略規則，知道為什麼大部分時候不需要手動寫生命週期標注。

## 概念說明

上一集學了生命週期標注，你可能會擔心：「每個有參考的函數都要寫 `'a` 嗎？好麻煩！」

好消息是：大部分時候不用。Rust 有一套**省略規則（elision rules）**，會自動幫你補上生命週期標注。

### 三條省略規則

Rust 編譯器按照這三條規則嘗試推斷生命週期：

**規則一：每個參數能放生命週期的位置各自獲得獨立的生命週期**

```rust,ignore
fn foo(a: &str, b: &str)
// 編譯器看成：fn foo<'a, 'b>(a: &'a str, b: &'b str)
```

**規則二：如果經過規則一之後只有一個 input lifetime，回傳值的生命週期就等於它**

```rust,ignore
fn first_word(s: &str) -> &str
// 規則一：fn first_word<'a>(s: &'a str) -> &str
// 規則二：只有一個 input lifetime 'a → fn first_word<'a>(s: &'a str) -> &'a str
```

這就是為什麼上面的 `first_word` 不用寫 `'a`——只有一個 input lifetime，規則二自動搞定。

注意一個參數可能帶有多個 input lifetime——比如 `&'a &'b T`（參考的參考）就有兩個（`'a` 和 `'b`）。如果有兩個以上的 input lifetime，規則二就不適用了。

**規則三：如果有 `&self` 或 `&mut self` 參數，回傳值的生命週期就等於 `self` 的**

```rust,ignore
impl MyStruct {
    fn name(&self) -> &str { ... }
    // 編譯器看成：fn name<'a>(&'a self) -> &'a str
}
```

### 什麼時候規則不夠用？

當有多個參考參數、但回傳值的生命週期不確定跟哪個綁定時——就是上一集 `longer` 函數的情況。這時候就必須手動標注。

### 總結

- 一個參考參數 → 幾乎不用寫
- method 回傳 `&self` 的一部分 → 不用寫
- 多個參考參數且回傳參考 → 要寫

## 範例程式碼

```rust,editable
// 規則二：一個 input lifetime，自動推斷
fn trim_hello(s: &str) -> &str {
    if s.len() >= 5 {
        &s[5..]
    } else {
        s
    }
}

struct Article {
    title: String,
    content: String,
}

impl Article {
    fn new(title: String, content: String) -> Article {
        Article { title, content }
    }

    // 規則三：&self 參數，回傳值生命週期跟 self 綁定
    fn title(&self) -> &str {
        &self.title
    }

    fn summary(&self) -> &str {
        &self.content
    }
}

// 多個參考參數 + 回傳參考 → 需要手動標注
fn pick_longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() {
        a
    } else {
        b
    }
}

fn main() {
    // 規則二：不用寫生命週期
    let greeting = String::from("Hello, world!");
    let trimmed = trim_hello(&greeting);
    println!("{}", trimmed);

    // 規則三：method 接收參考不用寫生命週期
    let article = Article::new(
        String::from("Rust 生命週期"),
        String::from("其實沒那麼可怕"),
    );
    println!("標題：{}", article.title());
    println!("摘要：{}", article.summary());

    // 多個參考參數：需要手動標注
    let a = String::from("hello");
    let b = String::from("hi");
    let result = pick_longer(&a, &b);
    println!("比較長的：{}", result);
}
```

## 重點整理

- Rust 有三條**省略規則**，大部分時候會自動補上生命週期標注
- 規則一：每個參數能放生命週期的位置各自獲得獨立的生命週期
- 規則二：只有一個 input lifetime → 回傳值的生命週期自動等於它
- 規則三：method 有 `&self` 或 `&mut self` → 回傳值的生命週期自動等於 `self`
- 有多個 input lifetime 且回傳型別有 lifetime 時，才需要手動標注
