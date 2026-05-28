# associated type

## 本集目標

學會在 `trait` 中定義 associated type（關聯型別），理解它和泛型參數的差別。

## 概念說明

第 18 集我們學了多參數 `trait`：`trait Convert<T>`。但有時候，型別參數不是「開放的」——一個型別只會有一種合理的實作。

### 問題：多參數 `trait` 太自由了

想像一個「容器」的 `trait`。容器裡面裝什麼型別的元素？用多參數 `trait` 的話：

```rust,noplayground
trait Container<T> {
    fn first(&self) -> Option<&T>;
}
#
# fn main() {}
```

但這意味著同一個型別可以同時實作 `Container<i32>` 和 `Container<String>`——通常容器只會有一種元素型別。

### associated type：一對一的關係

associated type 解決了這個問題：

```rust,noplayground
trait Container {
    type Item;
    // 要使用 Self 的 associated type，用 Self::Type 的語法
    fn first(&self) -> Option<&Self::Item>;
}
#
# fn main() {}
```

`type Item;` 宣告了一個 associated type。實作的時候必須指定它是什麼：

```rust,noplayground
# trait Container {
#     type Item;
#     fn first(&self) -> Option<&Self::Item>;
# }
#
# struct NumberList {
#     data: Vec<i32>,
# }
#
impl Container for NumberList {
    type Item = i32;
    fn first(&self) -> Option<&i32> {
        self.data.first()
    }
}
#
# fn main() {}
```

當 `Self`（`NumberList`）和角括號裡的參數（這裡沒有）都確定了，`Item` 就唯一確定是 `i32`，不會有歧義。

### 和泛型參數的差別

你可以把 `trait` 想像成一個函數，它接受一些「輸入」然後決定一些「輸出」：

- **輸入（input）**：`Self`（誰來實作這個 `trait`）和角括號裡的型別參數（`<T>`）
- **輸出（output）**：associated type（`type Item`）

輸入決定了輸出——當你確定了「誰」（`Self`）和「角括號裡的參數」，associated type 就唯一確定了。

舉例來說，`Convert<T>` 裡的 `T` 是輸入，所以同一個 `Self` 搭配不同的 `T` 可以有不同的實作：`i32` 可以同時實作 `Convert<String>` 和 `Convert<(i32,)>`。

但 `Container` 的 `Item` 是輸出。當你確定了 `Self` 是 `NumberList`，`Item` 就**只能有一個答案**——`i32`。

用哪個？如果「確定了所有 input 之後，這個型別就只有一個合理的答案」，把它放在 associated type（output）。如果「同一組 input 可以搭配多種不同答案」，把它放在角括號裡（input）。

### `Deref` 也有 associated type

第 23 集學的 `Deref` trait 就用了 associated type：

```rust,noplayground
trait Deref {
    type Target;
    fn deref(&self) -> &Self::Target;
}
#
# fn main() {}
```

`type Target` 決定了解參考後得到什麼型別。例如 `Box<T>` 的實作是 `type Target = T`——解參考 `Box<i32>` 得到 `i32`。這跟 `Container` 的 `type Item` 是同樣的道理：一個 `Box<i32>` 解參考後只會得到 `i32`，不會得到別的東西，所以用 associated type 而不是泛型參數。

### 在 `trait` bound 中指定 associated type

你可以在 `trait` bound 裡指定 associated type 的具體型別：

```rust,ignore
fn print_first<C: Container<Item = i32>>(c: &C) { ... }
#
# fn main() {}
```

`Container<Item = i32>` 表示「實作了 `Container`，而且 `Item` 是 `i32`」。

## 範例程式碼

```rust,editable
use std::fmt::Display;

// 用 associated type 定義容器 trait
trait Container {
    type Item;

    fn first(&self) -> Option<&Self::Item>;
    fn last(&self) -> Option<&Self::Item>;
    fn len(&self) -> usize;
}

struct NumberList {
    data: Vec<i32>,
}

impl Container for NumberList {
    type Item = i32; // 指定 associated type

    fn first(&self) -> Option<&i32> {
        self.data.first()
    }

    fn last(&self) -> Option<&i32> {
        self.data.last()
    }

    fn len(&self) -> usize {
        self.data.len()
    }
}

struct WordList {
    words: Vec<String>,
}

impl Container for WordList {
    type Item = String; // 不同的型別，不同的 Item

    fn first(&self) -> Option<&String> {
        self.words.first()
    }

    fn last(&self) -> Option<&String> {
        self.words.last()
    }

    fn len(&self) -> usize {
        self.words.len()
    }
}

// 在 trait bound 中用 associated type
fn print_first_item<C>(c: &C)
where
    C: Container,
    C::Item: Display,
{
    match c.first() {
        Some(item) => println!("第一個元素：{}", item),
        None => println!("容器是空的"),
    }
}

fn main() {
    let nums = NumberList { data: vec![10, 20, 30] };
    let words = WordList {
        words: vec![
            String::from("hello"),
            String::from("world"),
        ],
    };

    println!("數字容器長度：{}", nums.len());
    print_first_item(&nums);

    println!("文字容器長度：{}", words.len());
    print_first_item(&words);

    // last
    match nums.last() {
        Some(n) => println!("最後一個數字：{}", n),
        None => println!("空的"),
    }
}
```

## 重點整理

- `type Item;` 在 `trait` 中定義 associated type
- 用 `Self::Item` 的語法可以在 `trait` 定義中讀取 `Self` 的 associated type
- 實作時用 `type Item = i32;` 指定具體型別
- **input vs output**：`Self` 和角括號參數是 input，associated type 是 output。input 決定 output
- `Deref` 的 `type Target` 也是 associated type——`Box<T>` 的 `Target = T`，代表解參考後得到 `T`
- 在 `trait` bound 中用 `Container<Item = i32>` 指定 associated type

