# 生命週期基礎

## 本集目標

理解為什麼需要生命週期標注 `'a`，學會在函數回傳參考時標注生命週期。

## 概念說明

第 4 章講借用的時候，我們留了一個伏筆：「不能回傳區域變數的參考。」現在來正式面對這個問題。

### 問題一：回傳區域變數的參考

```rust,compile_fail
fn make_greeting() -> &str {
    let s = String::from("哈囉");
    &s // 編譯錯誤！
} // s 在這裡被釋放了，回傳的參考指向一塊已經不存在的記憶體
#
# fn main() {}
```

這個比較好理解——`s` 離開函數就沒了，回傳它的參考毫無意義。Rust 直接擋掉。

### 問題二：多個參考，回傳哪一個？

但這個情況就比較複雜了：

```rust,compile_fail
fn longer(a: &str, b: &str) -> &str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}
#
# fn main() {}
```

這段程式碼也會編譯失敗。`a` 和 `b` 都是外面傳進來的參考，不會在函數結束時消失，那為什麼不行？

因為 Rust 在檢查**呼叫端**的時候，需要知道回傳值的參考能「活多久」。看這個例子：

```rust,ignore
# fn main() {
    let s1 = String::from("hello world");
    let result;
    {
        let s2 = String::from("hi");
        result = longer(&s1, &s2);
    } // s2 在這裡被釋放了
    println!("{}", result); // result 到底還能不能用？
# }
```

如果 `longer` 回傳了 `a`（也就是 `&s1`），`result` 是安全的，因為 `s1` 還活著。但如果回傳了 `b`（也就是 `&s2`），`result` 就是懸垂參考——`s2` 已經被釋放了。

問題是：**編譯器在檢查 `longer` 的呼叫端時，不會去看 `longer` 的函數體**。它只看函數簽名。而簽名上寫 `-> &str`，沒有任何資訊告訴它回傳值和哪個參數的壽命有關。

### 生命週期標注 `'a`

解法是用生命週期標注，明確描述回傳值和參數的關係：

```rust,noplayground
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}
#
# fn main() {}
```

`'a` 是一個**生命週期參數**（和型別參數 `T` 類似，但用 `'` 開頭）。這段簽名告訴 Rust：「`a`、`b` 和回傳值都標注了同一個 `'a`。所以回傳值的壽命不能超過 `a` 和 `b` 中**較短**的那個。」注意生命週期參數和型別參數一樣寫在 `<>` 裡面。如果同時有生命週期和型別參數，**生命週期要寫在前面**：`fn foo<'a, T>(x: &'a T) -> &'a T`。

### 為什麼是較短的？

因為 `a` 和 `b` 共用同一個 `'a`，Rust 會取兩者的**交集**——也就是兩者都還活著的那段時間。

回到剛才的例子：

```rust,editable
# fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
#     if a.len() > b.len() {
#         a
#     } else {
#         b
#     }
# }
#
# fn main() {
    let s1 = String::from("hello world"); // s1 的壽命比較長
    let result;
    {
        let s2 = String::from("hi");      // s2 的壽命比較短
        result = longer(&s1, &s2);
        println!("{}", result);           // ✅ 這裡 s1 和 s2 都還活著
    } // s2 在這裡被釋放
    // println!("{}", result);            // ❌ 不行！'a 是取 s1 和 s2 的交集，s2 已經死了
# }
```

`'a` 被推斷為 `s2` 的壽命（較短的那個），所以 `result` 只能在 `s2` 還活著的範圍內使用。

### `&'a mut T`

可變參考也可以加生命週期標注，寫成 `&'a mut T`——就是把 `'a` 放在 `&` 和 `mut` 之間。`'a` 一樣描述這個參考能活多久。

```rust,noplayground
fn replace<'a>(target: &'a mut String, new_value: &str) {
    target.clear();
    target.push_str(new_value);
}
#
# fn main() {}
```

### 生命週期不改變壽命

**重要觀念**：生命週期標注不會讓任何參考活得更久或更短。它只是**描述**已有的關係，幫助編譯器做檢查。就像型別標注不會改變值的內容一樣。

### 不是所有函數都要標

如果函數只有一個參考參數，Rust 通常能自動推斷（下一集會詳細講）：

```rust,noplayground
fn first_char(s: &str) -> &str {
    &s[..1] // 回傳值的壽命顯然和 s 一樣，不用手動標
}
#
# fn main() {}
```

### `'static` 生命週期

有一個特殊的生命週期：`'static`，表示「活到程式結束」。

字串字面值就是 `'static`——`"hello"` 的型別是 `&'static str`，因為字串字面值被寫死在程式碼裡，整個程式執行期間都存在。

## 範例程式碼

```rust,editable
// 回傳借用時，需要標注生命週期
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}

// 回傳值只和 a 有關，b 不影響
fn always_first<'a>(a: &'a str, _b: &str) -> &'a str {
    a
}

fn main() {
    // 例子一：兩個參數壽命一樣長
    let s1 = String::from("很長的字串");
    let s2 = String::from("短");
    let result = longer(&s1, &s2);
    println!("比較長的是：{}", result);

    // 例子二：兩個參數壽命不同
    let s3 = String::from("hello world");
    let r;
    {
        let s4 = String::from("hi");
        r = longer(&s3, &s4);
        println!("在作用域內：{}", r); // ✅ s3 和 s4 都還活著
    }
    // println!("{}", r); // ❌ 編譯錯誤！s4 已經被釋放，r 的生命週期不夠長

    // 例子三：回傳值只借用其中一個參數
    let s5 = String::from("我會被回傳");
    let r2;
    {
        let s6 = String::from("我不會");
        r2 = always_first(&s5, &s6);
    }
    // r2 只借用 s5，所以即使 s6 被釋放也沒關係
    println!("{}", r2); // ✅ s5 還活著，r2 可以用

    // 'static 生命週期
    let s: &'static str = "我是靜態字串，活到程式結束";
    println!("{}", s);
}
```

## 重點整理

- 當函數回傳借用時，Rust 需要知道回傳值能活多久——這就是生命週期標注的目的
- `'a` 是生命週期參數，描述參考之間的壽命關係
- 多個參數共用同一個 `'a` 時，Rust 取交集（較短的那個）
- 生命週期標注**不改變壽命**，只是描述已有的關係
- `'static` 表示「活到程式結束」——字串字面值的型別是 `&'static str`
