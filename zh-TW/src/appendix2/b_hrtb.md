# HRTB

## 本集目標

理解 higher-ranked trait bound（HRTB）中的 `for<'a>`，學會分辨「只接受某一段生命週期」與「接受任何生命週期」。

> 本集是**第 5 章生命週期**與**第 6 章閉包**的補充。

## 概念說明

假設我們想寫一個函數，接收另一個函數或閉包，然後把區域變數的參考交給它：

```rust,noplayground
fn call_with_local<F>(f: F)
where
    F: Fn(&str),
{
    let text = String::from("區域字串");
    f(&text);
}
#
# fn main() {}
```

這段程式可以編譯。問題是：bound 裡的 `&str` 到底是哪一段生命週期？

完整概念其實是：不管 `call_with_local` 當下建立的參考活多久，`f` 都必須能接受。把省略的意思明寫出來，就是 HRTB：

```rust,ignore
F: for<'a> Fn(&'a str)
```

### `for<'a>` 的意思

`for<'a>` 表示「**對每一個可能的 `'a` 都成立**」。所以：

```rust,ignore
for<'a> F: Fn(&'a str)
```

或等價的：

```rust,ignore
F: for<'a> Fn(&'a str)
```

都表示 `F` 能接受任意生命週期的 `&str`。

HRTB 是 **higher-ranked trait bound** 的縮寫。名稱聽起來很硬，但眼前最重要的讀法只有一句：「這個 trait bound 對所有 `'a` 都要成立。」

### 誰有權選 `'a`？

比較下面兩個簽名：

```rust,ignore
fn one_lifetime<'a, F>(f: F, value: &'a str)
where
    F: Fn(&'a str),
{ /* ... */ }

fn every_lifetime<F>(f: F)
where
    F: for<'a> Fn(&'a str),
{ /* ... */ }
```

在 `one_lifetime` 裡，`'a` 是函數本身的泛型參數。呼叫者傳入 `value` 時，便決定了這次呼叫的 `'a`；`F` 只需要處理這一種 `'a`。

在 `every_lifetime` 裡，`for<'a>` 位於 `F` 的 bound 內。`every_lifetime` 的函數體可以一次又一次建立不同長度的借用，再交給 `f`。因此是**使用 `f` 的這一方**每次選 `'a`，`F` 必須全部接受。

### 為什麼普通 lifetime 參數不夠？

嘗試把 `'a` 放到外層函數：

```rust,compile_fail
fn call_with_local<'a, F>(f: F)
where
    F: Fn(&'a str),
{
    let text = String::from("區域字串");
    f(&text);
}
#
# fn main() {}
```

這裡的 `'a` 是呼叫者選的，可能比整個 `call_with_local` 還長。但 `text` 只是函數內的區域變數，不可能借用成任意長的 `&'a str`。

換成 `for<'a>` 後，`call_with_local` 只需要為這次短短的借用挑一個適合的 `'a`：

```rust,editable
fn call_with_local<F>(f: F)
where
    F: for<'a> Fn(&'a str),
{
    let text = String::from("區域字串");
    f(&text);
}

fn print_text(text: &str) {
    println!("收到：{text}");
}

fn main() {
    call_with_local(print_text);
    call_with_local(|text| println!("長度：{}", text.len()));
}
```

普通函數 `print_text` 和這個閉包都不會要求參考必須來自某個特定作用域，因此可以接受任何 `'a`。

### 常見的省略

實務上通常不必手寫這個 HRTB：

```rust,ignore
F: Fn(&str)
```

當 `Fn` 參數中的參考省略生命週期時，編譯器會把它理解成類似 `for<'a> F: Fn(&'a str)`。因此 HRTB 常常早就在你用過的程式裡，只是沒有露出 `for<'a>`。

你仍然需要認識明寫形式，因為更複雜的 bound、函數指標與函式庫 API 會直接出現它。

## 範例程式碼

```rust,editable
fn visit_twice<F>(visitor: F)
where
    F: for<'a> Fn(&'a str),
{
    let outer = String::from("第一段資料");
    visitor(&outer);

    {
        let inner = String::from("第二段、生命週期更短的資料");
        visitor(&inner);
    }
}

fn main() {
    let prefix = String::from("拜訪");

    visit_twice(|text| {
        println!("{prefix}：{text}");
    });
}
```

同一個 `visitor` 先收到借用 `outer` 的參考，再收到借用 `inner` 的參考。兩次參考的生命週期不同，但 `for<'a>` 保證它兩種都能處理。

## 重點整理

- `for<'a>` 表示後面的 trait bound 對每一個 `'a` 都成立。
- `F: for<'a> Fn(&'a str)` 表示 `F` 能接受任意生命週期的 `&str`。
- 外層的 `fn foo<'a>` 通常由呼叫者選 `'a`；HRTB 裡的 `for<'a>` 讓使用 `F` 的一方每次選 `'a`。
- 把 HRTB 的 `'a` 錯放到外層，常會要求區域借用活得不可能那麼久。
- `F: Fn(&str)` 通常已經省略了這類 HRTB，但讀進階簽名時仍會看到明寫的 `for<'a>`。
