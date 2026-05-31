# `..` 忽略多個值

## 本集目標

學會用 `..` 一次忽略 `struct` 或 tuple 中多個不關心的值。

## 概念說明

上一集學了用 `_` 忽略一個值。但如果一個 `struct` 有很多欄位，而你只關心其中一兩個呢？每個不要的都寫 `_` 太麻煩了。

Rust 提供了 `..`（兩個點），意思是「剩下的我都不要了」。

### 在 `match` `struct` 時使用

```rust,editable
struct Player {
    id: i32,
    hp: i32,
    mp: i32,
    level: i32,
}

fn main() {
    let p = Player { id: 1, hp: 0, mp: 50, level: 10 };

    match p {
        Player { hp: 0, .. } => println!("這個玩家倒下了！"),
        Player { level, .. } => println!("等級 {}", level),
    }
}
```

`Player { hp: 0, .. }` 表示「`hp` 是 0，其他欄位我不管」。不用每個不要的欄位都寫 `_`。

`enum` 的 `struct` variant 也能這樣匹配，用法完全一樣。

### 在 `match` tuple 時使用

```rust,editable
# fn main() {
    let scores = (90, 85, 78, 92, 88);

    match scores {
        (first, ..) => println!("第一科：{}", first),
    }

    match scores {
        (.., last) => println!("最後一科：{}", last),
    }

    match scores {
        (first, .., last) => println!("第一科 {}，最後一科 {}", first, last),
    }
# }
```

`(first, ..)` 只取第一個，`(.., last)` 只取最後一個，`(first, .., last)` 取頭和尾。

tuple `struct` 和 `enum` 的 tuple variant 也能用類似的方式匹配，例如 `MyStruct(first, ..)` 或 `MyEnum::Variant(first, ..)`。

### 在陣列和切片裡使用

第 13 集學過 slice pattern，`..` 在陣列和切片裡也一樣好用：

```rust,editable
# fn main() {
let data: &[i32] = &[10, 20, 30, 40, 50];

match data {
    [first, .., last] => println!("頭 = {}，尾 = {}", first, last),
    [only] => println!("只有一個：{}", only),
    [] => println!("空的"),
}
# }
```

### 注意：`..` 只能出現一次

`..` 在一層的模式裡只能出現一次，因為如果出現兩次，Rust 會不知道中間的值怎麼分配。

## 範例程式碼

```rust,editable
struct Player {
    id: i32,
    hp: i32,
    mp: i32,
    level: i32,
}

fn main() {
    // struct 上使用 ..
    let p1 = Player { id: 1, hp: 100, mp: 50, level: 10 };

    match p1 {
        Player { hp, .. } => println!("HP = {}", hp),
    }

    let p2 = Player { id: 2, hp: 0, mp: 30, level: 5 };

    match p2 {
        Player { hp: 0, .. } => println!("這個玩家已經倒下了！"),
        Player { level, .. } => println!("等級 {}", level),
    }

    // tuple 上使用 ..
    let scores = (90, 85, 78, 92, 88);

    match scores {
        (first, ..) => println!("第一科：{}", first),
    }

    match scores {
        (.., last) => println!("最後一科：{}", last),
    }

    match scores {
        (first, .., last) => println!("第一科 {}，最後一科 {}", first, last),
    }

    // 切片上使用 ..
    let data: &[i32] = &[10, 20, 30, 40, 50];

    match data {
        [first, .., last] => println!("頭 = {}，尾 = {}", first, last),
        [only] => println!("只有一個：{}", only),
        [] => println!("空的"),
    }
}
```

## 重點整理

- `..` 用來一次忽略多個欄位或值
- `match` struct 時：`Player { hp, .. }` 只取 `hp`，其他全部忽略；`enum` 的 `struct` variant 也一樣
- `match` tuple 時：`(first, ..)` 只取第一個，`(.., last)` 只取最後一個；tuple `struct` 和 `enum` 的 tuple variant 用類似寫法
- 陣列和切片裡：`[first, ..]` 取第一個，`[first, .., last]` 取頭和尾
- `..` 在一層模式裡只能出現一次
