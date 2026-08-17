# HRTB

## 本集目標

理解 higher-ranked trait bound（HRTB）中的 `for<'a>`，學會分辨「只處理某一段生命週期」與「能處理任何生命週期」，並看懂 `Fn` 三兄弟如何省略輸入與回傳值的生命週期。

> 本集是**第 5 章生命週期**與**第 6 章閉包**的補充。

## 概念說明

假設我們有兩份商品資料，想用同一套規則各自選出一項主打商品：

```rust,noplayground
fn select_from_both<'first, 'second, T, F>(
    first: &'first [T],
    second: &'second [T],
    choose: F,
) -> (Option<&'first T>, Option<&'second T>)
where
    F: Fn(&[T]) -> Option<&T>,
{
    let from_first = choose(first);
    let from_second = choose(second);
    (from_first, from_second)
}
#
# fn main() {}
```

`first` 和 `second` 是兩個不同的參數，生命週期分別是 `'first` 與 `'second`。函數內用同一個 `choose` 呼叫兩次：

- 第一次接收 `&'first [T]`，回傳 `Option<&'first T>`。
- 第二次接收 `&'second [T]`，回傳 `Option<&'second T>`。

回傳型別保留了兩段生命週期：第一個結果跟著 `first`，第二個結果跟著 `second`。因此不能只是把兩個輸入都縮短成同一段共同的生命週期。

bound 裡的生命週期雖然被省略，完整概念其實是：`choose` 不論收到哪一段生命週期的 slice，都會回傳借用自該 slice 的元素。把它明寫出來，就是 HRTB：

```rust,ignore
F: for<'a> Fn(&'a [T]) -> Option<&'a T>
```

第一次呼叫時，`'a` 可以是 `'first`；第二次呼叫時，`'a` 可以改成 `'second`。

### `Fn` 三兄弟也有 lifetime elision

第 5 章看過函數可以省略常見的生命週期：

```rust,ignore
fn first<T>(values: &[T]) -> Option<&T>
```

因為只有一個參考輸入，編譯器知道 `Option` 裡的 `&T` 必須借用自這個 `&[T]`。完整寫法是：

```rust,ignore
fn first<'a, T>(values: &'a [T]) -> Option<&'a T>
```

相同的 lifetime elision 也適用於 `Fn`、`FnMut` 與 `FnOnce` 的參數和回傳值。因此下面三個 bound 都省略了生命週期：

```rust,ignore
F: Fn(&[T]) -> Option<&T>
F: FnMut(&[T]) -> Option<&T>
F: FnOnce(&[T]) -> Option<&T>
```

把生命週期明寫出來，分別相當於：

```rust,ignore
F: for<'a> Fn(&'a [T]) -> Option<&'a T>
F: for<'a> FnMut(&'a [T]) -> Option<&'a T>
F: for<'a> FnOnce(&'a [T]) -> Option<&'a T>
```

三個 trait 的差別仍是閉包能用什麼方式呼叫，以及呼叫時會不會修改或消耗捕獲值；它們使用的 lifetime elision 規則則相同。

### `for<'a>` 的意思

`for<'a>` 表示「**對每一個可能的 `'a` 都成立**」。所以：

```rust,ignore
for<'a> F: Fn(&'a [T]) -> Option<&'a T>
```

或等價的：

```rust,ignore
F: for<'a> Fn(&'a [T]) -> Option<&'a T>
```

都表示 `F` 能接受任意生命週期的 `&[T]`，而且回傳的 `&T` 會和該次輸入使用同一段生命週期。

HRTB 是 **higher-ranked trait bound** 的縮寫。名稱聽起來很硬，但眼前最重要的讀法只有一句：「這個 trait bound 對所有 `'a` 都要成立。」

### 誰有權選 `'a`？

回到 `select_from_both` 的三段生命週期：

```rust,ignore
fn select_from_both<'first, 'second, T, F>(
    first: &'first [T],
    second: &'second [T],
    choose: F,
) -> (Option<&'first T>, Option<&'second T>)
where
    F: for<'a> Fn(&'a [T]) -> Option<&'a T>,
{
    /* ... */
}
```

`'first` 與 `'second` 是函數本身的泛型參數，由呼叫者傳入兩份資料時決定。

`for<'a>` 則位於 `F` 的 bound 裡。`select_from_both` 在第一次呼叫 `choose` 時選擇 `'a = 'first`，第二次再選擇 `'a = 'second`。因此是**使用 `choose` 的這一方**替每次呼叫選 `'a`，`F` 必須全部接受。

### 為什麼普通 lifetime 參數不夠？

若只把 `choose` 綁在 `'first`，第一次呼叫沒有問題，第二次就會失敗：

```rust,compile_fail
fn select_from_both<'first, 'second, T, F>(
    first: &'first [T],
    second: &'second [T],
    choose: F,
) -> (Option<&'first T>, Option<&'second T>)
where
    F: Fn(&'first [T]) -> Option<&'first T>,
{
    let from_first = choose(first);
    let from_second = choose(second);
    (from_first, from_second)
}
#
# fn main() {}
```

這個 bound 只保證 `choose` 能接收 `&'first [T]`，回傳 `Option<&'first T>`。第二次卻需要它接收 `&'second [T]`，回傳 `Option<&'second T>`。除非 `'first` 與 `'second` 完全相同，否則這項保證不夠。

改成 HRTB 後，同一個 `choose` 就能在兩次呼叫中使用不同的生命週期：

```rust,noplayground
fn select_from_both<'first, 'second, T, F>(
    first: &'first [T],
    second: &'second [T],
    choose: F,
) -> (Option<&'first T>, Option<&'second T>)
where
    F: for<'a> Fn(&'a [T]) -> Option<&'a T>,
{
    let from_first = choose(first);
    let from_second = choose(second);
    (from_first, from_second)
}
#
# fn main() {}
```

實務上通常可以使用 lifetime elision，把 bound 寫成：

```rust,ignore
F: Fn(&[T]) -> Option<&T>
```

你仍然需要認識明寫的 `for<'a>`，因為更複雜的 API 會直接出現它。

## 範例程式碼

```rust,editable
#[derive(Debug)]
struct Product {
    name: String,
    price: u32,
}

fn select_from_both<'first, 'second, F>(
    first: &'first [Product],
    second: &'second [Product],
    choose: F,
) -> (Option<&'first Product>, Option<&'second Product>)
where
    F: for<'a> Fn(&'a [Product]) -> Option<&'a Product>,
{
    let from_first = choose(first);
    let from_second = choose(second);
    (from_first, from_second)
}

fn main() {
    let first_catalog = vec![
        Product {
            name: String::from("鍵盤"),
            price: 2_500,
        },
        Product {
            name: String::from("滑鼠"),
            price: 1_200,
        },
    ];
    let second_catalog = vec![
        Product {
            name: String::from("螢幕"),
            price: 8_000,
        },
        Product {
            name: String::from("喇叭"),
            price: 3_000,
        },
    ];

    let (first_featured, second_featured) = select_from_both(
        &first_catalog,
        &second_catalog,
        |products: &[Product]| {
            products.iter().max_by_key(|product| product.price)
        },
    );

    if let (Some(first), Some(second)) = (first_featured, second_featured) {
        println!("第一份主打：{}，價格：{}", first.name, first.price);
        println!("第二份主打：{}，價格：{}", second.name, second.price);
    }
}
```

## 重點整理

- `Fn`、`FnMut` 與 `FnOnce` 的參數和回傳值也會套用 lifetime elision。
- 只有一個參考輸入時，`Fn(&[T]) -> Option<&T>` 相當於 `for<'a> Fn(&'a [T]) -> Option<&'a T>`。
- `for<'a>` 表示後面的 trait bound 對每一個 `'a` 都成立。
- 外層的 `fn foo<'a>` 通常由呼叫者選 `'a`；HRTB 裡的 `for<'a>` 讓使用 `F` 的一方每次選 `'a`。
- 同一個函數或閉包要對不同生命週期的參考各呼叫一次，並分別保留輸出的生命週期時，HRTB 能直接表達這項要求。
- 實務上常用 lifetime elision 省略這類 HRTB，但閱讀進階簽名時仍會看到明寫的 `for<'a>`。
