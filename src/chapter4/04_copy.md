# `Copy`

## 本集目標

理解 `Copy` `trait`——為什麼整數、浮點數、布林值、字元在賦值時不會 move。

## 概念說明

### 上一集的問題

上一集我們發現，`struct` 的值在賦值或傳入函數時會被 move，但整數不會：

```rust,editable
# fn main() {
    let a = 42;
    let b = a;
    println!("{}", a); // 完全沒問題！
# }
```

為什麼？答案就是 **`Copy` `trait`**。

### 什麼是 `Copy`？

`Copy` 是一個特殊的 trait。如果一個型別實作了 `Copy`，那麼在賦值或傳入函數時，Rust 會自動複製一份，而不是 move。

你可以把 Copy 想像成：「這個東西太小了、太簡單了，複製一份根本不費力，所以 Rust 直接幫你複製，不用特別寫 `.clone()`。」

### 哪些型別自動有 `Copy`？

以下這些型別天生就有 Copy：

- 整數：`i8`, `i16`, `i32`, `i64`, `i128`, `u8`, `u16`, `u32`, `u64`, `u128`, `isize`, `usize`
- 浮點數：`f32`, `f64`
- 布林值：`bool`
- 字元：`char`
- ……還有其他更多型別

另外，**tuple** 和**陣列**如果裡面每個元素都是 `Copy` 的，那它們整體也是 `Copy` 的：

```rust,editable
# fn main() {
    let t = (1, true, 'a');  // (i32, bool, char) → 全部 Copy → tuple 也是 Copy
    let t2 = t;
    println!("{:?}", t);     // OK！

    let arr = [1, 2, 3];     // [i32; 3] → i32 是 Copy → 陣列也是 Copy
    let arr2 = arr;
    println!("{:?}", arr);   // OK！
# }
```

這就是為什麼你在前面幾章寫的程式碼裡，整數、tuple、陣列可以隨便賦值給多個變數、傳進多個函數，完全不會有問題。

除了 `Copy` 之外，當 tuple 的每個型別都有實作 `Clone` 時，tuple 也會自動實作 `Clone`。事實上 tuple 對很多其他 `trait` 也有同樣的行為——只要所有元素都有實作某個 `trait`，tuple 整體就會有。這點以後不再贅述。

### 自己的型別也可以加 `Copy`

如果你的型別裡面所有值都是 `Copy` 的型別，那你的型別也可以加上 `#[derive(Copy, Clone)]`：

```rust,noplayground
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
#
# fn main() {}
```

注意：`#[derive(Copy)]` 一定要同時加 `Clone`——如果只寫 `#[derive(Copy)]` 而不寫 `Clone`，編譯器會報錯。

為什麼？因為 Rust 規定：任何可以 copy 的東西，也必須可以 `clone`。`Copy` 是「自動複製」，`Clone` 是「手動複製」。如果一個東西連手動複製都不行，那自動複製當然更不行。所以 `Copy` 要求你先有 `Clone`。

加上之後，`Point` 的行為就跟整數一樣了——賦值不會 move：

```rust,editable
# #[derive(Debug, Copy, Clone)]
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
    let p1 = Point { x: 1, y: 2 };
    let p2 = p1; // 自動複製，p1 還在！
    println!("{:?}", p1); // OK
# }
```

### copy 和 `clone` 的差別

| | copy | `clone` |
|---|---|---|
| 觸發方式 | 自動（賦值、傳入函數） | 手動（`.clone()`） |
| 適用場景 | 小而簡單的資料 | 任何資料 |
| 使用限制 | 所有欄位都必須是 `Copy` | 沒有特別限制 |

簡單來說：**copy 是自動的複製，`clone` 是手動的複製。**

## 範例程式碼

```rust,editable
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}

fn print_point(p: Point) {
    println!("函數收到：({}, {})", p.x, p.y);
}

fn double(n: i32) -> i32 {
    n * 2
}

fn main() {
    // 整數自動 Copy
    let a = 42;
    let b = a;
    println!("a = {}, b = {}", a, b); // 兩個都能用

    // bool 也是 Copy
    let flag = true;
    let flag2 = flag;
    println!("flag = {}, flag2 = {}", flag, flag2);

    // 整數傳進函數不會 move
    let x = 10;
    let result = double(x);
    println!("x = {}, result = {}", x, result);

    // 自訂的 struct 加上 Copy 後也不會 move
    let p1 = Point { x: 3, y: 7 };
    let p2 = p1;     // 自動複製
    print_point(p1); // p1 還能用
    println!("p1 = {:?}", p1); // 還是能用！
    println!("p2 = {:?}", p2);
}
```

## 不要隨便幫自己的型別加 `Copy`

看完這一集，你可能會想：「那我以後每個 `struct` 都加 `#[derive(Copy, Clone)]` 不就好了？」

**請不要這樣做。** 原因是：一旦加了 `Copy`，使用你這個型別的程式碼就會依賴「賦值時自動複製」的行為。如果有一天你需要修改這個 `struct`，加了一個不是 `Copy` 的欄位，你就必須拿掉 `Copy`。

問題來了：拿掉 `Copy` 之後，原本寫 `let p2 = p1;` 的地方全部會從「自動複製」變成「move」，`p1` 就不能再用了。所有用到這個型別的程式碼都可能因此壞掉，而且壞的地方可能很多、很分散。

所以好的習慣是：**只有你確定這個型別永遠都會很小、很簡單，而且不會再加非 `Copy` 的欄位時，才加 `Copy`。** 像 `Point { x: i32, y: i32 }` 這種就很適合。如果不確定，只加 `Clone` 就好——需要複製的時候手動寫 `.clone()`，未來要改也不會影響其他程式碼。

## 重點整理

- **`Copy`** 是一個 `trait`，讓型別在賦值和傳入函數時自動複製，而不是 move
- `i32`、`f64`、`bool`、`char` 等基本型別天生就有 `Copy`
- tuple 和陣列如果所有元素都是 `Copy`，整體也是 `Copy`
- tuple 對很多 `trait`（`Copy`、`Clone` 等）都有同樣的行為：所有元素都有實作 → tuple 就有實作
- 自訂 `struct` 可以加 `#[derive(Copy, Clone)]`，但所有欄位都必須是 `Copy` 的型別
- `Copy` 一定要搭配 `Clone` 一起 `derive`
- **`Copy` = 自動複製，`Clone` = 手動複製（`.clone()`）**
- 不要隨便加 `Copy`——未來拿掉會讓所有依賴自動複製的程式碼壞掉。不確定就只加 `Clone`
