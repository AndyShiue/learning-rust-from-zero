# `Vec` 與所有權

## 本集目標

理解 `Vec` 的所有權行為，以及它和 `String` / `&str` 的對稱關係。

## 概念說明

### `Vec` 和 `String` 是一對

在前面幾集，我們學了 `String` 和 `&str` 的關係：

| 擁有版本 | 借用版本 |
|---|---|
| `String` | `&str` |

`Vec` 也有完全一樣的對應：

| 擁有版本 | 借用版本 |
|---|---|
| `Vec` | `&[T]`（切片） |

`String` 擁有一段文字，`&str` 借用一段文字。`Vec` 擁有一組元素，`&[T]` 借用一組元素。**概念完全對稱。**

### `Vec` 會 move

`Vec` 的資料在 heap 上，所以它不是 `Copy`。賦值和傳入函數都會 move：

```rust,noplayground
# fn main() {
    let v1 = vec![1, 2, 3];
    let v2 = v1; // move！v1 不能再用了
# }
```

跟 `String` 一模一樣。

### 函數參數用切片 `&[T]`

跟 `String` / `&str` 的建議一樣——如果函數只需要讀取 `i32` 的 `Vec` 的內容，用切片 `&[i32]`：

```rust,editable
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn main() {
    let v = vec![1, 2, 3, 4, 5];
    let total = sum(&v); // &Vec 自動轉成 &[i32]
    println!("v 還在：{:?}", v);
}
```

就像 `&String` 會自動轉成 `&str`，`i32` 的 `&Vec` 也會自動轉成 `&[i32]`。

### `for` 迴圈與所有權

這是很重要的一點：`for` 迴圈走訪 `Vec` 時，可以選擇要 move 還是 borrow：

**`for x in v`——move！**

```rust,editable
fn main() {
    let v = vec![1, 2, 3];
    for x in v {
        println!("{}", x);
    }
    // v 被 move 走了，不能再用！
}
```

`for x in v` 會消耗整個 `Vec`。迴圈結束後，`v` 就不存在了。

**`for x in &v`——borrow！**

```rust,editable
fn main() {
    let v = vec![1, 2, 3];
    for x in &v {
        println!("{}", x);
    }
    println!("v 還在：{:?}", v); // OK！
}
```

`for x in &v` 只是借用，`v` 不會被消耗。

大部分情況你應該用 `for x in &v`，除非你確定不再需要這個 `Vec`。

## 範例程式碼

```rust,editable
// 參數用切片：&Vec 自動轉 &[i32]
fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for x in nums {
        total += x;
    }
    total
}

fn print_all(nums: &[i32]) {
    let mut first = true;
    for x in nums {
        if first {
            first = false;
        } else {
            print!(", ");
        }
        print!("{}", x);
    }
    println!();
}

fn main() {
    // Vec 會 move
    let v1 = vec![10, 20, 30];
    let v2 = v1.clone(); // clone 保留 v1
    println!("v1 = {:?}", v1);
    println!("v2 = {:?}", v2);

    // 函數用切片參數（借用）
    let scores = vec![85, 92, 78, 95, 88];
    println!("總分 = {}", sum(&scores));
    print_all(&scores);
    println!("scores 還在：{:?}", scores);

    // 切片操作
    let slice = &scores[1..4]; // 借用一部分
    println!("中間三筆：{:?}", slice);
    println!("中間三筆的總分 = {}", sum(slice));

    // for x in &v：借用走訪
    println!("逐一列出（借用）：");
    for s in &scores {
        println!("  {}", s);
    }
    println!("scores 還在：{:?}", scores);

    // for x in v：move 走訪（用完就沒了）
    let temp = vec![1, 2, 3];
    println!("消耗走訪：");
    for x in temp {
        println!("  {}", x);
    }
    // temp 已經被 move 了，下面會編譯錯誤：
    // println!("{:?}", temp);

    // 對稱關係整理
    // String  ↔ &str     （擁有 ↔ 借用 文字）
    // Vec     ↔ &[T]     （擁有 ↔ 借用 一組值）
    println!("--- 對稱關係 ---");
    let s = String::from("hello");
    let s_ref: &str = &s;     // &String → &str
    println!("String: {}, &str: {}", s, s_ref);

    let v = vec![1, 2, 3];
    let v_ref: &[i32] = &v;   // &Vec → &[i32]
    println!("Vec: {:?}, slice: {:?}", v, v_ref);
}
```

## `Vec` 的元素只能是 `i32` 嗎？

讀到這裡你可能有個疑問：`Vec` 的元素只能是 `i32` 嗎？當然不是！下一章將會花大量篇幅討論相關內容。

## 重點整理

- **`Vec` 和 `String` 的所有權行為完全對稱**：都在 heap 上，都會 move，都可以 `clone`
- `String` ↔ `&str` 就像 `Vec` ↔ `&[T]`（擁有 ↔ 借用）
- `&Vec` 會自動轉成 `&[T]`（跟 `&String` 自動轉 `&str` 一樣）
- 函數參數偏好用切片 `&[T]` 而不是 `&Vec`
- `for x in v`：**move**，消耗整個 `Vec`
- `for x in &v`：**borrow**，只是借用，`Vec` 還在
- 大部分情況用 `for x in &v`，除非你確定不再需要這個 `Vec`
- `Vec` 的元素不只能放 `i32`——下一章會學到怎麼讓它放其他型別

恭喜你完成了第 4 章！🎉 這一章你學會了 Rust 最核心的概念——所有權、move、`clone`、copy、borrowing，還有 `String` 和 `Vec` 這兩個最常用的非 `Copy` 型別。這些概念是 Rust 和其他語言最大的不同，也是 Rust 能在不需要犧牲效能的情況下保證記憶體安全的關鍵。下一章我們將進入泛型、`trait` bound 和生命週期——讓你的程式碼能處理任意型別，同時保持型別安全！
