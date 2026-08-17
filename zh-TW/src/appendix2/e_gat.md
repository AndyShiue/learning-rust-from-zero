# GAT

## 本集目標

理解 generic associated type（GAT），學會用帶生命週期參數的 associated type 表達「回傳型別隨每次借用而改變」。

> 本集是**第 5 章 associated type** 與本附錄 HRTB 的補充。

## 概念說明

第 5 章介紹 associated type 時，我們看過類似 `Iterator` 的設計：

```rust,ignore
trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;
}
```

每個實作者選定一個 `Item`。例如某個迭代器的 `Item` 是 `i32`，之後每次呼叫 `next` 都回傳同一個型別 `Option<i32>`。

但如果 `next` 想回傳一個**借用自迭代器本身**的值呢？每次 `&mut self` 的借用生命週期都可能不同，`Item` 也得跟著那次借用改變。普通 associated type 沒地方放這個生命週期參數。

### associated type 也能有泛型參數

GAT 讓 associated type 自己帶泛型參數：

```rust,noplayground
trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}
#
# fn main() {}
```

GAT 是 **generic associated type** 的縮寫。這裡的 `Item` 不再只代表一個型別，而是代表一整個型別家族：

```rust,ignore
Self::Item<'短借用>
Self::Item<'長借用>
```

每次呼叫 `next` 時，`&'a mut self` 的 `'a` 決定這一次使用哪個 `Item<'a>`。

### `where Self: 'a` 是什麼？

`Item<'a>` 可能借用 `Self` 裡面的資料。要讓這份借用在 `'a` 期間有效，`Self` 本身當然也必須活得過 `'a`：

```rust,ignore
type Item<'a>
where
    Self: 'a;
```

這正是第 5 章的 lifetime bound。它不是說 `Self` 永遠要是 `'static`，而是說每次選出一個 `'a` 時，那次使用的 `Self` 必須至少仍活到 `'a` 結束。

### 一個會借出自身資料的迭代器

下面的 `Lines` 擁有一批 `String`，每次 `next` 回傳其中一個 `&str`：

```rust,editable
trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}

struct Lines {
    data: Vec<String>,
    position: usize,
}

impl LendingIterator for Lines {
    type Item<'a> = &'a str
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
        let position = self.position;
        self.position += 1;
        self.data.get(position).map(String::as_str)
    }
}

fn main() {
    let mut lines = Lines {
        data: vec![
            String::from("第一行"),
            String::from("第二行"),
        ],
        position: 0,
    };

    while let Some(line) = lines.next() {
        println!("{line}");
    }
}
```

在這個實作中，`Item<'a>` 是 `&'a str`。回傳的字串切片借用 `lines.data`，而借用時間正好綁在這次 `&'a mut self` 上。

### 為什麼普通 `Iterator` 表達不了？

若硬套普通 `Iterator`，會想寫成：

```rust,compile_fail
struct Lines {
    data: Vec<String>,
    position: usize,
}

impl Iterator for Lines {
    type Item = &str;

    fn next(&mut self) -> Option<Self::Item> {
        let position = self.position;
        self.position += 1;
        self.data.get(position).map(String::as_str)
    }
}
#
# fn main() {}
```

`type Item = &str` 沒有生命週期來源。`Iterator::Item` 是實作時一次選定的固定型別，不能表示「這個 `&str` 的生命週期來自每次呼叫的 `&mut self`」。

當然，標準 `Iterator` 可以回傳迭代器**外部**資料的參考，例如 `slice.iter()` 的 `Item` 是建立迭代器時就已決定好的 `&'data T`。GAT 要解決的是另一件事：輸出直接借用每次呼叫時的 `self`。

### 一次借出的值要先用完

因為 `next` 的輸出借用了 `&mut self`，只要輸出仍在使用，就不能再次可變借用迭代器：

```rust,compile_fail
# trait LendingIterator {
#     type Item<'a> where Self: 'a;
#     fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
# }
#
# struct Lines { data: Vec<String>, position: usize }
#
# impl LendingIterator for Lines {
#     type Item<'a> = &'a str where Self: 'a;
#     fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
#         let p = self.position;
#         self.position += 1;
#         self.data.get(p).map(String::as_str)
#     }
# }
#
# fn main() {
    let mut lines = Lines {
        data: vec![String::from("一"), String::from("二")],
        position: 0,
    };

    let first = lines.next().expect("應該有第一行");
    let second = lines.next().expect("應該有第二行");
    println!("{first}、{second}");
# }
```

`first` 一直用到最後的 `println!`，所以它借用 `lines` 的期間還沒結束，第二次 `next()` 就不能再借用 `lines`。這不是 GAT 的缺陷，而是它忠實表達了 lending API 的借用關係。

### GAT 不只可以放生命週期

名稱裡的 generic 是認真的：associated type 也能帶型別或 const 參數，例如 `type Buffer<T>` 或 `type Array<const N: usize>`。不過生命週期參數最能展現普通 associated type 做不到的事，也是函式庫 API 中最常需要讀懂的形式。

## 範例程式碼

```rust,editable
trait View {
    type Output<'a>
    where
        Self: 'a;

    fn view<'a>(&'a self) -> Self::Output<'a>;
}

struct Document {
    title: String,
    body: String,
}

impl View for Document {
    type Output<'a> = (&'a str, &'a str)
    where
        Self: 'a;

    fn view<'a>(&'a self) -> Self::Output<'a> {
        (&self.title, &self.body)
    }
}

fn print_view<T: View>(value: &T)
where
    for<'a> T::Output<'a>: std::fmt::Debug,
{
    println!("{:?}", value.view());
}

fn main() {
    let document = Document {
        title: String::from("GAT"),
        body: String::from("associated type 也能有泛型參數"),
    };

    print_view(&document);
}
```

## 重點整理

- GAT 是帶泛型參數的 associated type。
- `type Item<'a>` 代表一整個隨 `'a` 改變的型別家族，而不是單一固定型別。
- `where Self: 'a` 保證輸出借用 `Self` 時，`Self` 在 `'a` 期間仍然有效。
- lending iterator 能讓每次輸出借用該次 `&mut self`，普通 `Iterator::Item` 無法表達這種關係。
- 一個 lending 輸出仍在使用時，對 `self` 的借用也仍存在。
- GAT 常和 HRTB 一起出現在進階 trait bound 裡。
