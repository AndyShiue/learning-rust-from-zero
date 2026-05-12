# `Iterator` `trait`

## 本集目標

認識 `Iterator` `trait` 的核心——只要實作 `next` 方法，就能免費獲得數十個好用的方法。

## 概念說明

### Iterator 的定義

`Iterator` `trait` 的核心簡單到不行：

```rust,noplayground
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}
#
# fn main() {}
```

就這樣。只有一個必須實作的方法 `next`，它每次被呼叫就回傳：

- `Some(值)` —— 還有下一個元素
- `None` —— 迭代結束了

還記得第五章學的 associated type 嗎？`type Item` 就是一個 associated type，代表「這個迭代器產出的元素型別」。

### 手動呼叫 `next`

你可以直接手動呼叫 `.next()` 來逐一取得元素：

```rust
# fn main() {
    let v = vec![10, 20, 30];
    let mut iter = v.iter();

    println!("{:?}", iter.next()); // Some(&10)
    println!("{:?}", iter.next()); // Some(&20)
    println!("{:?}", iter.next()); // Some(&30)
    println!("{:?}", iter.next()); // None
# }
```

注意 `iter` 必須是 `mut` 的，因為每次呼叫 `.next()` 都會推進內部狀態。

### 只需實作 `next`，其他方法免費送

`Iterator` `trait` 提供了大量的**預設實作**（還記得第五章嗎？）。因為所有的迭代操作本質上都是「不斷呼叫 `next` 直到 `None`」，所以只要你實作了 `next`，像 `map`、`filter`、`count`、`sum` 等幾十個方法全部自動可用。

### 自訂 `Iterator`

讓我們自己做一個迭代器。假設我們想要一個「倒數計時器」：

```rust,noplayground
struct Countdown {
    value: i32,
}

impl Iterator for Countdown {
    type Item = i32;

    fn next(&mut self) -> Option<i32> {
        if self.value > 0 {
            let current = self.value;
            self.value -= 1;
            Some(current)
        } else {
            None
        }
    }
}
#
# fn main() {}
```

只要實作了 `next`，`map`、`filter`、`sum`、`collect` 等幾十個方法全部自動可用。這些方法接下來幾集會陸續學到。

### 標準庫的迭代器工廠

標準庫提供了一些方便的函數來建立迭代器：

- `std::iter::repeat(value)` —— 無限重複同一個值
- `std::iter::from_fn(closure)` —— 用閉包來決定每次 `.next()` 回傳什麼

```rust
use std::iter;

fn main() {
    // 無限產生 42
    let mut repeater = iter::repeat(42);
    println!("{:?}", repeater.next()); // Some(42)
    println!("{:?}", repeater.next()); // Some(42)（永遠不會 None）

    // 用閉包產生遞增數字
    let mut n = 0;
    let mut counter = iter::from_fn(move || {
        n += 1;
        Some(n)
    });
    println!("{:?}", counter.next()); // Some(1)
    println!("{:?}", counter.next()); // Some(2)
}
```

注意 `repeat` 和 `from_fn` 產生的迭代器可能是**無限的**——永遠不會回傳 `None`。第 15 集會深入討論這個特性。

## 範例程式碼

```rust
use std::iter;

// 自訂迭代器：費氏數列（無限！）
struct Fibonacci {
    a: u64,
    b: u64,
}

impl Fibonacci {
    fn new() -> Fibonacci {
        Fibonacci { a: 0, b: 1 }
    }
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<u64> {
        let current = self.a;
        let new_b = self.a + self.b;
        self.a = self.b;
        self.b = new_b;
        Some(current) // 永遠不回傳 None
    }
}

fn main() {
    // 手動呼叫 Vec 的 iter().next()
    let names = vec!["Alice", "Bob", "Charlie"];
    let mut name_iter = names.iter();
    println!("第一個：{:?}", name_iter.next());
    println!("第二個：{:?}", name_iter.next());
    println!("第三個：{:?}", name_iter.next());
    println!("結束了：{:?}", name_iter.next());

    // 自訂 Iterator：費氏數列（手動呼叫 next）
    println!("\n費氏數列：");
    let mut fib = Fibonacci::new();
    println!("{:?}", fib.next()); // Some(0)
    println!("{:?}", fib.next()); // Some(1)
    println!("{:?}", fib.next()); // Some(1)
    println!("{:?}", fib.next()); // Some(2)
    println!("{:?}", fib.next()); // Some(3)
    println!("{:?}", fib.next()); // Some(5)
    // 永遠不會 None——這是一個無限迭代器

    // std::iter::repeat：無限重複
    let mut threes = iter::repeat(3);
    println!("\nrepeat(3)：");
    println!("{:?}", threes.next()); // Some(3)
    println!("{:?}", threes.next()); // Some(3)
    println!("{:?}", threes.next()); // Some(3)（永遠不會 None）

    // std::iter::from_fn：用閉包控制產出
    let mut n = 0;
    let mut squares = iter::from_fn(|| {
        n += 1;
        if n <= 3 {
            Some(n * n)
        } else {
            None
        }
    });
    println!("\nfrom_fn（前 3 個平方數）：");
    println!("{:?}", squares.next()); // Some(1)
    println!("{:?}", squares.next()); // Some(4)
    println!("{:?}", squares.next()); // Some(9)
    println!("{:?}", squares.next()); // None
}
```

## 重點整理

- `Iterator` `trait` 的核心是 `next(&mut self) -> Option<Self::Item>`
- 只需實作 `.next()`，就能免費獲得數十個預設實作（接下來會陸續學到）
- 自己幫型別實作 `Iterator` 很簡單——定義 `type Item` 和 `next` 就好
- `std::iter::repeat(value)` 建立無限重複的迭代器
- `std::iter::from_fn(closure)` 用閉包來控制每次產出的值
- 迭代器可以是無限的（永不回傳 `None`）
