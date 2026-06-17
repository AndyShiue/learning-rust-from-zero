# supertrait

## 本集目標

學會用 supertrait 定義 `trait` 之間的依賴關係，理解 `Copy: Clone` 以及 `DerefMut: Deref` 的設計原理。

## 概念說明

有時候一個 `trait` 需要建立在另一個 `trait` 的基礎之上。

### supertrait 語法

```rust,noplayground
trait Summarize: std::fmt::Display {
    fn summary(&self) -> String;
}
#
# fn main() {}
```

`Summarize: Display` 的意思是：「要實作 `Summarize`，你必須先實作 `Display`。」`Display` 就是 `Summarize` 的 **supertrait**，反過來說，`Summarize` 是 `Display` 的 **subtrait**。

好處是在 `Summarize` 的預設實作或使用者程式碼裡，可以確定 `self` 一定有 `Display` 的功能。

注意：**實作 `Summarize` 不會自動幫你實作 `Display`**。你必須自己手動實作 `Display`，然後才能實作 `Summarize`。supertrait 只是一個「前提條件」，不是「自動贈送」。

### `Copy: Clone`

第 4 章學過 `Copy` 和 `Clone`。它們之間就是 supertrait 的關係：

```rust,noplayground
trait Copy: Clone { }
#
# fn main() {}
```

這表示：**要實作 `Copy`，必須先實作 `Clone`。** 

為什麼？因為 `Copy` 是一種「自動複製」的能力，而 `Clone` 是「手動複製」的能力。邏輯上，如果你能自動複製，那你也一定能手動複製。所以 `Copy` 要求 `Clone` 作為前提。

這就是為什麼 `#[derive(Copy, Clone)]` 要同時寫兩個——只寫 `derive(Copy)` 會報錯，因為 `Copy` 要求 `Clone`。

### `DerefMut: Deref`

第 23 集學的 `DerefMut` 也是一樣的道理——`DerefMut` 的 supertrait 是 `Deref`。要能可變解參考，前提是先要能不可變解參考。所以實作了 `DerefMut` 的型別一定也實作了 `Deref`。

## 範例程式碼

```rust,editable
use std::fmt::Display;
use std::fmt::Formatter;

// 定義一個 supertrait：Summarize 要求 Display
trait Summarize: Display {
    fn summary(&self) -> String {
        // 因為有 Display supertrait，可以用 to_string()
        let full = self.to_string();
        if full.len() > 10 {
            let mut s = String::new();
            // 取前 10 個字元
            let mut count = 0;
            for c in full.chars() {
                if count >= 10 {
                    break;
                }
                s.push(c);
                count += 1;
            }
            s.push_str("...");
            s
        } else {
            full
        }
    }
}

struct Article {
    title: String,
    content: String,
}

// 必須先實作 Display（supertrait）
impl Display for Article {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{}: {}", self.title, self.content)
    }
}

// 然後才能實作 Summarize
impl Summarize for Article {}

// Copy: Clone 的示範
#[derive(Debug, Clone, Copy)]
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let article = Article {
        title: String::from("Rust"),
        content: String::from("一門很棒的程式語言，值得學習"),
    };

    // 用 Display（supertrait）
    println!("完整：{}", article);

    // 用 Summarize（預設實作會用到 Display）
    println!("摘要：{}", article.summary());

    // Copy 需要 Clone 的示範
    let p = Point { x: 1, y: 2 };
    let p2 = p; // copy（自動複製）
    let p3 = p.clone(); // clone（手動複製）也可以用
    println!("{:?} {:?} {:?}", p, p2, p3);
}
```

## 重點整理

- `trait A: B` 表示「要實作 `A`，必須先實作 `B`」——`B` 是 `A` 的 supertrait，`A` 是 `B` 的 subtrait
- `Copy: Clone`——`Copy` 要求 `Clone`，所以 `derive` 時必須同時寫兩個
- `DerefMut: Deref`——要能可變解參考，必須先能不可變解參考
- 實作 subtrait 不會自動實作 supertrait——你必須自己先寫 `impl Supertrait`
- subtrait 的預設實作裡可以使用 supertrait 的方法

