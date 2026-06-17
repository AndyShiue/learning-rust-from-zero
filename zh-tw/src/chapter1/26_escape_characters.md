# 跳脫字元

## 本集目標

學會用反斜線 `\` 在字串裡插入換行、tab 等特殊字元。

## 正文

有時候你想在字串裡面放一些「特殊」的東西，比如換行、tab、或者雙引號本身。這時候就需要**跳脫字元**（escape character）。

### `\n` —— 換行

```rust,editable
fn main() {
    println!("第一行\n第二行");
}
```

`\n` 就是告訴 Rust：「這裡換一行。」它不會真的印出 `\n` 這兩個字，而是產生一個換行的效果。

### `\t` —— tab

```rust,editable
fn main() {
    println!("名字\t分數");
    println!("小明\t85");
    println!("小華\t92");
}
```

`\t` 會插入一個 tab 空間。

### `\\` —— 反斜線本身

如果你想印出反斜線 `\` 本身呢？因為 `\` 已經被拿來當跳脫字元的開頭了，所以要用兩個反斜線：

```rust,editable
fn main() {
    println!("檔案路徑：C:\\Users\\Andy");
}
```

### `\"` —— 雙引號

字串是用 `"` 包起來的，那如果字串裡面要有 `"` 呢？

```rust,editable
fn main() {
    println!("他說：\"你好！\"");
}
```

`\"` 告訴 Rust：「這個雙引號是字串內容，不是字串的結尾。」

### 在 `char` 裡使用

跳脫字元在 `char` 裡面也能用：

```rust,editable
fn main() {
    let newline: char = '\n';
    let tab: char = '\t';
    let backslash: char = '\\';

    print!("A{}B{}C{}", newline, tab, backslash);
}
```

### `\'` —— 單引號

在 char 裡面，如果你想表示單引號本身，就要跳脫：

```rust,editable
fn main() {
    let quote: char = '\'';
    println!("{}", quote);
}
```

因為 char 是用 `'` 包起來的，所以裡面要放 `'` 就得用 `\'`。

### 不需要跳脫的情況

在字串（`""`）裡面，單引號不需要跳脫，可以直接用：

```rust,editable
fn main() {
    println!("It's a test"); // ' 在字串裡不用跳脫
}
```

同樣地，在 char（`''`）裡面，雙引號也不需要跳脫：

```rust,editable
fn main() {
    let c: char = '"'; // " 在 char 裡不用跳脫
    println!("{}", c);
}
```

簡單來說：**包在外面的那個符號才需要跳脫，另一個不用。**

### 一覽表

| 跳脫字元 | 效果 |
|----------|------|
| `\n` | 換行 |
| `\t` | tab |
| `\\` | 反斜線 `\` |
| `\"` | 雙引號 `"` |
| `\'` | 單引號 `'` |

## 重點整理

- 跳脫字元用 `\` 開頭，代表特殊字元：`\n`（換行）、`\t`（tab）、`\\`（反斜線）
- `\"` 在字串裡表示雙引號本身，`\'` 在 char 裡表示單引號本身
- 跳脫字元在字串和 `char` 裡都能使用
- 規則：包在外面的那個符號才需要跳脫，另一個不用
