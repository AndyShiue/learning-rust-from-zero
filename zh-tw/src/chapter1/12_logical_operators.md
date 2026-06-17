# 邏輯運算子

## 本集目標

學會用 `&&`（而且）、`||`（或者）、`!`（不是）來組合多個條件。

## 正文

上幾集我們學了 `if`，但條件都很簡單——只有一個。現實中常常需要同時考慮好幾個條件，比如「年滿 18 歲**而且**是學生」。這就需要邏輯運算子。

### `&&` —— 而且（AND）

兩個條件**都要成立**，結果才是 `true`：

```rust,editable
fn main() {
    let age = 24;
    let is_student = true;

    if age >= 18 && is_student {
        println!("是個成年學生");
    }
}
```

因為 24 >= 18 是 `true`，`is_student` 也是 `true`，兩個都成立，所以整體是 `true`。

如果把 `age` 改成 15，15 >= 18 是 `false`，不管 `is_student` 是不是 `true`，整體就是 `false`，就不會印了。

### `||` —— 或者（OR）

只要**其中一個**條件成立，結果就是 `true`：

```rust,editable
fn main() {
    let is_weekend = false;
    let is_holiday = true;

    if is_weekend || is_holiday {
        println!("今天放假！");
    }
}
```

雖然 `is_weekend` 是 `false`，但 `is_holiday` 是 `true`，只要有一個是 `true` 就夠了。

### `!` —— 不是（NOT）

把 `true` 變成 `false`，把 `false` 變成 `true`：

```rust,editable
fn main() {
    let raining = false;

    if !raining {
        println!("出門走走吧！");
    }
}
```

`raining` 是 `false`，加上 `!` 之後就變成 `true`，所以條件成立。

你可以讀成：「如果**沒有**在下雨，就出門走走。」

## 重點整理

- `&&`（而且）：兩邊都為 `true` 才是 `true`
- `||`（或者）：只要一邊為 `true` 就是 `true`
- `!`（不是）：把 `true` 變 `false`，`false` 變 `true`
- 用邏輯運算子組合多個條件，寫出更精確的判斷
