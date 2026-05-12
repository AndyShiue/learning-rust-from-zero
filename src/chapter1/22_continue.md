# `continue`

## 本集目標

用 `continue` 跳過迴圈中的某些輪次。

## 正文

之前學了 `break` 可以跳出迴圈。今天來學 `continue`——它不是跳出迴圈，而是**跳過這一次，直接進入下一次迴圈**。

### 只印奇數

```rust
fn main() {
    for i in 0..10 {
        if i % 2 == 0 {
            continue;
        }
        println!("{}", i);
    }
}
```

### 它是怎麼運作的？

迴圈 `i` 從 0 跑到 9：

- `i = 0` → `0 % 2 == 0` 嗎？是（偶數），`continue`！跳過，不印
- `i = 1` → `1 % 2 == 0` 嗎？不是（奇數），繼續往下跑，印出 1
- `i = 2` → 偶數，`continue`，跳過
- `i = 3` → 奇數，印出 3
- ……以此類推

### `break` vs `continue`

- **`break`**：整個迴圈結束，不再跑了
- **`continue`**：這一次跳過，但迴圈繼續跑下一次

和 `break` 一樣，`continue` 也是只作用在**迴圈**上，不會跳過 `if` 之類的控制結構。上面的程式碼裡，`continue` 是跳過 `for` 迴圈的這一次，不是跳過 `if`。

### 另一個例子

跳過 5 不印：

```rust
fn main() {
    for i in 1..=10 {
        if i == 5 {
            continue;
        }
        println!("{}", i);
    }
}
```

5 被跳過了，其他都正常印出來。

### continue + loop label

上一集學過 `break 'outer` 可以跳出指定層迴圈，`continue` 也可以搭配 label：

```rust
fn main() {
    'outer: for i in 1..=3 {
        for j in 1..=3 {
            if j == 2 {
                continue 'outer; // 跳過外層迴圈的這一次
            }
            println!("i={}, j={}", i, j);
        }
    }
}
```

每次 `j` 到 2，就 `continue 'outer` 直接跳到外層的下一輪，所以 `j=2` 和 `j=3` 都不會印。

## 重點整理

- `continue` 跳過這一次，直接進入下一次迴圈
- `break` 是「整個迴圈不跑了」，`continue` 是「這次跳過，跑下一次」
- 搭配 `if` 可以有選擇性地跳過特定情況
- `continue 'outer` 可以搭配 loop label 跳過外層迴圈的一輪
