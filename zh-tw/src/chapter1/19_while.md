# `while`

## 本集目標

用 `while` 迴圈改寫倒數計時，對比 `loop` + `break` 的寫法。

## 正文

上一集我們用 `loop` + `break` 做了倒數計時。今天來學另一種迴圈——`while`，它讓同樣的邏輯寫起來更乾淨。

### 用 `while` 改寫倒數計時

```rust,editable
fn main() {
    let mut count = 5;
    while count > 0 {
        println!("{}", count);
        count -= 1;
    }
    println!("發射！");
}
```

結果一模一樣！

### 跟 `loop` + `break` 比一下

上一集的寫法：

```rust,editable
fn main() {
    let mut count = 5;
    loop {
        if count == 0 {
            println!("發射！");
            break;
        }
        println!("{}", count);
        count -= 1;
    }
}
```

`while` 的寫法：

```rust,editable
fn main() {
    let mut count = 5;
    while count > 0 {
        println!("{}", count);
        count -= 1;
    }
    println!("發射！");
}
```

有看出差別嗎？`while` 把「條件判斷」和「迴圈」合在一起了。不需要自己寫 `if` 和 `break`，只要告訴 `while`：「一旦這個條件成立，就繼續跑。」

### `while` 的白話文

> **當**條件成立的時候，就一直做大括號裡的事。

`while count > 0` → 只要 `count` 大於 0，就繼續跑。`count` 一旦變成 0，條件不成立了，就自動停下來。

### 什麼時候用 `loop`，什麼時候用 `while`？

- **`while`**：你在迴圈開始前就知道要不要繼續（先檢查條件，再決定要不要跑）
- **`loop` + `break`**：你需要在迴圈中間某個地方才能決定要不要停下來

兩種都可以達成目的，只是 `while` 在很多情況下寫起來更簡潔。

## 重點整理

- `while` 迴圈：只要條件成立就一直跑，條件不成立就自動停
- 比 `loop` + `break` 更簡潔，適合在迴圈開始前就知道要不要繼續的情況
- `loop` + `break` 適合在迴圈中間才能決定要不要停的情況
