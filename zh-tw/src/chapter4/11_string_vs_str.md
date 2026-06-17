# `String` vs `&str`

## 本集目標

搞清楚 `String` 和 `&str` 的差別，以及函數參數該用哪一個。

## 概念說明

### 兩種字串，到底差在哪？

| | `String` | `&str` |
|---|---|---|
| 擁有資料？ | ✅ 擁有 | ❌ 只是借用 |
| 資料在哪？ | heap 上 | 可能在程式碼裡，也可能借用 `String` 的資料 |
| 可以修改？ | ✅ 可以（`push_str` 等） | ❌ 不行 |
| 會 move？ | ✅ 會 | ❌ 不會（它就是個參考） |

### `&String` 會自動轉成 `&str`

當你有一個 `String`，想把它的參考傳給接受 `&str` 的函數時，Rust 會自動幫你轉換：

```rust,editable
fn greet(name: &str) {
    println!("你好，{}！", name);
}

fn main() {
    let s = String::from("小明");
    greet(&s); // &String 自動轉成 &str，完全OK！
}
```

為什麼可以這樣？之後會學到。現在只要知道：**傳 `&String` 的地方如果參數型別是 `&str`，Rust 會自動處理**。

### 函數參數偏好 `&str`

如果你的函數只需要「讀」一段文字，不需要擁有它，參數型別就寫 `&str`：

```rust,noplayground
fn count_chars(s: &str) -> i32 {
    let mut count = 0;
    for _c in s.chars() {
        count += 1;
    }
    count
}
#
# fn main() {}
```

這裡用到的 `.chars()` 是一個 method——`String` 和 `&str` 都有實作。它會把字串拆成一個一個字元讓你走訪。

這樣做的好處是：

1. 傳 `&str`（字串字面值）可以用
2. 傳 `&String` 也可以用（自動轉換）
3. 不會 move 任何東西

這就是為什麼 Rust 社群普遍建議：**函數參數用 `&str` 而不是 `&String`**。

### 什麼時候用 `String`？

- 你需要**擁有**這段文字（存在 `struct` 裡、回傳給呼叫者）
- 你需要**修改**這段文字（`push_str` 等）

## 範例程式碼

```rust,editable
// 參數用 &str：既能接 &str，也能接 &String
fn greet(name: &str) {
    println!("你好，{}！", name);
}

fn char_count(s: &str) -> i32 {
    let mut count = 0;
    for _c in s.chars() {
        count += 1;
    }
    count
}

fn main() {
    // &str：字串字面值
    let literal = "世界";
    greet(literal);

    // String：擁有的字串
    let owned = String::from("小花");
    greet(&owned); // &String 自動轉 &str

    // 兩種都能傳給接受 &str 的函數
    println!("「{}」有 {} 個字元", literal, char_count(literal));
    println!("「{}」有 {} 個字元", owned, char_count(&owned));

    // String 可以修改，&str 不行
    let mut s = String::from("Rust");
    s.push_str(" 好好玩");
    println!("{}", s);

    // String 會 move
    let s1 = String::from("hello");
    let s2 = s1; // move
    // println!("{}", s1); // 編譯錯誤！
    println!("{}", s2);

    // &str 不會 move（它本身就是參考）
    let greeting: &str = "哈囉";
    let greeting2 = greeting;  // 這是 Copy！（&str 是 Copy 的）
    println!("{}", greeting);  // OK
    println!("{}", greeting2); // OK
}
```

## 重點整理

- **`String`** 擁有資料（heap 上），可以修改，會 move
- **`&str`** 是參考，不擁有資料，不能修改，不會 move
- `&String` 會自動轉成 `&str`
- 函數參數偏好用 `&str`——接受範圍更廣（`&str` 和 `&String` 都能傳）
- 需要擁有或修改字串時才用 `String`
