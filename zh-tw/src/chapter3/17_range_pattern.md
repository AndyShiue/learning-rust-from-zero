# range pattern

## 本集目標

學會在 `match` 裡用範圍來比對數值。

## 概念說明

之前學 `match` 的時候，我們都是一個一個值去比對。但如果想比對「1 到 5 之間的任何數字」呢？總不能寫五個分支吧。

Rust 提供了 **range pattern**，讓你在 `match` 裡用範圍來比對：

```rust,editable
fn main() {
    let score = 12;
    match score {
        1..=5 => println!("低分"),
        _ => {}
    }
}
```

`1..=5` 代表 1、2、3、4、5（包含頭尾）。這個 `..=` 和第 1 章學的 `for i in 0..=5` 是差不多的意思。

除了 `..=`（包含結尾），也可以用 `..`（不包含結尾）：

```rust,editable
fn main() {
    let score = 65;
    match score {
        0..50 => println!("不及格"),  // 0 到 49
        50..=100 => println!("及格"), // 50 到 100（包含）
        _ => {}
    }
}
```

### 注意：兩種 `..` 不要搞混！

上一集的 `..` 和這一集的 `..` 長得一模一樣，但意義完全不同：

- **上一集**：`Point { x, .. }` → 忽略剩餘欄位，`..` 代表「其他我不管了」
- **這一集**：`0..50` → 數值範圍，`..` 代表「從某個數到某個數」

Rust 編譯器會根據前後文判斷是哪一種，不會搞混。但初學時要注意分辨。

### 單邊範圍

range pattern 也支援只寫一邊：

```rust,editable
fn main() {
    let temperature = 25;
    match temperature {
        ..0 => println!("零下"),        // 小於 0
        0..=30 => println!("普通"),     // 0 到 30
        31.. => println!("很熱"),       // 31 以上
    }
}
```

### `char` 也能用

range pattern 不只能用在數字，也能用在 `char`：

```rust,editable
fn main() {
    let c = '哼';
    match c {
        'a'..='z' => println!("小寫英文字母"),
        'A'..='Z' => println!("大寫英文字母"),
        '0'..='9' => println!("數字"),
        _ => println!("其他字元"),
    }
}
```

## 範例程式碼

```rust,editable
fn main() {
    // 用 range pattern 判斷分數等級
    let score = 78;

    match score {
        90..=100 => println!("A"),
        80..90 => println!("B"),
        70..80 => println!("C"),
        60..70 => println!("D"),
        0..60 => println!("F"),
        _ => println!("分數超出範圍"),
    }

    // 單邊範圍
    let temperature = -5;

    match temperature {
        ..0 => println!("零下，很冷！"),
        0..=35 => println!("還可以"),
        36.. => println!("太熱了！"),
    }

    // char 的 range pattern
    let c = 'G';

    match c {
        'a'..='z' => println!("'{}' 是小寫字母", c),
        'A'..='Z' => println!("'{}' 是大寫字母", c),
        '0'..='9' => println!("'{}' 是數字", c),
        _ => println!("'{}' 是其他字元", c),
    }
}
```

## 重點整理

- `..` 和 `..=` 除了能用在 `for` 迴圈上，還能用來當作 pattern
- `1..=5` → 包含頭尾（1, 2, 3, 4, 5）
- `0..50` → 包含頭、不包含尾（0 到 49）
- `..0` → 小於 0；`31..` → 31 以上（單邊範圍）
- `char` 也能用 range pattern：`'a'..='z'`
- 這裡的 `..` 是「數值範圍」，和上一集忽略欄位的 `..` 是不同的東西，不要搞混
