# lifetime bound

## 本集目標

學會 `T: 'a` 這種 lifetime bound，理解為什麼 `&'a T` 需要 `T` 裡面的參考都活得過 `'a`。

## 概念說明

### 問題：`T` 裡面可能有參考

到目前為止，我們的泛型函數大多處理 `i32`、`String` 這些擁有自己資料的型別。但 `T` 也可能是 `&str` 或其他包含參考的型別。

看這個 `struct`：

```rust,noplayground
struct Ref<'a, T> {
    value: &'a T,
}
#
# fn main() {}
```

如果 `T` 是 `&'x str`，那 `value` 就是 `&'a &'x str`——一個參考指向另一個參考。這時候 `'x` 必須活得至少和 `'a` 一樣長，否則外層的 `&'a` 還活著的時候，裡面的 `&'x str` 可能已經失效了。

### `T: 'a` 的意思

`T: 'a` 是一個 **lifetime bound**，表示「`T` 裡面的所有參考都活得過 `'a`」。

如果 `T` 是 `i32`（沒有參考），`T: 'a` 自動滿足。
如果 `T` 是 `&'x str`，那 `T: 'a` 就要求 `'x` 至少活得和 `'a` 一樣長。

### 什麼時候要寫？

在很多情況下，編譯器看到 `&'a T` 就知道需要 `T: 'a`，會自動幫你加上。但在某些 `trait` 定義或比較複雜的泛型結構裡，你可能需要手動寫：

```rust,noplayground
struct Ref<'a, T: 'a> {
    value: &'a T,
}
#
# fn main() {}
```

這裡的 `T: 'a` 其實是多餘的（編譯器能從 `&'a T` 推出來），但手動寫出來也不會錯，而且讓意圖更清楚。

### 參考帶生命週期的型別

同樣的道理推廣到任何帶生命週期的型別。如果你有 `&'b A<'a>`——一個活 `'b` 那麼久的參考，指向一個 `A<'a>`——那 `A<'a>` 整體必須在 `'b` 的期間都是有效的。這意味著 `A` 裡面借用的資料必須活得過 `'b`，也就是 `'a` 必須至少和 `'b` 一樣長。

原因很直覺：你持有一個參考 `&'b`，透過它可以存取 `A` 裡面所有借用的資料。如果 `A` 借用的資料比你持有參考的時間更早失效，你就能存取到已經被回收的記憶體。所以 Rust 要求 `'a` 至少活得和 `'b` 一樣長。

## 範例程式碼

```rust,editable
struct Excerpt<'a> {
    text: &'a str,
}

// T: 'a 確保 T 裡的參考活得過 'a
struct Ref<'a, T: 'a> {
    value: &'a T,
}

impl<'a, T: 'a> Ref<'a, T> {
    fn new(value: &'a T) -> Ref<'a, T> {
        Ref { value }
    }

    fn get(&self) -> &T {
        self.value
    }
}

fn main() {
    // T = i32（沒有參考，T: 'a 自動滿足）
    let num = 42;
    let r = Ref::new(&num);
    println!("Ref<i32>: {}", r.get());

    // T = &str（T 本身就是參考）
    let text = String::from("hello");
    let slice: &str = &text;
    let r2 = Ref::new(&slice);
    println!("Ref<&str>: {}", r2.get());

    // &'b A<'a> 的例子
    let novel = String::from("很長的故事...");
    let excerpt = Excerpt { text: &novel };
    let r3 = &excerpt; // &'b Excerpt<'a>
    // 這裡 'a 是 novel 的壽命，'b 是 r3 借用 excerpt 的時間
    // novel 至少活得和 r3 一樣久，所以 'a 活得過 'b，條件滿足
    println!("透過參考讀取：{}", r3.text);

    // T = String（擁有資料，沒有參考，T: 'a 自動滿足）
    let s = String::from("world");
    let r3 = Ref::new(&s);
    println!("Ref<String>: {}", r3.get());
}
```

## 重點整理

- `T: 'a` 表示 `T` 裡面的所有參考都活得過 `'a`
- 如果 `T` 沒有參考（如 `i32`、`String`），`T: 'a` 自動滿足
- `&'a T` 要合法就需要 `T: 'a`——大部分情況編譯器能自動推斷
- 理解 lifetime bound 才能讀懂標準庫裡比較複雜的泛型
