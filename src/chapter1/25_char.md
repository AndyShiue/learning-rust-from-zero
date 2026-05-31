# `char`

## 本集目標

認識 `char` 型別——用來存放「一個字元」的型別。

## 正文

之前我們用過字串（string，用雙引號 `"` 包起來的文字），今天來認識一個更小的單位——**字元**（char）。

### char 是什麼？

`char` 就是**一個字元**。注意，是「一個」，不是一串。

```rust,editable
fn main() {
    let c = 'A';
    let c2 = '你';
    let c3 = '🦀';

    println!("{}", c);
    println!("{}", c2);
    println!("{}", c3);
}
```

### 單引號 vs 雙引號

這很重要：

- **單引號 `'`** → `char`，只能放**一個**字元
- **雙引號 `"`** → 字串，可以放很多字元

```rust,editable
# fn main() {
    let c = 'A';     // char，一個字元
    let s = "Hello"; // 字串，五個字元
# }
```

如果你用單引號放超過一個字元，Rust 會報錯：

```rust,compile_fail
# fn main() {
    let c = 'AB'; // ❌ 錯誤！char 只能放一個字元
# }
```

### Unicode

Rust 的 `char` 支援 **Unicode**，所以不只是英文字母，中文、日文、甚至 emoji 都可以：

```rust,editable
fn main() {
    let letter = 'R';
    let chinese = '美';
    let japanese = 'の';
    let emoji = '😊';

    println!("{} {} {} {}", letter, chinese, japanese, emoji);
}
```

每一個都是合法的 `char`。

### 型別標註

如果你想明確標註型別：

```rust,editable
fn main() {
    let c: char = 'Z';
    println!("{}", c);
}
```

不過通常不用特別標，Rust 看到單引號就知道是 `char`。

## 重點整理

- `char` 是「一個字元」的型別，用**單引號**包起來：`'A'`、`'你'`、`'🦀'`
- 支援 Unicode，中文、日文、emoji 都是合法的 `char`
- 單引號 `'` = `char`（一個字元），雙引號 `"` = 字串（一串字元），別搞混
