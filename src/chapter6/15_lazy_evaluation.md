# 惰性求值

## 本集目標

理解迭代器的惰性（lazy）本質——`.map(f)` 和 `.filter(pred)` 不會立刻執行，而是建立巢狀結構，等 `.collect()` 或 `for` 才逐一拉動。

## 概念說明

### 迭代器是惰性的

這可能是整個第 6 章最重要的概念：**迭代器的轉換方法不會立刻執行**。

```rust,editable
# fn main() {
    let v = vec![1, 2, 3, 4, 5];
    let iter = v.iter().map(|x| {
        println!("處理 {}", x);
        x * 2
    });
    // 到這裡為止，什麼都沒有印出來！
# }
```

`map` 並沒有「跑過」每個元素。它只是建立了一個新的迭代器結構，記錄了「等下要做什麼」。直到有人呼叫 `collect()`、`for`、`sum()` 等「消費」方法時，才會一個一個元素地拉動。

### 俄羅斯套娃

每次呼叫 `.map(f)` 或 `.filter(pred)`，你其實是在迭代器外面「套一層」。就像俄羅斯套娃：

```rust,noplayground
# fn main() {
#     let v = vec![2, 7, 1, 8, 2, 8];
    v.iter()                 // 最內層：原始迭代器
        .filter(|x| **x > 2) // 第二層：Filter 結構，存著 inner + 閉包
        .map(|x| x * 10);    // 第三層：Map 結構，存著 inner + 閉包
# }
```

每一層都是一個 `struct`，裡面存著內層的迭代器和自己的閉包。標準庫的 `Map` 和 `Filter` 大致長這樣：

```rust,noplayground
struct Map<I, F> {
    iter: I, // 內層迭代器
    f: F,    // 要套用的閉包
}

struct Filter<I, P> {
    iter: I,      // 內層迭代器
    predicate: P, // 過濾條件的閉包
}
#
# fn main() {}
```

它們的 `.next()` 實作也很直覺：

```rust,noplayground
# struct Map<I, F> {
#     iter: I, // 內層迭代器
#     f: F,    // 要套用的閉包
# }
#
# struct Filter<I, P> {
#     iter: I,      // 內層迭代器
#     predicate: P, // 過濾條件的閉包
# }
#
// Map 的 next()：從內層拿一個元素，套用閉包
impl<B, I: Iterator, F: FnMut(I::Item) -> B> Iterator for Map<I, F> {
    type Item = B;
    fn next(&mut self) -> Option<B> {
        let x = self.iter.next()?; // 問內層要一個元素
        Some((self.f)(x))          // 套用閉包回傳
    }
}

// Filter 的 next()：不斷從內層拿，直到找到符合條件的
impl<I: Iterator, P: FnMut(&I::Item) -> bool> Iterator for Filter<I, P> {
    type Item = I::Item;
    fn next(&mut self) -> Option<I::Item> {
        loop {
            let x = self.iter.next()?; // 問內層要一個元素
            if (self.predicate)(&x) {
                return Some(x);        // 符合條件，回傳
            }
            // 不符合，繼續問下一個
        }
    }
}
#
# fn main() {}
```

所以整條鏈就是一堆 `struct` 套在一起——呼叫最外層的 `.next()`，它去問內層，內層再問更內層，一路拉到最底。

### pull-based：一次只處理一個元素

當你呼叫 `.collect()` 或 `for` 迴圈時，最外層的迭代器開始「拉」：

1. 最外層（`Map`）問第二層（`Filter`）：「給我下一個元素」
2. Filter 問最內層（原始迭代器）：「給我下一個元素」
3. 最內層回傳 `Some(&1)`
4. Filter 檢查條件：`1 > 2`？不通過。再問一次。
5. 最內層回傳 `Some(&2)`
6. Filter 檢查：`2 > 2`？不通過。再問。
7. 最內層回傳 `Some(&3)`
8. Filter 檢查：`3 > 2`？通過！回傳給 Map。
9. Map 套用閉包：`3 * 10 = 30`，回傳 `Some(30)`

每個元素是**一路到底**處理完的——不像先做完所有 `filter`，再做所有 `map`。這意味著**中間不需要任何暫存的 `Vec`**。

### 無限迭代器

因為是惰性的，迭代器可以是**無限的**。`std::iter::repeat` 和 `std::iter::from_fn` 都可以產生永遠不回傳 `None` 的迭代器：

```rust,noplayground
use std::iter;

fn main() {
    // 永遠產出 1, 2, 3, 4, 5, ...
    let mut n = 0;
    let naturals = iter::from_fn(move || {
        n += 1;
        Some(n)
    });
}
```

這不會無窮迴圈，因為迭代器是惰性的——沒人呼叫 `.next()` 就什麼都不會發生。

### `.take(n)` 馴服無限迭代器

用 `.take(n)` 就能從無限迭代器中取出有限個元素：

```rust,noplayground
# use std::iter;
#
# fn main() {
#     // 永遠產出 1, 2, 3, 4, 5, ...
#     let mut n = 0;
#     let naturals = iter::from_fn(move || {
#         n += 1;
#         Some(n)
#     });
    let first_ten: Vec<i32> = naturals.take(10).collect();
    // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# }
```

這就是惰性求值的威力——你可以先描述一個「概念上無限」的計算，最後再決定要取多少。

### 不小心忘記消費？

因為迭代器是惰性的，如果你寫了 `.map(f)` 但忘記 `.collect()` 或 `for`，什麼事都不會發生。Rust 編譯器會發出警告：

```ignore
warning: unused `Map` that must be used
note: iterators are lazy and do nothing unless consumed
```

看到這個警告就知道：你忘了消費迭代器了。

## 範例程式碼

```rust,editable
use std::iter;

fn main() {
    // 惰性示範：map 不會立刻執行
    println!("--- 惰性示範 ---");
    let v = vec![1, 2, 3];
    let iter = v.iter().map(|x| {
        println!("  處理 {}", x);
        x * 2
    });
    println!("map 建立完了，但還沒執行...");
    println!("現在開始 collect：");
    let result: Vec<i32> = iter.collect();
    println!("結果：{:?}", result);

    // pull-based：filter + map 一次處理一個元素
    println!("\n--- Pull-based 示範 ---");
    let data = vec![1, 2, 3, 4, 5, 6];
    let processed: Vec<i32> = data
        .iter()
        .filter(|&&x| {
            println!("  filter 檢查 {}", x);
            x % 2 == 0
        })
        .map(|&x| {
            println!("  map 處理 {}", x);
            x * 10
        })
        .collect();
    println!("結果：{:?}", processed);
    // 注意印出的順序！filter 和 map 是交替執行的

    // from_fn 建立無限迭代器（取前 10 個質數）
    let mut candidate = 1;
    let primes: Vec<i32> = iter::from_fn(move || {
        loop {
            candidate += 1;
            let is_prime = (2..candidate).into_iter().all(|d| candidate % d != 0);
            if is_prime {
                return Some(candidate);
            }
        }
    })
    .take(10)
    .collect();
    println!("\n前 10 個質數：{:?}", primes);

    // 不需要中間 Vec——全部在一條管道裡
    println!("\n--- 零中間 Vec ---");
    let sum_of_even_squares: i32 = (1..=100)
        .into_iter()
        .filter(|x| x % 2 == 0)
        .map(|x| x * x)
        .sum();
    println!("1~100 偶數的平方和：{}", sum_of_even_squares);
    // 沒有任何中間的 Vec 被建立，全部是一次一個元素處理完的
}
```

## 重點整理

- 迭代器的 `.map(f)` / `.filter(pred)` 等方法是**惰性的**，不會立刻執行
- 每次呼叫轉換方法都是在外面「套一層」`struct`（俄羅斯套娃）
- 消費（`.collect()`、`for`、`.sum()` 等）才會觸發執行
- 執行方式是 **pull-based**——一次拉一個元素，完整通過所有層，不需要中間 `Vec`
- 因為惰性，迭代器可以是**無限的**
- 用 `.take(n)` 從無限迭代器中取出有限個元素
- 忘記消費迭代器的話，編譯器會發出警告提醒你

恭喜你完成了第 6 章！🎉 從函數指標到閉包的三種 `Fn` `trait`，再到迭代器的惰性求值——這一章結合了所有權、`trait`、泛型等前面學過的概念，展現了 Rust 函數式程式設計的威力。你現在已經能寫出簡潔、高效、不需要中間暫存的資料處理管道了。下一章我們將學習 Cargo、crate 與 `mod` 系統——讓你的程式碼從單一檔案擴展到真正的專案結構！
