# orphan rule

## 本集目標

理解 Rust 的 orphan rule（孤兒規則），以及當你想為外部型別實作外部 `trait` 時該怎麼辦。

## 概念說明

在第 5 章我們學過 `trait`——你可以為自己的型別實作任何 `trait`。但你有沒有試過這樣：

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

> **要 `impl` 一個 `trait`，`trait` 或型別至少有一個必須是你這個 `crate` 定義的。**

換句話說：**`trait` 是你的，或型別是你的**，至少要符合一個。

上面的例子裡，`Display` 是標準庫定義的，`Vec<i32>` 也是——兩個都不是你的，所以不行。

### 為什麼要有這個限制

想像一下如果沒有 orphan rule：

- `crate` `A` 為 `Vec<i32>` 實作了 `Display`，印出 `[1, 2, 3]`。
- `crate` `B` 也為 `Vec<i32>` 實作了 `Display`，印出 `1 | 2 | 3`。
- 你的程式同時用了 `A` 和 `B`……編譯器要用哪一個？

這就是衝突。orphan rule 從根本上避免了這個問題。

### 合法的情況

以下這些都是合法的：

```rust,noplayground
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

### 用自己的 `trait` 為外部型別增加 method

上面的情況 2 很實用。雖然 `Vec<i32>` 是標準庫的型別，但 `Describable` 是我們在目前 `crate` 定義的 `trait`，所以 orphan rule 允許我們寫 `impl Describable for Vec<i32>`。實作之後，`Vec<i32>` 的值就能用 method 語法呼叫 `.describe()`。

### 為什麼不能直接寫 `impl Vec<i32>`？

既然目標只是增加 method，你可能會想跳過 `trait`，直接這樣寫：

```rust,compile_fail
impl Vec<i32> {
    fn describe(&self) -> String {
        format!("一個有 {} 個元素的 Vec", self.len())
    }
}
#
# fn main() {}
```

Rust 也不允許這樣做。**`impl Type { ... }` 裡的 `Type` 必須是在目前 `crate` 定義的型別。** `Vec` 是標準庫定義的，就算用 `use` 把它帶入作用域，也不會變成你的型別。

理由和 orphan rule 一樣是怕兩個 `crate` 撞在一起，差別在於 `trait` 的版本撞了還分得出來。`trait` method 要能呼叫，那個 `trait` 得先在作用域裡；所以 `crate` `A` 和 `crate` `B` 就算各自定義 `trait`、都替 `Vec<i32>` 實作 `describe`，決定權還在你手上——你 `use` 進哪一個 `trait`，`.describe()` 就是哪一個。

`impl Vec<i32> { ... }` 裡的 method 沒有這一層。它不屬於任何 `trait`，呼叫前也不必 `use` 任何東西：只要你依賴那個 `crate`，`v.describe()` 就存在了。兩個 `crate` 各加一個，你連「我要哪一個」都說不出口。所以這種直接掛在型別上的 method，只有定義那個型別的 `crate` 能加。

這裡限制的是同一個 `crate`，不是同一個檔案或 `mod`。只要型別是在目前 `crate` 定義的，`impl Type { ... }` 可以放在同一個 `crate` 的其他 `mod` 裡。

因此，當你不想包裝外部型別、又想替它增加 method 時，可以像上面一樣先定義自己的 `trait`，再為外部型別實作它。

### newtype pattern（繞過限制的方法）

如果你真的需要為外部型別實作外部 `trait`，可以用 **newtype pattern**——建立一個 tuple `struct` 把外部型別包起來：

```rust,noplayground
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

```rust,editable
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

## 多參數 `trait` 的情況

上面講的規則是最簡單的版本。對於多參數 `trait`（像第 5 章學的 `From<T>`），規則其實更複雜。簡單來說：

```rust,ignore
// OK：你的型別出現在參數裡
impl From<MyType> for String { ... }

// 不行：兩邊都是外部的
impl From<String> for Vec<i32> { ... }
```

完整的規則涉及「covered type parameter」等概念，超出本教學的範圍。有興趣可以參考[官方文件](https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules)。

## 重點整理

- **orphan rule**：寫 `impl Trait for Type` 時，`trait` 或型別至少有一個必須是你的 `crate` 定義的。
- 「你的型別 + 外部 `trait`」✅ 合法。
- 「外部型別 + 你的 `trait`」✅ 合法。
- 「外部型別 + 外部 `trait`」❌ 不合法。
- 自己定義 `trait` 並為外部型別實作，可以替外部型別增加 method。
- `impl Type { ... }` 裡的 `Type` 必須由目前 `crate` 定義，但 `impl` 和型別不必位於同一個檔案或 `mod`。
- orphan rule 是為了防止不同 `crate` 之間的 `impl` 衝突。
- **newtype pattern**：用 `struct MyWrapper(OriginalType)` 把外部型別包起來，就變成你的型別了。
- 多參數 `trait` 的 orphan rule 遠比上面講的更複雜，詳見官方文件。
