# `struct` update syntax

## 本集目標

學會用 `..` 語法從既有的 `struct` 實例快速建立新實例，並理解 `Copy` 與 move 欄位的差異。

> 本集是**第 3 章**的補充。

## 概念說明

還記得建立 `struct` 的時候，每個欄位都要寫出來嗎？如果你只想改一兩個欄位，其他照舊，每次都全部寫一遍很煩。Rust 提供了 **`struct` update syntax**，用 `..` 來「填入剩下的欄位」。

### 基本語法

```rust,noplayground
# struct Point {
#     x: i32,
#     y: i32,
# }
#
# fn main() {
#     let p1 = Point { x: 0, y: 100 };
    let p2 = Point { x: 10, ..p1 };
# }
```

意思是：`p2` 的 `x` 設為 `10`，其餘欄位都從 `p1` 移過來。

`..p1` 必須放在最後面，而且前面要有逗號（如果前面有其他欄位的話）。

### copy 與 move 的差異

這裡有個重要的細節。`..p1` 並不是「`clone` 整個 `struct`」，而是**逐欄位**處理：

- 如果欄位的型別實作了 `Copy`（像 `i32`、`f64`、`bool`），就是 **copy**
- 如果欄位的型別**沒有** `Copy`（像 `String`），就是 **move**

也就是說，如果你用 `..p1` 並且移動了 `p1` 的某些非 `Copy` 欄位，那些欄位之後就不能再透過 `p1` 存取了。

### 搭配 `Default`

如果你的 `struct` 有實作 `Default` `trait`，可以用 `..Default::default()` 來建立「只指定幾個欄位，其他用預設值」的實例：

```rust,noplayground
# #[derive(Default)]
# struct Config {
#     debug: bool,
#     id: i32,
# }
#
# fn main() {
    let config = Config { debug: true, ..Default::default() };
# }
```

這在有很多欄位的 `struct` 特別好用。

## 範例程式碼

```rust,editable
#[derive(Debug)]
struct Config {
    width: u32,
    height: u32,
    fullscreen: bool,
    title: String,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            width: 800,
            height: 600,
            fullscreen: false,
            title: String::from("My App"),
        }
    }
}

#[derive(Debug, Clone, Copy)]
struct Point {
    x: f64,
    y: f64,
}

fn main() {
    // 基本用法：只改一個欄位
    let p1 = Point { x: 1.0, y: 2.0 };
    let p2 = Point { x: 10.0, ..p1 };
    println!("p1 = {:?}", p1); // p1 還能用，因為 f64 是 Copy
    println!("p2 = {:?}", p2);

    // 搭配 Default：只指定想改的欄位
    let custom = Config {
        width: 1920,
        height: 1080,
        ..Default::default()
    };
    println!("自訂設定：{:?}", custom);

    // 全部用預設值
    let default_config = Config { ..Default::default() };
    println!("預設設定：{:?}", default_config);

    // 注意 move 語義！
    let c1 = Config {
        width: 1024,
        height: 768,
        fullscreen: true,
        title: String::from("Game"),
    };
    let c2 = Config {
        fullscreen: false,
        ..c1 // title (String) 會被 move！
    };
    // println!("{}", c1.title); // 編譯錯誤！title 已經被 move 了
    println!("c1.width = {}", c1.width);  // 但 Copy 欄位還是能用
    println!("c2 = {:?}", c2);
}
```

## 重點整理

- `let p2 = Point { x: 1, ..p1 };` 用 `p1` 填入 `p2` 剩餘的欄位
- `..source` 必須放在最後面
- `Copy` 型別的欄位會被 copy，非 `Copy` 型別的欄位會被 move
- 如果所有欄位都是 `Copy`，原本的 `struct` 還能繼續使用
- 如果有非 `Copy` 欄位被 move，原本 `struct` 的那些欄位就不能再存取
- `..Default::default()` 很適合用在「大部分欄位用預設值，只改幾個」的場景
