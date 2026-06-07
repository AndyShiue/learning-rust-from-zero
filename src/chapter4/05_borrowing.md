# 借用 `&`

## 本集目標

學會用 `&` 借用值，不需要 move 也不需要 `clone`，就能讓別人讀取你的資料。

## 概念說明

### move 和 `clone` 都有代價

前面我們學了兩種方式來處理所有權：

- **move**：交出去就沒了，原本的變數不能再用
- **`clone`**：複製一份，但如果資料很大，複製就很浪費

有沒有辦法**不交出去、不複製，只是借別人看一下**？

有！這就是**借用（borrowing）**，用 `&` 符號。

### `&` 就是「借」

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
    let p = Point { x: 1, y: 2 };
    let r: &Point = &p; // r 借用了 p，p 還是擁有者
# }
```

`&p` 的意思是：「我不要拿走 `p` 的所有權，我只是借來看看。」`p` 還在，你隨時可以繼續用 `p`。

### 函數參數用 `&` 就不會 move

```rust,editable
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

fn print_point(p: &Point) {
    println!("({}, {})", p.x, p.y);
}

fn main() {
    let p1 = Point { x: 10, y: 20 };
    print_point(&p1); // 傳 &p1，只是借，不是 move
    println!("{:?}", p1); // p1 還在！
}
```

注意兩個地方：

1. 函數參數的型別寫 `&Point`（前面加 `&`）
2. 呼叫時傳 `&p1`（也加 `&`）

這樣函數只是「借」了 `p1` 來看，用完就還回去，`p1` 的所有權完全沒有改變。

### 之前的 & 原來是借用！

還記得之前學的 `&[i32]`（切片）和 `&str`（字串切片）嗎？當時我們說還不用深入理解，但現在我們可以說明了——那些 `&` 就是借用！

- `&[i32]` 是借用一段陣列的資料，不擁有它
- `&str` 是借用一段字串的資料，不擁有它

所以像這樣的函數：

```rust,noplayground
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}
#
# fn main() {}
```

用 `for x in nums` 就能走訪切片裡的每個元素，跟之前走訪陣列的方式一樣。函數只是借用了陣列的一段切片，不會把整個陣列 move 走。

### * 解參考

`&` 是「借」，反過來 `*` 就是「順著借用找到原本的值」，叫做**解參考（dereference）**：

```rust,editable
fn main() {
    let x = 42;
    let r = &x;
    println!("{}", *r); // 42，和 x 一樣
}
```

不過大部分情況下你不需要手動寫 `*`——Rust 在用 `.` 存取欄位、呼叫 method、或 `println!` 的時候都會自動幫你解參考。所以目前知道有這個東西就好，下一集會用到它。

注意：前面學的 `&[T]` 和 `&str` 比較特別，你沒辦法對它們使用 `*` 取得一個值。原因之後會學到，現在先知道就好。

### `&T` 都是 `Copy`

上一集學了 Copy——有些型別賦值的時候會自動複製，不會 move。不管 `T` 是什麼，`&T` 都是 Copy 的。畢竟參考只是借用，複製一個參考不會影響原本的資料，只是多了一個人在看而已：

```rust,editable
fn main() {
    let s = String::from("hello");
    let r1 = &s;
    let r2 = r1; // 複製參考，不是 move
    println!("{} {}", r1, r2); // r1 和 r2 都能用
}
```

注意：`String` 本身不是 `Copy`（賦值會 move），但 `&String` 是 `Copy`。

### 借用是唯讀的

用 `&` 借用的時候，你**只能讀，不能改**。如果你想借來改，那是下一集的內容。

## 範例程式碼

```rust,editable
#[derive(Debug, Clone)]
struct Point {
    x: i32,
    y: i32,
}

// 用借用，不會 move
fn print_point(p: &Point) {
    println!("({}, {})", p.x, p.y);
}

// 切片參數就是借用
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn main() {
    let p1 = Point { x: 10, y: 20 };

    // 借用：傳 &p1，p1 不會被 move
    print_point(&p1);
    print_point(&p1); // 可以借很多次！
    println!("p1 還在：{:?}", p1);

    // 陣列切片也是借用
    let numbers = [1, 2, 3, 4, 5];
    let total = sum(&numbers);
    println!("總和 = {}", total);
    println!("numbers 還在：{:?}", numbers);

    // &str 也是借用
    let greeting: &str = "你好";
    println!("{}", greeting);
    println!("{}", greeting); // 可以用很多次
}
```

## 重點整理

- `&` 是借用，**不轉移所有權**，原本的變數還能繼續用
- 函數參數寫 `&Type`，呼叫時傳 `&value`
- 借用可以多次進行，不像 move 只能一次
- `*` 是解參考——順著借用找到原本的值（但大部分情況 Rust 會自動幫你做）
- `&[T]` 和 `&str` 是比較特別的借用，沒辦法對它們用 `*` 取得值
- `&T` 都是 `Copy`——複製一個參考不影響原本的資料
- 借用是**唯讀**的，不能修改借來的資料
