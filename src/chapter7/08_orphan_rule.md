# orphan rule

## 本集目標

理解 Rust 的 orphan rule（孤兒規則），以及當你想為外部型別實作外部 trait 時該怎麼辦。

## 概念說明

在第五章我們學過 trait——你可以為自己的型別實作任何 trait。但你有沒有試過這樣：

```rust,compile_fail
use std::fmt;

impl fmt::Display for Vec<i32> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "my vec")
    }
}
#
# fn main() {}
```

編譯器會直接拒絕你。為什麼？

### orphan rule（孤兒規則）

Rust 有一條規則：

> **要 impl 一個 trait，trait 或型別至少有一個必須是你這個 crate 定義的。**

換句話說：**trait 是你的，或型別是你的**，至少要符合一個。

上面的例子裡，`Display` 是標準函式庫定義的，`Vec<i32>` 也是——兩個都不是你的，所以不行。

### 為什麼要有這個限制

想像一下如果沒有 orphan rule：

- Crate A 為 `Vec<i32>` 實作了 `Display`，印出 `[1, 2, 3]`
- Crate B 也為 `Vec<i32>` 實作了 `Display`，印出 `1 | 2 | 3`
- 你的程式同時用了 A 和 B……編譯器要用哪一個？

這就是衝突。orphan rule 從根本上避免了這個問題。

### 合法的情況

以下這些都是合法的：

```rust,no_run
// 情況 1：你的型別 + 外部 trait
struct MyPoint {
    x: f64,
    y: f64,
}

impl std::fmt::Display for MyPoint {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

// 情況 2：外部型別 + 你的 trait
trait Describable {
    fn describe(&self) -> String;
}

impl Describable for Vec<i32> {
    fn describe(&self) -> String {
        format!("一個有 {} 個元素的 Vec", self.len())
    }
}
#
# fn main() {}
```

### newtype pattern（繞過限制的方法）

如果你真的需要為外部型別實作外部 trait，可以用 **newtype pattern**——建立一個 tuple struct 把外部型別包起來：

```rust,no_run
use std::fmt;

struct MyVec(Vec<i32>);

impl fmt::Display for MyVec {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let items: Vec<String> = self.0.iter()
            .map(|x| x.to_string())
            .collect();
        write!(f, "[{}]", items.join(", "))
    }
}
#
# fn main() {}
```

`MyVec` 是你定義的型別，所以可以為它實作 `Display`。`self.0` 存取內部的 `Vec<i32>`。

## 範例程式碼

```rust
use std::fmt;

// newtype pattern：用自己的 struct 包住外部型別
struct Scores(Vec<i32>);

impl Scores {
    fn new() -> Scores {
        Scores(Vec::new())
    }

    fn add(&mut self, score: i32) {
        self.0.push(score);
    }

    fn total(&self) -> i32 {
        self.0.iter().sum()
    }
}

// 現在可以為「你的型別」實作 Display
impl fmt::Display for Scores {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let items: Vec<String> = self.0.iter()
            .map(|x| x.to_string())
            .collect();
        write!(f, "成績：[{}]，總分：{}", items.join(", "), self.total())
    }
}

fn main() {
    let mut scores = Scores::new();
    scores.add(85);
    scores.add(92);
    scores.add(78);
    scores.add(95);

    // 因為實作了 Display，可以直接 println
    println!("{}", scores);
}
```

## 多參數 trait 的情況

上面講的規則是最簡單的版本。對於多參數 trait（像第五章學的 `From<T>`），規則其實更複雜。簡單來說：

```rust,ignore
// OK：你的型別出現在參數裡
impl From<MyType> for String { ... }

// 不行：兩邊都是外部的
impl From<String> for Vec<i32> { ... }
```

完整的規則涉及「covered type parameter」等概念，超出本教學的範圍。有興趣可以參考[官方文件](https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules)。

## 重點整理

- **orphan rule**：要 impl trait，trait 或型別至少有一個必須是你的 crate 定義的
- 「你的型別 + 外部 trait」✅ 合法
- 「外部型別 + 你的 trait」✅ 合法
- 「外部型別 + 外部 trait」❌ 不合法
- 這個規則是為了防止不同 crate 之間的 impl 衝突
- **newtype pattern**：用 `struct MyWrapper(OriginalType)` 把外部型別包起來，就變成你的型別了
- 多參數 trait 的 orphan rule 遠比上面講的更複雜，詳見官方文件
