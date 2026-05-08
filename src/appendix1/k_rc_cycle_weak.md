# Rc 迴圈與 Weak

## 本集目標

理解 `Rc` 參考迴圈會造成記憶體洩漏，並學會用 `Weak` 來打破迴圈。

> 本集是**第五章**的補充。

## 概念說明

還記得第五章學的 `Rc<T>` 嗎？它透過參考計數來管理記憶體——每多一個 `Rc` 指向同一筆資料，計數就加一；每少一個就減一；歸零時釋放記憶體。

聽起來很完美，但有一個致命弱點：**參考迴圈（reference cycle）**。

### 什麼是參考迴圈？

想像 A 持有 `Rc` 指向 B，B 也持有 `Rc` 指向 A。當我們不再需要它們的時候：

1. A 的 `Rc` 被 drop → A 的計數減一，但 B 還在指向 A → 計數不為零 → A 不釋放
2. B 的 `Rc` 被 drop → B 的計數減一，但 A 還在指向 B → 計數不為零 → B 不釋放

結果：A 和 B **永遠不會被釋放**，這就是記憶體洩漏。

### Weak 救場

`Weak<T>` 是一種「弱參考」——它指向同一筆資料，但**不會增加強參考計數（strong count）**。這意味著 `Weak` 不會阻止資料被釋放。

用法：

```rust,no_run
use std::rc::{Rc, Weak};

fn main() {
    let strong = Rc::new(42);
    let weak: Weak<i32> = Rc::downgrade(&strong);
}
```

`Rc::downgrade` 把 `Rc` 降級成 `Weak`。

為什麼 `downgrade` 不會增加 strong count？因為 Rc 內部有**兩個**計數器：strong count 和 weak count。`clone()` 增加 strong count，`downgrade()` 只增加 weak count。而 Rc 判斷「要不要釋放值」只看 strong count——strong count 歸零就釋放，不管 weak count 是多少。這就是 `Weak` 不會阻止釋放的原因。

### 使用 Weak 的值

因為 `Weak` 指向的資料可能已經被釋放了（strong count 歸零），所以你不能直接存取。必須先 `upgrade()`：

```rust,ignore
    match weak.upgrade() {
        Some(rc) => println!("還在：{}", rc),
        None => println!("已經被釋放了"),
    }
```

`upgrade()` 回傳 `Option<Rc<T>>`——如果資料還在，給你一個 `Rc`；如果已經釋放，回傳 `None`。

### 用 Weak 打破迴圈

回到剛才 A 和 B 的例子：只要把其中一個方向改成 `Weak`，就能打破迴圈。通常的做法是：

- 父 → 子：用 `Rc`（父親擁有子女）
- 子 → 父：用 `Weak`（子女知道父親存在，但不擁有）

這樣當外部的 `Rc` 都 drop 之後，strong count 能夠正常歸零，記憶體就能正確釋放。

## 範例程式碼

```rust
use std::rc::Rc;

fn main() {
    // ===== 基本 Weak 用法 =====
    let strong = Rc::new(String::from("Hello"));
    println!("strong count = {}", Rc::strong_count(&strong));

    let weak = Rc::downgrade(&strong);
    println!("strong count = {}", Rc::strong_count(&strong)); // 還是 1
    println!("weak count = {}", Rc::weak_count(&strong));     // 1

    // upgrade：Weak → Option<Rc<T>>
    match weak.upgrade() {
        Some(rc) => println!("upgrade 成功：{}", rc),
        None => println!("已被釋放"),
    }

    // drop 強參考
    drop(strong);

    // 再次 upgrade
    match weak.upgrade() {
        Some(rc) => println!("upgrade 成功：{}", rc),
        None => println!("已被釋放——strong 沒了，Weak 也拿不到了"),
    }

    // ===== Weak 的生命週期 =====
    let weak_ref;
    {
        let temporary = Rc::new(100);
        weak_ref = Rc::downgrade(&temporary);
        println!("scope 內 upgrade：{:?}", weak_ref.upgrade()); // Some(100)
    }
    // temporary 已被 drop
    println!("scope 外 upgrade：{:?}", weak_ref.upgrade()); // None
}
```

## 重點整理

- `Rc` 的參考迴圈會造成記憶體洩漏——計數永遠不會歸零，記憶體永遠不會釋放
- `Rc::downgrade(&rc)` 建立 `Weak<T>`，**不增加 strong count**
- `weak.upgrade()` 回傳 `Option<Rc<T>>`——資料還在就給你 `Some(rc)`，被釋放了就是 `None`
- 用 `Weak` 打破迴圈的常見模式：強方向用 `Rc`，反向用 `Weak`
- 典型應用：樹狀結構中「父 → 子」用 `Rc`，「子 → 父」用 `Weak`
- `Rc::strong_count()` 和 `Rc::weak_count()` 可以查看目前的計數
