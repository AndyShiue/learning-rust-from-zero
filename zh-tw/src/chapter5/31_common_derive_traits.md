# 常見的 `derive` `trait`

## 本集目標

學會 `PartialEq`、`Eq`、`PartialOrd`、`Ord`、`Default` 等常見 `derive` `trait` 的用途和差別。

## 概念說明

第 4 章我們學了 `Debug`、`Clone`、`Copy`。Rust 標準庫還有其他可以 `derive` 的 `trait`，今天來認識最常用的幾個。

### `PartialEq` 和 `Eq`

`PartialEq` 讓你的型別可以用 `==` 和 `!=` 比較。

```rust,noplayground
#[derive(PartialEq)]
struct Point { x: i32, y: i32 }
#
# fn main() {}
```

`Eq` 是 `PartialEq` 的 supertrait（上一集學的），它保證**自反性**——每個值都等於自己。

「等一下，什麼值不等於自己？」——`f64::NAN`！在浮點數規範裡，`NAN != NAN`。所以 `f64` 只有 `PartialEq`，沒有 `Eq`。

如果你的型別不包含浮點數，通常 `PartialEq` 和 `Eq` 都可以 `derive`。

### `PartialOrd` 和 `Ord`

`PartialOrd` 讓你的型別可以用 `<`、`>`、`<=`、`>=` 比較。

`Ord` 是完整排序——保證任意兩個值都能比大小。`f64` 因為有 `NAN`，所以只有 `PartialOrd`，沒有 `Ord`。

`NAN` 和任何值比較都會回傳 `false`——包括它自己：

```rust,editable
fn main() {
    let nan = f64::NAN;
    println!("{}", nan < 1.0);  // false
    println!("{}", nan > 1.0);  // false
    println!("{}", nan == nan); // false
    println!("{}", nan <= nan); // false
}
```

這就是為什麼 `f64` 不能有 `Ord`——你沒辦法把 `NAN` 放進一個排序裡，因為它和誰比結果都是 `false`，沒有一個合理的位置可以放它。

### 四個 `trait` 的完整關係

先看它們的定義（簡化版）：

```rust,ignore
pub trait PartialEq { ... }
pub trait Eq: PartialEq { }
pub trait PartialOrd: PartialEq { ... }
pub trait Ord: PartialOrd + Eq { ... }
```

整理成繼承關係：

- `Eq: PartialEq` — 要有完整等價，先要有部分等價
- `PartialOrd: PartialEq` — 要能比大小，先要能比相不相等（因為 `<=` 包含了 `==`）
- `Ord: PartialOrd + Eq` — 要有完整排序，先要有部分排序**和**完整等價

為什麼 `PartialOrd` 要求 `PartialEq`？因為「比大小」本身隱含了「能判斷相等」——如果 `a <= b` 且 `b <= a`，那 `a == b`。

為什麼 `Ord` 要求 `Eq`？因為完整排序必須能比較任意兩個值，包括相等的情況。而且 `Ord` 保證所有值都有確定的位置，所以不允許 `NAN` 這種「和自己不相等」的值。

這就是為什麼 `f64` 只能走一邊（`PartialEq` + `PartialOrd`），無法走到另一邊（`Eq` + `Ord`）。

### `Default`

`Default` `trait` 提供一個「預設值」。數字的預設值是 `0`，`bool` 是 `false`，`String` 是空字串，`Vec` 是空 `Vec`。

如果 struct 的每個欄位都有 `Default`，你就可以 `derive` 它：

```rust,noplayground
#[derive(Debug, Default)]
struct Config {
    width: i32,
    height: i32,
    title: String,
}

fn main() {
    let config = Config::default();
    // Config { width: 0, height: 0, title: "" }
}
```

## 範例程式碼

```rust,editable
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Clone, Default)]
struct Student {
    grade: i32,
    name: String,
}

fn main() {
    let alice = Student { grade: 90, name: String::from("Alice") };
    let bob = Student { grade: 85, name: String::from("Bob") };
    let alice2 = Student { grade: 90, name: String::from("Alice") };

    // PartialEq：== 和 !=
    println!("alice == alice2: {}", alice == alice2);
    println!("alice == bob: {}", alice == bob);
    println!("alice != bob: {}", alice != bob);

    // PartialOrd：< > <= >=
    // derive 的 Ord 按欄位順序比較（先比 grade，再比 name）
    println!("alice > bob: {}", alice > bob);
    println!("bob < alice: {}", bob < alice);

    // 排序需要 Ord
    let mut students = vec![
        Student { grade: 70, name: String::from("Charlie") },
        Student { grade: 90, name: String::from("Alice") },
        Student { grade: 85, name: String::from("Bob") },
    ];

    students.sort();
    for s in &students {
        println!("{}: {}", s.name, s.grade);
    }

    // f64 的特殊情況：NAN
    let nan = f64::NAN;
    println!("NAN == NAN: {}", nan == nan); // false！
    println!("NAN < 1.0: {}", nan < 1.0);   // false！
    println!("NAN > 1.0: {}", nan > 1.0);   // false！

    // f64 沒有 Ord，所以不能用 .sort()
    // let mut floats = vec![1.0, 2.0, f64::NAN];
    // floats.sort(); // 編譯錯誤！f64 沒有實作 Ord

    // Default
    let default_student = Student::default();
    println!("預設學生：{:?}", default_student);
    // Student { grade: 0, name: "" }
}
```

## 重點整理

- `PartialEq`：`==`、`!=` 比較；`Eq`：保證自反性（`NAN` 是例外）
- `PartialOrd`：`<`、`>`、`<=`、`>=` 比較；`Ord`：保證完整排序
- `f64` 因為 `NAN` 的存在，只有 `Partial` 版本，沒有完整版
- derive 的 `Ord` 按欄位宣告順序逐一比較
- `Default`：提供預設值（數字 `0`、`bool` `false`、`String` 空字串）
