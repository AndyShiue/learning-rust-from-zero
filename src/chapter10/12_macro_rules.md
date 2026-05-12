# `macro_rules!`

## 本集目標

學會用 `macro_rules!` 定義自己的宣告式巨集。

## 概念說明

### 巨集 vs 函數

我們從第一章就一直在用巨集——`println!`、`vec!`、`format!`、`assert_eq!`。呼叫時有個驚嘆號 `!`，這就是巨集和函數的區別。

巨集和函數最根本的差異：巨集在**編譯期展開成程式碼**。你寫的巨集呼叫會在編譯的時候被替換成展開後的程式碼，然後編譯器再去編譯那段展開後的結果。巨集能產生任意的程式碼——定義新的函數、`struct`、甚至其他巨集呼叫。它也能接受型別名稱、模式等不是值的東西當參數。

但巨集也更難寫、更難讀、錯誤訊息比較差。能用函數就不要用巨集。

### 基本語法

```rust
macro_rules! say_hello {
    () => {
        println!("Hello!");
    };
}

fn main() {
    say_hello!(); // 印出 Hello!
}
```

結構是 `(pattern) => { expansion }`——左邊匹配，右邊展開。

### 帶參數

用 `$name:kind` 捕獲參數：

```rust
macro_rules! say {
    ($msg:expr) => {
        println!("{}", $msg);
    };
}

fn main() {
    say!("hi");
    say!(1 + 2);
}
```

常見的 kind：
- `expr`：表達式
- `ty`：型別
- `ident`：識別符（如變數名稱）
- `tt`：token tree（最靈活）

還有其他 kind，如果需要用到的話請自行搜尋。

### 多個分支

```rust
macro_rules! log {
    ($val:expr) => {
        println!("值：{}", $val);
    };
    ($name:expr, $val:expr) => {
        println!("{} = {}", $name, $val);
    };
}

fn main() {
    log!(42);           // 值：42
    log!("score", 100); // score = 100
}
```

### 重複匹配

`$( ... ),*` 的語法可以匹配重複的項目。拆開來看：

- `$( ... )` 裡面放要重複的模式
- `,` 是分隔符號——每個重複項之間要有逗號。分隔符號不一定要是逗號，也可以用 `;` 等其他符號，或是省略不用
- `*` 表示零個或更多個。也可以用 `+` 表示一個或更多個

```rust,noplayground
macro_rules! make_vec {
    ($($element:expr),*) => {
        {
            let mut v = Vec::new();
            $( v.push($element); )*
            v
        }
    };
}

fn main() {
    let v = make_vec![1, 2, 3];
}
```

展開的時候也用 `$( ... )*`——`$( v.push($element); )*` 會對每個捕獲的元素重複展開一次，變成：

```rust,ignore
v.push(1);
v.push(2);
v.push(3);
```

### 三種括號

巨集可以用三種括號呼叫，效果完全一樣：
- `macro!(...)` — 小括號，像函數呼叫
- `macro![...]` — 中括號，像陣列（`vec![1,2,3]` 用這個）
- `macro!{...}` — 大括號，像程式碼區塊

差別只是慣例。

### 巨集的作用域

`macro_rules!` 定義的巨集在定義之後才能用（跟函數不同——函數不受定義順序限制）。

如果想讓巨集可以被其他 crate 使用，在前面加 `#[macro_export]`。在巨集內部引用定義巨集的 crate 的東西時，用 `$crate` 路徑——這樣不管使用者的 crate 怎麼命名你的 crate，路徑都能正確指向：

```rust,noplayground
// 在 my_lib crate 裡

pub fn _log_impl(msg: &str) {
    println!("[LOG] {}", msg);
}

#[macro_export]
macro_rules! log_msg {
    ($msg:expr) => {
        $crate::_log_impl($msg);
    };
}
#
# fn main() {}
```

別的 crate 只要引入 `my_lib`，就能直接用 `log_msg!("hello")`。`$crate` 會自動替換成正確的 crate 路徑。

## 範例程式碼

```rust
macro_rules! max {
    ($a:expr, $b:expr) => {
        if $a > $b { $a } else { $b }
    };
}

macro_rules! print_all {
    ($($item:expr),*) => {
        $(
            println!("{}", $item);
        )*
    };
}

// stringify! 是內建巨集，把傳入的東西原樣變成字串
// stringify!(hello) 會變成 "hello"
macro_rules! create_fn {
    ($name:ident) => {
        fn $name() {
            println!("呼叫了函數 {}", stringify!($name));
        }
    };
}

create_fn!(hello);
create_fn!(world);

fn main() {
    println!("max(3, 7) = {}", max!(3, 7));

    print_all!["a", "b", "c"];

    hello();
    world();
}
```

## 重點整理

- 能用函數就不要用巨集
- `macro_rules!` 定義宣告式巨集：`(pattern) => { expansion }`
- 用 `$name:expr` 等接收參數，常見 kind：`expr`、`ty`、`ident`、`tt`
- `$(...),*` 匹配重複項，展開時 `$( ... )*` 對每個重複
- 三種括號 `()` / `[]` / `{}` 效果相同
- 巨集定義後才能用（跟函數不同）
- `#[macro_export]` 讓巨集可被其他 crate 使用