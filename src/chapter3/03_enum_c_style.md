# `enum`（C-style）

## 本集目標

學會用 `enum` 定義一組固定的選項，讓變數只能是其中一個值。

## 概念說明

上一集我們學了 `struct`——用來定義「把多個值組合在一起」的新型別。這一集要學另一種定義新型別的方式：`enum`。

有時候我們想表達「這個東西只能是幾個選項之一」。比如說，一個交通燈只能是紅、黃、綠其中一種。

`enum`（enumeration，列舉）就是用來定義這種「多選一」的型別。和 `struct` 一樣，定義一個 `enum` 就是在告訴 Rust：「我要一個新的型別，它的值只能是這幾個選項之一。」最簡單的 `enum` 長這樣：

```rust
enum Color {
    Red,
    Green,
    Blue,
}
#
# fn main() {}
```

每一個選項叫做一個 **variant**（變體）。建立 `enum` 值的時候，要用 `型別名::變體名` 的寫法：

```rust
# enum Color {
#     Red,
#     Green,
#     Blue,
# }
#
# fn main() {
    let c = Color::Red;
# }
```

注意中間是兩個冒號 `::`，這在 Rust 裡叫做「路徑運算子」，表示「`Color` 底下的 `Red`」。

這種最基本的 `enum`——每個 variant 都不帶任何額外資料——有時候稱為 C-style `enum`，因為 C 語言的 `enum` 就是這樣。

## 範例程式碼

```rust
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn main() {
    let dir = Direction::Up;

    // 目前我們還不會用 enum 做太多事
    // 下一集會學 match，就能根據 enum 的值做不同的事情
    // 這邊先展示怎麼建立不同的 enum 值

    let _d1 = Direction::Down;
    let _d2 = Direction::Left;
    let _d3 = Direction::Right;

    println!("方向已經設定好了！");
    println!("（下一集學 match 之後，就能根據方向做不同的事）");
}
```

## 重點整理

- `enum` 和 `struct` 一樣，都是定義新型別的方式
- `struct`：把多個值組合在一起；`enum`：從多個選項中選一個
- 用 `::` 來指定是哪一個 variant，例如 `Direction::Up`
- C-style `enum` 的每個 variant 都不帶額外資料
- 和 `struct` 一樣，`enum` 定義一般放在 `fn main()` 外面，上面或下面都可以
- 目前還無法直接印出 `enum` 的值（下一集學 `match` 就可以了）
