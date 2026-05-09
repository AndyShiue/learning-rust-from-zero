# 簡單函數

## 本集目標
用 `fn` 定義自己的函數，並在 `main` 裡呼叫它。

## 正文

到目前為止，我們幾乎所有的程式碼都寫在 `main` 裡面。但如果程式越來越大，全部擠在一起就很亂。這時候我們可以把一段程式碼「包裝」成一個**函數**（function），想用的時候呼叫它就好。

### 定義一個函數

```rust
fn greet() {
    println!("你好！歡迎來到 Rust 的世界！");
}

fn main() {
    greet();
}
```

拆解一下語法：
- `fn` → 告訴 Rust「我要定義一個函數」
- `greet` → 函數的名字
- `()` → 參數列表（目前是空的，下一集會學）
- `{ ... }` → 函數要做的事

然後在 `main` 裡面寫 `greet();` 就是呼叫它。

### 函數可以呼叫好幾次

```rust
fn greet() {
    println!("哈囉！");
}

fn main() {
    greet();
    greet();
    greet();
}
```

這就是函數的好處——寫一次，用很多次。

### 函數之間可以互相呼叫

不只是 `main`裡面可以呼叫函數——函數之間也可以互相呼叫。`main` 只是程式的**進入點**（程式開始執行的地方），但裡面呼叫的函數也能再呼叫其他函數：

```rust
fn say_name() {
    println!("我是 Rust！");
}

fn greet() {
    say_name();
}

fn main() {
    greet(); // main 呼叫 greet，greet 再呼叫 say_name
}
```

### 函數定義的位置：上面或下面都行

在某些語言裡，函數必須在使用之前先定義。但 Rust 不用！

```rust
fn main() {
    greet(); // ✅ 先呼叫
}

fn greet() { // 後定義
    println!("你好！");
}
```

這樣也完全沒問題。Rust 編譯器會先掃過整個檔案，所以不管你把函數放在 `main` 上面還是下面，都找得到。

### 函數命名慣例

Rust 的函數名用**蛇形命名法**（snake_case）：全小寫，單字之間用底線 `_` 隔開。

```rust,noplayground
fn say_hello() { // ✅ 蛇形命名
    println!("Hello!");
}

fn sayHello() {  // ⚠️ 可以跑，但編譯器會警告
    println!("Hello!");
}
#
# fn main() {}
```

## 重點整理

- 用 `fn 名字() { ... }` 定義函數
- 用 `名字();` 呼叫函數
- `main` 是程式的進入點，但函數之間也可以互相呼叫
- 函數定義放在 `main` 上面或下面都可以
- 命名慣例是 snake_case（全小寫加底線）
