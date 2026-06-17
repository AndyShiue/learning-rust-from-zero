# slice pattern

## 本集目標

學會用 slice pattern 解構陣列和切片。

## 概念說明

### 對陣列進行模式匹配

上一集我們學了如何解構 tuple，其實我們也可以對陣列和切片進行模式匹配！就是用 `[a, b, c]` 這種 slice pattern 來比對陣列的每個元素：

```rust,editable
fn main() {
    let rgb = [255, 128, 0];

    match rgb {
        [255, 0, 0] => println!("純紅色"),
        [0, 255, 0] => println!("純綠色"),
        [0, 0, 255] => println!("純藍色"),
        [r, g, b] => println!("自訂顏色：R={}, G={}, B={}", r, g, b),
    }
}
```

跟前面幾集很像，你可以在模式裡混用「固定的值」和「變數」。固定的值用來比對，變數用來接住資料。

### 切片也能用

不只固定長度的陣列，切片（`&[T]`）也能用 slice pattern。差別在於切片的長度在編譯期是未知的，所以你可以用不同長度的模式來匹配：

```rust,noplayground
fn describe(numbers: &[i32]) {
    match numbers {
        [] => println!("空的"),
        [x] => println!("只有一個元素：{}", x),
        [x, y] => println!("兩個元素：{} 和 {}", x, y),
        [x, y, z] => println!("三個元素：{}, {}, {}", x, y, z),
        _ => println!("超過三個元素"),
    }
}
#
# fn main() {}
```

固定長度的陣列永遠是固定的長度，像 `[i32; 3]` 的分支永遠不會匹配到 `[]` 或 `[x]`。切片才需要考慮不同長度的情況。

## 範例程式碼

```rust,editable
fn describe(data: &[i32]) {
    match data {
        [] => println!("空的切片"),
        [only] => println!("只有一個元素：{}", only),
        [first, second] => println!("兩個元素：{} 和 {}", first, second),
        _ => println!("有很多元素，第一個是 {}", data[0]),
    }
}

fn main() {
    // 固定長度陣列的 slice pattern
    let rgb = [255, 128, 0];

    match rgb {
        [255, 0, 0] => println!("純紅色"),
        [0, 255, 0] => println!("純綠色"),
        [0, 0, 255] => println!("純藍色"),
        [r, g, b] => println!("自訂顏色：R={}, G={}, B={}", r, g, b),
    }

    println!("---");

    // 切片的 slice pattern——可以匹配不同長度
    describe(&[]);
    describe(&[42]);
    describe(&[1, 2]);
    describe(&[10, 20, 30, 40, 50]);
}
```

## 重點整理

- 遇到陣列的時候，可以在 `match` 時用 `[a, b, c]` 這種 slice pattern，跟 tuple pattern 類似
- 切片 `&[T]` 長度不固定，可以用不同長度的模式來匹配（`[]`、`[x]`、`[x, y]`……）
