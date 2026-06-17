# `Box<T>`

## 本集目標

學會用 `Box<T>` 把資料放在 heap 上，理解它在遞迴型別中的必要性。

## 概念說明

還記得第 4 章的保險箱比喻嗎？鑰匙圈上掛著鑰匙，鑰匙可以打開保險箱，保險箱裡放著真正的東西。

`Box<T>` 就是那個保險箱——它把資料放在 heap 上，然後在 stack 上留一把鑰匙（指標）。

### 為什麼需要 `Box`？

大部分時候，Rust 把資料直接放在 stack 上就好了。但有兩種情況需要 `Box`：

**1. 資料太大**

如果一個 `struct` 有很多欄位、佔很多空間，放在 stack 上可能不太好（stack 空間有限）。用 `Box` 把它移到 heap 上，stack 上只留一個指標。

**2. 遞迴型別**

這是更重要的原因。假設你想定義一個連結串列（linked list）：

```rust,compile_fail
enum List {
    Node(i32, List), // 編譯錯誤！
    Empty,
}
#
# fn main() {}
```

Rust 需要在編譯時知道每個型別的大小。但這裡有個問題：要知道 `List` 的大小，你需要知道 `Node` 有多大。`Node` 包含一個 `i32` 和一個 `List`——所以你需要知道 `List` 有多大。但 `List` 裡面又有 `List`⋯⋯

展開來看：`List` 的大小 = `i32` + `List` 的大小 = `i32` + `i32` + `List` 的大小 = ⋯⋯ 永遠算不完。編譯器在這裡直接報錯：「recursive type has infinite size（遞迴型別大小無限大）」。

解法就是用 `Box`：

```rust,noplayground
enum List {
    Node(i32, Box<List>),
    Empty,
}
#
# fn main() {}
```

`Box<List>` 的大小是固定的（就是一個指標的大小），問題就解決了。

### `Box` 的使用

```rust,editable
fn main() {
    let x = Box::new(42);
    println!("{}", x); // 可以直接用，Rust 會自動拿裡面的值
}
```

`Box::new(value)` 把值搬到 heap 上。`Box` 擁有裡面的值，離開作用域時會自動釋放（因為 `Box` 實作了 `Drop`）。

## 範例程式碼

```rust,editable
// 用 Box 的遞迴型別：連結串列
enum List {
    Node(i32, Box<List>),
    Empty,
}

// 印出串列
fn print_list(list: &List) {
    match list {
        List::Node(value, next) => {
            print!("{} -> ", value);
            print_list(next);
        }
        List::Empty => {
            println!("end");
        }
    }
}

fn main() {
    // 基本的 Box 使用
    let x = Box::new(42);
    println!("Box 裡的值：{}", x);

    // 一步一步建立連結串列：3 -> 2 -> 1 -> end
    // 從最後面開始建立
    let list = List::Empty;                   // end
    let list = List::Node(1, Box::new(list)); // 1 -> end
    let list = List::Node(2, Box::new(list)); // 2 -> 1 -> end
    let list = List::Node(3, Box::new(list)); // 3 -> 2 -> 1 -> end

    print_list(&list);

    // Box 是唯一擁有者——鑰匙不是 Copy，所以 let b = a 是 move
    let a = Box::new(String::from("hello"));
    let b = a; // 鑰匙從 a 交給 b，a 就空了
    // println!("{}", a); // 編譯錯誤！a 已經被 move 了
    println!("{}", b);
}
```

## 重點整理

- `Box<T>` 把資料放在 heap 上，stack 上只留一個指標（保險箱比喻的「鑰匙」）
- 最重要的用途：**遞迴型別**（如連結串列）需要 `Box` 來打破無限大小的問題
- `Box::new(value)` 建立 `Box`，離開作用域時自動釋放
- `Box` 是唯一擁有者，move 語義和其他非 `Copy` 的型別一樣
