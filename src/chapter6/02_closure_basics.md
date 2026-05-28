# 閉包用法展示

## 本集目標

學會閉包的基本語法，了解閉包如何捕捉外部變數，並看到標準庫中使用閉包的實際案例。

## 概念說明

### 閉包的語法

上一集的函數指標很好用，但有個限制：它不能使用呼叫處的區域變數。閉包（closure）就是為了解決這個問題而存在的。

閉包的基本語法用 `|` 來包參數：

```rust,ignore
# fn main() {
    let add_one = |x| x + 1;
# }
```

你也可以加上型別標註，跟函數一樣明確：

```rust,noplayground
# fn main() {
    let add_one = |x: i32| -> i32 { x + 1 };
# }
```

呼叫閉包的方式和呼叫一般函數一樣，直接用 `add_one(5)` 就好了——不需要任何特殊語法。

### 什麼時候要加大括號？

規則很簡單：

- **只有一個表達式**的時候，可以省略大括號：`|x| x + 1`
- **有多行程式碼**或**需要 `let` 之類語句**的時候，要用大括號包起來：

```rust,noplayground
# fn main() {
    let process = |x: i32| {
        let doubled = x * 2;
        println!("計算中：{}", doubled);
        doubled + 1
    };
# }
```

跟函數一樣，大括號裡最後一行不加分號就是回傳值。

另外，如果有加型別標註（`-> i32`），就一定要加大括號：

```rust,noplayground
# fn main() {
    let add_one = |x: i32| -> i32 { x + 1 }; // 有 -> 就必須有 {}
    let add_one = |x: i32| x + 1;            // 沒有 -> 可以省略 {}
# }
```

### 閉包能捕捉外部變數

這是閉包和函數指標最大的差別：

```rust,editable
# fn main() {
    let offset = 10;
    let add_offset = |x| x + offset; // 捕捉了 offset
    println!("{}", add_offset(5));   // 15
# }
```

`add_offset` 這個閉包「記住」了外部的 `offset`，每次呼叫都會用到它。普通函數做不到這件事。

### 閉包不是只有一種

根據閉包**怎麼使用**捕捉到的變數，Rust 會把閉包分成不同的種類——有些閉包只能呼叫一次，有些可以呼叫很多次。這一集先看兩個例子感受一下差別，下幾集再深入解釋。

### `Result` 的 `map` —— `FnOnce` 的例子

標準庫很多方法都接受閉包。還記得第 5 章的 `Result<T, E>` 嗎？它有一個 `map` 方法，可以把 `Ok` 裡的值做轉換。`map` 只需要呼叫閉包一次，所以它接受 `FnOnce`——「至少能呼叫一次」就夠了。

這意味著你可以傳一個**會消耗捕捉到的變數**的閉包給它：

```rust,editable
# fn main() {
    let prefix = String::from("結果是：");
    let result: Result<i32, String> = Ok(42);
    let message = result.map(|x| {
        // prefix 被 move 進來，這個閉包只能呼叫一次
        let mut s = prefix; // move！
        s.push_str(&x.to_string());
        s
    });
    println!("{:?}", message); // Ok("結果是：42")
# }
```

這個閉包把 `prefix` move 進來了，呼叫一次之後 `prefix` 就沒了。但沒關係，`map` 本來就只呼叫接收的函數一次。

### `Vec` 的 `retain` —— `FnMut` 的例子

`Vec<T>` 的 `retain` 方法會保留符合條件的元素，移除不符合的。它接受一個閉包，這個閉包接收 `&T`（每個元素的參考）、回傳 `bool`（`true` 保留、`false` 移除）。因為 `retain` 要對每個元素都呼叫一次，所以它要求 `FnMut`——「可以多次呼叫」。

你可以傳一個**會修改捕捉到的變數**的閉包：

```rust,editable
# fn main() {
    let mut numbers = vec![1, 2, 3, 4, 5, 6];
    let mut removed_count = 0;
    numbers.retain(|x| {
        if x % 2 == 0 {
            true // 保留偶數
        } else {
            removed_count += 1; // 修改外部變數
            false
        }
    });
    println!("{:?}，移除了 {} 個", numbers, removed_count);
    // [2, 4, 6]，移除了 3 個
# }
```

這個閉包每次被呼叫都會修改 `removed_count`——它是 `FnMut`。注意它沒有 move 任何東西（只是透過 `&mut` 修改外部變數），所以可以被呼叫很多次。

### 如果把 `FnOnce` 傳給 `retain`？

上面傳給 `Result` 的 `map` 那種會 move 變數的閉包能傳給 `retain` 嗎？

```rust,compile_fail
# fn main() {
    let mut items = vec![1, 2, 3];
    let header = String::from("剔除：");
    items.retain(|x| {
        if *x <= 1 {
            let mut log = header; // move header
            log.push_str(&x.to_string());
            log.push(' ');
        }
        *x > 1
    }); // 編譯錯誤！
# }
```

這個閉包在第一次剔除元素時就把 `header` move 走了，第二次要剔除時 `header` 已經不存在。它只能呼叫一次（`FnOnce`），但 `retain` 需要多次呼叫（`FnMut`）。所以編譯器會報錯。

### 不捕捉變數的閉包 → 可以轉成函數指標

如果一個閉包沒有捕捉任何外部變數，它就跟普通函數沒什麼差別。Rust 允許它自動轉型成函數指標 `fn`：

```rust,noplayground
# fn main() {
    let add_one: fn(i32) -> i32 = |x| x + 1; // 沒有捕捉，可以轉成 fn
# }
```

但如果捕捉了外部變數，就不能這樣轉了。

## 範例程式碼

```rust,editable
fn apply_fn_pointer(f: fn(i32) -> i32, value: i32) -> i32 {
    f(value)
}

fn main() {
    // 基本閉包語法
    let square = |x: i32| -> i32 { x * x };
    println!("square(4) = {}", square(4));

    // 捕捉外部變數
    let base = 100;
    let add_base = |x| x + base;
    println!("add_base(7) = {}", add_base(7));

    // Result 的 map（FnOnce）
    let result: Result<i32, String> = Ok(21);
    let doubled = result.map(|x| x * 2);
    println!("doubled = {:?}", doubled);

    let err_result: Result<i32, String> = Err(String::from("oops"));
    let still_err = err_result.map(|x| x * 2);
    println!("still_err = {:?}", still_err);

    // Vec 的 retain（FnMut）
    let mut scores = vec![55, 72, 88, 43, 91, 60];
    scores.retain(|s| *s >= 60);
    println!("及格分數：{:?}", scores);

    // 不捕捉變數的閉包可以轉成函數指標
    let triple: fn(i32) -> i32 = |x| x * 3;
    println!("apply_fn_pointer(triple, 5) = {}", apply_fn_pointer(triple, 5));

    // 捕捉了變數的閉包不能轉成函數指標
    // let offset = 10;
    // let bad: fn(i32) -> i32 = |x| x + offset; // 編譯錯誤！
}
```

## 重點整理

- 閉包用 `|參數| 表達式` 語法，可以省略型別標註讓 Rust 推導
- 閉包最大的特色是能**捕捉外部變數**，這是函數指標做不到的
- `Result` 的 `map` 接受 `FnOnce` 閉包——只需呼叫一次
- `Vec` 的 `retain` 接受 `FnMut` 閉包——需要多次呼叫
- 如果閉包只能呼叫一次（`FnOnce`），就不能傳給需要多次呼叫的方法
- 不捕捉外部變數的閉包可以自動轉型成函數指標 `fn`
