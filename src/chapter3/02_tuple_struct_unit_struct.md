# tuple `struct` 與 unit `struct`

## 本集目標

學會用 tuple `struct` 定義沒有欄位名的 `struct`，以及完全沒有欄位的 unit `struct`。

## 概念說明

上一集學的 `struct` 每個欄位都有名字。但有時候，欄位的意義已經很明顯了，不需要特別取名。這時候可以用 **tuple `struct`**——它長得像 tuple 和 `struct` 的混合體。

```rust,editable
struct Point(i32, i32);
#
# fn main() {}
```

建立值的時候用 `Point(3, 7)`——注意，這裡的 `Point` 既是**型別的名字**，也是**建立值時使用的名字**。取值用 `.0`、`.1`，就像 tuple 一樣。

上一集的 named-field `struct` 也是同樣的道理：`Point` 既是型別名，也是建立值時寫 `Point { x: 1, y: 2 }` 用的名字。

另外還有一種更極端的情況：`struct` 完全沒有欄位，叫做 **unit `struct`**。它通常用來當作一個「標記」，表示某種身份或角色，但本身不帶任何資料。

```rust,editable
struct Marker;
#
# fn main() {}
```

## 範例程式碼

```rust,editable
// tuple struct：欄位沒有名字，用位置存取
struct Point(i32, i32);

// 另一個 tuple struct 的例子
struct Color(i32, i32, i32);

// unit struct：完全沒有欄位
struct Marker;

fn main() {
    let p: Point = Point(3, 7);
    println!("x = {}, y = {}", p.0, p.1);

    let red: Color = Color(255, 0, 0);
    println!("R={}, G={}, B={}", red.0, red.1, red.2);

    // unit struct 建立時不需要括號或大括號
    let _m: Marker = Marker;
    println!("Marker 被建立了！（它不帶任何資料）");
}
```

## 重點整理

- **tuple `struct`**：`struct Point(i32, i32);`，用 `.0`、`.1` 取值
- **unit `struct`**：`struct Marker;`，沒有任何欄位
- tuple `struct` 適合欄位意義明顯、不需要命名的情況
- unit `struct` 適合當標記用，本身不攜帶資料
- 即使兩個 tuple `struct` 的欄位型別完全一樣，它們也是不同的型別（例如 `Point(i32, i32)` 和 `Size(i32, i32)` 不能互換）