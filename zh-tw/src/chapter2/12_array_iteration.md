# 陣列走訪

## 本集目標

用 `for` 迴圈走過陣列裡的每一個元素。

## 正文

上一集我們學了怎麼用 `arr[0]`、`arr[1]` 一個一個取值。但如果陣列有 100 個元素，總不能寫 100 行吧？這時候就要用 `for` 迴圈來**走訪**（iterate）整個陣列。

### 基本語法

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];

    for x in arr {
        println!("{}", x);
    }
}
```

`for x in arr` 的意思是：「把 `arr` 裡的元素一個一個拿出來，每次放進 `x`，然後執行大括號裡的程式碼。」

### 幫元素做運算

```rust,editable
fn main() {
    let scores = [80, 95, 72, 88, 100];

    for score in scores {
        if score >= 90 {
            println!("{} 分 → 優秀！", score);
        } else {
            println!("{} 分 → 加油！", score);
        }
    }
}
```

### 加總所有元素

```rust,editable
fn main() {
    let arr = [1, 2, 3, 4, 5];
    let mut total = 0;

    for x in arr {
        total += x;
    }

    println!("總和：{}", total);
}
```

先用 `let mut total = 0;` 建立一個可變的累加器，每次迴圈把值加上去。

### `for` `in` range vs `for` `in` 陣列

第 1 章學的 `for i in 0..5` 是走訪一個**數字範圍**。這集的 `for x in arr` 是走訪一個**陣列**。語法一樣，只是 `in` 後面放的東西不同：

```rust,editable
fn main() {
    let arr = [10, 20, 30];

    // 走訪數字範圍：i 依序是 0, 1, 2
    for i in 0..3 {
        println!("索引 {}：{}", i, arr[i]);
    }

    // 走訪陣列：x 依序是 10, 20, 30
    for x in arr {
        println!("值：{}", x);
    }
}
```

走訪陣列時用 `for x in arr` 比用索引更簡潔、更安全、也更快速——不用擔心索引越界。需要同時拿到索引和值的時候，之後會學到更好的方式。

## 重點整理

- `for x in arr { ... }` 走訪陣列的每個元素
- 可以在迴圈裡對每個元素做運算、判斷、累加
- `for x in arr`（走訪陣列）和 `for i in 0..n`（走訪範圍）語法一樣，差在 `in` 後面的東西
- 走訪陣列時用 `for x in arr` 比用索引更簡潔、更安全、也更快速
