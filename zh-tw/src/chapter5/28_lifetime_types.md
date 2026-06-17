# 型別上的生命週期

## 本集目標

學會為包含參考的 `struct` 和 `enum` 標注生命週期，以及用 `'_` 匿名生命週期簡化標注。

## 概念說明

到目前為止，我們的 `struct` 和 `enum` 都擁有自己的資料（`String`、`i32` 等）。但有時候你想讓它們借用別人的資料——例如存一個 `&str` 而不是 `String`。

### 型別裡放參考

```rust,compile_fail
struct Excerpt {
    text: &str, // 編譯錯誤！
}
#
# fn main() {}
```

這會報錯。因為 Rust 需要知道：「這個 `&str` 能活多久？」如果借來的資料被釋放了，`struct` 裡的參考就變成懸垂參考。

解法是加上生命週期參數：

```rust,noplayground
struct Excerpt<'a> {
    text: &'a str,
}
#
# fn main() {}
```

`'a` 告訴 Rust：「這個 `struct` 的壽命不能超過它借用的資料。」

`enum` 也一樣——如果 variant 攜帶參考，就需要生命週期：

```rust,noplayground
enum Token<'a> {
    Word(&'a str),
    Number(i32),
}
#
# fn main() {}
```

`Token::Word` 借用了一段文字，所以 `Token` 的壽命不能超過那段文字。`Token::Number` 本身不包含任何參考，但因為它和 `Word` 是同一個 `enum`，建立 `Token::Number(42)` 時仍然需要指定 `'a`——只是這個 `'a` 對 `Number` 來說不起實際作用。

### 使用帶生命週期的型別

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
# fn main() {
    let novel = String::from("很長的故事...");
    let excerpt = Excerpt { text: &novel };
# }
```

`excerpt` 借用了 `novel` 的資料，所以 `excerpt` 不能活得比 `novel` 更久。

### `'_` 匿名生命週期

當生命週期可以被推斷的時候，你可以用 `'_` 來簡化：

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
fn print_excerpt(e: &Excerpt<'_>) {
    println!("{}", e.text);
}
#
# fn main() {}
```

`'_` 告訴 Rust「我知道這裡需要一個生命週期，你自己推斷吧」。還記得第 5 集學的型別佔位符 `_` 嗎？`'_` 就是它的生命週期版本。

### `impl` 帶生命週期的 `struct`

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
impl<'a> Excerpt<'a> {
    fn text(&self) -> &str {
        self.text
    }
}
#
# fn main() {}
```

和泛型 `struct` 的 `impl` 一樣——`impl<'a>` 宣告生命週期參數，`Excerpt<'a>` 使用它。

注意 `fn text(&self) -> &str` 不需要寫任何生命週期標注——上一集學的省略規則第三條在這裡生效了：method 有 `&self` 時，回傳值的生命週期自動等於 `self`。

### 帶 lifetime 的型別作為函數參數

如果函數接收帶 lifetime 的型別，可以搭配 `'_` 讓編譯器推斷：

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
fn into_text(e: Excerpt<'_>) -> &str {
    e.text
}
#
# fn main() {}
```

注意這裡不能直接寫 `Excerpt` 不加任何東西——`Excerpt` 有一個必要的生命週期參數，就像 `Vec` 有一個必要的型別參數一樣，不能省略。但我們可以用 `'_` 讓編譯器推斷。

完整寫出來是：

```rust,noplayground
# struct Excerpt<'a> {
#     text: &'a str,
# }
#
fn into_text<'a>(e: Excerpt<'a>) -> &'a str {
    e.text
}
#
# fn main() {}
```

省略規則看到 `Excerpt<'_>` 帶有一個 input lifetime，規則二把回傳值的生命週期也設為同一個。

注意這裡 `e` 本身不是參考，函數結束時 `e` 會被 `drop`。但回傳的 `&'a str` 不是借用 `e`，而是借用 `e` 裡面存的那段文字——那段文字的壽命是 `'a`，跟 `e` 本身的壽命無關。

## 範例程式碼

```rust,editable
// struct 裡放參考，需要生命週期標注
struct Excerpt<'a> {
    text: &'a str,
    page: i32,
}

impl<'a> Excerpt<'a> {
    fn new(text: &'a str, page: i32) -> Excerpt<'a> {
        Excerpt { text, page }
    }

    fn text(&self) -> &str {
        self.text
    }

    fn summary(&self) -> String {
        let mut s = String::from("第 ");
        let page_str = self.page.to_string();
        s.push_str(&page_str);
        s.push_str(" 頁：");
        s.push_str(self.text);
        s
    }
}

// 用 '_ 匿名生命週期
fn print_excerpt(e: &Excerpt<'_>) {
    println!("[p.{}] {}", e.page, e.text);
}

fn main() {
    let novel = String::from("在很久很久以前，有一個程式設計師...");

    // excerpt 借用了 novel 的資料
    let excerpt = Excerpt::new(&novel[..15], 1);
    println!("{}", excerpt.text());
    println!("{}", excerpt.summary());

    // 用匿名生命週期的函數
    print_excerpt(&excerpt);

    // excerpt 不能活得比 novel 更久
    // 如果 novel 被 drop 了，excerpt 就不能用了
}
```

## 重點整理

- `struct` 裡放參考時，必須標注生命週期：`struct Excerpt<'a> { text: &'a str }`
- 生命週期保證 ``struct`` 不會活得比借用的資料更久
- `'_` 是匿名生命週期，讓編譯器自己推斷（生命週期版的 `_`）
- `impl` 帶生命週期的 `struct`：`impl<'a> Excerpt<'a> { ... }`
