# shadowing

## 本集目標

用 `let` 重新宣告同名變數（shadowing），以及它和 `mut` 的關鍵差別。

## 正文

Rust 有一個很有趣的功能叫做 **shadowing**（遮蔽）。簡單說就是：你可以用 `let` 再次宣告一個同名的變數，新的會「蓋掉」舊的。

```rust,editable
fn main() {
    let x = 5;
    let x = x + 1;
    println!("x = {}", x);
}
```

第二行的 `let x = x + 1;` 其實是在說：「我要建立一個**全新的** `x`，它的值是舊的 `x` 加 1。」舊的 `x` 就被蓋掉了，從此以後 `x` 就是 6。

你甚至可以連續 shadow 好幾次：

```rust,editable
fn main() {
    let x = 1;
    let x = x + 1; // x = 2
    let x = x * 3; // x = 6
    println!("x = {}", x);
}
```

### shadowing vs `mut`：最大的差別

「等等，這跟 `mut` 有什麼不一樣？不都是改值嗎？」

最大的差別是：**shadowing 可以換型別，mut 不行。**

```rust,editable
fn main() {
    // shadowing：可以從數字變成字串
    let x = 5;
    let x = "hello";
    println!("x = {}", x);
}
```

這完全合法！因為第二個 `let x` 是一個**全新的變數**，只是剛好同名而已。

但如果用 `mut` 試試看：

```rust,compile_fail
fn main() {
    let mut x = 5;
    x = "hello"; // ❌ 編譯錯誤！不能把字串塞進 i32
}
```

`mut` 只是讓你改「值」，型別還是鎖死的。但 shadowing 是建立一個全新的變數，所以型別可以完全不同。

### 實際用途

shadowing 最常見的用途是「轉換型別但保留名字」：

```rust,editable
fn main() {
    let input = "42"; // 這是字串
    let input = input.trim().parse::<i32>().expect("請輸入數字"); // 轉成數字，還是叫 input
    println!("input + 1 = {}", input + 1);
}
```

如果沒有 shadowing，你就得取兩個不同的名字，像 `input_str` 和 `input_num`，有點囉嗦。

### shadowing 和作用域

還記得第 1 章第 9 集學的作用域嗎？Shadowing 在大括號 `{}` 裡面也能用，而且出了大括號，遮蔽就會結束，舊的變數會「回來」：

```rust,editable
fn main() {
    let x = 1;
    {
        let x = 2; // 在這個區塊這行之後，x 被遮蔽為 2
        println!("區塊內 x = {}", x); // 2
    }
    println!("區塊外 x = {}", x);     // 1
}
```

大括號裡的 `let x = 2` 建立了一個新的 `x`，遮蔽了外面的 `x`。但這個遮蔽只在大括號裡面有效——一出大括號，新的 `x` 就消失了，原本的 `x`（值為 1）又可以使用了。

這跟 `mut` 完全不同。如果用 `mut` 在區塊裡改值，出了區塊值就真的變了：

```rust,editable
fn main() {
    let mut x = 1;
    {
        x = 2; // 直接改值，不是 shadowing
    }
    println!("x = {}", x); // 2
}
```

所以再強調一次：shadowing 是**建立新變數**，`mut` 是**改舊變數的值**。在作用域裡這個差別特別明顯。

## 重點整理

- 用 `let` 重新宣告同名變數叫做 shadowing
- 新的變數會蓋掉舊的
- 和 `mut` 最大的差別：**shadowing 可以換型別**
- 實際上每次 `let` 都是建立一個全新的變數，只是名字一樣
- 在大括號裡 shadow 的變數，出了大括號就消失，原本的變數會「回來」
