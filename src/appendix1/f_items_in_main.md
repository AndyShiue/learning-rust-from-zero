# struct / enum 放在 fn 裡面

## 本集目標

了解 struct、enum、fn 等「項目」可以定義在函數內部，以及它們與 `let` 綁定在順序上的根本差異。

> 本集是**第三章**的補充。

## 概念說明

你可能習慣了把 `struct` 和 `enum` 定義在 `fn main()` 的外面，但其實把它們放在裡面也完全合法：

```rust
fn main() {
    struct Point {
        x: i32,
        y: i32,
    }
    let p = Point { x: 1, y: 2 };
    println!("{}", p.x);
}
```

這段程式碼完全可以編譯。

### 限制：只在該函數內可見

放在函數內的型別定義，只有那個 fn 看得到。其他函數無法使用它。所以慣例上，我們還是會把型別定義放在外面——除非你確定這個型別只在一個 fn 裡面用到。

### 重要差異：項目不受順序限制

這裡有一個很多人不知道的重點。在 Rust 裡，**項目（items）**——包括 `struct`、`enum`、`fn`、`trait`、`impl` 等——**不受定義順序影響**。你可以先使用，後定義：

```rust
fn main() {
    let p = Point { x: 1, y: 2 }; // 先使用
    println!("{}", p.x);

    struct Point {                // 後定義
        x: i32,
        y: i32,
    }
}
```

這和 `let` 完全不同！`let` 綁定必須在使用之前出現，否則編譯器會報錯。但項目定義是「全域可見」的（在它所在的作用域內），跟你寫在哪一行無關。

### 為什麼會這樣？

因為項目是在編譯期就確定的靜態定義，編譯器會先掃描所有項目，建立完整的型別資訊，然後才處理 `let` 等執行期的敘述。

## 範例程式碼

```rust
fn main() {
    // 先呼叫，後定義——完全合法
    greet();

    // 先使用 struct，後定義
    let color = Color::Red;
    describe(color);

    // 定義放在使用之後
    struct Point {
        x: f64,
        y: f64,
    }

    let p = Point { x: 3.0, y: 4.0 };
    println!("座標：({}, {})", p.x, p.y);

    // 這些項目定義的順序完全不重要
    enum Color {
        Red,
        Green,
        Blue,
    }

    fn describe(c: Color) {
        match c {
            Color::Red => println!("紅色"),
            Color::Green => println!("綠色"),
            Color::Blue => println!("藍色"),
        }
    }

    fn greet() {
        println!("哈囉！");
    }

    // 但 let 綁定必須在使用之前！
    // 以下如果取消註解會編譯失敗：
    // println!("{}", not_yet);
    let not_yet = 42;
    println!("let 綁定必須先宣告：{}", not_yet);
}
```

## 重點整理

- `struct`、`enum`、`fn` 等項目可以合法地定義在函數內部
- 定義在 fn 內的項目，只有該 fn 看得到（作用域限制）
- 一般還是把型別定義放在 fn 外面，除非只有單一 fn 使用
- **項目不受定義順序影響**——可以先使用、後定義
- **`let` 綁定必須在使用之前出現**——這是項目和 `let` 的根本差異
- 原因：項目是編譯期的靜態定義，編譯器會先掃描完所有項目再處理執行期程式碼
