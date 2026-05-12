# move 與 `Clone`

## 本集目標

理解 Rust 的 move 語意——賦值和傳入函數都會轉移所有權——以及用 `Clone` 來複製資料。

## 概念說明

### move：交出去就沒了

上一集我們學了 `trait`，現在來看所有權在程式碼裡的樣子。

在 Rust 裡，當你把一個 `struct` 的值賦給另一個變數，原本的變數就**不能再用了**。這就是第 1 集講的「把鑰匙圈交出去」：

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
    let p1 = Point { x: 1, y: 2 };
    let p2 = p1; // p1 的所有權移轉給 p2
    // 從這裡開始，p1 不能再用了！
# }
```

這個行為叫做 **move（移轉）**。Rust 編譯器會在編譯時就檢查這件事，如果你在 move 之後還嘗試使用原本的變數，編譯器會直接報錯。

### 傳進函數也是 move

不只是賦值，把值傳進函數也會發生 move：

```rust
# struct Point {
#     x: i32,
#     y: i32,
# }
#
fn print_point(p: Point) {
    println!("({}, {})", p.x, p.y);
}

fn main() {
    let p1 = Point { x: 1, y: 2 };
    print_point(p1); // p1 被 move 進函數了
    // p1 不能再用了！
}
```

因為函數的參數就像一個新的變數，值被「交」給了它。

### `Clone`：完整複製一份

如果你需要保留原本的值，又想要一份副本，就用 **`Clone`**。

首先，你的型別要加上 `#[derive(Clone)]`（當然也可以順便加 `Debug`）：

```rust,noplayground
#[derive(Debug, Clone)]
struct Point {
    x: i32,
    y: i32,
}
#
# fn main() {}
```

然後用 `.clone()` 來複製：

```rust
# #[derive(Debug, Clone)]
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
    let p1 = Point { x: 1, y: 2 };
    let p2 = p1.clone();  // 複製一份，p1 還在
    println!("{:?}", p1); // OK！p1 還能用
    println!("{:?}", p2); // p2 是獨立的副本
# }
```

回想第 1 集的比喻：`clone` 就是「複製一份完整的鑰匙圈和保險箱」。兩個變數各自擁有自己的資料，互不干擾。

### 整數不會 move？

你可能會注意到，整數的行為不太一樣：

```rust
# fn main() {
    let a = 42;
    let b = a;
    println!("{}", a); // 這居然可以！
# }
```

為什麼整數不會 move？這個問題我們下一集再來解答。

## 範例程式碼

```rust
#[derive(Debug, Clone)]
struct Point {
    x: i32,
    y: i32,
}

fn print_point(p: Point) {
    println!("函數收到的點：({}, {})", p.x, p.y);
}

fn main() {
    let p1 = Point { x: 10, y: 20 };

    // 用 clone 複製一份，這樣 p1 不會被 move 走
    let p2 = p1.clone();
    println!("p1 = {:?}", p1);
    println!("p2 = {:?}", p2);

    // 傳進函數也是 move，所以先 clone
    print_point(p1.clone());
    println!("p1 還在：{:?}", p1);

    // 如果不 clone，直接傳進去，p1 就被 move 走了
    print_point(p1);
    // 下面這行如果取消註解，編譯器會報錯：
    // println!("p1 不見了：{:?}", p1);
}
```

## 重點整理

- `let p2 = p1;` 會 **move**，之後 `p1` 不能再用
- 把值傳進函數也是 move
- `#[derive(Clone)]` + `.clone()` 可以複製一份獨立的副本
- `clone` 之後，原本的變數還可以繼續使用
- 整數（`i32` 等）不會 move——下一集會解釋為什麼
