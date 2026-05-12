# 可變借用 `&mut`

## 本集目標

學會用 `&mut` 借用值並修改它，不需要 move 就能改變別人的資料。

## 概念說明

### 上一集的限制

上一集我們學了 `&` 借用，但借用是唯讀的——你只能看，不能改。如果我們想借別人的東西來修改呢？

### `&mut` 就是「借來改」

```rust
# fn main() {
    let mut x = 10;
    let r: &mut i32 = &mut x; // 可變借用
    *r = 20;                  // 透過 r 修改 x 的值
# }
```

幾個重點：

1. 原本的變數必須是 `let mut`（因為你要改它）
2. 借用時寫 `&mut x`
3. 要透過借用去修改值，要寫 `*r`（上一集學的解參考——順著借用找到原本的值）

### 函數參數用 `&mut`

更常見的用法是在函數裡：

```rust
fn add_ten(n: &mut i32) {
    *n += 10;
}

fn main() {
    let mut x = 5;
    add_ten(&mut x);
    println!("{}", x); // 15
}
```

函數拿到的是 `&mut i32`——一個**可變借用**。透過 `*n` 可以修改原本的值。呼叫時傳 `&mut x`。

### `struct` 的可變借用

對 `struct` 也一樣：

```rust,noplayground
# #[derive(Debug)]
# struct Point {
#     x: i32,
#     y: i32,
# }
#
fn move_right(p: &mut Point) {
    p.x += 1; // struct 的欄位不需要寫 *，Rust 會自動處理
}
#
# fn main() {}
```

注意：修改 `struct` 的欄位時，不需要寫 `(*p).x += 1`，直接寫 `p.x += 1` 就好——上一集提過 Rust 會自動解參考。

## 範例程式碼

```rust
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

// 透過可變借用修改整數
fn add_ten(n: &mut i32) {
    *n += 10;
}

// 透過可變借用修改 struct 的欄位
fn move_right(p: &mut Point) {
    p.x += 1;
}

fn move_up(p: &mut Point) {
    p.y += 1;
}

fn main() {
    // 修改整數
    let mut score = 80;
    println!("修改前：{}", score);
    add_ten(&mut score);
    println!("修改後：{}", score);

    // 修改 struct
    let mut pos = Point { x: 0, y: 0 };
    println!("起始位置：{:?}", pos);

    move_right(&mut pos);
    move_right(&mut pos);
    move_up(&mut pos);
    println!("移動後：{:?}", pos);

    // 直接用 &mut 修改
    let mut val = 100;
    let r = &mut val;
    *r += 50;
    println!("val = {}", val);
}
```

## 重點整理

- `&mut` 是可變借用，借來之後可以修改原本的值
- 原本的變數必須是 `let mut`
- 函數參數寫 `&mut Type`，呼叫時傳 `&mut value`
- 修改 `struct` 欄位可以直接寫 `r.field`（自動解參考）
- 下一集會學到可變借用的重要限制規則
