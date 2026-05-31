# `match` guard

## 本集目標

學會在 `match` 分支加上額外的條件判斷（guard）。

## 概念說明

有時候光靠模式匹配還不夠，你還需要加上一些額外的條件。比如說，你想用 `match` 判斷一個數是奇數還是偶數——這沒辦法用 range pattern 或固定值表達，因為它需要做運算（`% 2`）。

Rust 的 **`match` guard** 讓你在模式後面加上 `if 條件`：

```rust,editable
# fn main() {
    let n = 137;
    match n {
        x if x % 2 == 0 => println!("{} 是偶數", x),
        x => println!("{} 是奇數", x),
    }
# }
```

`x if x % 2 == 0` 的意思是「先把值綁定到 `x`，然後額外檢查 `x % 2 == 0` 是否成立」。只有模式匹配**而且** guard 條件為 `true` 的時候，這個分支才會被執行。

注意：guard 不算在「窮舉」的判斷裡。就算你寫了所有可能的 guard，Rust 可能還是會要求你加 `_` 預設分支。

## 範例程式碼

```rust,editable
fn main() {
    let n = 8;

    match n {
        x if x % 2 == 0 => println!("{} 是偶數", x),
        x => println!("{} 是奇數", x),
    }

    // 搭配 tuple 使用
    let point = (3, 7);

    match point {
        (x, y) if x == y => println!("在對角線上：({}, {})", x, y),
        (x, y) if x > 0 && y > 0 => println!("({}, {}) 在第一象限", x, y),
        (x, y) => println!("其他的點 ({}, {})", x, y),
    }
}
```

## 重點整理

- `match` guard：在模式後面加 `if 條件` 做額外判斷
- 語法：`模式 if 條件 => ...`
- 只有模式匹配**且**條件為 `true` 時，分支才會執行
- guard 可以使用模式裡綁定的變數（如 `x if x > 0`）
- guard 條件不算窮舉，通常最後還是要加 `_` 預設分支
